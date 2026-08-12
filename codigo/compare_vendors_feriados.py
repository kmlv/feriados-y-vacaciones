"""Cruce de las dos mediciones independientes de feriados públicos 2026.

Lado Claude: tabla del reporte v1.0 (`sources/claude-2026-08-05/text/
reporte_feriados_vacaciones.txt`), construida sobre la compilación de Wikipedia
"List of minimum annual leave by country". Mide *feriados pagados obligatorios*
(de jure): si la ley no obliga a pagar el día, cuenta 0.

Lado ChatGPT: `sources/chatgpt-2026-08-05/ranking_feriados_observados_2026.csv`,
construido con la librería `holidays` 0.101 más overrides de Pew y de fuente
oficial. Mide *feriados nacionales observados* (calendario): no pregunta si el
día es pagado.

Son constructos distintos. El objeto de este script no es decidir cuál es
correcto, sino cuantificar cuánto se separan y dónde, porque esa separación es
el primer problema de medición que el diseño de investigación tiene que
resolver.

Salida: data/derived/cruce_feriados_2026.csv
"""

from __future__ import annotations

import csv
import re
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLAUDE_TXT = REPO / "sources/claude-2026-08-05/text/reporte_feriados_vacaciones.txt"
CHATGPT_CSV = REPO / "sources/chatgpt-2026-08-05/ranking_feriados_observados_2026.csv"
OUT = REPO / "data/derived/cruce_feriados_2026.csv"

# El reporte de Claude nombra los países en inglés; el CSV de ChatGPT en
# español. Sólo se mapean los nombres que no coinciden tras normalizar.
ES_TO_EN = {
    "Alemania": "Germany", "Arabia Saudí": "Saudi Arabia", "Argelia": "Algeria",
    "Azerbaiyán": "Azerbaijan", "Bangladés": "Bangladesh", "Baréin": "Bahrain",
    "Bielorrusia": "Belarus", "Bosnia y Herzegovina": "Bosnia and Herzegovina",
    "Botsuana": "Botswana", "Brasil": "Brazil", "Bélgica": "Belgium",
    "Camboya": "Cambodia", "Camerún": "Cameroon", "Canadá": "Canada",
    "Catar": "Qatar", "Chequia": "Czechia", "Chipre": "Cyprus",
    "Corea del Sur": "South Korea", "Costa de Marfil": "Ivory Coast",
    "Croacia": "Croatia", "Dinamarca": "Denmark", "Egipto": "Egypt",
    "Emiratos Árabes Unidos": "United Arab Emirates", "Eslovaquia": "Slovakia",
    "Eslovenia": "Slovenia", "España": "Spain", "Estados Unidos": "United States",
    "Estonia": "Estonia", "Esuatini": "Eswatini", "Etiopía": "Ethiopia",
    "Filipinas": "Philippines", "Finlandia": "Finland", "Francia": "France",
    "Grecia": "Greece", "Guinea Ecuatorial": "Equatorial Guinea",
    "Guinea-Bisáu": "Guinea-Bissau", "Haití": "Haiti", "Hungría": "Hungary",
    "Irak": "Iraq", "Irlanda": "Ireland", "Irán": "Iran", "Islandia": "Iceland",
    "Italia": "Italy", "Japón": "Japan", "Jordania": "Jordan",
    "Kazajistán": "Kazakhstan", "Kenia": "Kenya", "Kirguistán": "Kyrgyzstan",
    "Letonia": "Latvia", "Libia": "Libya", "Lituania": "Lithuania",
    "Líbano": "Lebanon", "Macedonia del Norte": "North Macedonia",
    "Malasia": "Malaysia", "Malaui": "Malawi", "Marruecos": "Morocco",
    "Mauricio": "Mauritius", "Moldavia": "Moldova", "México": "Mexico",
    "Myanmar (Birmania)": "Myanmar", "Mónaco": "Monaco", "Níger": "Niger",
    "Noruega": "Norway", "Nueva Zelanda": "New Zealand",
    "Países Bajos": "Netherlands", "Panamá": "Panama", "Paraguay": "Paraguay",
    "Perú": "Peru", "Polonia": "Poland", "Reino Unido": "United Kingdom",
    "República Democrática del Congo": "Congo (Dem. Rep.)",
    "República Dominicana": "Dominican Republic",
    "República Centroafricana": "Central African Republic",
    "República del Congo": "Congo (Rep.)", "Rumanía": "Romania", "Rusia": "Russia",
    "Ruanda": "Rwanda", "Serbia": "Serbia", "Sierra Leona": "Sierra Leone",
    "Singapur": "Singapore", "Siria": "Syria", "Sudáfrica": "South Africa",
    "Sudán": "Sudan", "Sudán del Sur": "South Sudan", "Suecia": "Sweden",
    "Suiza": "Switzerland", "Tailandia": "Thailand", "Tanzania": "Tanzania",
    "Tayikistán": "Tajikistan", "Timor-Leste": "Timor-Leste", "Turquía": "Turkey",
    "Túnez": "Tunisia", "Ucrania": "Ukraine", "Uzbekistán": "Uzbekistan",
    "Yemen": "Yemen", "Yibuti": "Djibouti", "Zambia": "Zambia",
    "Zimbabue": "Zimbabwe",
}

# Fila de ranking del reporte de Claude:
#   "<n> <País> <2026> <2015> <Δ> <estado…>"
ROW = re.compile(r"^\s*(\d{1,3})\s+([A-Za-z()\.\-' ]+?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?|ND)\s+")


def parse_claude_feriados() -> dict[str, float]:
    """Extrae el ranking de feriados 2026 de la sección 2 del reporte v1.0."""
    text = CLAUDE_TXT.read_text()
    start = text.index("2. Feriados públicos obligatorios")
    end = text.index("3. Vacaciones anuales de ley")
    out: dict[str, float] = {}
    for line in text[start:end].splitlines():
        m = ROW.match(line)
        if not m:
            continue
        rank, country, v2026, _v2015 = m.groups()
        country = country.strip()
        # El encabezado de tabla se repite en cada página; no matchea ROW, pero
        # por si acaso se descartan nombres de una sola palabra genérica.
        if country in {"País", "Pag", "Pág"}:
            continue
        out[country] = float(v2026)
    return out


def main() -> None:
    claude = parse_claude_feriados()

    rows = []
    with CHATGPT_CSV.open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            es = r["pais"]
            en = ES_TO_EN.get(es, es)
            if en not in claude:
                continue
            c, g = claude[en], float(r["feriados_final"])
            rows.append({
                "pais_en": en,
                "pais_es": es,
                "iso2": r["iso2"],
                "claude_obligatorios_pagados": c,
                "chatgpt_observados": g,
                "diferencia": round(g - c, 1),
                "chatgpt_estado": r["estado"],
                "chatgpt_fuente": r["fuente_principal"],
            })

    rows.sort(key=lambda x: -abs(x["diferencia"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    diffs = [r["diferencia"] for r in rows]
    agree = sum(1 for d in diffs if d == 0)
    print(f"Países emparejados: {len(rows)}")
    print(f"  Claude sin par en el CSV de ChatGPT: {len(claude) - len(rows)}")
    print(f"Coinciden exactamente: {agree} ({agree / len(rows):.0%})")
    print(f"Diferencia media (ChatGPT - Claude): {statistics.mean(diffs):+.2f}")
    print(f"Diferencia mediana: {statistics.median(diffs):+.1f}")
    print(f"Desviación absoluta media: {statistics.mean(abs(d) for d in diffs):.2f}")
    print(f"Rango: {min(diffs):+.0f} a {max(diffs):+.0f}")
    print(f"\nLas 15 discrepancias mayores -> {OUT.relative_to(REPO)}")
    for r in rows[:15]:
        print(f"  {r['pais_en']:<22} Claude {r['claude_obligatorios_pagados']:>5}"
              f"   ChatGPT {r['chatgpt_observados']:>4}   dif {r['diferencia']:+.0f}")


if __name__ == "__main__":
    main()
