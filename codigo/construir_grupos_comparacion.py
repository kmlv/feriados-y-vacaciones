#!/usr/bin/env python3
"""Construye el grupo de referencia del estudio de feriados y vacaciones de Perú,
aplicando mecánicamente las reglas de docs/03-grupo-referencia.md.

GRUPO DE REFERENCIA = unión de tres componentes, todos con población >= 5M:
  IBERO      países americanos de lengua ibérica (español o portugués)
  OCDE       miembros plenos de la OCDE
  ADHESION   países con proceso de adhesión a la OCDE abierto al corte

Entradas (data/raw/, ninguna se edita a mano después de generada):
  wdi_snapshot_2026-08-07.csv  indicadores del Banco Mundial, snapshot congelado
  paises_atributos.csv         atributos codificados por el investigador

Salidas (data/derived/grupos_comparacion/, TODAS regeneradas en cada corrida):
  grupo_referencia.csv          la unión: una fila por país con sus componentes
  componente_iberoamerica.csv
  componente_ocde.csv
  componente_adhesion.csv
  ledger_grupo_referencia.csv   auditoría: cada país evaluado y por qué entra o no

Uso:
  python3 scripts/construir_grupos_comparacion.py            # desde el snapshot congelado
  python3 scripts/construir_grupos_comparacion.py --fetch     # regenera el snapshot desde la API
  python3 scripts/construir_grupos_comparacion.py --verificar # corre sin escribir

No requiere dependencias externas.
"""

import argparse
import csv
import io
import os
import sys

# --------------------------------------------------------------------------
# Parámetros de las reglas. Cambiar algo aquí exige subir la versión del
# documento normativo y registrar el cambio en su log.
# --------------------------------------------------------------------------

VERSION_REGLAS = "2.0"
FECHA_CORTE = "2026-08-07"

PPP_ANIOS = (2021, 2022, 2023, 2024, 2025)   # ventana del promedio móvil
PPP_MIN_ANIOS = 4                            # años mínimos para calcular el promedio
POB_ANIO = 2024                              # vintage de población, congelado

POB_MIN = 5_000_000                          # piso común a los tres componentes

COMPONENTES = ("ibero", "ocde", "adhesion")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_RAW = os.path.join(RAIZ, "data", "raw")
DIR_OUT = os.path.join(RAIZ, "data", "derived", "grupos_comparacion")
SNAPSHOT = os.path.join(DIR_RAW, f"wdi_snapshot_{FECHA_CORTE}.csv")
ATRIBUTOS = os.path.join(DIR_RAW, "paises_atributos.csv")

API = "https://api.worldbank.org/v2"
IND_PPP = "NY.GDP.PCAP.PP.CD"
IND_POB = "SP.POP.TOTL"

BASE = "PER"


# --------------------------------------------------------------------------
# Lectura
# --------------------------------------------------------------------------

def leer_csv_con_comentarios(ruta):
    """Lee un CSV ignorando las líneas de cabecera que empiezan con '#'."""
    with open(ruta, encoding="utf-8") as fh:
        lineas = [ln for ln in fh if not ln.lstrip().startswith("#")]
    return list(csv.DictReader(io.StringIO("".join(lineas))))


def cargar_indicadores(ruta):
    datos = {}
    for fila in leer_csv_con_comentarios(ruta):
        valor = fila["valor"].strip()
        datos.setdefault(fila["iso3"], {}).setdefault(fila["indicador"], {})[
            int(fila["anio"])
        ] = float(valor) if valor else None
    return datos


# --------------------------------------------------------------------------
# Descarga opcional (requiere red)
# --------------------------------------------------------------------------

def descargar_snapshot(iso3s):
    """Regenera el snapshot desde la API. Sobrescribe el archivo congelado."""
    import json
    import urllib.request

    def pedir(codigos, indicador, desde, hasta):
        url = (f"{API}/country/{';'.join(codigos)}/indicator/{indicador}"
               f"?format=json&date={desde}:{hasta}&per_page=20000")
        with urllib.request.urlopen(url, timeout=60) as r:
            cuerpo = json.load(r)
        if not isinstance(cuerpo, list) or len(cuerpo) < 2 or cuerpo[1] is None:
            raise RuntimeError(f"respuesta inesperada de la API para {indicador}")
        return cuerpo[1]

    filas = []
    for trozo in [iso3s[i:i + 40] for i in range(0, len(iso3s), 40)]:
        for reg in pedir(trozo, IND_PPP, PPP_ANIOS[0], PPP_ANIOS[-1]):
            filas.append((reg["countryiso3code"], IND_PPP, reg["date"], reg["value"]))
        for reg in pedir(trozo, IND_POB, POB_ANIO, POB_ANIO):
            filas.append((reg["countryiso3code"], IND_POB, reg["date"], reg["value"]))

    filas = [f for f in filas if f[0]]
    filas.sort(key=lambda f: (f[1] != IND_PPP, f[0], f[2]))
    cabecera = []
    with open(SNAPSHOT, encoding="utf-8") as fh:
        for ln in fh:
            if ln.lstrip().startswith("#"):
                cabecera.append(ln)
            else:
                break
    with open(SNAPSHOT, "w", encoding="utf-8", newline="") as fh:
        fh.writelines(cabecera)
        w = csv.writer(fh)
        w.writerow(["iso3", "indicador", "anio", "valor"])
        for iso3, ind, anio, val in filas:
            w.writerow([iso3, ind, anio, "" if val is None else val])
    print(f"snapshot regenerado: {len(filas)} filas -> {SNAPSHOT}")


# --------------------------------------------------------------------------
# Reglas
# --------------------------------------------------------------------------

def promedio_ppp(serie):
    vals = [v for v in (serie.get(a) for a in PPP_ANIOS) if v is not None]
    if len(vals) < PPP_MIN_ANIOS:
        return None, len(vals)
    return sum(vals) / len(vals), len(vals)


def evaluar(at, pob):
    """Devuelve la pertenencia a cada componente. El piso de población y la
    exclusión sustantiva se aplican por igual a los tres."""
    if at["exclusion_sustantiva"]:
        return {c: False for c in COMPONENTES}
    if pob is None or pob < POB_MIN:
        return {c: False for c in COMPONENTES}
    return {
        "ibero": at["iberoamerica"] == "si",
        "ocde": at["ocde_estatus"] == "miembro",
        "adhesion": at["ocde_estatus"] == "adhesion",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true",
                    help="regenera el snapshot desde la API antes de construir")
    ap.add_argument("--verificar", action="store_true",
                    help="no escribe; sólo informa")
    args = ap.parse_args()

    atributos = {f["iso3"]: f for f in leer_csv_con_comentarios(ATRIBUTOS)}
    if args.fetch:
        descargar_snapshot(sorted(atributos))
    ind = cargar_indicadores(SNAPSHOT)

    m = {}
    for iso3, at in atributos.items():
        series = ind.get(iso3, {})
        prom, n = promedio_ppp(series.get(IND_PPP, {}))
        pob = series.get(IND_POB, {}).get(POB_ANIO)
        comp = evaluar(at, pob)
        m[iso3] = {"at": at, "ppp": prom, "n_anios": n, "pob": pob,
                   **comp, "ref": any(comp.values())}

    if not m[BASE]["ref"]:
        sys.exit(f"ERROR: el país base {BASE} no quedó en el grupo de referencia.")

    # --- ledger de auditoría ---
    ledger = []
    for iso3, r in sorted(m.items(), key=lambda kv: -(kv[1]["pob"] or 0)):
        at, pob = r["at"], r["pob"]
        excl = at["exclusion_sustantiva"]
        if excl:
            motivo = f"exclusion_sustantiva:{excl}"
        elif pob is None:
            motivo = "sin_dato_de_poblacion"
        elif pob < POB_MIN:
            motivo = f"poblacion_bajo_{POB_MIN // 1_000_000}M"
        elif not r["ref"]:
            motivo = "no_cumple_ningun_componente"
        else:
            motivo = ""
        ledger.append({
            "iso3": iso3, "pais": at["nombre_es"], "region": at["region"],
            "poblacion_2024": "" if pob is None else int(pob),
            "ppp_promedio_2021_2025": "" if r["ppp"] is None else f"{r['ppp']:.2f}",
            "anios_ppp_disponibles": r["n_anios"],
            "iberoamerica": at["iberoamerica"],
            "ocde_estatus": at["ocde_estatus"],
            "comp_ibero": si_no(r["ibero"]),
            "comp_ocde": si_no(r["ocde"]),
            "comp_adhesion": si_no(r["adhesion"]),
            "en_grupo_referencia": si_no(r["ref"]),
            "motivo_exclusion": motivo,
        })

    # --- informe ---
    print(f"Reglas v{VERSION_REGLAS} · corte {FECHA_CORTE} · piso de población "
          f"{POB_MIN // 1_000_000}M\n")
    etiquetas = {"ibero": "Iberoamérica", "ocde": "OCDE miembros",
                 "adhesion": "OCDE adhesión en curso"}
    for c in COMPONENTES:
        miembros = sorted((i for i, r in m.items() if r[c] and i != BASE),
                          key=lambda i: m[i]["at"]["nombre_es"])
        print(f"{etiquetas[c]} ({len(miembros)} comparadores): "
              + ", ".join(m[i]["at"]["nombre_es"] for i in miembros) + "\n")

    ref = [i for i, r in m.items() if r["ref"] and i != BASE]
    print(f"GRUPO DE REFERENCIA: {len(ref)} comparadores + {m[BASE]['at']['nombre_es']}\n")

    for a, b in (("ibero", "ocde"), ("ibero", "adhesion"), ("ocde", "adhesion")):
        inter = sorted((m[i]["at"]["nombre_es"] for i in m if m[i][a] and m[i][b] and i != BASE))
        print(f"  {etiquetas[a]} ∩ {etiquetas[b]}: "
              + (", ".join(inter) if inter else "vacío"))
    triple = [i for i in m if all(m[i][c] for c in COMPONENTES) and i != BASE]
    print(f"  en los tres componentes: {len(triple)}")

    print("\nExcluidos por causa sustantiva: "
          + ", ".join(f"{f['pais']} ({f['motivo_exclusion'].split(':')[1]})"
                      for f in ledger if f["motivo_exclusion"].startswith("exclusion")))
    bajo = [f for f in ledger if f["motivo_exclusion"].startswith("poblacion_bajo")]
    print(f"Excluidos por el piso de {POB_MIN // 1_000_000}M ({len(bajo)}): "
          + ", ".join(f"{f['pais']} ({int(f['poblacion_2024'])/1e6:.1f}M)" for f in bajo))

    sin_ppp = [f["pais"] for f in ledger
               if f["en_grupo_referencia"] == "si" and not f["ppp_promedio_2021_2025"]]
    print(f"En el grupo pero sin serie de ingreso: {', '.join(sin_ppp) or 'ninguno'}")
    print(f"\nUniverso evaluado: {len(m)} países")

    if args.verificar:
        print("\n--verificar: no se escribió nada.")
        return

    escribir_salidas(m, ledger)
    print(f"Salidas regeneradas en {os.path.relpath(DIR_OUT, RAIZ)}/")


def si_no(v):
    return "si" if v else "no"


def escribir_salidas(m, ledger):
    os.makedirs(DIR_OUT, exist_ok=True)

    def orden(iso3):
        return (iso3 != BASE, m[iso3]["at"]["nombre_es"])

    def fila(iso3):
        r, at = m[iso3], m[iso3]["at"]
        return {
            "iso3": iso3,
            "pais": at["nombre_es"],
            "rol": "base" if iso3 == BASE else "comparador",
            "region": at["region"],
            "poblacion_2024": "" if r["pob"] is None else int(r["pob"]),
            "ppp_promedio_2021_2025": "" if r["ppp"] is None else f"{r['ppp']:.2f}",
        }

    cols_base = ["iso3", "pais", "rol", "region", "poblacion_2024",
                 "ppp_promedio_2021_2025"]

    with open(os.path.join(DIR_OUT, "grupo_referencia.csv"), "w",
              encoding="utf-8", newline="") as fh:
        cols = cols_base + ["comp_iberoamerica", "comp_ocde", "comp_adhesion",
                            "ocde_estatus", "nucleo_comun", "base_juridica_nucleo"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for iso3 in sorted((i for i, r in m.items() if r["ref"]), key=orden):
            at = m[iso3]["at"]
            f = fila(iso3)
            f.update({
                "comp_iberoamerica": si_no(m[iso3]["ibero"]),
                "comp_ocde": si_no(m[iso3]["ocde"]),
                "comp_adhesion": si_no(m[iso3]["adhesion"]),
                "ocde_estatus": at["ocde_estatus"],
                "nucleo_comun": at["nucleo_comun"],
                "base_juridica_nucleo": at["base_juridica_nucleo"],
            })
            w.writerow(f)

    for comp, nombre, extra in (
        ("ibero", "componente_iberoamerica.csv", ["ocde_estatus"]),
        ("ocde", "componente_ocde.csv", ["ocde_anio", "nucleo_comun",
                                         "base_juridica_nucleo"]),
        ("adhesion", "componente_adhesion.csv", ["ocde_anio"]),
    ):
        with open(os.path.join(DIR_OUT, nombre), "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols_base + extra)
            w.writeheader()
            for iso3 in sorted((i for i, r in m.items() if r[comp]), key=orden):
                at = m[iso3]["at"]
                f = fila(iso3)
                for c in extra:
                    f[c] = at[c]
                w.writerow(f)

    with open(os.path.join(DIR_OUT, "ledger_grupo_referencia.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write(f"# Auditoría del grupo de referencia. Reglas v{VERSION_REGLAS}, "
                 f"corte {FECHA_CORTE}.\n")
        fh.write(f"# Grupo = union de tres componentes, todos con poblacion >= "
                 f"{POB_MIN // 1_000_000}M:\n")
        fh.write("#   ibero    = pais americano de lengua iberica\n")
        fh.write("#   ocde     = miembro pleno de la OCDE\n")
        fh.write("#   adhesion = proceso de adhesion a la OCDE abierto al corte\n")
        fh.write("# La exclusion sustantiva y el piso de poblacion se aplican antes "
                 "que los tres componentes.\n")
        fh.write("# Alcance: los paises listados en data/raw/paises_atributos.csv.\n")
        w = csv.DictWriter(fh, fieldnames=list(ledger[0].keys()))
        w.writeheader()
        w.writerows(ledger)


if __name__ == "__main__":
    main()
