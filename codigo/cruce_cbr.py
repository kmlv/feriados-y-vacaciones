"""Cruza nuestra captura contra el antecedente del CBR — DESPUES, nunca antes.

§23.2 exige que la captura sea ciega y que el cruce se compute despues. Ese orden
ya se cumplio: las ocho unidades estan capturadas y el esquema congelado. Este
guion es el paso siguiente.

QUE SE CRUZA, Y QUE NO.

No se cruzan NIVELES. El CBR normaliza sus variables a un indice entre 0 y 1, y
nosotros contamos dias; comparar 0,67 con 16 no significa nada. Lo comparable es
otra cosa, y es la que le importa a este proyecto:

    ¿REGISTRA EL ANTECEDENTE UN CAMBIO DONDE NOSOTROS REGISTRAMOS UNA REFORMA?

Las cuatro reformas que hallamos estan datadas y con su norma. El CBR codifica
por anio, asi que basta preguntarle si su serie se mueve en el anio de cada una.

LAS TRES RESPUESTAS POSIBLES, y ninguna es «el CBR se equivoco»:

  CONCUERDA      · su serie se mueve en el mismo anio. Refuerza ambas.
  DIVERGE        · nosotros vemos reforma y su serie no se mueve. Puede ser un
                   limite de su constructo —indice normalizado y topado, que no
                   registra el feriado numero 16— o un error nuestro. Hay que
                   leer su codebook antes de decir cual.
  FUERA DE VENTANA · su serie termina en 2022. Lo posterior no lo puede ver, y
                   eso no es divergencia sino cobertura.

Uso:  python3 scripts/cruce_cbr.py
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
XLSX = REPO / ("data/raw/bibliografia/cbr-cambridge_A_20260808/"
               "cbr-labour-regulation-index-2023-dataset.xlsx")

# Variable 9 = annual leave, 10 = public holidays, en la numeracion del CBR.
VARIABLES = {"9": "vacaciones anuales", "10": "feriados publicos"}

# Nuestras reformas datadas, con la norma que las produce. Se escriben aqui y no
# se leen de la base a proposito: son la afirmacion que se somete al cruce, y
# conviene que esten a la vista de quien lee el resultado.
REFORMAS = [
    ("peru", "10", 2022, "Ley 31381 — 9 dic, Batalla de Ayacucho"),
    ("peru", "10", 2022, "Ley 31530 — 6 ago, Batalla de Junin"),
    ("peru", "10", 2024, "Ley 31788 — 7 jun, Batalla de Arica"),
    ("peru", "10", 2023, "Ley 31822 — 23 jul, Fuerza Aerea"),
    ("germany", "10", 2019, "Berlin declara el Frauentag — SUBNACIONAL"),
    ("turkey", "10", 2017, "Ley 6752 — 15 jul, Democracia y Unidad Nacional"),
    ("mexico", "9", 2023, "DOF 27-dic-2022 — vacaciones de 6 a 12 dias laborables"),
    ("mexico", "10", 2024, "DOF 30-sep-2024 — el sexenal pasa de 1-dic a 1-oct "
                           "(regla, no cantidad)"),
]

FIN_DE_VENTANA_CBR = 2022

# LA REGLA DE SU PROPIA VARIABLE, citada de su codebook (p. 16):
#   «Measures the normal number of paid public holidays guaranteed by law or
#    collective agreement. […] The score is normalised on a 0-1 scale, with an
#    entitlement of 18 days equivalent to a score of 1.»
#
# Es LINEAL EN DIAS. Eso cambia el cruce entero: permite traducir su indice a
# dias y compararlo con nuestro conteo, y refuta de paso la explicacion comoda de
# que su escala esta topada. Peru esta en 0,67 — lejos del maximo, con sitio de
# sobra para moverse.
DIAS_POR_PUNTO = 18

# La regla de su variable 9, de la misma pagina: «Measures the normal length of
# annual paid leave […] normalised on a 0-1 scale, with a leave entitlement of
# 30 days equivalent to a score of 1.»
#
# Treinta dias DE QUE, no lo dice. Y sus propias notas muestran que no es una
# unidad sola: para Alemania escriben «24 working days if 6 days week; if 5 days
# week: 20 days» y codifican 20 —convierten—; para Turquia escriben «14 days» y
# codifican 14 —no convierten, y los 14 turcos excluyen domingo y feriados pero
# incluyen sabado, la misma estructura alemana—; y para Peru escriben «30 days»
# y codifican 30, que son dias CALENDARIO.
DIAS_VAC_POR_PUNTO = 30

# A dias de trabajo sobre una semana de `objetivo` dias. Que el objetivo sea un
# parametro y no una constante permite responder la pregunta obligada —cuanto del
# hallazgo es supuesto nuestro— sin escribir un ejercicio aparte.
#
# La respuesta, que no es la que yo esperaba: casi nada. Lo que se calcula por
# debajo son SEMANAS DE DERECHO, y ahi no hay parametro libre. Treinta dias
# corridos son 30/7 semanas se trabaje lo que se trabaje, y multiplicar por
# `objetivo` es cambiar el rotulo, no el supuesto. La base solo hace falta donde
# la norma cuenta en dias de trabajo y NO declara cuantos tiene la semana: dos
# unidades de cuarenta y cuatro.
def a_habiles(dias, tipo, base, objetivo=5.0):
    if tipo == "calendario":
        return dias * objetivo / 7.0
    if tipo == "semanas":
        return dias * objetivo
    if tipo in ("habil", "werktage"):
        return dias * objetivo / base if base and base != objetivo else dias
    return None


def a_habiles_5(dias, tipo, base):
    return a_habiles(dias, tipo, base, 5.0)

# ISO3 -> nombre de la hoja en el libro del CBR. Las que faltan no estan en su
# cobertura: son Guatemala y El Salvador, las dos unidades por las que entraron
# al piloto.
HOJA = {
    "ARG": "argentina", "AUS": "australia", "AUT": "austria", "BEL": "belgium",
    "BOL": "bolivia", "BRA": "brazil", "BGR": "bulgaria", "CAN": "canada",
    "CHL": "chile", "COL": "colombia", "CRI": "costa rica", "CZE": "czechia",
    "DEU": "germany", "DNK": "denmark", "DOM": "dominican republic",
    "ECU": "ecuador", "ESP": "spain", "FIN": "finland", "FRA": "france",
    "GBR": "UK", "GRC": "greece", "HND": "honduras", "HUN": "hungary",
    "IDN": "indonesia", "IRL": "ireland", "ISR": "israel", "ITA": "italy",
    "JPN": "japan", "KOR": "korea", "MEX": "mexico", "NIC": "nicaragua",
    "NLD": "netherlands", "NOR": "norway", "NZL": "new zealand", "PER": "peru",
    "POL": "poland", "PRT": "portugal", "PRY": "paraguay", "ROU": "romania",
    "SVK": "slovakia", "SWE": "sweden", "CHE": "switzerland", "THA": "thailand",
    "TUR": "turkey", "USA": "USA",
}

# Nuestro conteo verificado al final de la ventana del CBR, en dias, para la
# jurisdiccion de referencia. Sale del panel; se escribe aqui para que quien lea
# el cruce vea las dos cifras juntas.
NUESTRO_2022 = {
    "peru": (14, "12 en 2016 + Ayacucho y Junin, ambos con primer feriado en 2022"),
    "germany": (10, "Berlin: nucleo comun de 9 + Frauentag desde 2019"),
    "turkey": (7.5, "solo las civiles; las religiosas aun sin capturar"),
    "mexico": (7, "las de recurrencia ANUAL; el sexenal y la electoral no lo son"),
    "indonesia": (17, "decreto de 2026; el de 2022 no se ha leido"),
    "canada": (9, "Ontario"),
}


def hoja_de(z: zipfile.ZipFile, pais: str) -> str | None:
    wb = z.read("xl/workbook.xml").decode("utf-8", "replace")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8", "replace")
    m = re.search(r'<sheet name="%s"[^>]*r:id="(rId\d+)"' % re.escape(pais), wb)
    if not m:
        return None
    r = re.search(r'Id="%s"[^>]*Target="([^"]+)"' % m.group(1), rels)
    return "xl/" + r.group(1).lstrip("/") if r else None


def cadenas(z: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    xml = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
    return [re.sub(r"<[^>]+>", "", si) for si in re.findall(r"<si>(.*?)</si>", xml, re.S)]


def celdas(z: zipfile.ZipFile, ruta: str, ss: list[str]) -> dict:
    xml = z.read(ruta).decode("utf-8", "replace")
    out = {}
    for c in re.finditer(r'<c r="([A-Z]+)(\d+)"([^>]*)>(.*?)</c>', xml, re.S):
        col, fila, attr, cuerpo = c.groups()
        v = re.search(r"<v>(.*?)</v>", cuerpo, re.S)
        if not v:
            continue
        val = v.group(1)
        if 't="s"' in attr:
            i = int(val)
            val = ss[i] if i < len(ss) else val
        out[(col, int(fila))] = val
    return out


def serie(z: zipfile.ZipFile, pais: str, variable: str, ss: list[str]) -> dict:
    """{anio: valor} de una variable del CBR, o {} si no se pudo leer.

    La hoja de cada pais tiene la fila 1 con el NUMERO de cada variable por
    columna, la columna C con el anio, y una fila por anio. Mi primera version
    buscaba la fila de anios contando corridas de numeros y no acertaba: el anio
    esta en una sola columna, no en una fila. Se corrige mirando la hoja en vez
    de suponer su forma.
    """
    ruta = hoja_de(z, pais)
    if not ruta:
        return {}
    cel = celdas(z, ruta, ss)

    col_var = None
    for (col, fila), val in cel.items():
        if fila == 1 and str(val).strip() == variable:
            col_var = col
            break
    if col_var is None:
        return {}

    out = {}
    for (col, fila), val in cel.items():
        if col != "C" or fila == 1:
            continue
        try:
            anio = int(float(val))
        except (TypeError, ValueError):
            continue
        v = cel.get((col_var, fila))
        if v is not None:
            out[anio] = v
    return out


def nuestro_2022() -> dict:
    """{ISO3: dias de feriado vigentes al cierre de la ventana del CBR}.

    Se lee de la base, no se escribe a mano. Solo cuenta feriados de descanso
    obligatorio: los de observancia optativa y sin mandato nacional no son un
    derecho y contarlos inflaria a Paises Bajos, Japon y Estados Unidos.
    """
    import sqlite3
    base = REPO / "data/derived/piloto.db"
    if not base.exists():
        return {}
    con = sqlite3.connect(base)
    return {r[0]: r[1] for r in con.execute("""
        SELECT j.iso3, SUM(f.duracion_dias)
          FROM mediciones m
          JOIN feriado_version f
            ON f.feriado_version_id = m.hecho_id AND m.hecho_tipo = 'feriado_version'
          JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
         WHERE m.corte = 2026
           AND f.regimen IN ('descanso_obligatorio',
                             'descanso_salvo_requerimiento_con_recargo')
           AND f.vigencia_desde <= '2022-12-31'
         GROUP BY 1""")}


def main() -> int:
    if not XLSX.exists():
        sys.exit("no esta el dataset del CBR en %s" % XLSX.relative_to(REPO))
    z = zipfile.ZipFile(XLSX)
    ss = cadenas(z)

    print("CRUCE CONTRA EL CBR — computado DESPUES de la captura, por §23.2\n")
    print("  %-9s %-4s %-6s %-11s  %s" % ("Unidad", "var", "anio", "el CBR", "nuestra reforma"))
    print("  " + "-" * 92)

    concuerdan = diverge = fuera = ilegible = 0
    for pais, var, anio, norma in REFORMAS:
        s = serie(z, pais, var, ss)
        if not s:
            estado, det = "ILEGIBLE", "no pude aislar la serie"
            ilegible += 1
        elif anio > FIN_DE_VENTANA_CBR:
            estado, det = "FUERA", "su ventana termina en %d" % FIN_DE_VENTANA_CBR
            fuera += 1
        else:
            prev, act = s.get(anio - 1), s.get(anio)
            if prev is None or act is None:
                estado, det = "SIN DATO", "no hay valor para %d o %d" % (anio - 1, anio)
                ilegible += 1
            elif prev != act:
                estado, det = "CONCUERDA", "%s -> %s" % (prev, act)
                concuerdan += 1
            else:
                estado, det = "DIVERGE", "sin cambio (%s)" % act
                diverge += 1
        print("  %-9s %-4s %-6d %-11s  %s" % (pais, var, anio, estado, norma))
        print("  %-9s %-4s %-6s %-11s  %s" % ("", "", "", "", "· " + det))

    print("  " + "-" * 92)
    print("  concuerdan %d · divergen %d · fuera de ventana %d · ilegibles %d\n"
          % (concuerdan, diverge, fuera, ilegible))

    # RESOLUCION DEL INSTRUMENTO. Decir «diverge» caso por caso invita a leerlo
    # como desacuerdo sobre un hecho. Lo que en realidad se ve es otra cosa, y
    # solo aparece mirando la serie ENTERA: cuantas veces se mueve la variable en
    # los 53 anios que cubre. Si no se mueve nunca, la divergencia no es un
    # desacuerdo — es que el instrumento no resuelve esta clase de cambio.
    print("RESOLUCION DEL INSTRUMENTO — cuantas veces se mueve cada serie, 1970-2022\n")
    print("  %-10s %-22s %-9s  %s" % ("Unidad", "variable", "cambios", "valores"))
    print("  " + "-" * 78)
    for pais in ["peru", "germany", "turkey", "mexico", "indonesia", "canada"]:
        for var, nombre in VARIABLES.items():
            s = serie(z, pais, var, ss)
            if not s:
                continue
            cambios, prev = [], None
            for a in sorted(s):
                if s[a] != prev:
                    cambios.append("%d:%s" % (a, s[a]))
                    prev = s[a]
            print("  %-10s %-22s %-9d  %s"
                  % (pais, nombre, len(cambios) - 1, "  ".join(cambios)))
    print()

    # -- Traduccion a dias, ahora que se conoce la regla de la variable ---------
    print("SU INDICE, TRADUCIDO A DIAS CON SU PROPIA REGLA (score x %d)\n" % DIAS_POR_PUNTO)
    print("  %-10s %-12s %-13s %-12s  %s"
          % ("Unidad", "score 2022", "dias implicitos", "nuestro 2022", "nota"))
    print("  " + "-" * 92)
    for pais, (nuestro, nota) in NUESTRO_2022.items():
        s = serie(z, pais, "10", ss)
        if not s:
            continue
        v = float(s[max(s)])
        print("  %-10s %-12s %-13.1f %-12s  %s"
              % (pais, v, v * DIAS_POR_PUNTO, nuestro, nota))
    print()

    # -- CRUCE SISTEMATICO sobre las 47 -----------------------------------------
    nuestro = nuestro_2022()
    print("CRUCE SISTEMATICO — su indice traducido a dias contra nuestro conteo\n")
    print("  %-6s %8s %9s %9s   %s" % ("unidad", "CBR", "nosotros", "dif", "lectura"))
    print("  " + "-" * 74)
    filas, sin_cobertura = [], []
    for iso3, hoja in sorted(HOJA.items()):
        s = serie(z, hoja, "10", ss)
        if not s or iso3 not in nuestro:
            continue
        cbr = float(s[max(s)]) * DIAS_POR_PUNTO
        nos = float(nuestro[iso3])
        filas.append((iso3, cbr, nos, nos - cbr))
    for iso3 in ("GTM", "SLV"):
        if iso3 in nuestro:
            sin_cobertura.append((iso3, nuestro[iso3]))

    filas.sort(key=lambda r: -abs(r[3]))
    for iso3, cbr, nos, dif in filas:
        lectura = ("coincide" if abs(dif) < 1 else
                   "nosotros contamos MAS" if dif > 0 else "el CBR cuenta MAS")
        print("  %-6s %8.1f %9.1f %+9.1f   %s" % (iso3, cbr, nos, dif, lectura))
    print("  " + "-" * 74)
    coinc = sum(1 for _, _c, _n, d in filas if abs(d) < 1)
    print("  %d de %d coinciden dentro de un dia · %d discrepan\n"
          % (coinc, len(filas), len(filas) - coinc))
    if sin_cobertura:
        print("  Fuera de su cobertura, y por eso entraron al piloto: %s\n"
              % ", ".join("%s (%.0f dias)" % x for x in sin_cobertura))

    # -- CRUCE DE VACACIONES, que es donde vive la tesis del proyecto -----------
    import sqlite3
    base_db = REPO / "data/derived/piloto.db"
    if base_db.exists():
        con2 = sqlite3.connect(base_db)
        nuestras = {r[0]: r[1:] for r in con2.execute("""
            SELECT j.iso3, v.texto_legal_dias, v.tipo_de_dia, v.base_semanal_dias
              FROM vacaciones_version v
              JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id""")}
        print("VACACIONES — el numero legal, el del CBR, y los dos en la misma unidad\n")
        print("  %-6s %-16s %7s %9s %9s   %s"
              % ("unidad", "texto legal", "CBR", "convertido", "dif", ""))
        print("  " + "-" * 76)
        cmp_ = []
        for iso3, hoja in sorted(HOJA.items()):
            s = serie(z, hoja, "9", ss)
            if not s or iso3 not in nuestras:
                continue
            dias, tipo, bs = nuestras[iso3]
            conv = a_habiles_5(dias, tipo, bs)
            if conv is None:
                continue
            cbr = float(s[max(s)]) * DIAS_VAC_POR_PUNTO
            cmp_.append((iso3, "%g %s" % (dias, tipo), cbr, conv, conv - cbr))
        for iso3, legal, cbr, conv, dif in sorted(cmp_, key=lambda r: -abs(r[4])):
            print("  %-6s %-16s %7.1f %9.1f %+9.1f" % (iso3, legal, cbr, conv, dif))
        print("  " + "-" * 76)
        print("  %d unidades comparables · %d con diferencia mayor a 2 dias\n"
              % (len(cmp_), sum(1 for r in cmp_ if abs(r[4]) > 2)))

        # La diferencia no es ruido: separa exactamente segun la unidad en que
        # esta escrita la norma. Contarlo es lo que convierte la tabla en dato.
        por_unidad = {}
        for iso3, legal, cbr, conv, dif in cmp_:
            u = legal.split(" ", 1)[1]
            por_unidad.setdefault(u, []).append(dif)
        print("  DIFERENCIA MEDIA SEGUN LA UNIDAD EN QUE ESTA ESCRITA LA NORMA\n")
        print("  %-14s %6s %10s %10s" % ("unidad legal", "n", "dif media", "coinciden"))
        print("  " + "-" * 46)
        for u, ds in sorted(por_unidad.items(), key=lambda kv: sum(kv[1]) / len(kv[1])):
            coinc = sum(1 for d in ds if abs(d) < 0.5)
            print("  %-14s %6d %10.1f %7d/%d" % (u, len(ds), sum(ds) / len(ds), coinc, len(ds)))
        print()

        # CUANTO DEL HALLAZGO ES SUPUESTO NUESTRO. La pregunta es obligada: si la
        # conversion depende de una semana laboral que elegimos, el gradiente
        # podria ser un artefacto de esa eleccion.
        #
        # La respuesta resulto mejor de lo que yo esperaba, y por una razon
        # algebraica. La unidad comun no es «dias de trabajo»: es SEMANAS DE
        # DERECHO. Treinta dias corridos son 30/7 = 4,29 semanas se trabaje lo
        # que se trabaje; 24 Werktage sobre semana de seis son exactamente 4.
        # Reportar en dias sobre semana de cinco es multiplicar por cinco, o sea
        # un cambio de rotulo, no un supuesto.
        #
        # Asi que el unico supuesto vivo esta donde la norma NO declara base y la
        # unidad la necesita. Eso lo dice el dato: `base_semanal_dias` es NULL
        # exactamente ahi. Se mide con semana de cinco y de seis, y solo esas
        # unidades se mueven.
        # `semanas` NO entra: cuatro semanas son cuatro semanas de derecho se
        # trabaje cinco dias o seis, asi que su base no declarada no es un hueco.
        # Solo habil y werktage necesitan saber cuantos dias tiene la semana para
        # saber cuantas semanas son sus dias.
        sin_base = [i for i, (d, t, b) in nuestras.items()
                    if b is None and t in ("habil", "werktage")]
        print("  CUANTO DEPENDE DEL SUPUESTO DE SEMANA LABORAL\n")
        print("  La unidad comun son SEMANAS DE DERECHO, y para 42 de las 44")
        print("  titularidades se calculan SIN suponer nada: la norma declara su base,")
        print("  o cuenta en dias corridos —30/7 semanas se trabaje lo que se trabaje—,")
        print("  o cuenta en semanas directamente.")
        print()
        print("  Quedan %d unidades donde la norma no declara base y la unidad la"
              % len(sin_base))
        print("  necesita: %s. Solo esas se mueven." % ", ".join(sorted(sin_base)))
        print()
        print("  %-14s %6s %12s %12s" % ("unidad legal", "n", "sem. de 5", "sem. de 6"))
        print("  " + "-" * 48)
        por_unidad_6 = {}
        for iso3, hoja in sorted(HOJA.items()):
            s = serie(z, hoja, "9", ss)
            if not s or iso3 not in nuestras:
                continue
            dias, tipo, bs = nuestras[iso3]
            # La base declarada manda siempre; el supuesto solo rellena el hueco.
            conv6 = a_habiles(dias, tipo, bs or 6.0)
            if conv6 is None:
                continue
            cbr = float(s[max(s)]) * DIAS_VAC_POR_PUNTO
            por_unidad_6.setdefault(tipo, []).append(conv6 - cbr)
        for u, ds in sorted(por_unidad.items(), key=lambda kv: sum(kv[1]) / len(kv[1])):
            d6 = por_unidad_6.get(u, [])
            print("  %-14s %6d %12.1f %12s"
                  % (u, len(ds), sum(ds) / len(ds),
                     "%+.1f" % (sum(d6) / len(d6)) if d6 else "n/d"))
        print()
        print("  El gradiente no se mueve, y no por suerte: la conversion a semanas no")
        print("  tiene parametro libre. Lo que sigue siendo convencional es OTRA cosa,")
        print("  y conviene decirla en voz alta: leer su indice como si sus «dias»")
        print("  fueran dias de trabajo. Esa lectura es la que hace el usuario del")
        print("  indice, no nosotros, y es justamente la que el hallazgo cuestiona.")
        print()
        print("  LA COLUMNA QUE IMPORTA es la tercera. El CBR publica el numero que")
        print("  aparece en la norma, y las normas no cuentan en la misma unidad. La")
        print("  cuarta convierte todo a dias de trabajo sobre semana de cinco, que es")
        print("  la unica forma de que dos paises sean comparables.")
        print()
        print("  El caso Peru-Alemania resume el proyecto entero. Su Peru marca 1,0 y")
        print("  su Alemania 0,67: leido asi, Peru concede un 49% mas. Convertidos,")
        print("  Peru da unos 21 dias de trabajo y Alemania 20: un 7%.")
        print()

    print("ANTES DE LEER LAS DISCREPANCIAS COMO ERRORES SUYOS. No lo son, y")
    print("clasificarlas es la mitad del trabajo:\n")
    print("  ARTEFACTO NUESTRO, por el filtro de regimen. Contamos solo feriados de")
    print("  descanso obligatorio, y eso deja a FRA en 1 —en Francia solo el 1 de mayo")
    print("  lo es por ley— y a THA en 1, porque su ley nombra un solo feriado y el")
    print("  resto es una cuota que designa el empleador. Sus 11 y 13 miden otra cosa,")
    print("  no miden mal.")
    print()
    print("  DIFERENCIA DE CONSTRUCTO. GBR y TUR salen +8 y +7,5 porque el CBR los")
    print("  codifica en CERO por una razon que documenta: en ambos el descanso en")
    print("  feriado depende del contrato y no de la ley. Es una decision suya,")
    print("  razonada, y distinta de la nuestra.")
    print()
    print("  RUIDO DE REDONDEO. Su indice viene con dos decimales, asi que 0,67 x 18")
    print("  da 12,06 y no 12. Toda diferencia por debajo de 0,2 es aritmetica, no")
    print("  desacuerdo.")
    print()
    print("  LO QUE QUEDA. Una veintena de unidades con diferencias de uno a tres dias.")
    print("  Ahi si hay desacuerdo real sobre que cuenta como feriado, y es donde el")
    print("  proyecto aporta: nosotros publicamos la lista de fechas con su norma, y")
    print("  ellos un indice. La diferencia se puede auditar fecha por fecha; su")
    print("  numero, no.")
    print()

    print("QUE SALE DE ESTO\n")
    print("1. EL CRUCE VALIDA NUESTRA LINEA BASE, y esto es lo primero que hay que")
    print("   decir. Su Peru marca 0,67, que por su propia regla son 12 dias: el")
    print("   mismo numero que nosotros derivamos de las leyes modificatorias para")
    print("   el corte 2016. Dos metodos independientes coinciden.")
    print("   Y su Mexico marca 6,8, o sea 7 — exactamente nuestras siete de")
    print("   recurrencia ANUAL, dejando fuera el sexenal y la electoral. Su cifra")
    print("   confirma que separar la recurrencia no anual no era rebuscado.")
    print()
    print("2. LA EXPLICACION COMODA QUEDA REFUTADA POR SU PROPIO CODEBOOK. Yo habia")
    print("   escrito que su escala podia estar topada y que por eso no registraba")
    print("   los feriados nuevos de Peru. Su regla es lineal en dias y Peru esta en")
    print("   0,67, lejos del maximo. Tenia sitio de sobra para moverse.")
    print()
    print("   Peru anade dos feriados con primer efecto en 2022, DENTRO de su")
    print("   ventana, y su serie sigue en 12 dias. La diferencia son 2 dias sobre")
    print("   14, un 14%. Es un candidato solido a hallazgo, y ya no una conjetura")
    print("   sobre grano: contradice la regla que ellos mismos publican.")
    print()
    print("3. TURQUIA ES OTRO CASO, Y SU PROPIA FUENTE LO EXPLICA. Codifican 0 y lo")
    print("   justifican asi: «Law 1475 Art. 39 states that provision for whether")
    print("   operations are suspended on public holidays is to be resolved by")
    print("   contract or collective agreement. Thus, paid public holidays APPEAR TO")
    print("   BE OPTIONAL.» El hedge es de ellos.")
    print()
    print("   No es un error de captura: es una decision de constructo razonada. Lo")
    print("   que si conviene mirar es que la Ley 1475 fue sustituida por la 4857 en")
    print("   2003, que su variable de VACACIONES si se actualizo ese anio —de 0,4 a")
    print("   0,47— y que la de feriados no se reviso. Verificarlo exige leer si la")
    print("   4857 y la 2429 garantizan el descanso pagado, y eso no esta hecho.")
    print()
    print("4. LO QUE NO DEPENDE DE NINGUNA DE ESAS LECTURAS. Cuatro de nuestras ocho")
    print("   reformas caen despues del fin de su ventana, en 2023 y 2024. Y en las")
    print("   ocho, las nuestras van DATADAS y con su norma citada; ellos publican un")
    print("   indice por anio-pais, sin fecha ni norma.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
