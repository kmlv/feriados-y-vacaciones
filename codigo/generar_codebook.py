"""Genera el codebook DESDE el esquema, no a mano.

Un codebook escrito a mano se desincroniza del esquema exactamente igual que se
desincronizó la cabecera del DDL, que llegó a declarar v2.3 cuando el protocolo
iba en v2.5. La estructura —tablas, columnas, tipos, restricciones, dominios— se
extrae por introspección de SQLite. Lo único escrito a mano son las glosas, que
viven en `docs/codebook_glosas.json` y se cruzan por nombre.

Si una columna existe en el esquema y no tiene glosa, el codebook lo dice en vez
de callarlo: un hueco visible es preferible a una descripción inventada.

Salida: docs/08-codebook.md
"""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DDL = REPO / "schema/draft/001_schema.sql"
VALID = REPO / "schema/draft/900_validaciones.sql"
GLOSAS = REPO / "docs/codebook_glosas.json"
OUT = REPO / "docs/08-codebook.md"

# Agrupación temática, para que el codebook se lea como el protocolo y no como
# un volcado alfabético.
GRUPOS = [
    ("Capa común", ["hechos", "jurisdicciones", "fuentes", "evidencia",
                    "eventos_reforma", "reforma_versiones", "mediciones",
                    "lote_captura", "protocolo_congelado"]),
    ("Módulo feriados", ["feriado_version", "regla_fecha_version", "ocurrencias",
                         "determinaciones_fecha", "regimen_jornada",
                         "eventos_compensatorios"]),
    ("Módulo vacaciones", ["vacaciones_version", "escala_antiguedad",
                           "regla_colocacion", "particion_alternativa",
                           "particion_clase", "instrumento_supranacional"]),
    ("Antecedente externo", ["dataset_externo", "medicion_externa",
                             "reforma_externa", "crosswalk", "crosswalk_causa"]),
    ("Vocabularios y vistas", ["hecho_tipo", "asignacion_colocacion"]),
]


def cargar_esquema() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.executescript(DDL.read_text())
    return con


def dominio_de(ddl_tabla: str, col: str) -> str | None:
    """Extrae el dominio cerrado de un CHECK ... IN (...) para esa columna."""
    m = re.search(
        re.escape(col) + r"[^,]*?CHECK\s*\(\s*(?:" + re.escape(col)
        + r"\s+IS\s+NULL\s+OR\s+)?" + re.escape(col) + r"\s+IN\s*\(([^)]*)\)",
        ddl_tabla, re.S | re.I)
    if not m:
        return None
    vals = re.findall(r"'([^']+)'", m.group(1))
    return " · ".join("`%s`" % v for v in vals) if vals else None


def main() -> None:
    con = cargar_esquema()
    glosas = json.loads(GLOSAS.read_text()) if GLOSAS.exists() else {}
    # Glosas de campos que se repiten entre tablas y significan lo mismo en
    # todas. La glosa específica de la tabla, si existe, siempre gana.
    comunes = glosas.pop("_comunes", {})

    objetos = {r[0]: (r[1], r[2]) for r in con.execute(
        "SELECT name, type, sql FROM sqlite_schema "
        "WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'")}
    triggers = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_schema WHERE type='trigger'")]
    n_valid = len(re.findall(r"^SELECT 'V", VALID.read_text(), re.M))

    out = []
    out.append("# Codebook\n")
    out.append("**Generado desde el esquema, no escrito a mano.** "
               "Regenerar con `python3 scripts/generar_codebook.py`.\n")
    out.append("La estructura sale por introspección del DDL; las glosas viven "
               "en `docs/codebook_glosas.json`. Si una columna no tiene glosa, "
               "este documento lo dice — un hueco visible es preferible a una "
               "descripción inventada.\n")
    out.append("Las restricciones que **no** son expresables como CHECK viven "
               "en `schema/draft/900_validaciones.sql` y se listan al final.\n")
    out.append("| | |\n|---|---|")
    out.append("| Tablas y vistas | %d |" % len(objetos))
    out.append("| Triggers | %d |" % len(triggers))
    out.append("| Validaciones externas | %d |\n" % n_valid)

    vistos = set()
    sin_glosa = []
    for titulo, tablas in GRUPOS:
        presentes = [t for t in tablas if t in objetos]
        if not presentes:
            continue
        out.append("\n---\n\n## %s\n" % titulo)
        for t in presentes:
            vistos.add(t)
            tipo, sql = objetos[t]
            g = glosas.get(t, {})
            out.append("### `%s`%s\n" % (t, "  *(vista derivada)*" if tipo == "view" else ""))
            if g.get("_") :
                out.append("%s\n" % g["_"])
            else:
                out.append("*Sin glosa.*\n")
                sin_glosa.append(t)
            cols = list(con.execute("PRAGMA table_info(%s)" % t))
            if not cols:
                continue
            out.append("| Campo | Tipo | Nulo | Dominio | Glosa |")
            out.append("|---|---|:-:|---|---|")
            for _, name, ctype, notnull, _dflt, pk in cols:
                dom = dominio_de(sql or "", name) or ""
                gl = g.get(name) or comunes.get(name, "")
                if not gl:
                    sin_glosa.append("%s.%s" % (t, name))
                    gl = "—"
                marca = "no" if (notnull or pk) else "sí"
                out.append("| `%s` | %s | %s | %s | %s |"
                           % (name, ctype or "—", marca, dom, gl))
            out.append("")

    huerfanas = sorted(set(objetos) - vistos)
    if huerfanas:
        out.append("\n---\n\n## Sin agrupar\n")
        out.append("Existen en el esquema y no están en ningún grupo temático "
                   "de este generador. Es un aviso, no un error:\n")
        for t in huerfanas:
            out.append("- `%s`" % t)
        out.append("")

    out.append("\n---\n\n## Validaciones externas\n")
    out.append("Cada consulta debe devolver **cero filas**. Correr con "
               "`sqlite3 base.db < schema/draft/900_validaciones.sql`.\n")
    for m in re.finditer(r"^--\s+(V\d+\w*)\s+·\s+(.+?)$", VALID.read_text(), re.M):
        out.append("- **%s** — %s" % (m.group(1), m.group(2).rstrip(".")))

    faltan = len([x for x in sin_glosa if "." in x])
    out.append("\n\n---\n\n## Cobertura de glosas\n")
    total = sum(len(list(con.execute("PRAGMA table_info(%s)" % t))) for t in objetos)
    out.append("**%d de %d campos glosados** (%.0f%%). Los no glosados aparecen "
               "con guion en su fila.\n" % (total - faltan, total,
                                            100 * (total - faltan) / total if total else 0))

    OUT.write_text("\n".join(out) + "\n")
    print("codebook -> %s" % OUT.relative_to(REPO))
    print("  %d tablas y vistas · %d triggers · %d validaciones"
          % (len(objetos), len(triggers), n_valid))
    print("  glosas: %d de %d campos (%.0f%%)"
          % (total - faltan, total, 100 * (total - faltan) / total if total else 0))
    if huerfanas:
        print("  sin agrupar: %s" % ", ".join(huerfanas))


if __name__ == "__main__":
    main()
