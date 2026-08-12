"""Ataca al verificador del registro de congelamientos.

El verificador es la puerta que ofrece la garantia plena que §25.1 declara que
SQLite no puede dar. Una puerta que falla ABIERTA no es una puerta.

La revisión cruzada encontro justo eso: el parseo exigia `[0-9a-f]{64}` para reconocer una
entrada, asi que un SHA corrupto no producia un error — hacia desaparecer el
bloque. El verificador comprobaba las restantes y anunciaba que todas
reproducian, con salida 0.

Este guion corrompe el registro en memoria, sin tocar el archivo, y exige que el
verificador FALLE. Cada caso debe devolver 1.
"""

from __future__ import annotations

import io
import contextlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import verificar_congelamiento as V  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
ORIGINAL = (REPO / V.REGISTRO).read_text(encoding="utf-8")

# La version vigente se DERIVA, no se escribe. Esta suite la tenia a mano como
# «v2.15» y al pasar a v2.16 tres casos empezaron a apuntar a una entrada que ya
# no era la actual: dos fallaron y uno paso por falla abierta. Es la misma
# fragilidad que llevo todo el dia corrigiendo en el verificador — atar una
# comprobacion a un literal — cometida en la suite que la prueba.
VIG = "v%d.%d" % V.version_del_vigente()
ANTERIOR = "v%d.%d" % (V.version_del_vigente()[0], V.version_del_vigente()[1] - 1)

# El SHA de v2.10, que es el que se corrompe en la mayoria de los casos.
# La etiqueta admite sufijo de idioma desde que una entrada declara los dos:
# «SHA-256» a secas en las viejas, «SHA-256 (es)» en la vigente. Buscar solo la
# forma antigua reventaba aqui, en la propia suite, en cuanto el registro cambio
# de forma — y reventar al PARSEAR es mejor que pasar mirando la entrada
# equivocada, que es lo que habria hecho una expresion mas laxa.
SHA_V210 = re.search(
    r"## feriados y vacaciones · %s\b.*?\|\s*SHA-256(?:\s*\((?:es|en)\))?\s*\|"
    r"\s*`([0-9a-f]{64})`" % re.escape(VIG),
    ORIGINAL, re.S).group(1)


def sin_un_caracter(t: str) -> str:
    return t.replace("`%s`" % SHA_V210, "`%s`" % SHA_V210[:-1], 1)


def en_mayusculas(t: str) -> str:
    return t.replace("`%s`" % SHA_V210, "`%s`" % SHA_V210.upper(), 1)


def sin_fila_de_sha(t: str) -> str:
    """Quita TODAS las filas de SHA de la entrada vigente. Con una sola no basta
    desde que la entrada declara dos idiomas: quitar una deja la otra y el
    verificador denuncia el desemparejamiento —archivos y hashes en distinto
    numero—, que es un motivo correcto pero NO el que este caso prueba.
    """
    ini = t.index("## feriados y vacaciones · %s" % VIG)
    cab, cuerpo = t[:ini], t[ini:]
    return cab + re.sub(r"\| SHA-256(\s*\((?:es|en)\))? \| `[0-9a-f]{64}` \|\n",
                        "", cuerpo)


def sha_vacio(t: str) -> str:
    return re.sub(r"\| SHA-256(\s*\((?:es|en)\))? \| `%s` \|" % SHA_V210,
                  lambda m: "| SHA-256%s |  |" % (m.group(1) or ""),
                  t, count=1)


def sha_duplicado(t: str) -> str:
    """Filas de SHA de MAS. Desde que una entrada puede declarar dos idiomas, el
    limite ya no es una sino dos: para que el caso siga mordiendo hay que pasarse
    de dos, no de una. Un caso adversarial calibrado contra el limite viejo deja
    de probar nada en cuanto el limite se mueve, y por eso la suite comprueba que
    cada corrupcion CAMBIE el texto antes de darla por ejecutada.
    """
    m = re.search(r"\| SHA-256(\s*\((?:es|en)\))? \| `%s` \|" % SHA_V210, t)
    fila = m.group(0)
    return t.replace(fila, "\n".join([fila] * 3), 1)


def sin_comillas(t: str) -> str:
    return re.sub(r"\| SHA-256(\s*\((?:es|en)\))? \| `%s` \|" % SHA_V210,
                  lambda m: "| SHA-256%s | %s |" % (m.group(1) or "", SHA_V210),
                  t, count=1)


def archivo_a_ruta_traversa(t: str) -> str:
    """Travesia AISLADA: la ruta resuelve al vigente, que es byte-identico a la
    copia de v2.10, asi que su hash coincide. Sin esa igualdad el caso salia 1
    por discrepancia de hash y no probaba la regla de ruta plana — fallando por
    el motivo equivocado, que es el primer patron de esta serie. Lo encontro
    la revisión cruzada al ejecutar la suite sin la regla y ver que seguia saliendo 1.
    """
    return re.sub(
        r"\| Archivo(\s*\((?:es|en)\))? \| `docs/archivo/02-protocolo-%s\.md` \|"
        % re.escape(VIG),
        lambda m: "| Archivo%s | `docs/archivo/../02-protocolo.md` |"
                  % (m.group(1) or ""), t, count=1)


# --- Hallazgos de la revisión cruzada, rev140: la entrada entera desaparecia sin rastro y la
# --- version se forjaba, ambos con salida 0.

def registro_vacio(t: str) -> str:
    return "# Registro de congelamiento de protocolos\n"


def entrada_borrada(t: str) -> str:
    i = t.index("## feriados y vacaciones · %s" % ANTERIOR)
    j = t.index("## feriados y vacaciones · v2.11")
    return t[:i] + t[j:]


def etiquetas_con_homoglifos(t: str) -> str:
    """`А` y `Н` cirilicas, visualmente identicas a las latinas. El bloque se
    volvia invisible al parseo y el verificador anunciaba exito."""
    i = t.index("## feriados y vacaciones · v2.11")
    cab, cola = t[:i], t[i:]
    cola = cola.replace("| Archivo |", "| Аrchivo |", 1)
    cola = cola.replace("| SHA-256 |", "| SHА-256 |", 1)
    return cab + cola


def version_duplicada(t: str) -> str:
    i = t.index("## feriados y vacaciones · v2.11")
    return t + "\n\n---\n\n## " + t[i + 3:]


def version_apocrifa(t: str) -> str:
    i = t.index("## feriados y vacaciones · v2.11")
    bloque = t[i:].replace("v2.11", "v3.0")
    return t + "\n\n---\n\n## " + bloque[3:]


def entrada_apunta_a_otra_version(t: str) -> str:
    """Titulo de una version, archivo y hash de otra. Pasaba porque el titulo no
    se leia.

    TERCERA VEZ QUE LA ETIQUETA ROMPE UNA MUTACION, y ya es patron: al pasar el
    registro a dos idiomas —«Archivo (es)»— las mutaciones escritas contra la
    forma antigua dejan de morder una tras otra. Todas se ven porque la suite
    comprueba que su corrupcion CAMBIE el texto; si no, pasarian en verde. Lo que
    hay que recordar es que **un caso adversarial acoplado al formato exacto de
    lo que corrompe caduca con cada cambio de formato**, y caduca en silencio.
    """
    return re.sub(
        r"\| Archivo(\s*\((?:es|en)\))? \| `docs/archivo/02-protocolo-%s\.md` \|"
        % re.escape(ANTERIOR),
        lambda m: "| Archivo%s | `docs/archivo/02-protocolo-%s.md` |"
                  % (m.group(1) or "", VIG), t, count=1)


def excepcion_inexistente(t: str) -> str:
    return t.replace(
        "| `docs/archivo/02-protocolo-v2.3-correccion-editorial.md` |",
        "| `docs/archivo/02-protocolo-inventado.md` |", 1)


def esquema_actual_rancio(t: str) -> str:
    """Ensucia el hash de esquema DEL BLOQUE VIGENTE, y sólo de ese.

    La primera versión hacía `t.replace(linea, sucia, 1)` sobre el documento
    entero, dando por hecho que el hash del vigente aparece una sola vez. Deja de
    ser cierto en cuanto dos versiones consecutivas comparten esquema —v2.22 no
    lo cambió respecto de v2.21—: la corrupción caía en la entrada HISTÓRICA y el
    verificador reportaba otra cosa, así que el caso dejaba de probar lo suyo sin
    dejar de pasar por otras razones.

    Es la misma familia de error que ya me mordió con un reemplazo global sobre
    este registro: en un archivo append-only, tocar «la primera aparición»
    reescribe el pasado.
    """
    partes = re.split(r"(\n## )", t)
    for i, b in enumerate(partes):
        if re.search(r"^\|\s*Vigente\s*\|\s*si\s*\|", b, re.M | re.I):
            real = re.search(r"\| `schema/draft/001_schema\.sql` \| `([0-9a-f]{64})`",
                             b).group(1)
            partes[i] = b.replace(real, "c" * 64, 1)
            return "".join(partes)
    raise AssertionError("no hay bloque vigente en el registro")


def sin_marca_vigente(t: str) -> str:
    return t.replace("| Vigente | si |", "", 1)


def dos_marcas_vigentes(t: str) -> str:
    return t + "\n\n---\n\n## bloque intruso\n\n| | |\n|---|---|\n| Vigente | si |\n"


# --- Hallazgos de la revisión cruzada, rev145 y rev146 ------------------------------------

def entrada_vigente_borrada(t: str) -> str:
    """La mitad simetrica del B1: se borra la entrada de la version vigente.

    Con el archivo presente ya se detectaba como copia huerfana. Lo que NO se
    detectaba era borrar AMBOS lados: los dos conjuntos quedan mas pequenos pero
    igual de balanceados. El ancla externa —la version que el vigente declara en
    su propio encabezado— es lo que cierra esa variante, y este caso la prueba
    por la via del texto, sin tocar el disco.
    """
    i = t.index("## feriados y vacaciones · %s" % VIG)
    return t[:i].rstrip() + "\n"


def hueco_en_mitad_de_la_cadena(t: str) -> str:
    """Se borra una entrada intermedia. La cadena deja de ser contigua."""
    i = t.index("## feriados y vacaciones · v2.9")
    j = t.index("## feriados y vacaciones · %s" % ANTERIOR)
    return t[:i] + t[j:]


def hash_de_esquema_de_la_entrada_congelada(t: str) -> str:
    """Punto 4: la entrada congelada declara el hash del esquema y nadie lo
    comparaba. Coincidia con la realidad por accidente, porque el bloque vigente
    declara el mismo par; podia derivar sin alarma."""
    i = t.index("## feriados y vacaciones · %s" % VIG)
    cola = re.sub(r"\| `schema/draft/001_schema\.sql` \| `[0-9a-f]{64}` \|",
                  "| `schema/draft/001_schema.sql` | `%s` |" % ("d" * 64),
                  t[i:], count=1)
    return t[:i] + cola


def entrada_de_otra_serie_borrada(t: str) -> str:
    """Reproduccion A de la revisión cruzada, rev149. La serie v1 quedaba fuera del ancla del
    encabezado, porque el vigente es v2.x. El ancla de git no distingue series."""
    i = t.index("## feriados · v1.0")
    j = t.index("## feriados · v1.1")
    return t[:i] + t[j:]


def excepcion_blanquea_una_version(t: str) -> str:
    """El B1 de la revisión cruzada en su tercera vida, rev151. La tabla de excepciones era la
    unica salida del conjunto anclado y no estaba autenticada: bastaba una fila
    para des-congelar una version en silencio, con su archivo sin volver a
    hashear."""
    i = t.index("## feriados · v1.0")
    j = t.index("## feriados · v1.1")
    sin_entrada = t[:i] + t[j:]
    return sin_entrada.replace(
        "| `docs/archivo/02-protocolo-v2.3-correccion-editorial.md` |",
        "| `docs/archivo/02-protocolo-feriados-v1.0.md` | sacada del ancla |\n"
        "| `docs/archivo/02-protocolo-v2.3-correccion-editorial.md` |", 1)


def version_con_tres_componentes_en_el_titulo(t: str) -> str:
    """S1 de la revisión cruzada: el token de version no estaba anclado, asi que un titulo
    «· v2.15.1» parseaba v2.15 y se hacia pasar por la entrada vigente."""
    return t.replace("## feriados y vacaciones · %s" % VIG,
                     "## feriados y vacaciones · %s.1" % VIG, 1)


# Cada caso declara QUE MENSAJE espera, no solo que la salida sea 1. Es el cierre
# de la observacion de la revisión cruzada: su caso de travesia salia 1 tambien con la regla de
# ruta plana desactivada, o sea pasaba por el motivo equivocado. Comprobar solo el
# codigo de salida no distingue «detectado» de «detectado por otra cosa», y esa
# confusion es el primer patron de fallo de esta serie.
CASOS = [
    ("SHA de 63 caracteres",                sin_un_caracter,        "malformado"),
    ("SHA en mayusculas",                   en_mayusculas,          "malformado"),
    ("entrada sin fila de SHA-256",         sin_fila_de_sha,        "debe declarar una o dos"),
    ("fila de SHA-256 vacia",               sha_vacio,              "malformado"),
    ("filas de SHA-256 de mas en una entrada", sha_duplicado,      "debe declarar una o dos"),
    ("SHA sin comillas",                    sin_comillas,           "malformado"),
    ("archivo con travesia de ruta",        archivo_a_ruta_traversa, "copia plana"),
    ("registro vacio",                      registro_vacio,         "sin entrada en el registro"),
    ("entrada borrada entera",              entrada_borrada,        "%s.md" % ANTERIOR),
    ("homoglifos cirilicos en etiquetas",   etiquetas_con_homoglifos, "%s.md" % VIG),
    ("version duplicada",                   version_duplicada,      "duplicada"),
    ("version apocrifa v3.0",               version_apocrifa,       "v3.0"),
    ("titulo y archivo de versiones distintas", entrada_apunta_a_otra_version, "no corresponde a %s" % ANTERIOR),
    ("excepcion para archivo inexistente",  excepcion_inexistente,  "excepcion declarada"),
    ("hash de esquema actual rancio",       esquema_actual_rancio,  "001_schema.sql"),
    # La marca es lo que enciende el chequeo; perderla lo apaga, y eso ya paso dos
    # veces por renombrar el bloque. Ahora es un caso de prueba.
    ("marca `Vigente` borrada",             sin_marca_vigente,      "0 bloques con marca"),
    ("dos bloques marcados vigentes",       dos_marcas_vigentes,    "2 bloques con marca"),
    ("entrada de la version vigente borrada", entrada_vigente_borrada, "vigente declara %s" % VIG),
    ("hueco en mitad de la cadena",          hueco_en_mitad_de_la_cadena, "faltan entradas en la cadena"),
    ("hash de esquema de la entrada congelada", hash_de_esquema_de_la_entrada_congelada, "001_schema.sql"),
    ("entrada de otra serie borrada (v1.0)", entrada_de_otra_serie_borrada, "existio en el historial"),
    ("excepcion que blanquea una version", excepcion_blanquea_una_version, "excepcion invalida"),
    ("titulo con version de tres componentes", version_con_tres_componentes_en_el_titulo, "no declara una version"),
]


def correr(texto: str):
    """Devuelve (codigo, salida) del verificador contra un registro en memoria."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        codigo = V.main(texto=texto)
    return codigo, buf.getvalue()


def main() -> int:
    fallos = []

    print("== El registro intacto debe pasar ==")
    codigo, _ = correr(ORIGINAL)
    if codigo == 0:
        print("  OK         registro real, salida 0")
    else:
        print("  FALLA      el registro real no verifica (salida %d)" % codigo)
        fallos.append("registro real")

    print()
    print("== Registros corrompidos: el verificador debe FALLAR ==")
    for etiqueta, corromper, esperado in CASOS:
        texto = corromper(ORIGINAL)
        if texto == ORIGINAL:
            # Sin esto, un caso que no logra corromper nada se leeria como
            # 'detectado' cuando en realidad no se probo. Es el patron numero
            # uno de esta serie: pasar por el motivo equivocado.
            print("  INVALIDO   %-38s el caso no altero el registro" % etiqueta)
            fallos.append("%s (caso inefectivo)" % etiqueta)
            continue
        codigo, salida = correr(texto)
        if codigo != 1:
            print("  PASA       %-42s <-- FALLA ABIERTA (salida %d)"
                  % (etiqueta, codigo))
            fallos.append(etiqueta)
        elif esperado not in salida:
            # Salio 1, pero por otra cosa. Cuenta como no probado.
            print("  OTRO MOTIVO %-41s no menciona %r" % (etiqueta, esperado))
            fallos.append("%s (detectado por el motivo equivocado)" % etiqueta)
        else:
            print("  DETECTADO  %s" % etiqueta)

    # Reproduccion F de la revisión cruzada, rev149: BAJAR la version del encabezado del
    # vigente movia el ancla y dejaba borrar la entrada de arriba. Necesita
    # escribir un vigente falso, asi que va aparte del bucle de casos.
    print()
    print("== El ancla no se mueve editando el encabezado del vigente ==")
    import tempfile, shutil, os
    i = ORIGINAL.index("## feriados y vacaciones · %s" % VIG)
    sin_v215 = ORIGINAL[:i].rstrip() + "\n"
    tmp = tempfile.mkdtemp()
    os.makedirs(tmp + "/docs")
    bajado = (REPO / "docs/02-protocolo.md").read_text().replace(
        "anuales · %s" % VIG, "anuales · v2.1", 1)
    (pathlib.Path(tmp) / "docs/02-protocolo.md").write_text(bajado)
    orig_vig = V.VIGENTE
    V.VIGENTE = tmp + "/docs/02-protocolo.md"
    try:
        codigo, salida = correr(sin_v215)
    finally:
        V.VIGENTE = orig_vig
        shutil.rmtree(tmp)
    # ESTE CASO DEPENDE DEL ESTADO DE GIT, y decirlo ahorra el desconcierto que
    # ya costo dos veces. La comprobacion que se ejercita —«toda copia que
    # ALGUNA VEZ existio debe tener entrada»— se ancla en el historial, asi que
    # con la copia del vigente recien creada y SIN COMMITEAR, git no la ve y el
    # verificador denuncia por otro motivo: orfandad en disco. Detecta la
    # corrupcion igual, pero no por la via que este caso prueba.
    import subprocess as _sp
    _r = _sp.run(["git", "ls-files", "--error-unmatch",
                  "docs/archivo/02-protocolo-%s.md" % VIG],
                 capture_output=True, cwd=REPO)
    if _r.returncode != 0:
        print("  OMITIDO    la copia archivada de %s aun no esta en git; este "
              "caso\n             se ancla en el historial y no puede "
              "ejercitarse hasta el commit" % VIG)
    elif codigo == 1 and "existio en el historial" in salida:
        print("  DETECTADO  encabezado bajado a v2.1 + entrada %s borrada" % VIG)
    else:
        print("  PASA       el ancla se movio con el encabezado   <-- FALLA (salida %d)"
              % codigo)
        fallos.append("el ancla se mueve editando el encabezado del vigente")

    # El symlink no se puede montar en memoria: necesita sistema de archivos.
    # Va aparte, con limpieza garantizada, porque escribe en el repo.
    print()
    print("== Enlace simbolico en docs/archivo/ (toca disco) ==")
    señuelo = REPO / "docs/archivo/02-protocolo-v99.99.md"
    try:
        señuelo.symlink_to("../02-protocolo.md")
        codigo, salida = correr(ORIGINAL)
        if codigo == 1 and "enlace simbolico" in salida:
            print("  DETECTADO  señuelo con nombre de copia congelada")
        else:
            print("  PASA       señuelo no detectado (salida %d)   <-- FALLA" % codigo)
            fallos.append("enlace simbolico en docs/archivo/")
    finally:
        if señuelo.is_symlink():
            señuelo.unlink()
    if señuelo.exists() or señuelo.is_symlink():
        fallos.append("el señuelo no se limpio: %s" % señuelo)

    print()
    if fallos:
        print("FALLAN %d comprobaciones:" % len(fallos))
        for f in fallos:
            print("  - %s" % f)
        return 1
    print("Verificador: %d corrupciones detectadas por su motivo exacto, "
          "ninguna falla abierta." % len(CASOS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
