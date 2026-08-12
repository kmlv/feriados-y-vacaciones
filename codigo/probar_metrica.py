"""Regresiones de la metrica de descanso. Nace de dos numeros publicados mal.

Los dos fallaron IGUAL: nada se rompio. El CSV estaba bien, el esquema estaba
bien, las 37 validaciones pasaban, y el numero salia mal en el documento.

  1. `regimen_jornada` quedaba vacia en cada reconstruccion y la metrica caia a
     una convencion de cinco dias sin avisar.
  2. La seleccion de version era «la ultima fila del CSV gana». Mientras hubo una
     version por jurisdiccion daba igual; en cuanto Mexico gano su version
     historica, el reporte publico Mexico 2026 con SEIS dias en vez de doce.
     Israel entro en el mismo agujero al nacer.

Israel es lo que convierte esto en suite: con una jurisdiccion parecia un
descuido, con dos seguidas es la CLASE. Toda reforma que se capture a partir de
ahora entra por esa puerta.

Por eso la prueba central no es «Mexico da doce». Esa fija un caso. La central es
la INVARIANTE: ninguna jurisdiccion puede resolver a dos versiones en un corte.
Esa falla tambien con la tercera reforma, que aun no existe.

Uso:  python3 scripts/probar_metrica.py
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXPORT = REPO / "data/derived/export"

spec = importlib.util.spec_from_file_location("met", REPO / "scripts/metrica_descanso.py")
met = importlib.util.module_from_spec(spec)
spec.loader.exec_module(met)

fallos: list[str] = []


def ok(cond, etiqueta, detalle=""):
    print("  %-6s %s%s" % ("OK" if cond else "FALLA", etiqueta,
                           "" if cond else "\n            " + detalle))
    if not cond:
        fallos.append(etiqueta)


def vigente_en(corte: int) -> dict:
    """Las filas de vacaciones validas en un corte, SIN colapsar duplicados.

    Devuelve iso3 -> lista, a proposito: colapsar aqui esconderia justo el
    defecto que esta suite persigue.
    """
    dia = "%d-01-01" % corte
    out: dict[str, list] = {}
    for r in csv.DictReader((EXPORT / "vacaciones.csv").open(encoding="utf-8")):
        desde, hasta = r.get("vigencia_desde") or "", r.get("vigencia_hasta") or ""
        if desde and desde > dia:
            continue
        if hasta and dia >= hasta:
            continue
        out.setdefault(r["iso3"], []).append(r)
    return out


print("REGRESIONES DE LA METRICA DE DESCANSO\n")

# --- 1 · la invariante, que es la prueba de verdad -------------------------
for corte in (2016, 2026):
    dobles = {i: [r["dias_texto_legal"] for r in rs]
              for i, rs in vigente_en(corte).items() if len(rs) > 1}
    ok(not dobles, "corte %d: ninguna jurisdiccion resuelve a dos versiones" % corte,
       "ambiguas: %s. Con dos filas validas gana la ultima del CSV, que es "
       "arbitraria." % dobles)

# --- 2 · el extremo alto es ESTRICTO ---------------------------------------
# Israel corta en 2016-12-31 y su version vigente empieza ese mismo dia. Con
# `<=` en el extremo alto las dos filas serian validas para 2016. Es el caso que
# hace la frontera visible, y por eso se prueba por su fecha y no por su nombre.
bordes = [(i, rs) for i, rs in vigente_en(2016).items()
          if any((r.get("vigencia_hasta") or "").startswith("2016") for r in rs)]
ok(all(len(rs) == 1 for _, rs in bordes),
   "una version que EXPIRA dentro del ano del corte no empata con su sucesora",
   "empatan: %s" % [i for i, rs in bordes if len(rs) > 1])

# --- 3 · las dos reformas conocidas, por su valor --------------------------
# Fijan el caso concreto. Valen menos que la invariante y se conservan porque un
# numero equivocado que ya se publico merece su propia linea.
ESPERADO = {("MEX", 2016): 6.0, ("MEX", 2026): 12.0,
            ("ISR", 2016): 10.0, ("ISR", 2026): 11.4}
for (iso, corte), esperado in sorted(ESPERADO.items()):
    filas = {f["iso"]: f for f in met.filas_de(corte)}
    got = round(filas[iso]["v"], 1) if iso in filas else None
    ok(got == esperado, "%s corte %d: vacaciones convertidas = %s" % (iso, corte, esperado),
       "devuelve %s" % got)

# --- 4 · un solo calendario por fila ---------------------------------------
# La invariante que faltaba, y la encontro la revisión cruzada. La semana con la que una fila
# decide si un feriado habria caido en dia laborable tiene que ser LA MISMA con
# la que convierte sus vacaciones y construye su denominador. No lo era: los
# feriados usaban el descanso semanal minimo garantizado —un minimo legal, no una
# practica— y el resto la semana ordinaria. El mismo trabajador con dos
# calendarios, en 22 de 45 filas.
#
# Se prueba DIRECTO —cuantos dias de descanso usa el contador de feriados— y no
# por aritmetica sobre la salida. Mi primer intento puso un techo de
# `nominales x base/7` y fallo en 26 filas siendo el codigo correcto: da por
# supuesto que los feriados se reparten uniformemente en la semana, y los que van
# anclados a un dia —el lunes de Pascua, «el primer lunes de»— liberan siempre.
# Una prueba con un modelo mas pobre que el codigo acusa al codigo.
import sqlite3 as _sq
_con = _sq.connect(REPO / "data/derived/piloto.db")
_jor = {i: {"dord": d, "origen": o, "dsn": n, "texto": (t or "").lower()}
        for i, d, o, n, t in _con.execute(
            "SELECT j.iso3, r.dias_ordinarios, r.dias_ordinarios_origen, "
            "       r.dias_descanso_semanal_n, r.dias_descanso_semanal "
            "  FROM regimen_jornada r "
            "  JOIN jurisdicciones j ON j.jurisdiccion_id = r.jurisdiccion_id")}
malas = []
for iso, jj in sorted(_jor.items()):
    base = (float(jj["dord"]) if jj.get("dord") and jj["origen"] == "declarado"
            else 5.0)
    n = sum(met.dias_de_descanso(iso, jj, base).values())
    if abs(n - (7 - base)) > 0.01:
        malas.append("%s: semana de %g pero %g dias de descanso" % (iso, base, n))
ok(not malas, "el contador de feriados usa la MISMA semana que el denominador",
   "; ".join(malas[:6]))

# --- 5 · la jornada sigue siendo obligatoria -------------------------------
# El primer defecto de esta familia. Se prueba que la metrica se NIEGA, no que
# acierte: lo que la hacia peligrosa era seguir dando cifras plausibles.
import sqlite3
con = sqlite3.connect(":memory:")
con.executescript((REPO / "schema/draft/001_schema.sql").read_text())
try:
    met._calcular(con, 2026)
    ok(False, "sin regimen_jornada la metrica se niega a correr",
       "devolvio cifras en vez de negarse: volvio la degradacion silenciosa")
except SystemExit:
    ok(True, "sin regimen_jornada la metrica se niega a correr")
except Exception as e:
    ok(True, "sin regimen_jornada la metrica se niega a correr (%s)" % type(e).__name__)


# --- 6 · la procedencia del corte 2016 se busca por la clave correcta ------
# EL DEFECTO QUE ESTA PRUEBA FIJA. El cuadro de cambio gano una columna con el
# estado del corte 2016, y la primera version lo buscaba por NOMBRE DE CIUDAD en
# una tabla indexada por ISO3. Ninguna clave casaba, y como la busqueda tenia
# valor por defecto, el cuadro salio con «no capturado» en las 47 filas y el
# recuento de ausentes dio 47. Cifras plausibles, cero errores.
#
# La prueba es ESTRUCTURAL y no de valores: comprueba que las filas del cuadro
# mas las ausentes reproduzcan los totales del panel, estado por estado. Asi
# sigue valiendo cuando cambien los datos, que es de lo que ya nos hemos comido
# una version — un techo aritmetico acusando 26 filas correctas.
import collections
import csv as _csv

import reportes_nucleo as _rn

r = _rn.cifras_de_la_metrica()
filas_cuadro = [l for l in r["tabla_cambio"].splitlines()
                if l.startswith("| ") and "---" not in l][1:]
panel = list(_csv.DictReader(
    (REPO / "data/derived/export/panel_feriados.csv").open(encoding="utf-8")))
total = collections.Counter(x["estado_2016"] for x in panel)
ROT = {"verificado": "verificado", "verificado_parcial": "verificado en parte",
       "supuesto_sin_cambio": "supuesto sin cambio",
       "no_capturado": "no capturado"}
en_cuadro = collections.Counter(l.rstrip(" |").rsplit("| ", 1)[-1].strip()
                                for l in filas_cuadro)
ausentes = {"verificado": int(r["sc_verificado"]),
            "verificado_parcial": int(r["sc_verificado_parcial"]),
            "supuesto_sin_cambio": int(r["sc_supuesto"]),
            "no_capturado": int(r["sc_no_capturado"])}
malos = [e for e, n in total.items()
         if en_cuadro.get(ROT[e], 0) + ausentes[e] != n]
ok(not malos,
   "el estado del corte 2016 cuadra: filas del cuadro + ausentes = panel",
   "no cuadra en %s — la busqueda del estado no casa por su clave"
   % ", ".join(malos))
ok(int(r["sc_total"]) == sum(ausentes.values()),
   "el total de ausentes es la suma de su desglose")

print("\n%s" % ("Metrica: todas las regresiones pasan."
                if not fallos else "FALLAN %d: %s" % (len(fallos), ", ".join(fallos))))
sys.exit(1 if fallos else 0)
