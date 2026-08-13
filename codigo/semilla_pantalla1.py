"""Paso 1a · Semilla — pantalla 1 sobre la ventana completa.

QUÉ ES Y QUÉ NO ES. Esto es DESCUBRIMIENTO, no evidencia. Su salida se marca
`nivel_de_fuente = 6` y `estado_verificacion = 'supuesto'`, y no puede sostener
por sí sola ninguna celda del panel.

RECALL PARCIAL, declarado. "El conteo cambia entre t y t+1" detecta cambios de
quantum en feriados. NO detecta: sustituciones que dejan el conteo igual,
reformas de reglas sin cambio de quantum, cambios en la escala de antigüedad
vacacional, ni nada de vacaciones en absoluto. Por eso las pantallas 2 y 3 no
son redundantes: buscan lo que ésta no puede ver.

NO PRODUCE TASA DE FALSOS POSITIVOS. Una tasa necesita denominador adjudicado, y
la adjudicación ocurre en las pantallas 2 y 3. Aquí sólo hay `n_candidatos` y una
lista priorizada.

Salidas:
  data/derived/semilla/candidatos_pantalla1.csv
  data/derived/semilla/conteos_pantalla1.csv
  data/derived/semilla/manifiesto_pantalla1.json
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import holidays
import pycountry

REPO = Path(__file__).resolve().parent.parent
GRUPO = REPO / "data/derived/grupos_comparacion/grupo_referencia.csv"
OUT = REPO / "data/derived/semilla"

# Parámetros fijados ANTES de correr, como exige el plan.
ANIOS = list(range(2015, 2027))          # bracket de los dos cortes
VARIABLE = "feriados_nacionales_conteo"
NIVEL_DE_FUENTE = 6
ESTADO = "supuesto"

# Definición operativa de candidato, declarada antes de ver la salida:
# un par (unidad, año) es candidato si su conteo difiere del año anterior.
# El primer año de la ventana no puede ser candidato: no tiene predecesor.


def iso3_a_iso2(iso3: str) -> str | None:
    try:
        return pycountry.countries.get(alpha_3=iso3).alpha_2
    except Exception:
        return None


def conteo(iso2: str, anio: int) -> tuple[int | None, str]:
    """Conteo de fechas feriadas nacionales distintas. Devuelve (valor, nota)."""
    try:
        cal = holidays.country_holidays(iso2, years=anio, observed=False,
                                        language="en_US")
    except NotImplementedError:
        return None, "sin_soporte_en_libreria"
    except Exception as e:  # noqa: BLE001
        return None, f"error:{type(e).__name__}"

    # Se eliminan descansos semanales genéricos codificados como feriado.
    dias = {"monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday"}
    fechas = {d for d, n in cal.items() if n.strip().lower() not in dias}
    quitados = len(cal) - len(fechas)
    nota = f"descansos_genericos_eliminados={quitados}" if quitados else ""
    return len(fechas), nota


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    unidades = []
    with GRUPO.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            iso2 = iso3_a_iso2(r["iso3"])
            unidades.append({"iso3": r["iso3"], "iso2": iso2,
                             "pais": r["pais"], "rol": r["rol"]})

    sin_iso2 = [u["iso3"] for u in unidades if not u["iso2"]]

    conteos, sin_soporte = [], []
    for u in unidades:
        if not u["iso2"]:
            continue
        for a in ANIOS:
            v, nota = conteo(u["iso2"], a)
            if v is None:
                sin_soporte.append((u["iso3"], a, nota))
            conteos.append({"iso3": u["iso3"], "pais": u["pais"], "anio": a,
                            "conteo": v, "nota": nota})

    # Candidatos: cambio respecto del año anterior, dentro de la misma unidad.
    por_unidad: dict[str, dict[int, int | None]] = {}
    for c in conteos:
        por_unidad.setdefault(c["iso3"], {})[c["anio"]] = c["conteo"]

    candidatos = []
    for iso3, serie in por_unidad.items():
        pais = next(u["pais"] for u in unidades if u["iso3"] == iso3)
        for a in ANIOS[1:]:
            prev, cur = serie.get(a - 1), serie.get(a)
            if prev is None or cur is None or prev == cur:
                continue
            candidatos.append({
                "iso3": iso3, "pais": pais, "anio_cambio": a,
                "conteo_anterior": prev, "conteo_nuevo": cur,
                "delta": cur - prev, "magnitud": abs(cur - prev),
                "variable": VARIABLE,
                "nivel_de_fuente": NIVEL_DE_FUENTE,
                "estado_verificacion": ESTADO,
            })

    # Prioridad: magnitud del salto, y dentro de eso el año más reciente
    # primero, porque 2023-2026 no tiene cobertura del antecedente CBR.
    candidatos.sort(key=lambda c: (-c["magnitud"], -c["anio_cambio"]))
    for i, c in enumerate(candidatos, 1):
        c["prioridad"] = i

    with (OUT / "conteos_pantalla1.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(conteos[0]))
        w.writeheader()
        w.writerows(conteos)

    with (OUT / "candidatos_pantalla1.csv").open("w", newline="", encoding="utf-8") as fh:
        campos = ["prioridad", "iso3", "pais", "anio_cambio", "conteo_anterior",
                  "conteo_nuevo", "delta", "magnitud", "variable",
                  "nivel_de_fuente", "estado_verificacion"]
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows([{k: c[k] for k in campos} for c in candidatos])

    sha = hashlib.sha256((OUT / "candidatos_pantalla1.csv").read_bytes()).hexdigest()
    manifiesto = {
        "paso": "1a semilla · pantalla 1",
        "herramienta": "holidays",
        "version_herramienta": holidays.__version__,
        "python": sys.version.split()[0],
        "plataforma": platform.platform(),
        "anios": ANIOS,
        "variable": VARIABLE,
        "universo_filas_grupo": len(unidades),
        "unidades_evaluadas": len([u for u in unidades if u["iso2"]]),
        "unidades_sin_iso2": sin_iso2,
        "pares_sin_soporte_en_libreria": len(sin_soporte),
        "unidades_sin_soporte": sorted({s[0] for s in sin_soporte}),
        "definicion_candidato": "conteo(t) != conteo(t-1) dentro de la misma unidad",
        "n_candidatos": len(candidatos),
        "unidades_con_al_menos_un_candidato": len({c["iso3"] for c in candidatos}),
        "nivel_de_fuente": NIVEL_DE_FUENTE,
        "estado_verificacion": ESTADO,
        "no_produce": "tasa de falsos positivos; requiere adjudicación de pantallas 2 y 3",
        "recall_parcial": [
            "no detecta sustituciones que dejan el conteo igual",
            "no detecta reformas de reglas sin cambio de quantum",
            "no detecta cambios en la escala de antigüedad vacacional",
            "no cubre la variable de vacaciones",
        ],
        "sha256_candidatos_csv": sha,
    }
    (OUT / "manifiesto_pantalla1.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(manifiesto, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
