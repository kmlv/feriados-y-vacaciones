"""Deriva el panel de dos cortes desde la base, y dice lo que no sabe.

El panel NO se escribe: se deriva. Cada feriado lleva su vigencia, y el conteo de
cada corte sale de preguntar cuales estaban vigentes en esa fecha. Dos listas
escritas a mano —una por corte— pueden discrepar entre si sin que nadie lo note;
una derivacion no puede.

La columna que mas importa es la ultima. `no_capturado` no es un cero ni una
copia del otro corte: es la declaracion de que ese corte no se leyo. Indonesia es
el caso que lo justifica — su calendario se fija POR DECRETO CADA ANIO, asi que
el de 2016 es otro documento, y copiar el de 2026 no seria una aproximacion sino
una invencion.

Uso:  python3 scripts/panel.py
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# LAS RUTAS SE RESUELVEN CONTRA EL ARBOL QUE SE ESTE LEYENDO, y no se
# escriben aqui: en el paquete publicado el esquema, las capturas y los
# datos viven en otro sitio, y este guion tiene que arrancar en los dos.
from rutas import BASE, CAPTURAS, REPO
CRUDO = CAPTURAS

GLOSA = {
    "verificado": "las modificatorias de la ventana estan localizadas y datadas",
    "verificado_parcial": "el conteo se verifico; hay cambio de regla sin cambio de cantidad",
    "supuesto_sin_cambio": "no se hallo modificatoria — AUSENCIA NO VERIFICADA",
    "no_capturado": "el corte 2016 no se leyo; no se rellena con el otro",
}


def estados_del_corte() -> dict:
    fuera = {}
    for d in sorted(CRUDO.iterdir()):
        for nombre in ("captura.json", "captura-feriados.json"):
            if (d / nombre).exists():
                cap = json.loads((d / nombre).read_text())
                fuera[cap.get("unidad", d.name)] = (cap.get("corte_2016") or {}).get(
                    "estado", "no_capturado")
                break
    return fuera


def main() -> int:
    if not BASE.exists():
        sys.exit("no existe %s — corre primero scripts/cargar_piloto.py"
                 % BASE.relative_to(REPO))
    con = sqlite3.connect(BASE)
    estados = estados_del_corte()

    filas = list(con.execute("""
        SELECT j.nombre, j.iso3,
               SUM(CASE WHEN m.corte = 2016 THEN f.duracion_dias ELSE 0 END),
               SUM(CASE WHEN m.corte = 2026 THEN f.duracion_dias ELSE 0 END)
          FROM mediciones m
          JOIN feriado_version f
            ON f.feriado_version_id = m.hecho_id AND m.hecho_tipo = 'feriado_version'
          JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
         -- Un feriado condicional medido como `na` se evaluo y NO aplica ese
         -- anio. Sumarlo contaria un dia que no hubo.
         WHERE m.estado_verificacion <> 'na'
         GROUP BY 1, 2
         ORDER BY 4 DESC"""))

    print("PANEL DE FERIADOS — dias por jurisdiccion de referencia\n")
    print("  %-22s %7s %7s %8s   %s" % ("Unidad", "2016", "2026", "delta", "corte 2016"))
    print("  " + "-" * 78)
    comparables = 0
    for nombre, iso3, c16, c26 in filas:
        est = estados.get(iso3, "no_capturado")
        if est == "no_capturado":
            print("  %-22s %7s %7.1f %8s   %s" % (nombre, "n/c", c26, "n/a", est))
            continue
        comparables += 1
        print("  %-22s %7.1f %7.1f %+8.1f   %s" % (nombre, c16, c26, c26 - c16, est))
    print("  " + "-" * 78)
    print("  %d de %d unidades comparables entre cortes.\n" % (comparables, len(filas)))

    print("Que significa cada estado:")
    for k, v in GLOSA.items():
        usados = sum(1 for i in estados.values() if i == k)
        if usados:
            print("  %-20s (%d)  %s" % (k, usados, v))

    print("\nADVERTENCIA DE LECTURA. Un delta de cero puede significar dos cosas muy")
    print("distintas: que no hubo reforma, o que no se busco. Las unidades marcadas")
    print("`supuesto_sin_cambio` estan en el segundo caso y su cero NO es un hallazgo.")

    print("\nReformas datadas en la ventana:")
    for iso3, texto in [
            ("PER", "+4 feriados: leyes 31381 (2021), 31530 (2022), 31788 y 31822 (2023)"),
            ("DEU", "+1 en Berlin: Frauentag, 2019 — reforma SUBNACIONAL, invisible a nivel nacional"),
            ("TUR", "+1: Ley 6752, publicada oct-2016, primer feriado en 2017"),
            ("MEX", "0 en cantidad, pero la regla del feriado sexenal cambio de 1-dic a 1-oct (DOF 2024)")]:
        print("  %s  %s" % (iso3, texto))
    return 0


if __name__ == "__main__":
    sys.exit(main())
