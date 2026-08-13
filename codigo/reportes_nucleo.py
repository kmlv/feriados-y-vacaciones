"""Nucleo del sistema de reportes: identidad del snapshot y resolucion de cifras.

QUE PROBLEMA RESUELVE, y es el que este proyecto ya se comio dos veces: un
documento con un numero tecleado a mano se queda viejo solo. La cabecera del
esquema llego a declarar una version dos por detras del protocolo, y el README
describio durante dias un proyecto que ya no existia. Ninguno mintio al
escribirse.

LA REGLA: **ningun numero de resultado se teclea.** La prosa lleva marcas
`{{q:identificador}}` y este modulo las sustituye por el valor que devuelve la
consulta registrada. Si una marca no tiene consulta, la compilacion FALLA — no
se deja el hueco ni se pone un cero.

LO QUE NO ES UN RESULTADO tambien esta declarado, porque la distincion es la
parte dificil: `v2.20`, `§35`, `art. 14`, `2016` y `2026` son ETIQUETAS, no
cifras derivadas, y viven en la lista blanca de `reportes_pruebas.py`. Una prueba
que grite ante cada uno de esos se apaga al tercer dia, y apagada no protege
nada.

IDENTIDAD DEL SNAPSHOT. Todo entregable declara en portada el hash de la base,
la version de protocolo, el hash del generador y el commit. Dos entregables
compilados contra snapshots distintos no pueden convivir en el paquete, y
`reportes_pruebas.py` lo comprueba.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "data/derived/piloto.db"
CRUDO = REPO / "data/raw"
EXPORT = REPO / "data/derived/export"
SALIDA = REPO / "reportes"

MARCA = re.compile(r"\{\{q:([a-z0-9_]+)\}\}")


# --- identidad ------------------------------------------------------------

def sha256_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


SIN_PUBLICAR = "sin-publicar"


def version_publicada() -> str:
    """La ETIQUETA con la que este paquete se publica. No un commit, y esa es la
    correccion.

    EL CAMPO GUARDABA UN COMMIT Y NO PODIA. El sello tenia que llevar el commit
    del repositorio PUBLICO —el privado arranca con otro historial y su hash no
    resuelve a nada que el lector pueda consultar—, pero el commit publico es el
    que CONTIENE el paquete:

        C1 = commit(paquete que dice «sin-publicar»)
        regenerar con ese C1  ->  el paquete cambia
        C2 = commit(paquete que dice C1)          C2 != C1

    Un artefacto no puede declarar el identificador que lo contiene. Es circular
    por construccion, no por descuido: el paquete existe ANTES que su commit.

    LA ETIQUETA ROMPE EL CIRCULO porque se pone DESPUES del commit y no forma
    parte de su contenido. Decision del principal, y es lo que hacen los
    conjuntos de datos citables: se cita `v1.0`, y la etiqueta resuelve a un
    commit concreto en la pagina del repositorio.

    Y EL CAMPO CAMBIA DE NOMBRE, no solo de contenido. Un campo llamado `commit`
    con una etiqueta dentro es un rotulo afirmando lo que el cuerpo niega — la
    forma de defecto que este paquete lleva dos dias corrigiendo en otros sitios.
    Se llama `version_publicada`.

    Sin `VERSION_PUBLICA` dice `sin-publicar`, que es la verdad de esa copia, y
    **no repliega a ningun identificador interno**: el repliegue silencioso
    volveria a publicar el hash privado con la diferencia de que ya nadie estaria
    mirando. Los hashes de contenido —base, protocolo, generador— no dependen de
    esto y siguen siendo la procedencia comprobable sin salir del paquete.
    """
    v = os.environ.get("VERSION_PUBLICA", "").strip()
    return v if v else SIN_PUBLICAR


def snapshot(con: sqlite3.Connection) -> dict:
    """Identidad completa de esta compilacion. Va en la portada de los cuatro."""
    protocolo = con.execute("SELECT version, hash FROM protocolo_congelado "
                            "ORDER BY congelado_en DESC LIMIT 1").fetchone()
    generadores = sorted(REPO.glob("scripts/reportes*.py")) + \
        [REPO / "scripts/generar_reportes.py"]
    h = hashlib.sha256()
    for g in generadores:
        if g.exists():
            h.update(g.read_bytes())
    return {
        "base_sha256": sha256_de(BASE),
        "protocolo": protocolo[0] if protocolo else "desconocida",
        "protocolo_sha256": protocolo[1] if protocolo else "",
        "generador_sha256": h.hexdigest(),
        "version_publicada": version_publicada(),
    }


def cubierta(titulo: str, subtitulo: str = "") -> str:
    """Sólo el título. Para documentos que se leen, no que se auditan.

    El reporte principal se abre con su argumento y no con una caja de hashes:
    quien lo lee quiere la respuesta, no la procedencia. La procedencia no se
    pierde — baja al colofón, donde la busca quien la necesita.
    """
    return "# %s\n%s" % (titulo, "\n%s\n" % subtitulo if subtitulo else "")


# Las cinco etiquetas de la tabla de procedencia, por idioma. Eran parte de los
# catorce fragmentos de andamiaje que quedaron fuera del catalogo de traduccion
# —trozos de barras con un rotulo suelto, que traducidos rompian la tabla—. Aqui
# el rotulo va separado de su andamio, que es lo que aquel aplazamiento pedia.
ETIQUETAS_PROCEDENCIA = {
    "es": ("Protocolo", "Hash del protocolo", "Hash de la base",
           "Hash del generador", "Versión publicada"),
    "en": ("Protocol", "Protocol hash", "Database hash",
           "Generator hash", "Published version"),
}


def _tabla_procedencia(snap: dict, idioma: str = "es") -> str:
    a, b, c, d, e = ETIQUETAS_PROCEDENCIA[idioma]
    return f"""| | |
|---|---|
| {a} | `{snap['protocolo']}` |
| {b} | `{snap['protocolo_sha256'][:16]}…` |
| {c} | `{snap['base_sha256'][:16]}…` |
| {d} | `{snap['generador_sha256'][:16]}…` |
| {e} | `{snap['version_publicada']}` |"""


COLOFON_EN = (
    "\n\n---\n\n## Colophon\n\nGenerated automatically. **Do not edit by hand**: "
    "any correction goes into the source data and the document is regenerated. "
    "Two documents from the same package share these five values; if they "
    "differ, they do not belong to the same compilation.\n\n")


def colofon(snap: dict, idioma: str = "es") -> str:
    """La procedencia al final, para el documento que se lee de principio a fin."""
    cabeza = COLOFON_EN if idioma == "en" else (
        "\n\n---\n\n## Colofón\n\nGenerado automáticamente. **No editar a "
        "mano**: cualquier corrección va en el dato de origen y el documento se "
        "regenera. Dos documentos de un mismo paquete comparten estos cinco "
        "valores; si difieren, no pertenecen a la misma compilación.\n\n")
    return cabeza + _tabla_procedencia(snap, idioma) + "\n"


def portada(snap: dict, titulo: str, subtitulo: str = "") -> str:
    """Título más la caja de procedencia arriba. Para los apéndices.

    Aquí la caja SÍ va delante, y no es descuido: D2 y D3 se consultan por
    partes, y quien abre el apéndice de una unidad para cotejar un número
    necesita saber contra qué compilación lo coteja antes de leer nada.
    """
    return cubierta(titulo, subtitulo) + "\n> **Procedencia de este documento.** " \
        "Generado automáticamente. No editar a mano.\n>\n" + \
        "\n".join("> " + l for l in _tabla_procedencia(snap).splitlines()) + "\n"


# --- el registro de cifras -------------------------------------------------

IDIOMA_ACTUAL = "es"


def _fmt(x, decimales: int = 0, idioma: str = None) -> str:
    """Formatea una cifra en la convencion de SU IDIOMA. Redondea siempre.

    Redondea tambien a cero decimales: la primera version solo lo hacia con
    `decimales` distinto de cero y dejaba salir «6.999999999999984» donde tocaba
    «7». Un numero asi en un documento publicado se lee como descuido y contamina
    lo que lo rodea.

    Y LLEVA IDIOMA porque la decision de convencion estaba tomada DENTRO de la
    funcion —«formato español: coma decimal»— y el paquete pasa a ser bilingue.
    En ingles el separador decimal es el punto, asi que la misma cifra bien
    formateada sale «32,4» en un documento y «32.4» en el otro. Sacar la decision
    a la llamada es lo que permite que las dos sean correctas a la vez.

    Consecuencia para la compuerta de paridad, y es lo que la salva: comparar el
    TEXTO resuelto daria falso positivo en toda cifra decimal. Lo que se compara
    es el conjunto de marcas y el valor SUBYACENTE, no su formato.
    """
    idioma = idioma or IDIOMA_ACTUAL
    if isinstance(x, float):
        t = "%.*f" % (decimales, x)
        if idioma == "es":
            # Signo menos tipografico (U+2212), no guion. En un documento
            # publicado el guion delante de una cifra se lee como raya de
            # dialogo o como separador, y en una tabla alineada se nota.
            return t.replace(".", ",").replace("-", "\u2212")
        return t.replace("-", "\u2212")
    return str(x)


def temporales_al_corte(con, iso3, corte: int) -> list[dict]:
    """Medidas TEMPORALES vigentes en el ano del corte, con su restitucion.

    Existe por Eslovaquia y es el aviso que le faltaba al lector de D2. Su corte
    de 2026 cae en el unico ano en que una disposicion transitoria suspende dos
    feriados: el panel dice que perdio cuatro y los permanentes son dos. La cifra
    del panel es CORRECTA y la lectura que invita es falsa, que es peor que un
    error, porque no hay nada que falle.

    Una medida temporal esta viva en el corte si empezo antes de que acabe el
    anio y NADA POSTERIOR la cerro. Cerrarla es cualquiera de dos cosas: una
    `restitucion`, que es el cierre que el esquema previo; o un evento
    PERMANENTE posterior, que la reemplaza. Esa segunda mitad no estaba en mi
    primera version y hacia falta: el puente israeli de 2016 —seis meses leyendo
    quince donde la ley decia catorce— salia avisado en el corte de 2026, diez
    anios despues de agotarse, porque nadie emite una `restitucion` de algo que
    simplemente fue superado por la reforma definitiva. El aviso se disparaba
    donde no habia nada que avisar, y un aviso que aparece de mas se aprende a
    ignorar.
    """
    evs = con.execute(
        "SELECT e.tipo, e.vigencia_desde, e.permanente_o_temporal, e.causa, e.cita "
        "  FROM eventos_reforma e "
        "  JOIN jurisdicciones j ON j.jurisdiccion_id = e.jurisdiccion_id "
        " WHERE j.iso3 = ? ORDER BY e.vigencia_desde", (iso3,)).fetchall()
    fin = "%d-12-31" % corte
    ini = "%d-01-01" % corte
    def cerrada(desde):
        return any((t == "restitucion" or pt == "permanente")
                   and d > desde and d <= ini for t, d, pt, *_ in evs)
    return [{"tipo": t, "desde": d, "que": c, "cita": q}
            for t, d, pt, c, q in evs
            if pt == "temporal" and d <= fin and not cerrada(d)]


def vuelve_en(con, iso3) -> str | None:
    r = con.execute(
        "SELECT MIN(e.vigencia_desde) FROM eventos_reforma e "
        "  JOIN jurisdicciones j ON j.jurisdiccion_id = e.jurisdiccion_id "
        " WHERE j.iso3 = ? AND e.tipo = 'restitucion'", (iso3,)).fetchone()[0]
    return r


def construir_registro(con: sqlite3.Connection, idioma: str = "es") -> dict:
    """id -> valor ya formateado. Cada entrada es una consulta, nunca un literal.

    Se construye entero de una vez y no perezosamente a proposito: asi una
    consulta rota se ve al compilar y no cuando alguien lee el documento.
    """
    global IDIOMA_ACTUAL
    previo, IDIOMA_ACTUAL = IDIOMA_ACTUAL, idioma
    try:
        return _construir(con)
    finally:
        IDIOMA_ACTUAL = previo


def _construir(con: sqlite3.Connection) -> dict:
    def uno(sql, *args):
        return con.execute(sql, args).fetchone()[0]

    fuentes = list(csv.DictReader((EXPORT / "fuentes.csv").open(encoding="utf-8")))
    convert = list(csv.DictReader((EXPORT / "vacaciones_convertido.csv").open(encoding="utf-8")))

    r: dict = {}
    r["unidades"] = uno("SELECT COUNT(*) FROM jurisdicciones WHERE nivel='subnacional'")
    # Unidades CON titularidad, distinto de versiones de titularidad. Desde que
    # el panel de vacaciones dejo de ser plano, una jurisdiccion con reforma
    # aparece dos veces, y una tabla de cobertura que cuente filas dice 46 donde
    # el lector espera 45.
    r["unidades_con_vacaciones"] = uno(
        "SELECT COUNT(DISTINCT jurisdiccion_id) FROM vacaciones_version")
    r["feriados"] = uno("SELECT COUNT(*) FROM feriado_version")
    r["vacaciones"] = uno("SELECT COUNT(*) FROM vacaciones_version")
    r["colocaciones"] = uno("SELECT COUNT(*) FROM regla_colocacion")
    r["fuentes"] = len(fuentes)
    r["fuentes_n12"] = sum(1 for f in fuentes if int(f["nivel"]) <= 2)
    r["fuentes_n3mas"] = r["fuentes"] - r["fuentes_n12"]
    r["evidencia"] = uno("SELECT COUNT(*) FROM evidencia")
    r["protocolo"] = uno("SELECT version FROM protocolo_congelado "
                         "ORDER BY congelado_en DESC LIMIT 1")
    r["validaciones"] = 37

    # Reparto por unidad de conteo, que es el eje del hallazgo.
    for tipo in ("calendario", "habil", "werktage", "semanas"):
        r["n_%s" % tipo] = uno(
            "SELECT COUNT(*) FROM vacaciones_version WHERE tipo_de_dia = ?", tipo)
    r["sin_base_declarada"] = uno(
        "SELECT COUNT(*) FROM vacaciones_version WHERE base_semanal_dias IS NULL")
    r["habil_sin_base"] = uno(
        "SELECT COUNT(*) FROM vacaciones_version "
        "WHERE base_semanal_dias IS NULL AND tipo_de_dia IN ('habil','werktage')")

    # El caso Peru-Alemania, entero por consulta: es la cifra mas citada del
    # documento y la que peor envejeceria escrita a mano.
    def conv(iso):
        fila = next(x for x in convert if x["iso3"] == iso)
        return float(fila["dias_trabajo_semana5"]), float(fila["dias_texto_legal"])
    per_c, per_l = conv("PER")
    deu_c, deu_l = conv("DEU")
    r["per_legal"] = _fmt(per_l)
    r["deu_legal"] = _fmt(deu_l)
    r["per_conv"] = _fmt(per_c, 1)
    r["deu_conv"] = _fmt(deu_c, 1)
    r["per_deu_real_pct"] = _fmt(100 * (per_c / deu_c - 1), 0)
    # Su indice, con sus valores TAL COMO LOS PUBLICA —dos decimales, 1,00 y
    # 0,67—, no recalculados por nosotros. Recalcularlos daria 50% y lo que hay
    # que citar es la brecha que un lector obtiene de su tabla, que es 49%.
    # PREFORMATEADAS EN CASTELLANO, y por eso eran las dos unicas cifras del PDF
    # ingles con coma decimal: 290 con punto y estas dos con coma. Una cadena
    # literal se salta `_fmt` y por tanto se salta el idioma.
    r["per_indice"] = _fmt(1.00, 2)
    r["deu_indice"] = _fmt(0.67, 2)
    r["per_deu_indice_pct"] = _fmt(100 * (1.00 / 0.67 - 1), 0)
    # Cuantas veces la brecha publicada es la real. Iba escrito «siete veces» en
    # la prosa y era correcto por casualidad: es una cifra derivada y le toca
    # entrar por consulta como todas.
    r["per_deu_factor"] = _fmt((1.00 / 0.67 - 1) / (per_c / deu_c - 1), 0)

    # Contra UNIDADES con titularidad, no contra filas. Restar las 46 filas de
    # las 47 unidades daba 1, y son 2 —Bolivia y Estados Unidos—: Mexico aporta
    # dos versiones y se comia una unidad sin titularidad. El cambio de grano se
    # propago un nivel mas abajo de donde lo arregle.
    r["unidades_sin_vacaciones"] = r["unidades"] - r["unidades_con_vacaciones"]
    r["feriados_condicionales"] = uno(
        "SELECT COUNT(DISTINCT feriado_version_id) FROM regla_fecha_version "
        "WHERE condicion_dia_semana IS NOT NULL")
    # Unidades sin corte 2016. Iba en la prosa como «tres jurisdicciones» y en
    # letra, que es como la compuerta C1 no lo veia. Es un recuento y le toca
    # entrar por consulta. Se cuenta por iso3 porque los feriados cuelgan del
    # pais y la unidad de referencia es la ciudad.
    r["unidades_sin_corte_2016"] = uno("""
        SELECT COUNT(*) FROM jurisdicciones u
         WHERE u.nivel='subnacional' AND u.iso3 NOT IN (
               SELECT j.iso3 FROM mediciones m
                 JOIN feriado_version f
                   ON f.feriado_version_id = m.hecho_id
                  AND m.hecho_tipo='feriado_version'
                 JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
                WHERE m.corte = 2016 AND m.estado_verificacion <> 'na')""")
    # LA MEDIDA TEMPORAL AL CORTE, para que el hallazgo esloveno no viaje en
    # cifras tecleadas. La sesion de reportes escribio «dos de los cuatro dias» y
    # «solo la mitad de esa perdida es permanente»: son resultados, y la
    # compuerta no los caza porque van junto a «dias», que es una tolerancia suya
    # y no una licencia.
    #
    # `suspendidos` cuenta feriados suspendidos por una medida TEMPORAL viva en
    # el corte; `observado` y `permanente` son la caida que el panel muestra y la
    # que sobrevive a la restitucion. Se derivan del mismo registro de eventos
    # que genera el aviso de D2, no de una lista aparte que se quedaria vieja.
    temporales = {iso: temporales_al_corte(con, iso, 2026)
                  for (iso,) in con.execute(
                      "SELECT DISTINCT j.iso3 FROM eventos_reforma e "
                      "  JOIN jurisdicciones j ON j.jurisdiccion_id=e.jurisdiccion_id")}
    temporales = {i: t for i, t in temporales.items() if t}
    r["unidades_con_medida_temporal"] = len(temporales)
    r["dias_suspendidos_al_corte"] = sum(len(t) for t in temporales.values())
    if temporales:
        iso = sorted(temporales)[0]
        a, b = con.execute(
            "SELECT SUM(CASE WHEN m.corte=2016 THEN f.duracion_dias ELSE 0 END), "
            "       SUM(CASE WHEN m.corte=2026 THEN f.duracion_dias ELSE 0 END) "
            "  FROM mediciones m "
            "  JOIN feriado_version f ON f.feriado_version_id=m.hecho_id "
            "   AND m.hecho_tipo='feriado_version' AND m.estado_verificacion<>'na' "
            "  JOIN jurisdicciones j ON j.jurisdiccion_id=f.jurisdiccion_id "
            " WHERE j.iso3=?", (iso,)).fetchone()
        r["caida_observada_temporal"] = abs(b - a)
        r["caida_permanente_temporal"] = abs(b - a) - len(temporales[iso])
        r["unidad_con_medida_temporal"] = con.execute(
            "SELECT nombre FROM jurisdicciones WHERE iso3=? AND nivel='nacional'",
            (iso,)).fetchone()[0]
    # FERIADOS NOMINALES SIN RESPALDO EXIGIBLE. Lo pidio la sesion de reportes
    # para no teclear el conteo, y la cifra mide de golpe cuanto engana comparar
    # calendarios: cuatro jurisdicciones publican un calendario entero cuyo
    # respaldo exigible al empleador privado es CERO, y en el conjunto son 59 de
    # 571 dias nominales.
    #
    # `sin_respaldo` cuenta unidades con calendario y cero exigible; `parcial`,
    # las que tienen algo de los dos —Costa Rica y Francia— y que sin su propia
    # cifra quedarian invisibles entre las dos categorias limpias.
    exig = con.execute("""
        SELECT SUM(CASE WHEN nom > 0 AND ex = 0 THEN 1 ELSE 0 END),
               SUM(CASE WHEN nom > ex AND ex > 0 THEN 1 ELSE 0 END),
               SUM(nom - ex), SUM(nom)
          FROM (SELECT j.iso3,
                       SUM(f.duracion_dias) nom,
                       SUM(CASE WHEN f.categoria='descanso_pagado_obligatorio'
                                THEN f.duracion_dias ELSE 0 END) ex
                  FROM mediciones m
                  JOIN feriado_version f ON f.feriado_version_id=m.hecho_id
                   AND m.hecho_tipo='feriado_version' AND m.estado_verificacion<>'na'
                  JOIN jurisdicciones j ON j.jurisdiccion_id=f.jurisdiccion_id
                 WHERE m.corte=2026 GROUP BY j.iso3)""").fetchone()
    r["unidades_sin_feriados_exigibles"] = exig[0]
    r["unidades_con_feriados_parcialmente_exigibles"] = exig[1]
    # Un decimal SOLO si lo hay. «59,0 de los 571,5» se lee mal y afirma una
    # precision que en el 59 no hace falta; redondear los dos a entero borraria
    # el medio dia turco, que es real. La cifra manda sobre el formato.
    def _dias(x):
        return _fmt(x, 0) if float(x) == int(x) else _fmt(x, 1)
    r["dias_nominales_sin_respaldo"] = _dias(exig[2])
    r["dias_nominales_totales"] = _dias(exig[3])
    # EL DESGLOSE ENTERO Y NO UN TROZO. La primera version emitia solo los
    # niveles 1 a 3, y la revisión de plantillas iba a poner `fuentes_n3` donde la prosa
    # decia «76 en nivel 3-4»: la marca vale 40 y habria publicado 40 por 76.
    # Su formulacion es la que hay que recordar — **una marca MAL USADA es peor
    # que una cifra tecleada**: la tecleada se desfasa, la mal usada publica con
    # autoridad. Con las seis emitidas no hay que agregar nada a mano.
    for n in (1, 2, 3, 4, 5):
        r["fuentes_n%d" % n] = uno(
            "SELECT COUNT(*) FROM fuentes WHERE nivel_de_fuente = ?", n)
    # El 6 es «no consta», que no es un nivel sino su ausencia, y por eso lleva
    # nombre propio en vez de `fuentes_n6`.
    r["fuentes_sin_nivel"] = uno(
        "SELECT COUNT(*) FROM fuentes WHERE nivel_de_fuente >= 6")
    r["fuentes_n3mas"] = uno(
        "SELECT COUNT(*) FROM fuentes WHERE nivel_de_fuente > 2")
    # El hallazgo que cambio el esquema, por consulta. Iba tecleado en el
    # apendice —«nueve unidades» y «seis regimenes»— y las dos son hechos vivos:
    # se cuentan de la colocacion y del campo de resolucion que ese mismo
    # hallazgo obligo a crear. Que la cifra que justifica un campo salga de ese
    # campo es la forma mas limpia que tiene de envejecer bien.
    r["colocacion_negociadas"] = uno(
        "SELECT COUNT(DISTINCT v.jurisdiccion_id) FROM regla_colocacion c "
        "  JOIN vacaciones_version v "
        "    ON v.vacaciones_version_id = c.vacaciones_version_id "
        " WHERE c.iniciativa = 'negociada'")
    r["regimenes_desacuerdo"] = uno(
        "SELECT COUNT(DISTINCT resolucion_desacuerdo) FROM regla_colocacion "
        " WHERE resolucion_desacuerdo IS NOT NULL")
    r["mediciones_na"] = uno(
        "SELECT COUNT(*) FROM mediciones WHERE estado_verificacion='na'")
    r.update(cifras_de_travail())
    r.update(cifras_del_cruce())
    r.update(cifras_de_fiabilidad())
    r.update(cifras_de_auditoria())
    r.update(cifras_de_la_metrica())
    return {k: _fmt(v) if not isinstance(v, str) else v for k, v in r.items()}


def cifras_de_travail() -> dict:
    """Lo recuperado de la base TRAVAIL de la OIT, que murio y se rescato.

    Es sustancia y estaba sin citar: convierte «por que no usamos TRAVAIL» en
    «la rescatamos del archivo, la conservamos y decimos su cosecha».
    """
    cob = list(csv.DictReader(
        (REPO / "data/derived/travail_oit_cobertura.csv").open(encoding="utf-8")))
    ok = [c for c in cob if c.get("estado") == "ok"]
    return {
        "travail_unidades": str(len(ok)),
        "travail_intentadas": str(len(cob)),
        "travail_con_colocacion": str(sum(1 for c in ok
                                          if c.get("tiene_colocacion") == "1")),
        "travail_campos": str(sum(int(c.get("campos") or 0) for c in ok)),
    }


def cifras_de_auditoria() -> dict:
    """Reparto de las divergencias auditadas. Son resultados, no prosa."""
    d = json.loads((REPO / "data/derived/auditoria.json").read_text())
    return {
        "aud_unidades": str(d["unidades_auditadas"]),
        "aud_error_nuestro": str(d["error_nuestro"]),
        "aud_desactualizacion": str(d["desactualizacion_del_antecedente"]),
        "aud_constructo": str(d["diferencia_de_constructo"]),
        "aud_indeterminado": str(d["indeterminado"]),
        "aud_desactualizadas": ", ".join(d["desactualizadas"]),
    }


def cifras_de_fiabilidad() -> dict:
    """Lee la medicion CONGELADA. No recalcula, y la razon importa.

    La tasa se mueve cada vez que se corrige una captura — y corregirlas es
    exactamente lo que el ejercicio provoca. Recalcularla despues de aplicar los
    hallazgos del segundo codificador ya no mide fiabilidad ciega: mide el
    acuerdo despues de habernos dado la razon, que es circular.

    El archivo lo escribe `cruzar_doble.py --congelar` y lleva dentro el commit
    en que se tomo la medicion.

    ESTAS CIFRAS YA NO SE PUBLICAN, y esta funcion sigue existiendo a proposito.
    Decision del principal: la medicion de fiabilidad vive en el repositorio
    privado y en la documentacion interna, y no viaja al paquete. Ni el guion que
    la calcula ni las segundas lecturas se embarcan, asi que **este modulo, leido
    dentro del paquete, cita una herramienta que el lector no tiene**.
    Se queda porque los documentos internos si la usan, y se dice aqui porque un
    comentario que manda a un guion ausente es una instruccion imposible — la
    misma figura que ya costo el remedio con cara de instruccion en la compuerta
    de figuras.
    """
    ruta = REPO / "data/derived/fiabilidad.json"
    if not ruta.exists():
        # EL REMEDIO SE DERIVA DE DONDE SE ESTE LEYENDO. Dentro del paquete,
        # `cruzar_doble.py` no existe y mandar a correrlo seria peor que no dar
        # remedio: quien lo intenta cree haberlo arreglado.
        cruce = Path(__file__).resolve().parent / "cruzar_doble.py"
        raise SystemExit(
            "falta data/derived/fiabilidad.json — " +
            ("corre: python3 scripts/cruzar_doble.py --congelar" if cruce.exists()
             else "esta medicion es interna y su guion no viaja en este paquete; "
                  "las cifras de fiabilidad no forman parte de la publicacion "
                  "(ver EXCLUSIONES.md)."))
    d = json.loads(ruta.read_text())
    return {
        "dobles": str(d["n_unidades"]),
        "fer_apareados": str(d["feriados_apareados"]),
        "fer_menciones": str(d["feriados_menciones"]),
        "fer_acuerdo_pct": str(d["feriados_acuerdo_pct"]),
        "vac_campos_ok": str(d["vacaciones_campos_ok"]),
        "vac_campos": str(d["vacaciones_campos"]),
        "vac_acuerdo_pct": str(d["vacaciones_acuerdo_pct"]),
        "dobles_sin_divergencia": str(len(d["unidades_sin_divergencia"])),
        "fiabilidad_commit": d["commit"][:12],
        # LOS DOS ESTRATOS, porque la independencia solo esta EVIDENCIADA en
        # parte de las unidades y la tasa se anuncia como acuerdo entre
        # codificadores independientes. Publicar solo el estrato evidenciado
        # subiria la cifra quitando los peores casos; publicar solo el total
        # mantendria dentro unidades que no evidencian lo que la tasa afirma.
        "dobles_ev": str(d["evidenciada"]["n_unidades"]),
        "fer_acuerdo_ev": str(d["evidenciada"]["feriados_acuerdo_pct"]),
        "vac_acuerdo_ev": str(d["evidenciada"]["vacaciones_acuerdo_pct"]),
        "dobles_noev": str(d["no_evidenciada"]["n_unidades"]),
        "fer_acuerdo_noev": str(d["no_evidenciada"]["feriados_acuerdo_pct"]),
        "vac_acuerdo_noev": str(d["no_evidenciada"]["vacaciones_acuerdo_pct"]),
    }


def resolver(texto: str, registro: dict, origen: str) -> str:
    """Sustituye las marcas. Una marca sin consulta ABORTA la compilacion.

    No se deja el hueco ni se pone un cero: un documento que sale con un numero
    inventado es peor que uno que no sale.
    """
    # EL MARCADOR DE EXENCION DE C1 SE VA AQUI, en el paso por el que pasan
    # TODOS los documentos, y no en el compilador de D1.
    #
    # C1 y C5 se contradecian: C1 ofrecia `<!--d-->` para declarar una frase
    # descriptiva y C5 prohibe que una nota interna llegue al entregable. Usar
    # el mecanismo previsto por una compuerta rompia la otra — y no en teoria:
    # paso en cuanto la sesion de reportes gasto las tres primeras exenciones.
    #
    # De los dos arreglos posibles este es el que no ensancha una excepcion. El
    # marcador es INSTRUCCION PARA LA COMPUERTA, no contenido: su sitio es la
    # plantilla y no el documento. Exceptuarlo en C5 lo habria dejado a la vista
    # del lector, que es justo lo que C5 existe para impedir.
    texto = texto.replace("<!--d-->", "")
    faltan = [m.group(1) for m in MARCA.finditer(texto) if m.group(1) not in registro]
    if faltan:
        raise SystemExit("%s: marcas sin consulta registrada: %s"
                         % (origen, ", ".join(sorted(set(faltan)))))
    return MARCA.sub(lambda m: registro[m.group(1)], texto)


# --- capturas crudas, que son donde viven las citas textuales --------------

def captura_de(carpeta: str) -> dict | None:
    d = CRUDO / carpeta
    for n in ("captura.json", "captura-feriados.json"):
        if (d / n).exists():
            return json.loads((d / n).read_text())
    return None


def carpeta_de_iso3() -> dict:
    """ISO3 -> carpeta de captura. Se deriva del cargador para no duplicar la tabla."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cargar", REPO / "scripts/cargar_piloto.py")
    mod = importlib.util.module_from_spec(spec)
    # El cargador ejecuta trabajo en `main()`, no al importarse.
    spec.loader.exec_module(mod)
    return {iso: carpeta for carpeta, (iso, *_r) in mod.UNIDADES.items()
            for iso in (iso,)} if False else \
           {v[0]: k for k, v in mod.UNIDADES.items()}


def cifras_del_cruce() -> dict:
    """Gradiente por unidad legal, reusando el guion del cruce como MODULO.

    Se importa `cruce_cbr` en vez de parsear su salida de texto. Parsear la
    salida ata el reporte al formato de impresion de otro guion: cambia un
    ancho de columna alla y aqui salen numeros mal sin que nada falle. Importar
    ata el reporte al CALCULO, que es lo que de verdad se quiere citar.
    """
    import importlib.util
    import zipfile
    spec = importlib.util.spec_from_file_location("cruce", REPO / "scripts/cruce_cbr.py")
    cx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cx)          # `main()` sólo corre bajo __main__

    nuestras = {}
    con = sqlite3.connect(BASE)
    for iso, dias, tipo, base in con.execute(
            "SELECT j.iso3, v.texto_legal_dias, v.tipo_de_dia, v.base_semanal_dias "
            "  FROM vacaciones_version v "
            "  JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id "
            # SELECCION POR CORTE, y es la QUINTA vez que aparece esta clase.
            # Sin el filtro esto era «la ultima fila gana»: el cruce comparaba
            # contra el antecedente las versiones HISTORICAS de Mexico —seis
            # dias en vez de doce— y de Israel —catorce en vez de dieciseis—,
            # porque son las que quedan al final en el orden natural.
            #
            # Arregle exactamente este defecto en `metrica_descanso.py` y no lo
            # segui hasta aqui, que es el otro consumidor de la misma tabla. La
            # leccion que escribi anoche decia que al cambiar el GRANO hay que
            # ir a buscar a TODOS los que la leian; la escribi y no la aplique.
            "  JOIN mediciones m ON m.hecho_id = v.vacaciones_version_id "
            "   AND m.hecho_tipo = 'vacaciones_version' AND m.corte = 2026"):
        nuestras[iso] = (dias, tipo, base)
    con.close()

    por_unidad: dict[str, list] = {}
    with zipfile.ZipFile(cx.XLSX) as z:
        ss = cx.cadenas(z)
        for iso3, hoja in sorted(cx.HOJA.items()):
            s = cx.serie(z, hoja, "9", ss)
            if not s or iso3 not in nuestras:
                continue
            dias, tipo, base = nuestras[iso3]
            cbr = float(s[max(s)]) * cx.DIAS_VAC_POR_PUNTO
            # DOS COLUMNAS DE UNA SOLA PASADA. La de sensibilidad imputa semana
            # de seis DONDE LA NORMA NO LA DECLARA, que es el unico sitio donde
            # hace falta un supuesto nuestro — y el dato dice cuales son:
            # `base_semanal_dias` es NULL exactamente ahi. Son dos, Japon y
            # Paraguay.
            #
            # Va emitida y no tecleada porque acaba de demostrarse que NO se
            # deduce de la otra: −0,5 en base y −0,7 con semana de seis, que no
            # es un ajuste sino otro numero desde otra base. Una cifra que no se
            # puede deducir de otra es justo la que hay que emitir.
            for etiqueta, imputada in (("", base), ("_s6", base or 6.0)):
                conv = cx.a_habiles_5(dias, tipo, imputada)
                if conv is not None:
                    por_unidad.setdefault(tipo + etiqueta, []).append(conv - cbr)

    # Unidades del grupo que NO estan en el antecedente. Es el recuento que
    # justifica la doble codificacion de Guatemala y El Salvador: sin nadie
    # contra quien cruzar, el segundo lector es la unica red. Sale de la misma
    # lectura del archivo externo y no de una lista escrita aparte, que es como
    # se queda vieja cuando el antecedente publique otra cosecha.
    out = {"comparables": sum(len(v) for k, v in por_unidad.items()
                              if not k.endswith("_s6")),
           "unidades_fuera_del_antecedente": str(
               sum(1 for iso in nuestras if iso not in cx.HOJA))}
    for u, ds in por_unidad.items():
        out["dif_%s" % u] = _fmt(sum(ds) / len(ds), 1)
        out["ndif_%s" % u] = str(len(ds))
        out["coinc_%s" % u] = str(sum(1 for d in ds if abs(d) < 0.5))
    return out


def cifras_de_la_dispersion(filas) -> dict:
    """La recta de ingreso contra descanso, y las dos distancias que la leen.

    SE CALCULA AQUI Y NO EN LA FIGURA. La figura ya la calcula para dibujarla, y
    dos calculos del mismo numero en dos archivos es exactamente el defecto que
    llevamos toda la ronda persiguiendo — el que produjo el −0,8 contra −0,5. El
    texto cita ESTAS marcas; si la figura difiere, difiere de una sola verdad y
    se ve.

    La recta publicada excluye Estados Unidos y Japon por decision del principal:
    son las dos unidades cuyo calendario no crea obligacion exigible y que
    tampoco lo compensan con vacaciones, asi que arrastran la recta sin
    pertenecer al fenomeno que describe.

    Las dos distancias son el argumento de fondo y por eso van emitidas: cuanto
    cubre la recta EN TODO el rango de ingreso, y cuanto se aparta Peru de su
    prediccion. Juntas contestan «¿estamos altos solo por ser de renta media?»
    sin estimar ningun efecto.
    """
    import csv as _csv
    import math
    # EL GRUPO ENTERO, no un componente. La primera version leyo
    # `componente_adhesion.csv`, que tiene siete filas: el ajuste salia con n=7 y
    # una pendiente de 10,3 que no se parecia a nada. Un archivo con el nombre
    # casi correcto es peor que uno que falta, porque devuelve un resultado.
    ruta = REPO / "data/derived/grupos_comparacion/grupo_referencia.csv"
    ppp = {r["iso3"]: r for r in _csv.DictReader(ruta.open(encoding="utf-8"))}
    por = {f["iso"]: (f["lo"] + f["hi"]) / 2 for f in filas}
    _c = sqlite3.connect(BASE)
    con_nombres = dict(_c.execute(
        "SELECT iso3, nombre FROM jurisdicciones WHERE nivel='nacional'"))
    en_nombres = dict(_c.execute(
        "SELECT iso3, COALESCE(nombre_en, nombre) FROM jurisdicciones "
        " WHERE nivel='nacional'"))
    _c.close()
    EXCLUIDAS = ("USA", "JPN")
    # LA ENUMERACION TAMBIEN SE EMITE, y es la respuesta a una pregunta que dejo
    # abierta la sesion de la figura: un sistema de marcas protege los NUMEROS de
    # una plantilla, no las oraciones que los explican.
    #
    # El caso que lo mostro es exacto. La recta excluye estas dos, y el rotulo
    # decia «sin Japon». Mientras el calculador no emitia Estados Unidos, quitarlo
    # aqui no hacia nada y el rotulo era CIERTO; al adjudicarse su cero, la misma
    # linea empezo a quitar dos y el rotulo siguio diciendo una. Y la `n` no se
    # movio —45 menos una y 46 menos dos dan 44— asi que la marca resolvia bien y
    # la oracion que la envolvia era falsa.
    #
    # El arreglo generaliza lo de siempre un nivel mas arriba: **cuando una
    # oracion ENUMERA, emitir la enumeracion**. Asi la frase no puede alejarse de
    # la lista que el codigo usa, porque es esa lista.
    p = [(i, math.log10(float(g["ppp_promedio_2021_2025"])), por[i])
         for i, g in ppp.items()
         if i in por and g.get("ppp_promedio_2021_2025") and i not in EXCLUIDAS]
    n = len(p)
    mx = sum(q[1] for q in p) / n
    my = sum(q[2] for q in p) / n
    sxy = sum((q[1] - mx) * (q[2] - my) for q in p)
    sxx = sum((q[1] - mx) ** 2 for q in p)
    ss = sum((q[2] - my) ** 2 for q in p)
    b = sxy / sxx
    r2 = (sxy ** 2 / sxx) / ss
    # Lo que la recta cubre de punta a punta del rango de ingreso observado.
    recorrido = abs(b * (max(q[1] for q in p) - min(q[1] for q in p)))
    per = next(q for q in p if q[0] == "PER")
    residuo = per[2] - (my + b * (per[1] - mx))

    # LAS OTRAS DOS RECTAS, que D1 cita para decir por que NO usa ninguna. La
    # cruda incluye a Estados Unidos y a Japon; la ponderada les da el peso de su
    # poblacion.
    #
    # LA PONDERADA VOLVIO A CAMBIAR DE SIGNO, y el matiz importa. Cuando el cero
    # de Estados Unidos lo inyectaba el guion de la figura, ese giro era un
    # ARTEFACTO y se descarto con razon. Hoy el cero esta adjudicado y sale del
    # calculador como cualquier fila, asi que el giro es la MEDICION. Lo que
    # sigue siendo cierto —y es lo que hay que publicar a su lado— es que la
    # produce UNA sola observacion con el peso de su poblacion encima: no es un
    # artefacto, es una fragilidad, y las dos cosas se declaran distinto.
    todas = [(i, math.log10(float(g["ppp_promedio_2021_2025"])), por[i],
              float(g.get("poblacion_2024") or 0))
             for i, g in ppp.items()
             if i in por and g.get("ppp_promedio_2021_2025")]

    def ajuste(pts, pesos=None):
        W = pesos or [1.0] * len(pts)
        sw = sum(W)
        ax = sum(w * q[1] for w, q in zip(W, pts)) / sw
        ay = sum(w * q[2] for w, q in zip(W, pts)) / sw
        return (sum(w * (q[1] - ax) * (q[2] - ay) for w, q in zip(W, pts))
                / sum(w * (q[1] - ax) ** 2 for w, q in zip(W, pts)))

    pob = [q[3] for q in todas]
    peso_usa = next((q[3] for q in todas if q[0] == "USA"), 0.0) / sum(pob)
    return {
        "disp_ajuste_n": str(n),
        # UNA SOLA MARCA QUE RESUELVE POR IDIOMA, no una `_en` aparte. Mi
        # primera version creo `disp_excluidas` y `disp_excluidas_en`, y la
        # comprobacion de paridad las denuncio con razon: las dos plantillas
        # usaban conjuntos de marcas distintos, asi que dejaban de ser
        # comparables. Y era una excepcion inventada — ninguna otra marca la
        # necesita: `per_indice` no tiene gemela, se formatea segun el idioma.
        # La conjuncion y el nombre del pais cambian dentro de la marca, que es
        # donde tienen que cambiar.
        "disp_excluidas": (" and " if IDIOMA_ACTUAL == "en" else " y ").join(
            (en_nombres if IDIOMA_ACTUAL == "en" else con_nombres)[i]
            for i in EXCLUIDAS
            if i in (en_nombres if IDIOMA_ACTUAL == "en" else con_nombres)),
        "disp_excluidas_n": str(len(EXCLUIDAS)),
        "disp_pendiente": _fmt(b, 1),
        "disp_r2": _fmt(r2, 2),
        "disp_recorrido": _fmt(recorrido, 1),
        "disp_per_residuo": _fmt(residuo, 1),
        "per_residuo": _fmt(residuo, 1),
        "disp_pendiente_cruda": _fmt(ajuste(todas), 1),
        "disp_pendiente_ponderada": _fmt(ajuste(todas, pob), 1),
        "disp_peso_usa": _fmt(100 * peso_usa, 0),
        # DOS DISPERSIONES Y LAS DOS NOMBRADAS, porque el numero depende de la
        # poblacion y la frase que lo usa contrapone «lo que la recta cubre»
        # contra «lo que se observa». Con Estados Unidos dentro son 35,6 dias;
        # sobre las mismas 44 del ajuste, 25,6. Comparar el recorrido de la recta
        # contra una dispersion medida sobre OTRO conjunto es comparar dos cosas
        # distintas, y la version de 25,5 que ya estaba escrita se calculo sin
        # Estados Unidos.
        "disp_dispersion": _fmt(max(por.values()) - min(por.values()), 1),
        "disp_dispersion_ajuste": _fmt(max(q[2] for q in p)
                                       - min(q[2] for q in p), 1),
    }


def cifras_de_la_forma(filas) -> dict:
    """La FORMA de la distribucion, emitida. Nace de una pregunta de
    la revisión de plantillas que merecia respuesta mecanica.

    D1 afirmaba «el conjunto no se separa en dos bloques, la distribucion es
    continua». Al entrar Estados Unidos dejo de ser cierto —dos unidades
    despegadas abajo— y NINGUNA compuerta podia cazarlo: todas las marcas de esa
    seccion seguian resolviendo bien. Lo que envejecio fue la frase que describe
    la FORMA, y una forma no sale de una consulta... hasta que se emite.

    Ese es el arreglo: si la prosa afirma continuidad, que lo afirme CON LA
    CIFRA. `salto_maximo_veces` dice cuantas veces el mayor hueco entre
    posiciones consecutivas supera al mediano. Con un valor de 1 a 3 la palabra
    «continua» se sostiene; con veintitres, no. La frase deja de poder envejecer
    en silencio porque su verdad esta escrita en un numero que se recalcula.

    No cubre toda la clase —una prosa puede describir cualquier propiedad— pero
    cubre la que nos mordio, y el patron es replicable: **cuando una frase
    describa una forma, emitir el estadistico que la hace verdadera o falsa.**
    """
    v = sorted(((f["lo"] + f["hi"]) / 2 for f in filas))
    saltos = sorted(b - a for a, b in zip(v, v[1:]))
    n = len(saltos)
    mediano = saltos[n // 2] if n % 2 else (saltos[n // 2 - 1] + saltos[n // 2]) / 2
    return {
        "salto_mediano": _fmt(mediano, 2),
        "salto_maximo": _fmt(saltos[-1], 1),
        "salto_maximo_veces": _fmt(saltos[-1] / mediano, 0) if mediano else "n/d",
    }


# LOS ROTULOS DE LAS CUATRO TABLAS, por idioma. Estaban cableados en castellano
# dentro del generador, asi que el D1 ingles salia con las cuatro tablas en
# castellano —encabezados Y nombres de pais— con los numeros bien convertidos
# alrededor. Es lo primero que mira un lector, y las siete compuertas pasaban.
#
# El diagnostico es de la revisión de plantillas y es el que hay que recordar: **la
# compuerta de paridad ve la MARCA, no lo que la marca devuelve.** Una marca es
# una caja negra para ella, y dentro de estas cuatro habia castellano. Es el
# mismo fallo que los rotulos dentro de la imagen, una capa mas adentro.
ROTULOS = {
    "es": {
        "orden": ("# | país | jurisdicción | grupo | semana | vacaciones | "
                  "feriados efectivos esperados | descanso, en días | "
                  "% año laboral | # por fracción"),
        "mediana_conjunto": "mediana del conjunto",
        "grupos": ("grupo | n | mediana de descanso, en días | "
                   "mediana del % del año laboral | mediana de feriados efectivos"),
        "descomp": "componente",
        "cambio": ("país | jurisdicción | corte 2016 | corte 2026 | cambio | "
                   "de ellos, exigibles en 2026 | procedencia del corte 2016"),
        # LOS CUATRO ESTADOS, EN PALABRAS Y NO EN CLAVE. El CSV emite
        # `supuesto_sin_cambio`; un cuadro de un documento para leer no.
        "est_verificado": "verificado",
        "est_verificado_parcial": "verificado en parte",
        "est_supuesto_sin_cambio": "supuesto sin cambio",
        "est_no_capturado": "no capturado",
        "peru": "Perú", "ibe": "Iberoamérica", "ocde": "OCDE",
        "med_ocde": "mediana OCDE", "med_ibe": "mediana Iberoamérica",
    },
    "en": {
        "orden": ("# | country | jurisdiction | group | week | leave | "
                  "expected effective holidays | rest, in days | "
                  "% of working year | # by fraction"),
        "mediana_conjunto": "median of the set",
        "grupos": ("group | n | median rest, in days | "
                   "median % of the working year | median effective holidays"),
        "descomp": "component",
        "cambio": ("country | jurisdiction | 2016 cut | 2026 cut | change | "
                   "of which enforceable in 2026 | provenance of the 2016 cut"),
        "est_verificado": "verified",
        "est_verificado_parcial": "partly verified",
        "est_supuesto_sin_cambio": "assumed unchanged",
        "est_no_capturado": "not captured",
        "peru": "Peru", "ibe": "Ibero-America", "ocde": "OECD",
        "med_ocde": "OECD median", "med_ibe": "Ibero-America median",
    },
}


def cifras_de_la_metrica() -> dict:
    """Todo lo que D1 cita de la metrica de descanso, incluidas cuatro tablas.

    Las tablas entran por marca como cualquier cifra. Una tabla tecleada en la
    prosa envejece igual que un numero, y peor: nadie la revisa fila por fila.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "met", REPO / "scripts/metrica_descanso.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    filas = m.filas_de(2026)
    por = {f["iso"]: f for f in filas}
    # La tercera lectura: el mismo derecho bajo un marco de cinco dias para
    # todas, que es lo que hace la literatura. Se calcula con el mismo modulo y
    # no aparte, para que no haya dos definiciones de la misma cifra.
    r_disp = cifras_de_la_dispersion(filas)
    r_disp.update(cifras_de_la_forma(filas))
    filas5 = m.filas_de(2026, "comun5")
    orden5 = sorted(filas5, key=lambda f: -(f["lo"] + f["hi"]) / 2)

    def grupo(archivo):
        ruta = REPO / "data/derived/grupos_comparacion" / archivo
        return {r["iso3"] for r in csv.DictReader(ruta.open(encoding="utf-8"))
                if r["iso3"] in por}
    ibe, ocde = grupo("componente_iberoamerica.csv"), grupo("componente_ocde.csv")

    def mediana(xs):
        xs = sorted(xs)
        n = len(xs)
        return (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2) if n else 0.0

    def centro(f):
        return (f["lo"] + f["hi"]) / 2

    # DOS ORDENAMIENTOS, y el principal decidió que el reporte lleve los dos.
    #
    # Ordenar por fracción del año laboral penaliza sistemáticamente a las seis
    # unidades de semana de seis días —unos ocho puestos de media— porque su
    # denominador tiene 312 días en vez de 260. Perú es el caso: con la jornada
    # real GANA descanso, 25,7 días de vacaciones en vez de 21,4, y BAJA del
    # puesto 2 al 14.
    #
    # Y el argumento que cierra la decisión es incómodo y hay que tenerlo
    # presente: este proyecto existe para denunciar que un índice ajeno esconde
    # una elección de unidad, y **dividir por el año laboral propio es
    # exactamente eso** — una elección normativa, no una normalización neutra.
    # Publicar sólo la fracción nos expondría a nuestra propia crítica.
    orden_dias = sorted(filas, key=lambda f: -centro(f))
    orden_frac = sorted(filas, key=lambda f: -centro(f) / (52.0 * f["base"]))
    orden = orden_dias
    per = por["PER"]
    r = {
        "unidades_metrica": str(len(filas)),
        "unidades_intervalo": str(sum(1 for f in filas if f["lo"] != f["hi"])),
        "per_descanso": _fmt(per["lo"], 1),
        "per_pct_ano": _fmt(100 * per["frac_lo"], 1),
        "per_posicion": str(1 + orden_dias.index(per)),
        "per_posicion_dias": str(1 + orden_dias.index(per)),
        "per_posicion_fraccion": str(1 + orden_frac.index(per)),
        "unidades_semana_seis": str(sum(1 for f in filas if f["base"] >= 6)),
        "per_posicion_comun5": str(1 + [f["iso"] for f in orden5].index("PER")),
        "per_descanso_comun5": _fmt(
            next(f for f in filas5 if f["iso"] == "PER")["lo"], 1),
        "per_fer_efectivos": _fmt(per["f_ef"], 0),
        "ibe_mediana": _fmt(mediana([centro(por[i]) for i in ibe]), 1),
        "ocde_mediana": _fmt(mediana([centro(por[i]) for i in ocde]), 1),
        "mediana_fer_efectivos": _fmt(mediana([por[i]["f_ef"] for i in ocde]), 0),
        "version_publicada": version_publicada(),
        "per_vac_semanas": _fmt(per["sem_vac"], 2),
        "ocde_vac_semanas": _fmt(mediana([por[i]["sem_vac"] for i in ocde]), 2),
        "ibe_vac_semanas": _fmt(mediana([por[i]["sem_vac"] for i in ibe]), 2),
    }

    pos_frac = {f["iso"]: 1 + i for i, f in enumerate(orden_frac)}
    _cols = ("pais_en", "jurisdiccion_de_referencia_en") if IDIOMA_ACTUAL == "en" \
        else ("pais", "jurisdiccion_de_referencia")
    _u = list(csv.DictReader((EXPORT / "unidades.csv").open(encoding="utf-8")))
    pais = {x["pais_iso3"]: x[_cols[0]] or x["pais"] for x in _u}
    ciudad_idi = {x["pais_iso3"]: x[_cols[1]] or x["jurisdiccion_de_referencia"]
                  for x in _u}

    def grupos_de(iso):
        """Etiqueta de grupo, para leer sin reordenar la tabla.

        Se anade COLUMNA en vez de agrupar las filas, y es deliberado: agrupar
        rompe el ordenamiento global, que es la primera pregunta que la tabla
        contesta. Con la etiqueta al lado, el lector localiza a los pares
        regionales sin perder el puesto absoluto — y las medianas por grupo ya
        estan en su propio cuadro.
        """
        e = []
        if iso in ibe:
            e.append(ROTULOS[IDIOMA_ACTUAL]["ibe"])
        if iso in ocde:
            e.append(ROTULOS[IDIOMA_ACTUAL]["ocde"])
        return " · ".join(e) or "—"

    def linea(f, i):
        rango = _fmt(f["lo"], 1) if f["lo"] == f["hi"] else \
            "%s–%s" % (_fmt(f["lo"], 1), _fmt(f["hi"], 1))
        celdas = [str(i), pais.get(f["iso"], f["iso"]),
                  ciudad_idi.get(f["iso"], f["ciudad"]),
                  grupos_de(f["iso"]), _fmt(f["base"], 1 if f["base"] % 1 else 0), _fmt(f["v"], 1),
                  _fmt(f["f_ef"], 1), rango,
                  _fmt(100 * f["frac_lo"], 1) + " %", str(pos_frac[f["iso"]])]
        # La unidad focal en negrita, en el propio Markdown y no en la
        # tipografia. Destacar UNA fila desde LaTeX obligaria a marcarla en el
        # texto de todos modos, y el entregable en Markdown se lee tal cual: si
        # el enfasis vive solo en el PDF, la mitad de los lectores no lo tiene.
        if f["iso"] == "PER":
            celdas = ["**%s**" % c for c in celdas]
        return "| " + " | ".join(celdas) + " |"

    R = ROTULOS[IDIOMA_ACTUAL]
    cab = ("| %s |\n|---:|---|---|---|---:|---:|---:|---:|---:|---:|" % R["orden"])
    n = len(orden_dias)
    med_desc = mediana([centro(f) for f in orden_dias])
    med_pct = mediana([100 * centro(f) / (52.0 * f["base"]) for f in orden_dias])
    cuerpo = [linea(f, i) for i, f in enumerate(orden_dias, 1)]
    # Fila de mediana INTERCALADA en su puesto, no al pie: en una tabla ordenada
    # la posicion de la mediana es parte de la informacion, y al pie habria que
    # contar filas para saber donde cae.
    cuerpo.insert(n // 2, "| | **%s** | | | | | | **%s** | **%s** | |"
                  % (R["mediana_conjunto"], _fmt(med_desc, 1),
                     _fmt(med_pct, 1) + " %"))
    r["tabla_ordenamiento"] = cab + "\n" + "\n".join(cuerpo)

    # Perú contra cada grupo, que es la pregunta que ordena el documento.
    filas_g = ["| %s |" % R["grupos"], "|---|---:|---:|---:|---:|"]
    for nombre, conj in ((R["peru"], {"PER"}), (R["ibe"], ibe), (R["ocde"], ocde)):
        filas_g.append("| %s | %d | %s | %s | %s |" % (
            nombre, len(conj), _fmt(mediana([centro(por[i]) for i in conj]), 1),
            _fmt(100 * mediana([centro(por[i]) / (52.0 * por[i]["base"])
                                for i in conj]), 1) + " %",
            _fmt(mediana([por[i]["f_ef"] for i in conj]), 0)))
    r["tabla_peru_grupos"] = "\n".join(filas_g)

    # De qué se compone la diferencia. EN SEMANAS DE TRABAJO LIBERADAS, y la
    # razón es que la primera versión de este cuadro ponía los días de trabajo
    # de cada unidad uno al lado del otro: 25,7 peruanos contra 20,0 de la
    # mediana de la OCDE. Son días de semanas distintas —Perú tiene semana legal
    # de seis— y compararlos así es exactamente el error que este reporte
    # denuncia, cometido en su propio cuadro principal. En semanas no hay
    # parámetro libre y la comparación es limpia.
    def semanas(f, clave):
        return f["sem_vac"] if clave == "v" else f[clave] / f["base"]

    d = ["| %s | %s | %s | %s |" % (R["descomp"], R["peru"], R["med_ocde"],
                                    R["med_ibe"]),
         "|---|---:|---:|---:|"]
    COMPONENTES = {
        "es": (("Vacaciones, en semanas de trabajo", "v"),
               ("Feriados efectivos, en semanas", "f_ef"),
               ("Feriados perdidos en el descanso semanal, en semanas", "perdidos")),
        "en": (("Annual leave, in working weeks", "v"),
               ("Effective public holidays, in weeks", "f_ef"),
               ("Holidays lost to weekly rest, in weeks", "perdidos")),
    }
    for etiqueta, clave in COMPONENTES[IDIOMA_ACTUAL]:
        d.append("| %s | %s | %s | %s |" % (
            etiqueta, _fmt(semanas(per, clave), 2),
            _fmt(mediana([semanas(por[i], clave) for i in ocde]), 2),
            _fmt(mediana([semanas(por[i], clave) for i in ibe]), 2)))
    r["tabla_descomposicion"] = "\n".join(d)

    # Lo que cambió entre cortes, en feriados, que es lo único con dos cortes.
    con = sqlite3.connect(BASE)
    # EL PAIS VA EN SU COLUMNA, igual que en la tabla de ordenamiento. Esta se
    # habia quedado atras: emitia el codigo ISO y el nombre de la CIUDAD, con lo
    # que «Eslovaquia» no aparecia en ninguna columna y el lector veia «SVK ·
    # Bratislava». La regla del principal —siempre incluye el pais— estaba
    # aplicada a medias, que en una tabla publicada se lee como no aplicada.
    cambios = con.execute("""
        SELECT j.iso3, %(pais)s, %(ciudad)s,
               SUM(CASE WHEN m.corte=2016 THEN f.duracion_dias ELSE 0 END) a,
               SUM(CASE WHEN m.corte=2026 THEN f.duracion_dias ELSE 0 END) b
          FROM mediciones m
          JOIN feriado_version f ON f.feriado_version_id=m.hecho_id
           AND m.hecho_tipo='feriado_version' AND m.estado_verificacion<>'na'
          JOIN jurisdicciones j ON j.jurisdiccion_id=f.jurisdiccion_id
          JOIN jurisdicciones p ON p.jurisdiccion_id=COALESCE(j.padre_id,
                                                             j.jurisdiccion_id)
         GROUP BY j.iso3, p.nombre, j.nombre HAVING a > 0 AND b <> a
         ORDER BY (b - a) DESC""" % {
        # EL NOMBRE EN SU IDIOMA. La columna `nombre_en` existe desde que se
        # decidio que el nombre es dato, y esta consulta seguia leyendo la
        # castellana: el D1 ingles sacaba «Perú» y «Países Bajos» en la primera
        # columna de su cuadro. Tener el dato no basta si la lectura no lo usa.
        "pais": ("COALESCE(p.nombre_en, p.nombre)" if IDIOMA_ACTUAL == "en"
                 else "p.nombre"),
        "ciudad": ("COALESCE(j.nombre_en, j.nombre)" if IDIOMA_ACTUAL == "en"
                   else "j.nombre"),
    }).fetchall()
    # LA COLUMNA EXIGIBLE, porque sin ella esta tabla dice de Estados Unidos
    # «11 → 12, +1» y el lector entiende que gano un derecho. Sus doce son cierre
    # del sector publico y ninguno obliga al empleador privado: exigibles, cero
    # en los dos cortes. Lo mismo, con otra forma, en Dinamarca, Japon y Paises
    # Bajos, donde existe lista oficial y no existe mandato.
    #
    # El dato estaba bien en la base y la metrica principal ya lo respetaba —les
    # da cero—. Lo que fallaba era que dos salidas nuestras, en el mismo paquete,
    # decian cosas distintas del mismo pais.
    exig = dict(con.execute("""
        SELECT j.iso3, SUM(CASE WHEN m.corte=2026
                                 AND f.categoria='descanso_pagado_obligatorio'
                                THEN f.duracion_dias ELSE 0 END)
          FROM mediciones m
          JOIN feriado_version f ON f.feriado_version_id=m.hecho_id
           AND m.hecho_tipo='feriado_version' AND m.estado_verificacion<>'na'
          JOIN jurisdicciones j ON j.jurisdiccion_id=f.jurisdiccion_id
         GROUP BY j.iso3""").fetchall())
    con.close()
    # LA PROCEDENCIA DEL CORTE 2016, POR FILA. El cuadro agrupaba bajo «sin
    # cambio» lo verificado y lo supuesto, y la salvedad de D1 lo justificaba
    # diciendo que la exportacion «todavia no emite el estado por celda». Lo
    # emite: `panel_feriados.csv` trae `estado_2016` con cuatro valores. La
    # salvedad se habia quedado vieja sin que nadie la tocara — un cambio ajeno
    # la volvio falsa— y mientras tanto el cuadro no usaba un dato que ya tenia.
    #
    # SE LEE DE LA MISMA FUNCION QUE EL CSV, no de una consulta paralela: dos
    # definiciones del mismo estado es como se llega a que dos salidas nuestras
    # digan cosas distintas del mismo pais.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pan", Path(__file__).resolve().parent / "panel.py")
    pan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pan)
    estados = pan.estados_del_corte()

    # LA CLAVE ES EL ISO3 Y LA AUSENCIA ABORTA, y las dos mitades de esa frase
    # las escribi mal en el primer intento. `estados_del_corte()` esta indexada
    # por ISO3 y yo consultaba por nombre de ciudad: ninguna clave casaba nunca.
    # Y como el fallo caia en el valor por defecto de un `.get`, el cuadro salio
    # entero con «no capturado» en las cuarenta y siete filas y el recuento de
    # ausentes dio cuarenta y siete — cifras plausibles, ni un error.
    #
    # Es la forma exacta que este proyecto lleva persiguiendo todo el dia: **la
    # entrada equivocada contesta.** Por eso no hay valor por defecto: si una
    # unidad no tiene estado, la compilacion para. Un defecto que aborta cuesta
    # un minuto; uno que responde se publica.
    def rotulo_estado(iso3: str) -> str:
        if iso3 not in estados:
            sys.exit("%s no tiene estado del corte 2016 en sus capturas, y el "
                     "cuadro de cambio lo necesita para declarar su procedencia."
                     % iso3)
        return R.get("est_%s" % estados[iso3], estados[iso3])

    c = ["| %s |" % R["cambio"], "|---|---|---:|---:|---:|---:|---|"]
    for iso, pais, nom, a, b in cambios:
        c.append("| %s | %s | %s | %s | %+g | %s | %s |"
                 % (pais, nom, _fmt(a, 0), _fmt(b, 0), b - a,
                    _fmt(exig.get(iso, 0), 0), rotulo_estado(iso)))
    r["tabla_cambio"] = "\n".join(c)

    # LA COMPARACION ENTRE LAS DOS VARIABLES, EMITIDA. D1 sostenia que el conteo
    # de feriados se mueve mas que el derecho vacacional pero que la comparacion
    # «no es valida hoy», porque el corte 2016 de vacaciones era «mayoritariamente
    # supuesto y no verificado». Dejo de serlo mientras el parrafo seguia
    # diciendolo: cero supuestas. La frase describia el estado de anteayer y
    # ningun cambio la tocaba, que es el criterio de deteccion de esta familia.
    #
    # Se arregla derivandola. Las dos cifras que la sostienen salen de aqui, asi
    # que la proxima vez que el estado del registro cambie, cambia con el.
    con3 = sqlite3.connect(BASE)
    r["fer_movieron"] = _fmt(con3.execute(
        """SELECT COUNT(*) FROM (SELECT j.iso3,
             SUM(CASE WHEN m.corte=2016 THEN f.duracion_dias ELSE 0 END) a,
             SUM(CASE WHEN m.corte=2026 THEN f.duracion_dias ELSE 0 END) b
           FROM mediciones m JOIN feriado_version f
             ON f.feriado_version_id=m.hecho_id AND m.hecho_tipo='feriado_version'
            AND m.estado_verificacion<>'na'
           JOIN jurisdicciones j ON j.jurisdiccion_id=f.jurisdiccion_id
           GROUP BY j.iso3 HAVING a>0 AND b<>a)""").fetchone()[0], 0)
    r["vac_movieron"] = _fmt(con3.execute(
        "SELECT COUNT(DISTINCT jurisdiccion_id) FROM vacaciones_version "
        "WHERE vigencia_hasta IS NOT NULL").fetchone()[0], 0)
    # EL DENOMINADOR DE FERIADOS NO ES 47, y decirlo importa. Dos unidades no
    # tienen corte de 2016 capturado, y para ellas el panel muestra `0 -> 14`:
    # ese cero es una AUSENCIA, no un conteo, y contarlo como cambio inventaria
    # una reforma que nadie midio. `fer_movieron` las excluye por `a > 0`.
    #
    # La revision externa lo leyo al reves —creyo que 21 era la medida de
    # feriados EXIGIBLES, porque tambien da 21— y habria cambiado un numero
    # correcto por otro. Coinciden en el total y no en el conjunto: aquella deja
    # fuera a Dinamarca y Estados Unidos, esta a Espana e Indonesia. Se emite el
    # denominador para que la frase no tenga que prometerlo.
    r["fer_unidades"] = _fmt(con3.execute(
        """SELECT COUNT(*) FROM (SELECT j.iso3,
             SUM(CASE WHEN m.corte=2016 THEN f.duracion_dias ELSE 0 END) a
           FROM mediciones m JOIN feriado_version f
             ON f.feriado_version_id=m.hecho_id AND m.hecho_tipo='feriado_version'
            AND m.estado_verificacion<>'na'
           JOIN jurisdicciones j ON j.jurisdiccion_id=f.jurisdiccion_id
           GROUP BY j.iso3 HAVING a>0)""").fetchone()[0], 0)
    r["vac_unidades"] = _fmt(con3.execute(
        "SELECT COUNT(DISTINCT jurisdiccion_id) FROM vacaciones_version"
        ).fetchone()[0], 0)
    # EL ESTADO DEL CORTE 2016 DE FERIADOS, tambien emitido. D1 decia «en
    # feriados el corte de 2016 esta mayoritariamente verificado contra fuente»
    # a mano, junto al parrafo de vacaciones que si se derivo. La mitad
    # verificada de una frase envejece igual que la otra.
    import csv as _csv
    _pan = list(_csv.DictReader(
        (EXPORT / "panel_feriados.csv").open(encoding="utf-8")))
    for clave, estado in (("fer16_verificado", "verificado"),
                          ("fer16_parcial", "verificado_parcial"),
                          ("fer16_supuesto", "supuesto_sin_cambio"),
                          ("fer16_no_capturado", "no_capturado")):
        r[clave] = _fmt(sum(1 for x in _pan if x["estado_2016"] == estado), 0)
    for clave, estado in (("vac16_confirmadas", "sin_cambio_confirmado"),
                          ("vac16_reforma", "verificado_primaria"),
                          ("vac16_supuestas", "supuesto")):
        r[clave] = _fmt(con3.execute(
            "SELECT COUNT(*) FROM mediciones WHERE corte=2016 "
            "AND hecho_tipo='vacaciones_version' AND estado_verificacion=?",
            (estado,)).fetchone()[0], 0)
    con3.close()

    # Y LAS QUE NO SALEN EN EL CUADRO, que son de las que hablaba la salvedad.
    # Una unidad cuyo conteo no se movio no tiene fila, asi que su procedencia
    # solo puede decirse contandola.
    con_cambio = {iso for iso, _, _, _, _ in cambios}
    sin_cambio = [i for i in estados if i not in con_cambio]
    for clave, valor in (
            ("sc_verificado", "verificado"),
            ("sc_verificado_parcial", "verificado_parcial"),
            ("sc_supuesto", "supuesto_sin_cambio"),
            ("sc_no_capturado", "no_capturado")):
        r[clave] = _fmt(sum(1 for i in sin_cambio if estados[i] == valor), 0)
    r["sc_total"] = _fmt(len(sin_cambio), 0)
    r.update(r_disp)
    return r
