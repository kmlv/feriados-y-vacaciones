"""La métrica de una sola dimensión: días de trabajo liberados y pagados al año.

QUE SE MIDE, Y CONTRA QUE. Un día de descanso sólo significa algo contra los días
que el trabajador habría trabajado. Por eso la unidad es **días de trabajo
liberados**, y por eso un feriado que cae en el descanso semanal no libera nada.

CUATRO ELECCIONES, y las cuatro se declaran porque las cuatro cambian el número.

1 · FERIADOS EFECTIVOS, NO NOMINALES. Se resuelve la fecha real de cada feriado
    en el año del corte y se cuenta sólo si cae de lunes a viernes. Es lo que
    §4.1 exige al hablar de «ocurrencias observadas», y pesa mucho: en 2026 va de
    cero a seis días según la unidad, más que todo el gradiente de vacaciones.

2 · LA SEMANA SALE DE LA LEY DE JORNADA, no de un supuesto. La primera versión
    de esta métrica usaba la base sobre la que está escrita la norma de
    VACACIONES como si fuera la semana que el trabajador trabaja, y no es lo
    mismo: los 30 Werktage austriacos están escritos sobre semana de seis
    mientras el trabajador austriaco hace cinco. Con esa confusión Austria salía
    primera; era un artefacto.

    Ahora hay dato propio. La captura de jornada dio, para 44 de las 47, los días
    ordinarios que fija la ley de jornada o los que se siguen de su descanso
    semanal garantizado. Donde la ley declina fijarlos —y declinar es distinto de
    callar— la columna lo dice.

3 · LA UNIDAD ES LA FRACCION DEL AÑO LABORAL, además de los días. Un día hábil de
    quien trabaja seis no es el mismo bien que uno de quien trabaja cinco: son
    fracciones distintas de su semana. La fracción no tiene ese problema.

4 · LA IMPUTACION SIGUE §4.2 AL PIE. Donde los feriados extienden, se suman;
    donde se computan contra, se resta la superposición esperada; y donde la
    norma calla, **no se elige**: la métrica es un intervalo. Medido, ese
    intervalo es de menos de día y medio, más pequeño que casi cualquier
    diferencia que interese.

LO QUE ESTA METRICA NO PUEDE HACER HOY, declarado y contado en la salida: las
reglas de traslado no están capturadas como campo. Las que se capturaron como
clase de fecha —el traslado Emiliani colombiano, por ejemplo— sí se resuelven; las
que no, hacen que la unidad aparezca perdiendo días que en la práctica recupera.
Es el sesgo conocido de esta versión y va en la salida, no en una nota al pie.

Uso:  python3 scripts/metrica_descanso.py [--corte 2026]
"""

from __future__ import annotations

import argparse
import csv
import datetime
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# LA CONVERSION VIVE EN UN SOLO SITIO. Estuvo escrita aqui y otra vez en SQL
# dentro del exportador, y las dos copias divergieron: Colombia salia 12,5 en el
# informe y 15,0 en el CSV publicado. Ver `conversion.py`.
from conversion import BASE_POR_DEFECTO, semanas_de_derecho  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "data/derived/piloto.db"
EXPORT = REPO / "data/derived/export"



def pascua(anio: int) -> datetime.date:
    """Domingo de Pascua gregoriano (Meeus/Jones/Butcher). Exacto."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f, g = (b + 8) // 25, (b - (b + 8) // 25 + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(anio, mes, dia)


def pascua_ortodoxa(anio: int) -> datetime.date:
    """Pascua ortodoxa: se calcula en juliano y se traslada al gregoriano."""
    a, b, c = anio % 4, anio % 7, anio % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    mes, dia = (d + e + 114) // 31, ((d + e + 114) % 31) + 1
    juliano = datetime.date(anio, mes, dia)
    return juliano + datetime.timedelta(days=13 if anio >= 1900 else 12)


def solsticio_o_equinoccio(anio: int, cual: str) -> datetime.date:
    """Aproximación de Meeus de baja precisión, buena a ±1 día en este rango.

    Se usa una aproximación y no una efeméride exacta a propósito: el error es de
    horas y la métrica cuenta días de la semana, así que sólo importa en los años
    en que el instante cae cerca de medianoche. La salida cuenta cuántos feriados
    dependen de esto para que el lector sepa el tamaño de la duda.
    """
    y = (anio - 2000) / 1000.0
    tabla = {
        "equinoccio_marzo":      (2451623.80984, 365242.37404, 0.05169, -0.00411, -0.00057),
        "solsticio_junio":       (2451716.56767, 365241.62603, 0.00325, 0.00888, -0.00030),
        "equinoccio_septiembre": (2451810.21715, 365242.01767, -0.11575, 0.00337, 0.00078),
        "solsticio_diciembre":   (2451900.05952, 365242.74049, -0.06223, -0.00823, 0.00032),
    }
    a, b, c, d, e = tabla[cual]
    jde = a + b * y + c * y * y + d * y ** 3 + e * y ** 4
    # De día juliano a fecha civil (algoritmo de Fliegel-Van Flandern).
    z = int(jde + 0.5)
    alpha = int((z - 1867216.25) / 36524.25)
    aa = z + 1 + alpha - alpha // 4
    bb, cc = aa + 1524, int((aa + 1524 - 122.1) / 365.25)
    dd, ee = int(365.25 * cc), int((bb - int(365.25 * cc)) / 30.6001)
    dia = bb - dd - int(30.6001 * ee)
    mes = ee - 1 if ee < 14 else ee - 13
    return datetime.date(anio, mes, int(dia))


def fecha_de(r: dict, anio: int):
    """Fecha real de un feriado en `anio`, o None si su regla no es resoluble."""
    c = r["clase"]
    try:
        if c == "fija":
            return datetime.date(anio, r["mes"], r["dia"])
        if c == "ordinal":
            primero = datetime.date(anio, r["mes"], 1)
            desfase = (r["dia_semana"] - primero.isoweekday()) % 7
            if r["ordinal"] == -1:
                ultimo = (datetime.date(anio + (r["mes"] == 12), r["mes"] % 12 + 1, 1)
                          - datetime.timedelta(days=1))
                return ultimo - datetime.timedelta(
                    days=(ultimo.isoweekday() - r["dia_semana"]) % 7)
            return primero + datetime.timedelta(days=desfase + 7 * (r["ordinal"] - 1))
        if c == "relativa":
            anclas = {"pascua": pascua, "pascua_ortodoxa": pascua_ortodoxa}
            if r["ancla"] in anclas:
                base = anclas[r["ancla"]](anio)
            elif r["ancla"] in ("equinoccio_marzo", "equinoccio_septiembre",
                                "solsticio_junio", "solsticio_diciembre"):
                base = solsticio_o_equinoccio(anio, r["ancla"])
            else:
                return None                      # ano_nuevo_lunar: no resoluble
            return base + datetime.timedelta(days=r["offset"] or 0)
        if c == "relativa_a_fecha":
            # «el lunes siguiente al 9 de julio»: ancla mes-día, objetivo día de
            # la semana, y el signo del desplazamiento da la dirección. Es la
            # forma en que se capturaron los traslados que SI están.
            ancla = datetime.date(anio, r["mes"], r["dia"])
            paso = 1 if (r["offset"] or 1) > 0 else -1
            d = ancla
            for _ in range(7):
                if d.isoweekday() == r["dia_semana"] and d != ancla:
                    return d
                d += datetime.timedelta(days=paso)
            return ancla
    except (ValueError, TypeError):
        return None
    return None


def probabilidad_de_liberar(clase, ancla, off, dsem, ordinal, descanso, efecto):
    """Probabilidad de que este feriado libere un dia de trabajo. Analitica.

    POR QUE LA ESPERANZA Y NO EL ANIO CONCRETO. La cifra de un anio se mueve
    porque el calendario rota, no porque cambie una ley: un feriado en fecha fija
    cae en fin de semana unos dos anios de cada siete. Comparar 2016 con 2026 con
    valores realizados mide esa rotacion y no la reforma, y el ruido —del orden
    de dos dias— es del mismo tamanio que las reformas que buscamos.

    Y NO SUAVIZA TODO, que es lo que la hace defendible. Medido sobre el corte
    2026, **la mitad del conteo ya es determinista**: un 32% lo rescata la ley
    caiga donde caiga, un 14% esta anclado en Pascua y por tanto cae siempre en
    el mismo dia de la semana, y los ordinales y los trasladados tienen su dia
    objetivo escrito. La aleatoriedad vive en el 49% de fecha fija sin rescate, y
    es ahi y solo ahi donde entra la fraccion.
    """
    # `descanso` es dia -> peso, y el peso puede ser 0,5: ver dias_de_descanso.
    laborables = 7 - sum(descanso.values())
    if efecto == "dia_libre":
        return 1.0                      # la ley lo rescata caiga donde caiga
    if clase == "relativa" and ancla in ("pascua", "pascua_ortodoxa"):
        # La Pascua es siempre domingo, asi que el desplazamiento fija el dia de
        # la semana para todos los anios. No hay nada que promediar.
        dia = ((7 + (off or 0) - 1) % 7) + 1
        return 1.0 - descanso.get(dia, 0.0)
    if clase in ("ordinal", "relativa_a_fecha") and dsem:
        return 1.0 - descanso.get(dsem, 0.0)
    # Fecha fija, lunar, remision, solsticio: el dia de la semana rota.
    return laborables / 7.0


def dias_de_descanso(iso: str, j: dict, base: float) -> set:
    """Qué días de la semana son de descanso, en numeración ISO (1 lunes … 7 domingo).

    CUÁLES sale del texto que la captura leyó de la ley. CUÁNTOS sale de `base`,
    que es la misma semana con la que esta fila convierte sus vacaciones y
    construye su denominador. Las dos mitades vienen de sitios distintos a
    propósito: la ley nombra el día de descanso aunque no fije la semana.

    LO QUE HACÍA ANTES Y POR QUÉ ESTABA MAL, que lo encontró la revisión cruzada. `cuántos`
    salía de `dias_descanso_semanal_n`, el descanso semanal MÍNIMO GARANTIZADO.
    Perú garantiza uno, así que el sábado quedaba como laborable y un feriado en
    sábado le liberaba un día — mientras sus vacaciones y su denominador usaban
    semana de cinco. El mismo trabajador con dos calendarios: catorce feriados
    efectivos bajo un calendario de seis y veintiún días de vacaciones bajo uno
    de cinco.

    Es la CUARTA aparición de la trampa de siempre: un mínimo legal garantizado
    no describe una práctica. Ya la había corregido para los días ordinarios y
    no la seguí hasta aquí, que es el otro sitio donde el mismo dato decidía.

    La excepción que obliga a mirar el texto y no contar «los últimos de la
    semana» es ISRAEL: su descanso es el Shabbat, así que su semana laboral
    empieza el domingo y un feriado en domingo SÍ le libera un día. Contarlo con
    la regla occidental le quitaría días que la ley le da.
    """
    # PESOS Y NO UN CONJUNTO, por la media jornada. Argentina y Dominicana
    # declaran semana de 5,5: su descanso es un dia y medio, y un conjunto de
    # numeros de dia no sabe decir «el sabado descansa medio». Con conjunto, las
    # dos redondeaban a dos dias de descanso mientras su denominador usaba 5,5, y
    # quedaba media jornada del mismo hibrido que este arreglo persigue.
    texto, n = j.get("texto", ""), 7 - base
    def repartir(dias):
        """`n` días de descanso repartidos sobre `dias`, el último a peso parcial."""
        out, resto = {}, n
        for d in dias:
            if resto <= 0:
                break
            out[d] = min(1.0, resto)
            resto -= 1.0
        return out

    if "shabbat" in texto or ("sábado" in texto and "domingo" not in texto) \
            or ("sabado" in texto and "domingo" not in texto):
        return repartir([6, 5])          # sábado primero, luego viernes
    if "domingo" in texto and ("sábado" in texto or "sabado" in texto or "lunes" in texto):
        return repartir([7, 6])
    if "domingo" in texto:
        return repartir([7, 6])
    # Sin día nombrado: se toman los últimos de la semana. Es un supuesto y por
    # eso la salida cuenta cuántas unidades dependen de él.
    return repartir([7, 6])


def _calcular(con, corte: int, marco: str = "real",
              conteo: str = "esperado") -> list[dict]:
    """`marco='real'` usa la semana de cada ley; `'comun5'`, cinco para todas.

    El tercer criterio existe porque los otros dos no bastan. Con el MISMO dato,
    Peru sale 2.º por dias liberados, 14.º por fraccion de su anio laboral y 3.º
    bajo el marco comun de cinco. Las tres lecturas son defendibles y la tercera
    es la que hace la literatura: comparar «como si todos trabajaran igual».

    Publicar una sola y callar las otras seria cometer la omision que este
    proyecto le senala al antecedente — esconder una eleccion de unidad dentro
    de un numero. Con las tres, el lector ve de un vistazo cuanto del
    ordenamiento depende del criterio y cuanto de la ley.

    Bajo `comun5` NO se toca nada mas: mismos feriados, misma imputacion, mismos
    intervalos, y las reglas de rescate siguen valiendo porque son hechos de la
    ley y no del marco.
    """
    # SELECCION POR CORTE, y no «la ultima fila del CSV gana».
    #
    # Este diccionario era `{r["iso3"]: r for ...}`. Mientras hubo una version
    # por jurisdiccion daba igual; en cuanto Mexico gano su version historica, la
    # ultima fila sobrescribio a la vigente y el reporte PUBLICO Mexico 2026 con
    # seis dias en vez de doce. Israel entro en el mismo agujero al nacer, con lo
    # que no era un descuido sino la clase entera: toda reforma que se capture
    # entra rota por esta puerta mientras la puerta siga asi.
    #
    # Y entra en SILENCIO, que es la familia de siempre: el CSV esta bien, el
    # esquema esta bien, las 37 validaciones pasan, y el numero sale mal en el
    # documento.
    #
    # El extremo alto va ESTRICTO —`corte < hasta` y no `<=`— y no es un detalle
    # de estilo. Israel corta en 2016-12-31 y su version vigente empieza ese
    # mismo dia; con `<=` las dos filas serian validas para 2016 y volveria el
    # empate que este arreglo existe para deshacer.
    vac = {}
    for r in csv.DictReader((EXPORT / "vacaciones.csv").open(encoding="utf-8")):
        desde, hasta = r.get("vigencia_desde") or "", r.get("vigencia_hasta") or ""
        dia = "%d-01-01" % corte
        if desde and desde > dia:
            continue
        if hasta and dia >= hasta:
            continue
        vac[r["iso3"]] = r
    unidades = {r["pais_iso3"]: r["jurisdiccion_de_referencia"] for r in
                csv.DictReader((EXPORT / "unidades.csv").open(encoding="utf-8"))}

    # La jornada, que es lo que convierte esta métrica en medida y no en supuesto.
    jor = {}
    for iso, dord, orig, dsn, texto, efecto in con.execute("""
            SELECT j.iso3, r.dias_ordinarios, r.dias_ordinarios_origen,
                   r.dias_descanso_semanal_n, r.dias_descanso_semanal,
                   r.efecto_traslado
              FROM regimen_jornada r
              JOIN jurisdicciones j ON j.jurisdiccion_id = r.jurisdiccion_id"""):
        jor[iso] = {"dord": dord, "origen": orig, "dsn": dsn,
                    "texto": (texto or "").lower(), "efecto": efecto}
    if not jor:
        # Sin jornada esta metrica SIGUE dando numeros, y ese es el peligro: cae
        # a la convencion de cinco dias para todas y devuelve cifras plausibles y
        # equivocadas. Degradarse en silencio es peor que fallar.
        raise SystemExit(
            "regimen_jornada esta vacia: la metrica caeria a la convencion de "
            "cinco dias sin avisar.\n  Corre antes: python3 scripts/cargar_piloto.py")

    reglas = con.execute("""
        SELECT j.iso3, f.feriado_version_id, f.duracion_dias, r.clase_de_regla,
               r.mes, r.dia, r.ordinal, r.dia_semana, r.ancla, r.offset_dias
          FROM mediciones m
          JOIN feriado_version f ON f.feriado_version_id = m.hecho_id
           AND m.hecho_tipo='feriado_version'
          JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
          LEFT JOIN regla_fecha_version r
                 ON r.feriado_version_id = f.feriado_version_id
                AND r.condicion_dia_semana IS NULL
         WHERE m.corte = ? AND m.estado_verificacion <> 'na'
           AND f.categoria = 'descanso_pagado_obligatorio'""", (corte,)).fetchall()

    # SEMBRAR EL CERO. La primera version construia este diccionario solo con
    # las filas que devolvia la consulta, y la consulta filtra por feriados de
    # descanso pagado obligatorio. Tokio, Copenhague y Amsterdam tienen CERO
    # —hecho medido y afirmativo: sus feriados estan capturados como observancia
    # optativa o sin mandato nacional— y las tres tienen vacaciones. Sin fila, la
    # unidad se caia de la tabla sin dejar rastro.
    #
    # El argumento que lo cierra, y es de la revisión cruzada: Paris con UN feriado obligatorio
    # se queda en la tabla y Tokio con cero desaparece. Un cero medido no es una
    # ausencia de medicion, y desaparecer es lo que hace una ausencia.
    #
    # Y EL MISMO ARGUMENTO, UN NIVEL MAS ARRIBA, PARA ESTADOS UNIDOS. No tiene
    # fila de vacaciones y por eso se caia de la tabla entera — pero la ausencia
    # ES el dato: no existe mandato federal de vacaciones pagadas, y sus doce
    # feriados son cierre de sector publico sin obligacion para el empleador
    # privado. Cero por lectura de la norma.
    #
    # Hasta hoy ese cero lo afirmaba el guion de la FIGURA, que lo dibujaba
    # aparte porque el calculador no lo emitia: un valor publicado nacido en la
    # capa de presentacion. Es el blocker de la revisión cruzada y tenia razon, con el
    # argumento de la recta ponderada — un cero inventado en el dibujo tendria
    # peso real sobre una recta publicada.
    #
    # BOLIVIA NO ENTRA, y la distincion es el proyecto entero. Tampoco tiene fila
    # de vacaciones, pero por la razon OPUESTA: su norma tiene una ambiguedad
    # gramatical que no hemos resuelto. En Estados Unidos el hueco es del
    # legislador y es el hallazgo; en Bolivia el hueco es NUESTRO. Sembrar los
    # dos ceros por igual aplastaria justo la diferencia que este proyecto existe
    # para no aplastar.
    CERO_POR_NORMA = {
        "USA": "sin mandato federal de vacaciones pagadas; sus feriados son "
               "cierre de sector publico sin obligacion para el empleador privado",
    }
    por_unidad: dict[str, dict] = {
        iso: {"nominal": 0.0, "efectivo": 0.0, "sin_resolver": 0.0,
              "en_descanso": 0.0, "rescatados": 0.0}
        for iso in list(vac) + [i for i in CERO_POR_NORMA if i not in vac]}
    def base_de(iso: str) -> tuple[float, str]:
        """La semana de esta fila. UN SOLO SITIO la decide, y esa es la
        correccion de fondo.

        Antes la decidian dos trozos de codigo separados por ochenta lineas: uno
        para el denominador y las vacaciones, otro —dentro del contador de
        feriados— para saber que dia habria sido laborable. Divergieron, y el
        resultado fue un estimando hibrido en 34 de 45 filas.
        """
        jj = jor.get(iso, {})
        if marco == "comun5":
            return 5.0, "marco comun"
        if jj.get("dord") and jj.get("origen") == "declarado":
            return float(jj["dord"]), jj["origen"]
        # `derivado` NO cuenta como semana real: un numero de dias deducido de
        # dividir el techo semanal entre el diario dice cuanto se PUEDE
        # trabajar, no cuanto se trabaja.
        return float(BASE_POR_DEFECTO), "convencion"

    for iso, fid, dur, clase, mes, dia, ordinal, dsem, ancla, off in reglas:
        u = por_unidad.setdefault(iso, {"nominal": 0.0, "efectivo": 0.0,
                                        "sin_resolver": 0.0, "en_descanso": 0.0,
                                        "rescatados": 0.0})
        u["nominal"] += dur
        jj = jor.get(iso, {})
        # Bajo el marco comun, todas descansan sabado y domingo: es lo que
        # significa «como si todos trabajaran igual».
        descanso = ({6: 1.0, 7: 1.0} if marco == "comun5"
                    else dias_de_descanso(iso, jj, base_de(iso)[0]))
        if conteo == "esperado":
            pr = probabilidad_de_liberar(clase, ancla, off, dsem, ordinal,
                                         descanso, jj.get("efecto"))
            u["efectivo"] += dur * pr
            u["en_descanso"] += dur * (1 - pr)
            if pr == 1.0 and jj.get("efecto") == "dia_libre":
                u["rescatados"] += dur
            continue
        f = fecha_de({"clase": clase, "mes": mes, "dia": dia, "ordinal": ordinal,
                      "dia_semana": dsem, "ancla": ancla, "offset": off}, corte)
        if f is None:
            u["sin_resolver"] += dur
            u["efectivo"] += dur          # no resoluble: se cuenta y se declara
        elif descanso.get(f.isoweekday(), 0.0) < 1.0:
            # Con pesos, un dia de descanso PARCIAL —el sabado de una semana de
            # 5,5— libera la fraccion que se trabajaba. `not in descanso` lo
            # trataba como dia entero de trabajo y devolvia medio dia de mas.
            libera = 1.0 - descanso.get(f.isoweekday(), 0.0)
            u["efectivo"] += dur * libera
            u["en_descanso"] += dur * (1 - libera)
        elif jj.get("efecto") == "dia_libre":
            # Cae en el descanso PERO la ley lo rescata: traslada, anade dia o
            # reduce la cuota de horas. El efecto para el trabajador es el mismo.
            u["efectivo"] += dur
            u["rescatados"] += dur
        else:
            u["en_descanso"] += dur

    filas = []
    for iso in sorted(unidades):
        v, u = vac.get(iso), por_unidad.get(iso)
        if not u:
            continue
        if not v:
            # SIN FILA DE VACACIONES. Solo pasa si la ausencia es el DATO —hoy
            # Estados Unidos— y entonces la unidad entra con cero derecho
            # vacacional y su razon escrita. Bolivia no esta en esa lista porque
            # su hueco es nuestro, no del legislador, y sigue cayendo aqui.
            if iso not in CERO_POR_NORMA:
                continue
            v = {"dias_texto_legal": "0", "tipo_de_dia": "habil",
                 "base_semanal_dias": None, "imputacion_feriados": "extienden"}
        base_norm = int(v["base_semanal_dias"]) if v["base_semanal_dias"] else None
        dias, tipo = float(v["dias_texto_legal"]), v["tipo_de_dia"]
        # Vacaciones en SEMANAS de derecho. Es la magnitud sin parámetro libre:
        # 30 días corridos son 30/7 semanas se trabaje lo que se trabaje.
        # La conversion vive en `conversion.py` y no aqui: estuvo duplicada en
        # SQL y las dos copias divergieron. Ver el modulo para el caso concreto.
        sem = semanas_de_derecho(dias, tipo, base_norm)
        # LA SEMANA DEL TRABAJADOR, y aquí estuve a punto de repetir por tercera
        # vez la misma confusión. La primera versión tomó la base de la norma de
        # VACACIONES por la semana real; la segunda quiso deducirla del descanso
        # semanal garantizado, restando de siete. También es falso: que la ley
        # británica garantice UN día de descanso no significa que se trabajen
        # seis. El mínimo garantizado y la jornada ordinaria son cosas distintas,
        # y restar de siete da el MÁXIMO PERMITIDO, no lo ordinario.
        #
        # Así que sólo se usa el dato cuando la ley fija los días ordinarios. En
        # las 26 unidades donde no los fija se aplica la convención de cinco y se
        # marca. La ganancia de la captura no es haber rellenado esas 26: es
        # saber CUÁLES son.
        jj = jor.get(iso, {})
        base, origen_base = base_de(iso)
        supuesta = origen_base == "convencion"
        v_habiles = sem * base
        f_habiles = u["efectivo"]
        anio_laboral = 52.0 * base
        # §4.1: superposición esperada con inicio uniforme sobre días hábiles.
        superp = f_habiles * v_habiles / anio_laboral
        imp = v["imputacion_feriados"]
        alto = v_habiles + f_habiles
        bajo = alto - superp
        if imp == "extienden":
            lo = hi = alto
        elif imp == "se_computan_contra":
            lo = hi = bajo
        else:
            lo, hi = bajo, alto           # §4.2: intervalo, no punto
        # El descanso semanal MINIMO GARANTIZADO por la ley. Se puede publicar
        # porque ahora es dato, pero se rotula por lo que es: un mínimo, no el
        # descanso efectivo. Quien trabaje cinco días descansa más que su mínimo.
        semanal = (float(jj["dsn"]) * 52.0) if jj.get("dsn") is not None else None
        filas.append({
            "iso": iso, "ciudad": unidades[iso], "base": base,
            "origen_base": origen_base, "supuesta": supuesta, "sem_vac": sem,
            "v": v_habiles, "f_nom": u["nominal"], "f_ef": f_habiles,
            "perdidos": u["en_descanso"], "rescatados": u["rescatados"],
            "sinres": u["sin_resolver"],
            "lo": lo, "hi": hi, "frac_lo": lo / anio_laboral, "frac_hi": hi / anio_laboral,
            "semanal": semanal,
            "total": (lo + semanal) if semanal is not None else None, "imp": imp,
        })
    return filas


def filas_de(corte: int = 2026, marco: str = "real",
             conteo: str = "esperado") -> list[dict]:
    """Las filas de la metrica, para que los reportes las CITEN y no recalculen.

    Recalcular en el generador de reportes duplicaria la definicion, y dos
    definiciones de la misma cifra divergen con el tiempo. Aqui esta la unica.
    """
    con = sqlite3.connect(BASE)
    try:
        return _calcular(con, corte, marco, conteo)
    finally:
        con.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", type=int, default=2026)
    ap.add_argument("--marco", choices=("real", "comun5"), default="real",
                    help="`real` usa la semana de cada ley; `comun5`, cinco para todas")
    ap.add_argument("--conteo", choices=("esperado", "realizado"), default="esperado",
                    help="`esperado` promedia el dia de la semana donde rota; "
                         "`realizado` usa el calendario del anio del corte")
    args = ap.parse_args()
    corte = args.corte
    con = sqlite3.connect(BASE)
    filas = _calcular(con, corte, args.marco, args.conteo)

    print("\nDIAS DE TRABAJO LIBERADOS Y PAGADOS AL AÑO · corte %d · marco %s\n"
          % (corte, {"real": "la semana de cada ley",
                     "comun5": "cinco dias para todas"}[args.marco])
          + "  · conteo %s" % {"esperado": "ESPERADO (sin ruido de calendario)",
                               "realizado": "realizado en el anio"}[args.conteo])
    print("  %-4s %-18s %5s %6s %5s %5s %5s  %-11s %6s %7s"
          % ("iso", "jurisdicción", "sem", "vacac", "fer", "resc", "perd",
             "descanso", "% año", "+semanal"))
    print("  " + "-" * 92)
    # Ordenada por DIAS y no por fraccion, por decision del principal: dividir
    # por el año laboral propio penaliza sistematicamente a las unidades de
    # semana de seis —unos ocho puestos— y es en si misma una eleccion de unidad,
    # que es justo lo que este proyecto denuncia en otros. Las dos columnas van
    # juntas y el lector decide.
    for f in sorted(filas, key=lambda x: -(x["lo"] + x["hi"]) / 2):
        rango = ("%5.1f" % f["lo"]) if f["lo"] == f["hi"] else \
            ("%4.1f–%4.1f" % (f["lo"], f["hi"]))
        pct = ("%5.1f%%" % (100 * f["frac_lo"])) if f["lo"] == f["hi"] else \
            ("%.1f-%.1f%%" % (100 * f["frac_lo"], 100 * f["frac_hi"]))
        marca = {"declarado": "", "derivado": "d", "convencion": "*",
                 "marco comun": "="}.get(f["origen_base"], "?")
        # Con conteo esperado los feriados son fraccionarios —7,86 en vez de 8—
        # y `%g` los imprimia con seis cifras. Un decimal es lo que la cifra
        # sostiene: la esperanza no tiene precision de milesima.
        print("  %-4s %-18s %5s %6.1f %5.1f %5.1f %5.1f  %11s %6s %7s"
              % (f["iso"], f["ciudad"][:18], "%g%s" % (f["base"], marca),
                 f["v"], f["f_ef"], f["rescatados"], f["perdidos"], rango, pct,
                 ("%.0f" % f["total"]) if f["total"] is not None else "n/d"))
    print("  " + "-" * 92)

    supuestas = sum(1 for f in filas if f["supuesta"])
    sinres = sum(1 for f in filas if f["sinres"])
    intervalo = [f for f in filas if f["lo"] != f["hi"]]
    print("""
COMO LEER ESTA TABLA

  `sem`  días ordinarios de trabajo por semana. Sin letra, **la ley de jornada
         los escribe**; `d` se derivan de dividir su techo semanal entre el
         diario; `*` la ley NO los fija y se aplica la convención de cinco — son
         %d unidades, y saber cuáles son es lo que ganó la captura de jornada.
         Con `--marco comun5` va `=` en todas: cinco para todo el mundo, que es
         la tercera lectura y la que hace la literatura.
  `fer`    feriados pagados que liberan un día de trabajo en el año del corte.
  `resc`   de esos, los que caían en el descanso semanal y la ley RESCATA —los
         traslada, añade un día o reduce la cuota de horas—.
  `perd`   feriados pagados que caen en el descanso y no liberan nada.
  `descanso`  vacaciones + feriados efectivos, en días de trabajo de esa unidad,
         con la regla de imputación de §4.2 aplicada. Donde la norma no dice si
         los feriados dentro de las vacaciones las extienden, va INTERVALO y no
         punto: son %d unidades.
         AVISO SOBRE EL DESCUENTO, que lo levantó la revisión cruzada y es justo. Donde los
         feriados se computan CONTRA las vacaciones, lo que se resta es una
         **esperanza y no un derecho leído**: supone que el trabajador empieza
         sus vacaciones con igual probabilidad en cualquier día hábil del año.
         Ninguna norma dice eso. En la práctica las vacaciones se concentran en
         verano y alrededor de las fiestas, que es donde están los feriados, así
         que si esa concentración es real el descuento verdadero es MAYOR que
         éste. Es un supuesto del analista y va rotulado como tal.
  `%% año`  el mismo número como fracción del año laboral de esa unidad. Es la
         cifra adimensional y **la única comparable entre regímenes**: la tabla
         va ordenada por ella y no por los días.
  `+semanal` descanso total en días al año sumando el descanso semanal **mínimo
         garantizado** por la ley. Es un mínimo y no el descanso efectivo: quien
         trabaje cinco días descansa más que su mínimo legal. Ordena distinto que
         la columna anterior, y por eso se publica.

LO QUE ESTA VERSION NO SABE, y hay que decirlo antes de usarla:

  · La semana del trabajador y las reglas de traslado eran los dos huecos de la
    versión anterior, y una tanda de captura sobre las 47 los cerró. Lo que queda
    es más pequeño y va abajo.

  · La ley de jornada de tres unidades —Australia, Indonesia y Estados Unidos—
    no fija ni días ordinarios ni descanso semanal garantizado, así que su
    semana es supuesto nuestro. En Estados Unidos eso no es un hueco de la
    captura: es que **no hay mandato federal**, y la ausencia es el dato.

  · Polonia rescata el feriado reduciendo la cuota de horas del período, y esa
    reducción opera cuando el feriado cae en día distinto del domingo. La
    columna guarda un valor por jurisdicción, así que su sábado y su domingo
    reciben el mismo trato y no deberían. Sobreestima a Polonia en, como mucho,
    los feriados que le caen en domingo.

  · Nicaragua dice que el día «será compensado» y no dice con qué. Va como
    indeterminado, o sea sin rescate, lo que la subestima si la compensación
    resulta ser en días.
  · %d unidades tienen feriados cuya fecha no es resoluble —calendarios lunares,
    remisión normativa, costumbre local—. Se cuentan como si liberaran, lo que
    sobreestima esas unidades en, como mucho, sus dos séptimos.
  · El corte es un año concreto. Un feriado en fecha fija cae en fin de semana
    unos dos años de cada siete, así que la cifra de una unidad se mueve entre
    años sin que cambie ninguna ley. Comparar dos unidades en el mismo corte es
    legítimo; leer la evolución de una entre cortes exige mirar la ley, no el
    número.
""" % (supuestas, len(intervalo), sinres))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
