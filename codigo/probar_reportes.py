"""Compuertas del sistema de reportes, y todas son ejecutables.

UNA COMPUERTA O ES EJECUTABLE O NO ES COMPUERTA. Y hay una segunda regla, que
este proyecto ya pagó: **una compuerta que grita se apaga, y apagada deja de
proteger a las demás.** Por eso la prueba de cifras literales tiene escapes
declarados y cortos en vez de señalar cada dígito de la prosa.

  C1   Ningún número de RESULTADO tecleado en la prosa de D1.
  C2   D1 lleva las advertencias obligatorias.
  C3   Todos los documentos del paquete comparten el mismo snapshot.
  C4   El paquete no está completo sin su manifiesto de exclusiones.
  C5   Ni notas internas, ni nombres de sesión, ni identificadores privados.
  C10  El paquete no se contradice a sí mismo: enlaces y hashes.
  C11  El paquete se reproduce a sí mismo desde sus capturas.

ESTE ENCABEZADO DECÍA «CUATRO, Y LAS CUATRO SON EJECUTABLES» cuando ya eran once,
y la lista se quedó en C5. Es exactamente lo que las compuertas persiguen —un
rótulo afirmando lo que el cuerpo niega— escrito en la primera línea del guion
que existe para impedirlo. El recuento ya no se teclea: el cierre lo deriva de la
lista, que es la única cifra de este archivo que no puede mentir. La ENUMERACIÓN
sigue siendo a mano y hay que mantenerla; por eso ahora no lleva número delante.

Uso:  python3 scripts/probar_reportes.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SALIDA = REPO / "reportes"
PLANTILLA = REPO / "plantillas/D1-reporte-principal.md"

fallos: list[str] = []


# --- C1 · ninguna cifra de resultado tecleada -----------------------------

# Lo que SÍ puede llevar dígitos sin ser un resultado. La lista es corta a
# proposito: cada entrada que se añade es un sitio donde la compuerta deja de
# mirar, y una lista larga acaba no protegiendo nada.
ESCAPES = [
    re.compile(r"\{\{q:[a-z0-9_]+\}\}"),        # la propia marca de consulta
    re.compile(r"§\s?\d+(\.\d+)*"),             # referencia al protocolo
    re.compile(r"\bv\d+\.\d+\b"),               # version del protocolo
    re.compile(r"\bart(ículo|\.)\s*\d+"),       # articulo de una norma
    re.compile(r"\b(19|20)\d{2}\b"),            # años: cortes y fechas de norma
    re.compile(r"\bCC BY 4\.0\b|\bcff-version: [\d.]+"),
    re.compile(r"^\s*\|?\s*\d+\.\s", re.M),      # numeracion de listas
    re.compile(r"^#{1,6} \d+(\.\d+)*\.?\s", re.M),  # numeracion de secciones
    # Bloque de EVIDENCIA CITADA: valores publicados por un tercero que se
    # reproducen tal cual. No son resultados nuestros y no pueden salir de una
    # consulta nuestra. El bloque se abre y se cierra explicitamente para que el
    # escape sea estrecho y visible en la fuente.
    re.compile(r"<!-- citado:.*?-->.*?<!-- /citado -->", re.S),
    # BLOQUE HISTORICO, y por que NO se mete dentro de `citado`. Las cifras que
    # narran un error nuestro pasado —«decia 126 de 250, y 126 mas 77 dan 203»—
    # tampoco pueden salir de una consulta: la consulta devuelve el valor
    # CORRECTO y borra lo que la frase estaba contando. El registro del error se
    # autocorregiria y la leccion desapareceria.
    #
    # Pero no son de un tercero: son NUESTROS valores publicados ayer. Meterlas
    # en `citado` seria mentir sobre su procedencia para pasar una compuerta, que
    # es la forma exacta de fingimiento que este proyecto persigue. La distincion
    # es de la revisión de plantillas y es correcta: bloque propio, nombrado por lo que
    # es. Se abre y se cierra explicitamente para que el escape sea estrecho y
    # visible en la fuente, igual que el de citado.
    re.compile(r"<!-- historico:.*?-->.*?<!-- /historico -->", re.S),
    # Rotulo de cuadro o figura: «**Cuadro 3.** Descomposicion…». Es una etiqueta
    # en su punto de DEFINICION, igual que el numero de una seccion en su
    # encabezado.
    #
    # Y a proposito NO se escapa la referencia cruzada —«ver el cuadro 3»—: esa
    # si envejece al reordenar, que es justo por lo que quite «la seccion 6» de
    # la version anterior en vez de ensanchar el escape. El rotulo se define una
    # vez; la referencia se queda vieja sola.
    re.compile(r"\*\*(Cuadro|Figura) \d+\.\*\*"),
    # Los mismos dos, en ingles. Sin ellos la version inglesa salia con diez
    # cifras desnudas que son rotulos y citas, no resultados.
    re.compile(r"\*\*(Table|Figure) \d+\.\*\*"),
    re.compile(r"\barticle\s*\d+"),
    # UNA FECHA COMPLETA FILTRA DOS CIFRAS, y vale para los dos idiomas. El
    # escape de anios se lleva el «2026» de «2026-08-11» y deja sueltos el mes y
    # el dia, que C1 denuncia como cifras tecleadas. Lo caza escapando la fecha
    # ENTERA antes de que el escape de anios la parta.
    re.compile(r"\b(19|20)\d{2}-\d{2}-\d{2}\b"),
    # RUTA ENTRE COMILLAS INVERTIDAS. Los nombres de archivo con prefijo
    # numerico —`docs/10-hallazgos.md`, `docs/00-ESTADO.md`— son rutas, no
    # resultados. Lo propuso la sesion de reportes ya verificado en las dos
    # direcciones, y es estrecho a proposito: exige separador de directorio o
    # extension, asi que sigue vigilando `47` y `0,89` sueltos entre comillas.
    re.compile(r"`[^`\s]*(?:/[^`\s]*|\.[a-z]{2,4})[^`\s]*`"),
]

# NUMEROS ESCRITOS CON LETRA. La observacion es de la revisión cruzada y es la mejor critica
# que ha recibido esta compuerta: si vigila digitos y exceptua las palabras,
# exceptua el agujero por el que se cuela justo lo que persigue. Se escribieron
# afirmaciones de dato en letra —«la mayor separacion es de tres puestos»— el
# mismo dia en que ese dato se movio cinco veces.
#
# Pero no todas las palabras son iguales, y por eso hay DOS listas.
#
# Los sustantivos DUROS nombran cosas que solo salen de una consulta: puestos,
# posiciones, porcentajes, jurisdicciones. Un numero en letra junto a uno de
# ellos es un resultado tecleado, y la compuerta FALLA.
NUMERO_ES = (r"cero|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|"
             r"trece|catorce|quince|dieciséis|diecisiete|dieciocho|veinte|treinta|"
             r"cuarenta|cincuenta")
# `un`/`una` quedan FUERA en castellano: son casi siempre articulo —«un dia
# habil»— y meterlos convertia la compuerta en ruido puro, que es como se
# desactivan.
#
# `one` SI entra en ingles, y no es una inconsistencia: en ingles `one` es casi
# siempre numeral —«one jurisdiction», «one day»— y no articulo. La compuerta
# inglesa gana ahi una cobertura que la castellana no puede tener.
NUMERO_EN = (r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
             r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
             r"twenty|thirty|forty|fifty")

IDIOMAS = {
    "es": {
        "plantillas": [REPO / "plantillas/D1-reporte-principal.md",
                       REPO / "plantillas/README-es.md",
                       REPO / "plantillas/hallazgos-es.md"],
        # DUROS: nombran cosas que solo salen de una consulta. FALLA.
        # LOS SUSTANTIVOS SE AMPLIARON, y la razon la trajo la revision externa
        # midiendo mejor que yo. Yo habia probado detectar CUANTIFICADORES
        # —unico, casi todos, mayoritariamente— y lo descarte con razon: 22
        # impactos y 8 escapes retoricos legitimos, la lista larga que acaba no
        # protegiendo nada.
        #
        # La especificacion buena es otra: **cuatro de los cinco defectos reales
        # de estos dos dias fueron NUMEROS tecleados, no palabras vagas.** «Las
        # reformas verificadas son dos», «43 de 45», «dos unidades», «tres de las
        # ocho unidades». Los numeros tienen firma sintactica y los
        # cuantificadores no. Medido sobre las plantillas con los escapes de
        # arriba aplicados: **un impacto**, y ese se arreglo quitando el recuento
        # de una frase que ya enumeraba su propia lista.
        #
        # `casos` queda FUERA a proposito: «en los dos casos» es idiomatico y lo
        # metia todo en ruido. Un sustantivo que produce mas falsos que ciertos
        # apaga la compuerta, y apagada no protege a las demas.
        "duro": re.compile(r"\b(%s)\s+(puestos?|posiciones?|por ciento|veces|"
                           r"jurisdicci(?:ón|on|ones)|unidades?|pa[ií]ses|"
                           r"fichas|celdas|reformas)\b" % NUMERO_ES, re.I),
        # BLANDOS: abundan en descripcion legal legitima. AVISA y no falla,
        # porque una compuerta que grita ante cada frase de derecho comparado se
        # apaga, y apagada no protege a las demas.
        "blando": re.compile(r"\b(%s)\s+(días?|semanas?|feriados?)\b"
                             % NUMERO_ES, re.I),
        "potencial": ("pued", "podría", "podria"),
    },
    "en": {
        "plantillas": [REPO / "plantillas/D1-main-report.md",
                       REPO / "plantillas/README-en.md",
                       REPO / "plantillas/hallazgos-en.md"],
        "duro": re.compile(r"\b(%s)\s+(places?|positions?|per ?cent|percent|"
                           r"times|jurisdictions?|units?|countries|records|"
                           r"cells|reforms)\b" % NUMERO_EN, re.I),
        "blando": re.compile(r"\b(%s)\s+(days?|weeks?|holidays?)\b"
                             % NUMERO_EN, re.I),
        "potencial": ("can ", "could ", "may ", "might "),
    },
}


def c1_sin_cifras_tecleadas() -> None:
    """Se corre sobre TODAS las plantillas, no solo la castellana.

    Cuando el paquete paso a bilingue, C1 seguia mirando un solo archivo y
    decia OK. El ingles no tenia ninguna proteccion contra un resultado tecleado
    —ni en cifra ni en letra— y la compuerta lo certificaba igual. Una compuerta
    que solo vigila una de las dos salidas es peor que no tenerla, porque su
    verde afirma las dos.
    """
    for idioma, cfg in IDIOMAS.items():
        for ruta in cfg["plantillas"]:
            if not ruta.exists():
                print("  AVISO  C1  falta «%s»; nada que vigilar" % ruta.name)
                continue
            _c1_una("%s·%s" % (idioma, ruta.stem.split("-")[0]), cfg,
                    ruta.read_text(encoding="utf-8"))


def _c1_una(idioma: str, cfg: dict, txt: str) -> None:
    # Se vigila la PLANTILLA, no el documento compilado: en el compilado todo
    # numero es legitimo porque ya paso por una consulta. Lo que hay que impedir
    # es que alguien teclee uno en la fuente.
    limpio = txt
    for e in ESCAPES:
        limpio = e.sub(" ", limpio)
    desnudos = sorted(set(re.findall(r"(?<![\w.])\d[\d.,]*(?![\w])", limpio)))
    # Las citas textuales llevan sus propias cifras y son evidencia, no un
    # resultado nuestro. Van entre comillas angulares y se descuentan.
    citadas = set()
    for cita in re.findall(r"«[^»]*»", txt):
        citadas.update(re.findall(r"\d[\d.,]*", cita))
    desnudos = [d for d in desnudos if d not in citadas]
    if desnudos:
        print("  FALLA  C1  [%s] cifras tecleadas en la plantilla: %s"
              % (idioma, ", ".join(desnudos[:12])))
        fallos.append("C1")
    else:
        print("  OK     C1  [%s] ninguna cifra de resultado tecleada" % idioma)

    # LA SALIDA, Y POR QUE ES CONTADA. La compuerta no sabe distinguir «dos
    # jurisdicciones NO EXISTEN en el antecedente», que es un recuento nuestro,
    # de «dos jurisdicciones PUEDEN tener el mismo total», que es una
    # ilustracion. Sin salida obliga a marcar lo que no es dato y acaba borrada;
    # con salida silenciosa, se vacia sola. Existe, es explicita —«<!--d-->»
    # pegado detras— y se CUENTA en voz alta.
    duros, exentos = [], 0
    for m in cfg["duro"].finditer(txt):
        cola = txt[m.end():m.end() + 70]
        cabeza = txt[max(0, m.start() - 70):m.start()]
        # EL MODO POTENCIAL NO ESTA EN EL MISMO SITIO EN LOS DOS IDIOMAS. En
        # castellano va en el verbo que sigue —«dos jurisdicciones PUEDEN
        # diferir»— y bastaba mirar la cola. En ingles el modal puede ir detras
        # —«two jurisdictions CAN differ»— o delante —«there can be two
        # jurisdictions…»—, asi que se miran las DOS ventanas. Se hace igual en
        # castellano porque «pueden coincidir dos jurisdicciones» tambien es
        # hipotetico y la cola no lo veia.
        cola_b, cabeza_b = cola.lower(), cabeza.lower()
        if any(t in cola_b or t in cabeza_b for t in cfg["potencial"]):
            continue
        if cola[:8] == "<!--d-->":
            exentos += 1
        else:
            duros.append(m.group(0))
    if duros:
        for l in duros[:6]:
            print("  FALLA  C1  [%s] resultado escrito con letra: «%s»" % (idioma, l))
        print("            Un puesto, un porcentaje o un recuento de unidades sale "
              "de una consulta.\n            En letra o en cifra, tecleado es "
              "tecleado.")
        fallos.append("C1")
    if exentos:
        print("  AVISO  C1  [%s] %d frase(s) marcadas como descriptivas con "
              "«<!--d-->». Si crecen, revise." % (idioma, exentos))
    blandos = cfg["blando"].findall(txt)
    if blandos:
        print("  AVISO  C1  [%s] numeros en letra junto a dias, semanas o "
              "feriados: %s" % (idioma, ", ".join(" ".join(l) for l in blandos[:6])))
        print("            No falla: en descripcion legal suelen ser legitimos. "
              "Compruebe que ninguno sea un resultado.")


def c1_casos_adversariales() -> None:
    """C1 vigila dos idiomas, y una compuerta que nunca dispara no prueba nada.

    Estos casos existen porque al escribir la version inglesa aparecieron dos
    huecos que la plantilla real no habria destapado: el SINGULAR faltaba en las
    dos listas —«one jurisdiction» y «una unidad» son recuentos igual que sus
    plurales— y la deteccion del modo potencial iba sensible a mayusculas, asi
    que «Pueden coincidir dos jurisdicciones» al principio de frase se
    denunciaba como resultado.
    """
    CASOS = [
        ("en", "The gap is three positions wide.", True),
        ("en", "Two jurisdictions can differ by one day.", False),
        ("en", "One jurisdiction has no 2016 cut.", True),
        ("en", "Coverage reached fifty per cent of the set.", True),
        ("en", "There can be two jurisdictions with the same total.", False),
        ("es", "La mayor separación es de tres puestos.", True),
        ("es", "Dos jurisdicciones pueden diferir en un día.", False),
        ("es", "Pueden coincidir dos jurisdicciones distintas.", False),
        ("es", "Tres jurisdicciones no tienen corte de 2016.", True),
        ("es", "Dos unidades del grupo no están en la base.", True),
    ]
    import contextlib
    import io as _io
    malos = []
    for idi, txt, debe in CASOS:
        antes = list(fallos)
        with contextlib.redirect_stdout(_io.StringIO()):
            _c1_una(idi, IDIOMAS[idi], txt)
        salta = len(fallos) > len(antes)
        del fallos[len(antes):]
        if salta != debe:
            malos.append("[%s] «%s» %s" % (idi, txt[:44],
                                           "no salta" if debe else "salta de mas"))
    if malos:
        print("  FALLA  C1  la compuerta no se comporta en %d caso(s): %s"
              % (len(malos), "; ".join(malos[:4])))
        fallos.append("C1")
    else:
        print("  OK     C1  los %d casos adversariales de las dos lenguas se "
              "comportan" % len(CASOS))


def c1_los_desgloses_suman() -> None:
    """Un desglose publicado tiene que sumar su total. Lo pidio
    la revisión de plantillas y el caso es casi literario: el parrafo que lleva ese
    desglose NARRA que una version anterior no sumaba —«126 de 250», y 126 mas
    77 dan 203— y que el verificador solo vigilaba el total.

    O sea que el documento cuenta el defecto y hasta hoy nada impedia repetirlo:
    las seis filas podian volver a no cuadrar con las seis compuertas en verde.
    Emitir cada fila por marca quita el desfase pero NO la incoherencia — seis
    consultas correctas pueden seguir sin sumar si una mide otra cosa, que es
    exactamente lo que estuvo a punto de pasar cuando `fuentes_n3` iba a ir
    donde la prosa decia «nivel 3-4».
    """
    import sqlite3 as _s
    import sys as _sy
    _sy.path.insert(0, str(Path(__file__).resolve().parent))
    from reportes_nucleo import BASE, construir_registro
    reg = construir_registro(_s.connect(BASE))

    def num(k):
        return float(str(reg[k]).replace("\u2212", "-").replace(",", "."))

    DESGLOSES = [
        ("fuentes por nivel", ["fuentes_n1", "fuentes_n2", "fuentes_n3",
                               "fuentes_n4", "fuentes_n5", "fuentes_sin_nivel"],
         "fuentes"),
    ]
    malos = []
    for etiqueta, partes, total in DESGLOSES:
        falta = [k for k in partes + [total] if k not in reg]
        if falta:
            malos.append("%s: no existen %s" % (etiqueta, ", ".join(falta)))
            continue
        suma = sum(num(k) for k in partes)
        if abs(suma - num(total)) > 0.01:
            malos.append("%s: las partes suman %g y el total dice %g"
                         % (etiqueta, suma, num(total)))
    if malos:
        print("  FALLA  C1  un desglose no cuadra: %s" % "; ".join(malos))
        fallos.append("C1")
    else:
        print("  OK     C1  los %d desglose(s) publicados suman su total"
              % len(DESGLOSES))


def c1_sin_fuga_de_idioma() -> None:
    """Ninguna palabra del otro idioma en el documento emitido.

    La propuso la revisión de plantillas despues de abrir el PDF ingles y encontrarlo con
    las CUATRO tablas en castellano —encabezados y nombres de pais— mientras las
    siete compuertas pasaban y los numeros salian bien convertidos alrededor.

    Su diagnostico es el que hay que recordar: **la compuerta de paridad ve la
    MARCA, no lo que la marca devuelve.** Una marca es una caja negra para ella, y
    dentro de aquellas cuatro habia castellano. Mismo fallo que los rotulos
    dentro de una imagen, una capa mas adentro.

    Es tosca a proposito y ella lo dijo primero: busca palabras que solo existen
    en un idioma y falla. No es elegante y tiene falsos positivos —«vacaciones
    dignas» es el nombre propio de una reforma mexicana y debe quedarse en
    ingles— y por eso hay una lista corta de excepciones, declarada. Lo que
    consigue es convertir en RUIDOSO un fallo que hoy es invisible, que es
    exactamente el trato que este proyecto le da a esta familia.
    """
    # Con limite de palabra a los DOS lados. Sin el de la derecha, «median»
    # casaba dentro de «mediana» y la compuerta denunciaba al documento
    # castellano por escribir castellano. Los ingleses son subcadenas de sus
    # equivalentes espanoles mas veces de lo que parece.
    DELATORAS = {
        "en": ("días", "día", "feriados", "vacaciones", "jurisdicción",
               "mediana", "medianas", "semana", "semanas", "país", "descanso"),
        "es": ("days", "holidays", "jurisdiction", "jurisdictions", "median",
               "week", "weeks", "country", "countries"),
    }
    # Nombres propios que viajan sin traducir y contienen una palabra delatora.
    EXCEPCIONES = ("vacaciones dignas", "Ley de Vacaciones", "días de asueto")
    for idi, cfg in IDIOMAS.items():
        doc = SALIDA / ("D1-main-report.md" if idi == "en"
                        else "D1-reporte-principal.md")
        if not doc.exists():
            continue
        txt = doc.read_text(encoding="utf-8")
        # LO CITADO NO CUENTA, y es la mayor fuente de falsos positivos. El
        # documento castellano reproduce literales de normas en su idioma
        # —«24 working days if 6 days week» de la nota alemana— y esas palabras
        # inglesas son evidencia, no una fuga. Se descuentan las comillas
        # angulares, que es como este proyecto marca la cita, y los bloques
        # `citado`. Es la misma excepcion que C1 ya aplica a las cifras.
        txt = re.sub(r"«[^»]*»", " ", txt)
        txt = re.sub(r"<!-- citado:.*?-->.*?<!-- /citado -->", " ", txt, flags=re.S)
        for e in EXCEPCIONES:
            txt = txt.replace(e, " ")
        fugas = sorted({p for p in DELATORAS[idi]
                        if re.search(r"\b%s\b" % re.escape(p), txt, re.I)})
        if fugas:
            print("  FALLA  C1  [%s] palabras del otro idioma en el documento "
                  "emitido: %s" % (idi, ", ".join(fugas[:8])))
            print("            Una marca es una caja negra para la paridad: "
                  "comprueba que lo que\n            devuelve hable el idioma "
                  "del documento, no solo que exista.")
            fallos.append("C1")
        else:
            print("  OK     C1  [%s] el documento emitido no mezcla idiomas" % idi)


def c1_formato_numerico_del_idioma() -> None:
    """En un documento castellano ninguna CANTIDAD lleva punto decimal, y al
    reves en el ingles.

    Es un HUECO ENTRE COMPUERTAS y no dentro de una, que es la octava forma de
    la familia y la primera que no consiste en que algo enmudezca sino en que
    nadie tenia el encargo. C1 vigila que no se tecleen cifras, y estas salen de
    una consulta: legitimas. La compuerta de idioma busca palabras del otro
    idioma, y «4.29» no es una palabra. La de paridad compara estructura y
    marcas, no formato. Cada una hacia bien su trabajo.

    El caso vivio un dia entero en 27 apendices castellanos, y era literalmente
    el caso testigo con el que se escribio `FORMATO.md`: «el mismo numero sale
    21,4 en D1 y 21.4 en D2, dentro del mismo paquete». Lo encontro
    la revisión de plantillas mirando, no razonando.

    Y la internacionalizacion lo volvia mas raro, no menos: el apendice INGLES lo
    tenia bien por accidente, porque el punto es correcto en ingles. El defecto
    era invisible en la mitad del paquete donde no lo era.

    LOS TRES DESCUENTOS VAN DECLARADOS porque son los que hacen fallar la
    medicion, y le costaron dos intentos a quien la propuso: identificadores de
    norma —«Ley 27.802», «RS 822.11»—, referencias de seccion y de articulo
    —«§34.2», «articulos 37.2»— y lo citado entre comillas angulares o
    invertidas. Sin ellos la comprobacion denuncia el numero de una ley suiza.
    """
    IDENT = [
        re.compile(r"«[^»]*»"),
        re.compile(r"`[^`]*`"),
        re.compile(r"§\s?\d+(\.\d+)*"),
        # NUMERACION DE ENCABEZADO. «### 5.5. La union no es una particion» no es
        # una cantidad de cinco y medio: es la seccion. Mi primera version solo
        # descontaba «§N.N» y denuncio el indice del propio documento.
        re.compile(r"(?m)^#{1,6}\s+\d+(\.\d+)*\.?"),
        # Numero de norma: va detras de su palabra, en cualquiera de las lenguas
        # del corpus, porque el nombre de la norma no se traduce.
        re.compile(r"(?i)\b(ley|leyes|decreto|lei|loi|legge|act|wet|besluit|"
                   r"n\.º|nr\.|no\.|núm\.?|art(?:iculo|ículo|\.)?s?|"
                   # Colecciones sistematicas suizas: «RS 822.11», «LS 822.4».
                   # No llevan la palabra «ley» delante y por eso no bastaba la
                   # lista anterior.
                   r"RS|LS|SR)\s*[\d.,/-]+"),
        # Identificador con tres decimales: ninguna cantidad de este proyecto los
        # tiene, y las numeraciones de norma —«13.000173», «27.802»— si.
        re.compile(r"(?<![\w.])\d+[.,]\d{3,}(?![\w])"),
    ]
    SEPARADOR = {"es": re.compile(r"(?<![\w.,])\d+\.\d+(?![\w.,])"),
                 "en": re.compile(r"(?<![\w.,])\d+,\d+(?![\w.,])")}
    DOCS = {"es": ["D1-reporte-principal.md", "D2-paises", "D3-verificacion",
                   "LEEME.md"],
            "en": ["D1-main-report.md", "README.md"]}
    for idi, entradas in DOCS.items():
        malos = []
        for nombre in entradas:
            ruta = SALIDA / nombre
            for doc in (sorted(ruta.glob("*.md")) if ruta.is_dir()
                        else [ruta] if ruta.exists() else []):
                t = doc.read_text(encoding="utf-8")
                for e in IDENT:
                    t = e.sub(" ", t)
                hit = SEPARADOR[idi].findall(t)
                if hit:
                    malos.append("%s (%s)" % (doc.relative_to(SALIDA), hit[0]))
        if malos:
            print("  FALLA  C1  [%s] cantidades con el separador decimal del otro "
                  "idioma en %d documento(s): %s"
                  % (idi, len(malos), ", ".join(malos[:5])))
            fallos.append("C1")
        else:
            print("  OK     C1  [%s] toda cantidad usa el separador decimal de su "
                  "idioma" % idi)


# --- C2 · las advertencias obligatorias -----------------------------------

OBLIGATORIAS = [
    ("unidad de conteo", r"unidad de conteo",
     "sin ella el número de vacaciones no es comparable entre países"),
    ("ausencia no verificada", r"[Aa]usencia no verificada no es ausencia",
     "un delta de cero puede ser «no hubo reforma» o «no se buscó»"),
    ("no más exactos", r"[Nn]o afirmamos ser más exactos",
     "el trabajo afirma auditabilidad, no exactitud superior"),
    # LA ADVERTENCIA SIGUE SIENDO OBLIGATORIA Y SU SUJETO CAMBIO. Se llamaba «la
    # tasa no se extrapola» cuando el paquete publicaba una tasa. Ya no la
    # publica —la medicion de fiabilidad quedo interna por decision del
    # principal— y lo que no se extrapola es el EJERCICIO: describe la muestra
    # doblemente codificada, no el conjunto. El aviso no sobra porque el
    # documento sigue mencionando que el ejercicio se hizo, y una mencion sin
    # esta salvedad invita a leerla como propiedad del dataset entero.
    ("el ejercicio de fiabilidad no se extrapola", r"[Nn]o se extrapola",
     "describe la muestra doblemente codificada, no el conjunto"),
    ("jurisdicción, no país", r"jurisdicción, no un país|no es el país",
     "en un federal sin ley nacional «el número del país» no existe"),
]


def c2_advertencias() -> None:
    doc = SALIDA / "D1-reporte-principal.md"
    if not doc.exists():
        print("  FALLA  C2  no hay D1 compilado")
        fallos.append("C2")
        return
    txt = doc.read_text(encoding="utf-8")
    # El texto se aplana antes de buscar: una advertencia partida por un salto
    # de linea SI esta, y un test que la da por ausente es un falso positivo — y
    # los falsos positivos son como se desactivan las compuertas.
    plano = " ".join(txt.split())
    faltan = [(n, p) for n, r, p in OBLIGATORIAS if not re.search(r, plano)]
    if faltan:
        for n, porque in faltan:
            print("  FALLA  C2  falta la advertencia «%s» — %s" % (n, porque))
        fallos.append("C2")
    else:
        print("  OK     C2  las %d advertencias obligatorias están en D1"
              % len(OBLIGATORIAS))


# --- C3 · un solo snapshot ------------------------------------------------

def c3_snapshot_unico() -> None:
    docs = sorted(SALIDA.rglob("*.md"))
    if not docs:
        print("  FALLA  C3  no hay documentos compilados")
        fallos.append("C3")
        return
    hallazgos: dict[str, set] = {}
    sin_portada = []
    # `datos/` es el subarbol de la exportacion y trae su propia procedencia en
    # `datos/MANIFEST.csv`; se comprueba aparte, mas abajo. Y la licencia no es
    # un documento de datos: sus condiciones no dependen del snapshot.
    EXENTOS = {"LICENCIA.md"}
    # SUBARBOLES QUE VIAJAN TAL CUAL. `metodo/` lleva el protocolo y su registro
    # de congelamiento; `codigo/`, los guiones; `capturas/`, el dato crudo con
    # procedencia. Los tres se copian VERBATIM y por eso no llevan portada:
    # estamparles una seria modificar el documento que se publica para que pase
    # una comprobacion, y en el caso del protocolo eso cambia el texto cuyo hash
    # el propio paquete certifica. Su procedencia es otra y mas fuerte —el hash
    # del protocolo va en la portada de todos los demas documentos— asi que la
    # exencion no abre un hueco: lo cierra por otra via.
    # `notes/` entra en la lista por la misma razon que las otras tres: la nota
    # de doble codificacion viaja VERBATIM porque el protocolo la cita por enlace
    # relativo, y su hash lo certifica el paquete. Estamparle portada seria
    # modificar un documento citado para que pase una comprobacion.
    VERBATIM = {"metodo", "codigo", "capturas", "notes"}
    for d in docs:
        if d.parts[-2:-1] == ("datos",) or d.name in EXENTOS:
            continue
        if VERBATIM & set(d.relative_to(SALIDA).parts[:-1]):
            continue
        t = d.read_text(encoding="utf-8")
        # LA ETIQUETA SE DERIVA, no se cablea. Buscaba «Hash de la base» en
        # castellano, asi que el D1 ingles —que dice «Database hash»— aparecia
        # como documento SIN portada de procedencia teniendola. Una compuerta
        # bilingue que busca en un solo idioma denuncia al documento correcto.
        import sys as _sy2
        _sy2.path.insert(0, str(Path(__file__).resolve().parent))
        from reportes_nucleo import ETIQUETAS_PROCEDENCIA
        etiquetas = "|".join(re.escape(e[2])
                             for e in ETIQUETAS_PROCEDENCIA.values())
        m = re.search(r"\| (?:%s) \| `([0-9a-f]+)…` \|" % etiquetas, t)
        if not m:
            if d.name not in ("INDICE.md",):
                sin_portada.append(d.relative_to(SALIDA))
            continue
        hallazgos.setdefault(m.group(1), set()).add(str(d.relative_to(SALIDA)))
    if len(hallazgos) > 1:
        print("  FALLA  C3  el paquete mezcla %d snapshots distintos:" % len(hallazgos))
        for h, ds in hallazgos.items():
            print("            %s… en %d documentos (p.ej. %s)"
                  % (h, len(ds), sorted(ds)[0]))
        fallos.append("C3")
    elif sin_portada:
        print("  FALLA  C3  documentos sin portada de procedencia: %s"
              % ", ".join(str(x) for x in sin_portada[:5]))
        fallos.append("C3")
    else:
        # Y el subarbol de datos tiene que declarar el MISMO protocolo, o el
        # paquete estaria juntando documentos de una compilacion con datos de
        # otra — que es el fallo que esta compuerta existe para impedir.
        import csv
        man = {r["archivo"]: r for r in
               csv.DictReader((SALIDA / "datos/MANIFEST.csv").open(encoding="utf-8"))}
        proto_datos = man.get("__protocolo__", {}).get("filas")
        t = (SALIDA / "D1-reporte-principal.md").read_text(encoding="utf-8")
        proto_doc = re.search(r"\| Protocolo \| `([^`]+)` \|", t).group(1)
        if proto_datos != proto_doc:
            print("  FALLA  C3  los datos declaran protocolo %s y los documentos %s"
                  % (proto_datos, proto_doc))
            fallos.append("C3")
        else:
            print("  OK     C3  los %d documentos y los datos comparten un solo "
                  "snapshot (protocolo %s)" % (len(docs), proto_doc))


# --- C4 · el paquete declara sus exclusiones -------------------------------

IMPRESCINDIBLES = ["EXCLUSIONES.md", "LICENCIA.md", "CITATION.cff", "LEEME.md",
                   "SNAPSHOT.json", "D1-reporte-principal.md",
                   "datos/MANIFEST.csv", "D2-paises/INDICE.md",
                   "D3-verificacion/INDICE.md"]


def c4_paquete_completo() -> None:
    # EL ARBOL EMITIDO TIENE QUE SER EXACTAMENTE EL MANIFIESTO. Lista blanca:
    # deniega por defecto, y comprueba IGUALDAD, no inclusion.
    #
    # Los dos lados han fallado ya. De mas: `reportes/` llevaba un `.DS_Store`
    # de 6 KB que el Finder dejo despues de generar, dentro del arbol que
    # ibamos a publicar, y nadie lo vio. De menos: `EXCLUSIONES.md` prometia
    # «las capturas crudas con procedencia, el protocolo con su registro de
    # congelamiento y el codigo que lo regenera todo» y el paquete llevaba solo
    # los CSV derivados — el documento que declara lo excluido estaba
    # equivocado sobre lo incluido, y no habia nada contra lo que compararlo.
    import sys as _s
    _s.path.insert(0, str(Path(__file__).resolve().parent))
    from generar_reportes import manifiesto_publicable
    import csv as _csv
    isos = sorted({r["pais_iso3"] for r in _csv.DictReader(
        (SALIDA / "datos/unidades.csv").open(encoding="utf-8"))})
    esperado = manifiesto_publicable(isos)
    hay = {str(f.relative_to(SALIDA)) for f in SALIDA.rglob("*") if f.is_file()}
    sobra, falta = sorted(hay - esperado), sorted(esperado - hay)
    # El PDF es lo unico opcional: solo existe si se compilo con --pdf.
    falta = [f for f in falta if f != "D1-reporte-principal.pdf"]
    if sobra or falta:
        if sobra:
            print("  FALLA  C4  en el paquete hay %d archivo(s) que el "
                  "manifiesto no autoriza: %s" % (len(sobra), ", ".join(sobra[:6])))
        if falta:
            print("  FALLA  C4  el manifiesto promete %d archivo(s) que no "
                  "estan: %s" % (len(falta), ", ".join(falta[:6])))
        fallos.append("C4")
        return

    faltan = [f for f in IMPRESCINDIBLES if not (SALIDA / f).exists()]
    if faltan:
        print("  FALLA  C4  el paquete no tiene: %s" % ", ".join(faltan))
        fallos.append("C4")
        return
    # Y las exclusiones tienen que decir algo, no existir vacías.
    exc = (SALIDA / "EXCLUSIONES.md").read_text(encoding="utf-8")
    if exc.count("\n## ") < 2:
        print("  FALLA  C4  el manifiesto de exclusiones no nombra ninguna")
        fallos.append("C4")
        return
    # Un apéndice por unidad, sin faltar ninguna.
    import csv
    unidades = {r["pais_iso3"] for r in
                csv.DictReader((SALIDA / "datos/unidades.csv").open(encoding="utf-8"))}
    for carpeta in ("D2-paises", "D3-verificacion"):
        hay = {p.stem for p in (SALIDA / carpeta).glob("*.md")} - {"INDICE"}
        if hay != unidades:
            print("  FALLA  C4  %s no cubre todas las unidades: faltan %s"
                  % (carpeta, ", ".join(sorted(unidades - hay)) or "—"))
            fallos.append("C4")
            return
    # Toda imagen referenciada tiene que VIAJAR en el paquete. Un `.md` que
    # apunta a una ruta de fuera se ve bien en el repositorio y sale con un
    # hueco en cuanto el paquete se mueve — y el hueco no rompe nada: el
    # documento compila igual.
    rotas = []
    for d in sorted(SALIDA.rglob("*.md")):
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", d.read_text(encoding="utf-8")):
            ref = m.group(1).split()[0].strip("<>")
            if ref.startswith(("http://", "https://")):
                continue
            base = (d.parent / ref)
            if not (base.exists() or any(base.with_suffix(e).exists()
                                         for e in (".pdf", ".png", ".jpg", ".svg"))):
                rotas.append((d.relative_to(SALIDA), ref))
    if rotas:
        for ruta, ref in rotas[:5]:
            print("  FALLA  C4  %s referencia una imagen que no viaja en el paquete: %s"
                  % (ruta, ref))
        fallos.append("C4")
        return
    print("  OK     C4  paquete completo: exclusiones, licencia, cita, %d apéndices "
          "por lado y las imágenes referenciadas" % len(unidades))


def c5_sin_notas_internas() -> None:
    """Ningun comentario HTML sobrevive al compilado, salvo los declarados.

    Nace de un defecto real: la plantilla abria con un bloque de comentario que
    llevaba el contrato de redaccion y los pendientes internos, y salia publicado
    en el `.md`. Pandoc lo descarta al hacer el PDF, asi que en el PDF no se veia
    — y por eso paso desapercibido. El `.md` es entregable por si mismo.

    Los `<!-- citado: … -->` SI sobreviven a proposito: delimitan la evidencia de
    terceros y la compuerta C1 los usa como escape. Se comprueban aparte.
    """
    malos = []
    for d in sorted(SALIDA.rglob("*.md")):
        for m in re.finditer(r"<!--(.*?)-->", d.read_text(encoding="utf-8"), re.S):
            if not m.group(1).strip().startswith(("citado", "/citado")):
                malos.append((d.relative_to(SALIDA),
                              " ".join(m.group(1).split())[:60]))
    if malos:
        for ruta, txt in malos[:5]:
            print("  FALLA  C5  nota interna publicada en %s: «%s…»" % (ruta, txt))
        fallos.append("C5")

    # NINGUN NOMBRE DE SESION EN EL CODIGO QUE VIAJA, y esto no es cosmetica.
    # Los comentarios de `scripts/` son la mitad del valor del paquete —explican
    # POR QUE cada comprobacion existe, casi siempre con el defecto que la
    # provoco— y viajan enteros a `codigo/`. Atribuirlos al identificador interno
    # de la sesion que los encontro obliga al lector externo a un organigrama que
    # no tiene, y convierte una leccion de metodo en una anecdota interna. Ese
    # identificador ya no aparece aqui por la misma razon: el porque se conserva
    # entero; lo
    # que cambia es que el hallazgo se atribuye al PAPEL —la revision cruzada, la
    # revision de plantillas, la campana del corte 2016— que es lo unico que el
    # lector puede interpretar.
    #
    # Va comprobado y no confiado porque el arreglo fue una pasada de reemplazo
    # sobre 42 referencias: sin compuerta, el comentario numero 43 las devuelve.
    # EL PROVEEDOR NO ES UNA SESION, y la distincion la trajo la propia
    # compuerta al denunciar `sources/claude-2026-08-05/`. Ese guion compara
    # nuestros feriados contra la tabla que publico un asistente comercial: ahi
    # el nombre es el OBJETO DE ESTUDIO, no la firma de quien escribio el
    # comentario, y borrarlo destruiria lo que la frase dice. El escape se define
    # por la forma —nombre seguido de una fecha, que es como se nombra una
    # captura fechada de una fuente— y no por una lista de rutas, que crece.
    #
    # Y LA PROPIA COMPUERTA SE DENUNCIABA: su patron deletrea los nombres que
    # prohibe, asi que al viajar a `codigo/` se acusaba a si misma. El escape es
    # declarado y de UNA linea, marcada donde esta —no una exencion para el
    # archivo entero, que dejaria de mirar justo el guion mas largo del paquete.
    MARCA = "# escape:definicion"
    SESIONES = re.compile(
        r"\b(codex|fable5|opus5|agy|claude-(?!\d{4}-\d{2}-\d{2})[a-z0-9-]+)\b",  # escape:definicion
        re.I)
    # LAS CAPTURAS TAMBIEN VIAJAN, y la primera version de esta compuerta solo
    # miraba `codigo/`. Treinta y nueve fichas de dato crudo llevaban dentro el
    # identificador de la sesion que las escribio y las treinta y nueve salian
    # publicadas. Arreglado donde se encontro y no donde vive, otra vez.
    #
    # PERO AQUI EL NOMBRE NO SIEMPRE SOBRA. En una captura, «quien miro» es
    # PROCEDENCIA: El Salvador distingue quien hizo la pantalla 2 de quien hizo
    # la 3, y esa distincion es el dato. Lo que se quita es el identificador
    # interno; lo que se conserva —y hay que conservar— es que fueron manos
    # distintas. Por eso `capturado_por` guarda el LOTE y no la sesion: fundir
    # los diez lotes en una etiqueta comun borraria la propiedad sobre la que
    # descansa la cifra de fiabilidad.
    #
    # TRES UNIDADES QUEDAN EXENTAS Y LA EXENCION SE DECLARA AQUI, no se hereda
    # de un olvido. En Francia, Grecia e Israel la captura y su «segunda
    # codificacion independiente» llevan el mismo identificador. Despersonalizar
    # los dos lados haria invisible esa coincidencia, que es hoy una pregunta
    # abierta sobre el Anexo A. Se sale de la exencion resolviendo la pregunta,
    # no renombrando los archivos.
    EXENTAS = {"francia", "grecia", "israel"}
    # SE RECORRE TODO EL ARBOL QUE VIAJA, y esta es la tercera version de esta
    # comprobacion. La primera miraba `codigo/`. La segunda añadio `capturas/`,
    # cuando resulto que el dato crudo llevaba identificadores dentro. Y al
    # auditar el arbol que se iba a publicar aparecio que `metodo/` —el protocolo
    # y su registro, los documentos mas leidos del paquete— tenia treinta y dos
    # referencias por idioma.
    #
    # **Arreglado donde se encontro y no donde vive, tres veces seguidas.** Por
    # eso ya no hay lista de carpetas: se recorre lo que sale, que es la unica
    # definicion que no se queda corta cuando el paquete crezca.
    reincidentes = []
    for f in sorted(SALIDA.rglob("*")):
        if not f.is_file() or f.suffix not in (".py", ".json", ".md", ".csv"):
            continue
        rel = f.relative_to(SALIDA)
        if rel.parts[0] == "capturas" and len(rel.parts) > 1 \
                and rel.parts[1] in EXENTAS:
            continue
        for n, linea in enumerate(f.read_text(encoding="utf-8",
                                              errors="ignore").splitlines(), 1):
            if MARCA in linea:
                continue
            if SESIONES.search(linea):
                reincidentes.append("%s:%d" % (rel, n))
    if reincidentes:
        for r in reincidentes[:5]:
            print("  FALLA  C5  nombre de sesion en el paquete: %s" % r)
        fallos.append("C5")

    # NINGUN IDENTIFICADOR DE ESTE REPOSITORIO VIAJA. El sello de `SNAPSHOT.json`
    # se corrigio para no publicar el commit privado —el repositorio publico
    # arranca con historial limpio y ese hash no resuelve a nada que el lector
    # pueda consultar—, y el manifiesto de datos seguia escribiendolo un archivo
    # mas alla. Se arreglo donde se encontro y no donde vivia, que es un defecto
    # con nombre en este proyecto.
    #
    # La comprobacion no busca un hash concreto: le PREGUNTA A GIT si alguno de
    # los identificadores que viajan existe en este repositorio. Asi tambien caza
    # el commit de manana, y el que escriba un guion que aun no existe.
    import subprocess
    candidatos = set()
    for f in list(SALIDA.rglob("*.md")) + list(SALIDA.rglob("*.json")) \
            + list(SALIDA.rglob("*.csv")):
        candidatos |= set(re.findall(r"\b[0-9a-f]{40}\b",
                                     f.read_text(encoding="utf-8", errors="ignore")))
    privados = []
    for h in sorted(candidatos):
        r = subprocess.run(["git", "-C", str(REPO), "cat-file", "-t", h],
                           capture_output=True, text=True)
        if r.returncode == 0:
            privados.append(h[:12])
    if privados:
        for h in privados[:5]:
            print("  FALLA  C5  identificador de ESTE repositorio en el paquete: "
                  "%s… (el lector externo no puede resolverlo)" % h)
        fallos.append("C5")

    if "C5" not in fallos:
        print("  OK     C5  ni notas internas, ni nombres de sesion, ni "
              "identificadores privados llegaron al entregable")


# --- C10 · el paquete no se contradice a si mismo -------------------------

def c10_coherencia_interna() -> None:
    """Dos cosas que el paquete afirma de si mismo, comprobadas contra el disco.

    LAS DOS SALEN DEL MISMO ERROR, que es el que enseña por que esta compuerta
    existe. El protocolo citaba dos archivos que el paquete no traia, y el
    arreglo evidente —reescribir los enlaces al copiar— dejaba el protocolo
    embarcado sin casar con el hash que declara el registro embarcado a su lado.
    Se cambiaba un enlace muerto, que es una molestia, por un hash que no cuadra,
    que se lee como manipulacion.

    Ninguna de las nueve compuertas anteriores lo veia, y no por descuido: todas
    comprueban que el paquete CONTENGA lo que promete. Esta comprueba que lo que
    contiene no se desmienta entre si.

      (1) Todo enlace relativo resuelve. Sustituye a la vigilancia del literal de
          un enlace concreto: aquella protegia el unico que ya conociamos.
      (2) Todo archivo que el registro embarcado certifica y que el paquete
          embarca casa con su hash. Los que el registro cita y el paquete no
          trae no se comprueban — no estan.
    """
    import hashlib

    rotos = []
    for f in sorted(SALIDA.rglob("*.md")):
        txt = f.read_text(encoding="utf-8")
        for rel in re.findall(r"\]\((?!https?:|mailto:|#)([^)#]+)\)", txt):
            if not (f.parent / rel.strip()).exists():
                rotos.append("%s -> %s" % (f.relative_to(SALIDA), rel.strip()))
    if rotos:
        for r in rotos[:6]:
            print("  FALLA  C10 enlace relativo muerto en el paquete: %s" % r)
        fallos.append("C10")

    registro = SALIDA / "metodo/PROTOCOL_FREEZE.md"
    if not registro.exists():
        print("  FALLA  C10 el paquete no embarca el registro que sus documentos citan")
        fallos.append("C10")
        return

    # El registro nombra sus archivos por la ruta del REPOSITORIO
    # —`docs/archivo/02-protocolo-v2.25.md`— y en el paquete viajan renombrados.
    # El puente es el unico dato que ya se comprueba en otro sitio y aqui hace
    # falta: que sea el ultimo vigente. Se toma la fila `Vigente | si`.
    bloques = re.split(r"\n## ", registro.read_text(encoding="utf-8"))
    vigente = [b for b in bloques if re.search(r"\|\s*Vigente\s*\|\s*si\s*\|", b)]
    if not vigente:
        print("  FALLA  C10 el registro embarcado no declara ninguna version vigente")
        fallos.append("C10")
        return
    b = vigente[-1]
    esperado = {}
    for idioma, archivo in (("es", "metodo/protocolo.md"),
                            ("en", "metodo/protocol.md")):
        m = re.search(r"\|\s*SHA-256 \(%s\)\s*\|\s*`([0-9a-f]{64})`" % idioma, b)
        if m:
            esperado[archivo] = m.group(1)
    for nombre, sha in (("metodo/esquema.sql", "001_schema.sql"),
                        ("metodo/validaciones.sql", "900_validaciones.sql")):
        m = re.search(r"\|\s*`schema/draft/%s`\s*\|\s*`([0-9a-f]{64})`"
                      % re.escape(sha), b)
        if m:
            esperado[nombre] = m.group(1)
    if not esperado:
        print("  FALLA  C10 la version vigente del registro no declara ningun hash")
        fallos.append("C10")
        return

    desajustes = []
    for rel, sha in sorted(esperado.items()):
        f = SALIDA / rel
        if not f.exists():
            continue
        real = hashlib.sha256(f.read_bytes()).hexdigest()
        if real != sha:
            desajustes.append("%s: el registro dice %s… y el archivo es %s…"
                              % (rel, sha[:12], real[:12]))
    if desajustes:
        for d in desajustes:
            print("  FALLA  C10 %s" % d)
        fallos.append("C10")

    if "C10" not in fallos:
        print("  OK     C10 %d enlaces resuelven y %d archivos casan con el hash "
              "que el paquete certifica" % (
                  sum(len(re.findall(r"\]\((?!https?:|mailto:|#)[^)#]+\)",
                                     f.read_text(encoding="utf-8")))
                      for f in SALIDA.rglob("*.md")),
                  len([r for r in esperado if (SALIDA / r).exists()])))


# --- C11 · el paquete se reproduce a si mismo -----------------------------

def c11_el_paquete_corre() -> None:
    """LA UNICA COMPUERTA QUE EJECUTA EL PAQUETE, y por eso existe.

    Las otras diez comprueban que el paquete CONTENGA lo que promete. Ninguna
    comprobaba que lo que promete FUNCIONE, y por esa rendija el paquete estuvo
    publicando veinticinco guiones que no arrancaban: resolvian sus rutas contra
    el arbol del repositorio y el paquete tiene otro. Las diez compuertas pasaban
    y el primer comando de un tercero devolvia un error de archivo no encontrado.
    La comprobacion llegaba al borde del artefacto y se paraba ahi.

    SE COPIA ANTES DE EJECUTAR, y la copia no es higiene. Corriendolo sobre
    `reportes/` la reproduccion escribiria dentro del arbol emitido y la
    siguiente compuerta de lista blanca denunciaria una carpeta que ella misma
    creo. Peor: correr en su sitio no prueba lo que hace falta probar, porque el
    paquete que importa es el que el lector descomprime en otro lado.

    Y NO COMPRUEBA «QUE TERMINE SIN ERROR». Un guion que sale con cero podria
    haber escrito cualquier cosa. La reproduccion rehace el dataset desde las
    capturas y lo compara hash por hash con el que viaja: la afirmacion que se
    verifica es la del LEEME, palabra por palabra.
    """
    import shutil
    import subprocess
    import tempfile

    repro = SALIDA / "reproducir.sh"
    if not repro.exists():
        print("  FALLA  C11 el paquete no trae el comando de reproduccion que "
              "su LEEME promete")
        fallos.append("C11")
        return

    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "paquete"
        shutil.copytree(SALIDA, copia)
        r = subprocess.run(["sh", str(copia / "reproducir.sh")],
                           capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        print("  FALLA  C11 el paquete NO se reproduce desde sus capturas:")
        for linea in (r.stdout + r.stderr).strip().splitlines()[-8:]:
            print("             %s" % linea)
        fallos.append("C11")
        return
    n = re.search(r"(\d+) archivo\(s\) reproducen", r.stdout)
    print("  OK     C11 el paquete copiado se reproduce entero desde sus "
          "capturas (%s archivos)" % (n.group(1) if n else "?"))


print("COMPUERTAS DEL SISTEMA DE REPORTES\n")
# La lista se recorre en vez de llamarlas a mano: asi el recuento del cierre no
# puede mentir. Decia «las cuatro compuertas pasan» cuando ya eran cinco — una
# cifra tecleada en el guion que existe para impedir cifras tecleadas.
COMPUERTAS = [c1_sin_cifras_tecleadas, c1_casos_adversariales,
              c1_los_desgloses_suman, c1_sin_fuga_de_idioma,
              c1_formato_numerico_del_idioma,
              c2_advertencias, c3_snapshot_unico,
              c4_paquete_completo, c5_sin_notas_internas,
              c10_coherencia_interna, c11_el_paquete_corre]
for compuerta in COMPUERTAS:
    compuerta()
print()
if fallos:
    # SE CUENTAN COMPUERTAS DISTINTAS, no anotaciones. Una compuerta que
    # denuncia dos cosas —C10 mira enlaces y hashes— se apuntaba dos veces y el
    # cierre decia «FALLAN 3 de 10» habiendo fallado dos. Otra cifra tecleada,
    # esta vez por el propio contador, en el guion que existe para impedirlas.
    distintas = list(dict.fromkeys(fallos))
    print("FALLAN %d de %d compuertas: %s"
          % (len(distintas), len(COMPUERTAS), ", ".join(distintas)))
    sys.exit(1)
print("Las %d compuertas pasan." % len(COMPUERTAS))
