#!/usr/bin/env python3
"""Cruza el grupo de referencia contra el CBR Labour Regulation Index (2023).

Bloque A de T-002 (prior art del instrumento). Responde tres cosas:

1. Cuáles de las 47 unidades del grupo de referencia están cubiertas por el
   CBR-LRI y cuáles no.
2. Qué valor le asigna el CBR a las dos variables del proyecto —vacaciones
   anuales (variable 9) y feriados públicos (variable 10)— en los años
   disponibles.
3. Cuántas de esas celdas están censuradas por el tope de la normalización,
   que es lo que decide si el dato es reutilizable como ancla o solo como
   indicio.

El CBR publica puntajes normalizados 0-1, no días. La conversión a días es
exacta solo por debajo del tope: 30 días equivalen a 1 en vacaciones y 18 días
equivalen a 1 en feriados (codebook 2023, definiciones de las variables 9 y 10).
En el tope el número de días es una cota inferior, no una medición.

Entrada:  data/raw/bibliografia/cbr-cambridge_A_20260808/*.xlsx
          data/derived/grupos_comparacion/grupo_referencia.csv
Salida:   data/derived/prior_art_cbr.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
XLSX = (
    RAIZ
    / "data/raw/bibliografia/cbr-cambridge_A_20260808"
    / "cbr-labour-regulation-index-2023-dataset.xlsx"
)
GRUPO = RAIZ / "data/derived/grupos_comparacion/grupo_referencia.csv"
SALIDA = RAIZ / "data/derived/prior_art_cbr.csv"

# Tope de la normalización declarado en el codebook 2023.
TOPE_DIAS = {"vacaciones_anuales": 30, "feriados_publicos": 18}

# Columnas del xlsx: la fila 0 rotula las variables 1..40 desde la columna 3,
# y la columna 2 lleva el año. Variable N vive en la columna 2 + N.
COL_ANIO = 2
VAR_VACACIONES = 9
VAR_FERIADOS = 10

# iso3 -> nombre de hoja en el libro del CBR. El CBR nombra hojas en inglés y
# minúsculas, con abreviaturas propias para cuatro países.
HOJAS = {
    "PER": "peru", "DEU": "germany", "ARG": "argentina", "AUS": "australia",
    "AUT": "austria", "BOL": "bolivia", "BRA": "brazil", "BGR": "bulgaria",
    "BEL": "belgium", "CAN": "canada", "CHL": "chile", "COL": "colombia",
    "KOR": "korea", "CRI": "costa rica", "DNK": "denmark", "ECU": "ecuador",
    "SVK": "slovakia", "ESP": "spain", "USA": "USA", "FIN": "finland",
    "FRA": "france", "GRC": "greece", "HND": "honduras", "HUN": "hungary",
    "IDN": "indonesia", "IRL": "ireland", "ISR": "israel", "ITA": "italy",
    "JPN": "japan", "MEX": "mexico", "NIC": "nicaragua", "NOR": "norway",
    "NZL": "new zealand", "PRY": "paraguay", "NLD": "netherlands",
    "POL": "poland", "PRT": "portugal", "GBR": "UK", "CZE": "czechia",
    "DOM": "dominican republic", "ROU": "romania", "SWE": "sweden",
    "CHE": "switzerland", "THA": "thailand", "TUR": "turkey",
    # Sin hoja en el CBR-LRI 2023: SLV (El Salvador), GTM (Guatemala).
}

# Años de interés: el ancla del proyecto y el último año que publica el CBR.
ANIOS = [2016, 2022]


def serie_pais(libro: pd.ExcelFile, hoja: str) -> pd.DataFrame:
    """Devuelve año -> puntaje para las variables 9 y 10 de una hoja país."""
    bruto = libro.parse(sheet_name=hoja, header=None)
    filas = []
    for i in range(1, bruto.shape[0]):
        anio = bruto.iloc[i, COL_ANIO]
        if pd.isna(anio):
            continue
        filas.append(
            {
                "anio": int(anio),
                "vacaciones_anuales": bruto.iloc[i, COL_ANIO + VAR_VACACIONES],
                "feriados_publicos": bruto.iloc[i, COL_ANIO + VAR_FERIADOS],
            }
        )
    return pd.DataFrame(filas)


def main() -> int:
    if not XLSX.exists():
        print(f"Falta la captura cruda: {XLSX}", file=sys.stderr)
        return 1

    grupo = pd.read_csv(GRUPO)
    libro = pd.ExcelFile(XLSX)
    disponibles = set(libro.sheet_names)

    registros = []
    for _, u in grupo.iterrows():
        iso3 = u["iso3"]
        hoja = HOJAS.get(iso3)
        if hoja is None or hoja not in disponibles:
            registros.append(
                {
                    "iso3": iso3, "pais": u["pais"], "rol": u["rol"],
                    "en_cbr": False, "hoja_cbr": "", "anio": pd.NA,
                    "variable": pd.NA, "puntaje_cbr": pd.NA,
                    "dias_implicados": pd.NA, "censurado_en_tope": pd.NA,
                }
            )
            continue

        serie = serie_pais(libro, hoja)
        for anio in ANIOS:
            fila = serie[serie["anio"] == anio]
            for variable, tope in TOPE_DIAS.items():
                puntaje = (
                    fila.iloc[0][variable] if not fila.empty else pd.NA
                )
                censurado = (
                    bool(puntaje >= 1) if pd.notna(puntaje) else pd.NA
                )
                dias = (
                    round(float(puntaje) * tope, 2)
                    if pd.notna(puntaje)
                    else pd.NA
                )
                registros.append(
                    {
                        "iso3": iso3, "pais": u["pais"], "rol": u["rol"],
                        "en_cbr": True, "hoja_cbr": hoja, "anio": anio,
                        "variable": variable, "puntaje_cbr": puntaje,
                        "dias_implicados": dias,
                        "censurado_en_tope": censurado,
                    }
                )

    salida = pd.DataFrame(registros)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    salida.to_csv(SALIDA, index=False)

    cubiertos = salida[salida["en_cbr"]]["iso3"].nunique()
    faltantes = sorted(salida[~salida["en_cbr"]]["iso3"].unique())
    celdas = salida.dropna(subset=["puntaje_cbr"])
    censuradas = celdas[celdas["censurado_en_tope"] == True]  # noqa: E712

    print(f"Unidades del grupo de referencia: {len(grupo)}")
    print(f"Cubiertas por el CBR-LRI:         {cubiertos}")
    print(f"Sin cobertura:                    {faltantes}")
    print(f"Celdas país-año-variable:         {len(celdas)}")
    print(
        f"Censuradas en el tope:            {len(censuradas)}"
        f" ({100 * len(censuradas) / max(len(celdas), 1):.0f}%)"
    )
    for variable in TOPE_DIAS:
        sub = celdas[celdas["variable"] == variable]
        cen = sub[sub["censurado_en_tope"] == True]  # noqa: E712
        print(
            f"  {variable}: {len(cen)}/{len(sub)} en el tope"
            f" ({100 * len(cen) / max(len(sub), 1):.0f}%)"
        )
    print(f"\nEscrito: {SALIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
