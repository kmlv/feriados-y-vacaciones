#!/usr/bin/env python3
"""Recupera del Internet Archive las fichas de tiempo de trabajo de la base
juridica de la OIT (Database of Conditions of Work and Employment Laws,
"TRAVAIL"), para las unidades del proyecto.

POR QUE ESTE SCRIPT EXISTE. La base murio: `www.ilo.org/dyn/travail/*` devuelve
404 tras la migracion del sitio de la OIT a `webapps.ilo.org`, y el path nuevo
tampoco responde. El ultimo snapshot vivo en el Internet Archive es de abril de
2024. Su seccion de tiempo de trabajo contiene, por pais y con cita al articulo,
vacaciones anuales (periodo de calificacion, duracion, pago y **programacion y
fraccionamiento**), feriados publicos (numero y lista de fechas, pago, trabajo
en feriado), limites de jornada y descanso semanal con dia nombrado.

QUE ES Y QUE NO ES. Es ANTECEDENTE, no fuente de captura: cosecha unica de
~2011, fuera de la ventana 2016-2026 del proyecto. Por eso el crudo vive en
`data/raw/bibliografia/` junto al CBR de Cambridge y NO en la carpeta de cada
unidad, y por eso el derivado no lo carga nadie a la base.

SALIDAS
  data/raw/bibliografia/ilo-travail_A_<fecha>/<ISO3>.html   crudo tal cual
  data/raw/bibliografia/ilo-travail_A_<fecha>/MANIFEST.csv  procedencia + sha256
  data/derived/travail_oit.csv                              formato largo
  data/derived/travail_oit_cobertura.csv                    47 filas, siempre

COBERTURA. Las 47 unidades aparecen SIEMPRE en el archivo de cobertura, tambien
las que el archivo no tiene. Una unidad sin ficha es un resultado declarado, no
una fila ausente.

USO
  python3 scripts/recuperar_travail.py            # incremental
  python3 scripts/recuperar_travail.py --refresh  # vuelve a bajar todo
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import html
import json
import re
import sys
import time
import zlib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UNIDADES = RAIZ / "data" / "derived" / "export" / "unidades.csv"
COSECHA = "20260811"
DIR_CRUDO = RAIZ / "data" / "raw" / "bibliografia" / f"ilo-travail_A_{COSECHA}"
SALIDA_LARGA = RAIZ / "data" / "derived" / "travail_oit.csv"
SALIDA_COBERTURA = RAIZ / "data" / "derived" / "travail_oit_cobertura.csv"

CDX = "http://web.archive.org/cdx/search/cdx"
UA = "Mozilla/5.0 (compatible; Feriados-Vacaciones/1.0; investigacion academica)"
PAUSA = 1.0  # segundos entre peticiones al archivo

# ISO3 -> codigos ISO2 candidatos que TRAVAIL pudo haber usado. La lista es
# explicita y no depende de ninguna libreria: son 47 unidades, no 200.
ISO2 = {
    "ARG": ["AR"], "AUS": ["AU"], "AUT": ["AT"], "BEL": ["BE"], "BGR": ["BG"],
    "BOL": ["BO"], "BRA": ["BR"], "CAN": ["CA"], "CHE": ["CH"], "CHL": ["CL"],
    "COL": ["CO"], "CRI": ["CR"], "CZE": ["CZ"], "DEU": ["DE"], "DNK": ["DK"],
    "DOM": ["DO"], "ECU": ["EC"], "ESP": ["ES"], "FIN": ["FI"], "FRA": ["FR"],
    "GBR": ["GB", "UK"], "GRC": ["GR"], "GTM": ["GT"], "HND": ["HN"],
    "HUN": ["HU"], "IDN": ["ID"], "IRL": ["IE"], "ISR": ["IL"], "ITA": ["IT"],
    "JPN": ["JP"], "KOR": ["KR"], "MEX": ["MX"], "NIC": ["NI"], "NLD": ["NL"],
    "NOR": ["NO"], "NZL": ["NZ"], "PER": ["PE"], "POL": ["PL"], "PRT": ["PT"],
    "PRY": ["PY"], "ROU": ["RO"], "SLV": ["SV"], "SVK": ["SK"], "SWE": ["SE"],
    "THA": ["TH"], "TUR": ["TR"], "USA": ["US"],
}


# --------------------------------------------------------------------------
# red
# --------------------------------------------------------------------------

def _pedir(url: str, intentos: int = 3, espera: float = 3.0) -> bytes:
    """GET con reintentos. Devuelve bytes DESCOMPRIMIDOS o lanza la excepcion.

    El archivo sirve algunos snapshots con `Content-Encoding: gzip` sin que se
    lo pidan. La primera version de este script no lo trataba y guardaba el
    binario comprimido: el parseo devolvia cero campos y la unidad quedaba
    marcada como ficha vacia. Indonesia fue el caso que lo destapo.
    """
    ultimo: Exception | None = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
            with urllib.request.urlopen(req, timeout=90) as r:
                crudo = r.read()
                cod = (r.headers.get("Content-Encoding") or "").lower()
            if "gzip" in cod or crudo[:2] == b"\x1f\x8b":
                crudo = gzip.decompress(crudo)
            elif "deflate" in cod:
                crudo = zlib.decompress(crudo, -zlib.MAX_WBITS)
            return crudo
        except Exception as e:  # noqa: BLE001 - se reporta, no se traga
            ultimo = e
            if i < intentos - 1:
                time.sleep(espera * (i + 1))
    raise ultimo  # type: ignore[misc]


def buscar_snapshot(iso2: str) -> dict | None:
    """Busca en el CDX del Internet Archive la mejor ficha de tiempo de trabajo.

    Prefiere la version imprimible (`p_print=Y`), que trae el documento entero
    sin paginar, y dentro de ellas el snapshot mas reciente.
    """
    # El filtro del CDX se deja LAXO a proposito y el recorte fino se hace
    # abajo, en Python. Una alternancia `|` dentro del filtro del CDX no hace
    # lo que uno cree y descartaba en silencio paises que si estaban
    # archivados: Israel y Polonia salieron «sin ficha» por eso.
    params = {
        "url": "ilo.org/dyn/travail/travmain.sectionReport1*",
        "output": "json",
        "fl": "original,timestamp,statuscode",
        "collapse": "digest",
        "limit": "2000",
        "filter": f"original:.*p_countries={iso2}.*",
    }
    url = f"{CDX}?{urllib.parse.urlencode(params)}"
    try:
        crudo = _pedir(url)
    except Exception as e:  # noqa: BLE001
        print(f"    ! CDX fallo para {iso2}: {e}", file=sys.stderr)
        return None
    if not crudo.strip():
        return None
    try:
        filas = json.loads(crudo)
    except json.JSONDecodeError:
        return None
    if len(filas) < 2:
        return None

    cab, *datos = filas
    regs = [dict(zip(cab, f)) for f in datos]
    # recorte fino: el codigo de pais exacto (no `IL` dentro de otra cosa),
    # seccion de tiempo de trabajo (estructura 2) y respuesta valida
    exacto = re.compile(rf"p_countries={iso2}(?:&|$)")
    regs = [
        r for r in regs
        if exacto.search(r["original"])
        and "p_structure=2" in r["original"]
        and r.get("statuscode") == "200"
    ]
    if not regs:
        return None
    regs.sort(key=lambda r: ("p_print=Y" in r["original"], r["timestamp"]),
              reverse=True)
    return regs[0]


def estructuras_archivadas(iso2: str) -> str:
    """Que secciones de TRAVAIL guarda el archivo para este pais.

    Sirve para que una unidad sin ficha diga POR QUE no la tiene. Israel y
    Polonia solo estan archivados en la seccion 1 (salarios minimos) y la 3
    (proteccion de la maternidad): del tiempo de trabajo, la que nos importa,
    el archivo no guardo nada. Eso es un hueco del archivo, no del script.
    """
    params = {
        "url": "ilo.org/dyn/travail/travmain.sectionReport1*",
        "output": "text", "fl": "original", "collapse": "urlkey", "limit": "2000",
        "filter": f"original:.*p_countries={iso2}.*",
    }
    try:
        txt = _pedir(f"{CDX}?{urllib.parse.urlencode(params)}").decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return "consulta al archivo fallo"
    exacto = re.compile(rf"p_countries={iso2}(?:&|$)")
    ests = sorted({m.group(1) for l in txt.splitlines() if exacto.search(l)
                   for m in [re.search(r"p_structure=(\d)", l)] if m})
    if not ests:
        return "el archivo no guarda ninguna ficha de este pais"
    nombre = {"1": "salarios minimos", "2": "tiempo de trabajo",
              "3": "proteccion de la maternidad"}
    return ("archivadas solo las secciones: "
            + ", ".join(f"{e} ({nombre.get(e, '?')})" for e in ests))


def bajar(reg: dict) -> bytes:
    """Baja el snapshot en crudo (`id_`), sin la barra del archivo."""
    return _pedir(f"https://web.archive.org/web/{reg['timestamp']}id_/{reg['original']}")


# --------------------------------------------------------------------------
# parseo
# --------------------------------------------------------------------------

RE_H3 = re.compile(
    r'<h3 class="red[^"]*"[^>]*padding-left:\s*(\d+)px[^>]*>(.*?)</h3>',
    re.I | re.S,
)
RE_CITA = re.compile(r'<div align="right" class="little">\s*<em>(.*?)</em>', re.I | re.S)
RE_GRIS = re.compile(r'<div class="gray[^"]*">(.*?)<!-- close gray div -->', re.I | re.S)


def _texto(fragmento: str) -> str:
    """HTML -> texto plano, conservando los saltos que el documento marca."""
    t = re.sub(r"(?i)<br\s*/?>", "\n", fragmento)
    t = re.sub(r"(?is)<div align=\"right\" class=\"little\">.*?</div>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = t.replace("\xa0", " ").replace("»", "").replace("&raquo;", "")
    t = re.sub(r"[ \t]+", " ", t)
    t = "\n".join(l.strip() for l in t.split("\n"))
    return re.sub(r"\n{2,}", "\n", t).strip()


def parsear(crudo: bytes, iso3: str) -> tuple[list[dict], dict]:
    """Devuelve (filas en formato largo, metadatos de la ficha).

    El documento codifica la jerarquia en el `padding-left` de cada titulo:
    0 = seccion, 15 = subseccion, 30 = campo, 45+ = subcampo. Se conserva tal
    cual en vez de aplanarla, porque «Duration» significa una cosa bajo
    ANNUAL LEAVE y otra bajo WEEKLY REST.
    """
    doc = crudo.decode("utf-8", errors="replace")
    meta: dict = {"titulo": "", "ultima_actualizacion": ""}

    m = re.search(r"([A-Z][^<>\n]{2,60})\s*-\s*Working time\s*-\s*(\d{4})", doc)
    if m:
        meta["titulo"] = f"{m.group(1).strip()} - Working time - {m.group(2)}"
        meta["anio_ficha"] = m.group(2)

    hits = list(RE_H3.finditer(doc))
    filas: list[dict] = []
    seccion = subseccion = ""

    for i, h in enumerate(hits):
        nivel = int(h.group(1))
        titulo = _texto(h.group(2))
        if not titulo:
            continue
        cuerpo = doc[h.end(): hits[i + 1].start() if i + 1 < len(hits) else len(doc)]

        gris = RE_GRIS.search(cuerpo)
        contenido = _texto(gris.group(1)) if gris else ""
        cita_m = RE_CITA.search(cuerpo)
        cita = _texto(cita_m.group(1)) if cita_m else ""

        if nivel == 0:
            seccion, subseccion = titulo, ""
        elif nivel <= 15:
            subseccion = titulo

        if titulo.upper() == "LAST UPDATE" and contenido:
            meta["ultima_actualizacion"] = contenido.split("\n")[0]

        if not contenido and nivel >= 30:
            continue  # titulo de campo sin cuerpo: no aporta

        filas.append({
            "iso3": iso3,
            "seccion": seccion,
            "subseccion": subseccion,
            "campo": titulo,
            "nivel": nivel,
            "contenido": contenido,
            "cita_normativa": cita,
        })
    return filas, meta


# --------------------------------------------------------------------------
# principal
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true",
                    help="vuelve a bajar aunque el crudo ya exista")
    args = ap.parse_args()

    if not UNIDADES.exists():
        print(f"No existe {UNIDADES}. Corre antes scripts/exportar.py.", file=sys.stderr)
        return 2

    with UNIDADES.open(encoding="utf-8") as fh:
        unidades = list(csv.DictReader(fh))
    print(f"Unidades del proyecto: {len(unidades)}")

    DIR_CRUDO.mkdir(parents=True, exist_ok=True)
    SALIDA_LARGA.parent.mkdir(parents=True, exist_ok=True)

    # Procedencia previa. Sin esto, una corrida incremental reescribia el
    # manifiesto dejando en blanco la URL y el timestamp de todo lo que ya
    # estaba en disco: el crudo sobrevivia y su procedencia se perdia, que es
    # peor que no tener el archivo.
    previo: dict[str, dict] = {}
    man_path = DIR_CRUDO / "MANIFEST.csv"
    if man_path.exists():
        with man_path.open(encoding="utf-8") as fh:
            previo = {r["iso3"]: r for r in csv.DictReader(fh)}

    manifiesto: list[dict] = []
    cobertura: list[dict] = []
    largas: list[dict] = []

    for u in unidades:
        iso3, pais = u["pais_iso3"], u["pais"]
        destino = DIR_CRUDO / f"{iso3}.html"
        print(f"  {iso3} {pais}", end=" ", flush=True)

        reg = None
        if destino.exists() and not args.refresh:
            print("(crudo en disco)", end=" ")
            crudo = destino.read_bytes()
            p = previo.get(iso3)
            if p:
                reg = {"original": p["url_original"],
                       "timestamp": p["timestamp_archivo"],
                       "iso2": p["iso2"]}
            else:
                print("[SIN PROCEDENCIA REGISTRADA]", end=" ")
        else:
            for cand in ISO2.get(iso3, []):
                reg = buscar_snapshot(cand)
                time.sleep(PAUSA)
                if reg:
                    reg["iso2"] = cand
                    break
            if not reg:
                motivo = estructuras_archivadas(ISO2.get(iso3, [""])[0])
                print(f"SIN FICHA EN EL ARCHIVO — {motivo}")
                cobertura.append({
                    "iso3": iso3, "pais": pais, "estado": "sin_ficha",
                    "iso2": "|".join(ISO2.get(iso3, [])), "timestamp_archivo": "",
                    "anio_ficha": "", "ultima_actualizacion": "", "campos": 0,
                    "tiene_vacaciones": 0, "tiene_feriados": 0,
                    "tiene_colocacion": 0, "motivo": motivo,
                })
                continue
            try:
                crudo = bajar(reg)
            except Exception as e:  # noqa: BLE001
                print(f"DESCARGA FALLO: {e}")
                cobertura.append({
                    "iso3": iso3, "pais": pais, "estado": "descarga_fallo",
                    "iso2": reg.get("iso2", ""), "timestamp_archivo": reg["timestamp"],
                    "anio_ficha": "", "ultima_actualizacion": "", "campos": 0,
                    "tiene_vacaciones": 0, "tiene_feriados": 0, "tiene_colocacion": 0,
                })
                continue
            destino.write_bytes(crudo)
            time.sleep(PAUSA)

        filas, meta = parsear(crudo, iso3)
        largas.extend(filas)

        secs = {f["seccion"].upper() for f in filas}
        campos = {f["campo"].upper() for f in filas}
        estado = "ok" if filas else "ficha_vacia"
        print(f"-> {len(filas)} campos [{estado}]")

        manifiesto.append({
            "iso3": iso3, "pais": pais, "iso2": (reg or {}).get("iso2", ""),
            "url_original": (reg or {}).get("original", ""),
            "timestamp_archivo": (reg or {}).get("timestamp", ""),
            "url_archivo": (
                f"https://web.archive.org/web/{reg['timestamp']}/{reg['original']}"
                if reg else ""),
            "archivo": destino.name,
            "bytes": len(crudo),
            "sha256": hashlib.sha256(crudo).hexdigest(),
        })
        cobertura.append({
            "iso3": iso3, "pais": pais, "estado": estado,
            "iso2": (reg or {}).get("iso2", ""),
            "timestamp_archivo": (reg or {}).get("timestamp", ""),
            "anio_ficha": meta.get("anio_ficha", ""),
            "ultima_actualizacion": meta.get("ultima_actualizacion", ""),
            "campos": len(filas),
            "tiene_vacaciones": int(any("ANNUAL LEAVE" in s for s in secs)),
            "tiene_feriados": int(any("PUBLIC HOLIDAY" in f for f in campos)
                                  or any("PUBLIC HOLIDAY" in s for s in secs)),
            "tiene_colocacion": int(any("SCHEDULE AND SPLITTING" in f for f in campos)),
            "motivo": "",
        })

    # ---- escritura -------------------------------------------------------
    with SALIDA_LARGA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "iso3", "seccion", "subseccion", "campo", "nivel",
            "contenido", "cita_normativa"])
        w.writeheader()
        w.writerows(largas)

    with SALIDA_COBERTURA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "iso3", "pais", "estado", "iso2", "timestamp_archivo", "anio_ficha",
            "ultima_actualizacion", "campos", "tiene_vacaciones", "tiene_feriados",
            "tiene_colocacion", "motivo"])
        w.writeheader()
        w.writerows(cobertura)

    if manifiesto:
        with (DIR_CRUDO / "MANIFEST.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=[
                "iso3", "pais", "iso2", "url_original", "timestamp_archivo",
                "url_archivo", "archivo", "bytes", "sha256"])
            w.writeheader()
            w.writerows(manifiesto)

    # ---- resumen, que se imprime siempre ---------------------------------
    ok = [c for c in cobertura if c["estado"] == "ok"]
    sin = [c for c in cobertura if c["estado"] != "ok"]
    print()
    print(f"Fichas recuperadas : {len(ok)}/{len(unidades)}")
    print(f"Con vacaciones     : {sum(c['tiene_vacaciones'] for c in ok)}")
    print(f"Con feriados       : {sum(c['tiene_feriados'] for c in ok)}")
    print(f"Con COLOCACION     : {sum(c['tiene_colocacion'] for c in ok)}")
    print(f"Campos totales     : {len(largas)}")
    if sin:
        print(f"\nSIN FICHA ({len(sin)}), declaradas en el archivo de cobertura:")
        for c in sin:
            print(f"  - {c['iso3']} {c['pais']}: {c['estado']}")
    anios = sorted({c["anio_ficha"] for c in ok if c["anio_ficha"]})
    if anios:
        print(f"\nCosecha declarada por las fichas: {', '.join(anios)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
