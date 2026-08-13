"""Ataque end-to-end al vinculo lote -> protocolo congelado.

La revisión cruzada reprodujo sobre el esquema de v2.8 un ciclo completo -sembrar una version
inventada, atar un lote, congelarlo, cruzarlo- que cerraba sin una sola
violacion. Este guion fija ese ataque para que no vuelva.

Tiene DOS mitades, y ninguna basta sola:

  1. Estados que deben rechazarse. Formato de version, ruta ausente o apuntando
     al documento vigente.

  2. La limitacion declarada, ejecutada. Un hash bien formado que no corresponde
     a ningun archivo SIGUE entrando, porque SQLite no lee el disco ni calcula
     SHA-256. El guion lo demuestra y lo reporta como limitacion esperada, no
     como aprobacion. Un hueco que se ejecuta y se declara deja de ser
     silencioso; callarlo aqui lo volveria silencioso otra vez.

Salida cero si todo se comporta como se declara.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DDL = REPO / "schema/draft/001_schema.sql"

HASH_OK = "a" * 64
FECHA_OK = "2026-08-09T04:15:00Z"

# (etiqueta, version, hash, archivo) que el catalogo DEBE rechazar.
RECHAZOS = [
    ("version con 'v' interpuesta",      "v2v.8",  HASH_OK, "docs/archivo/x.md"),
    ("version con 'v' final",            "v2.8v",  HASH_OK, "docs/archivo/x.md"),
    ("version de tres componentes",      "v2.8.1", HASH_OK, "docs/archivo/x.md"),
    ("version sin punto",                "v28",    HASH_OK, "docs/archivo/x.md"),
    ("ruta vacia",                       "v9.1",   HASH_OK, ""),
    ("ruta al documento vigente",        "v9.2",   HASH_OK, "docs/02-protocolo.md"),
    ("ruta fuera de docs/archivo",       "v9.3",   HASH_OK, "otro/lugar/x.md"),
    ("ruta sin nombre de archivo",       "v9.4",   HASH_OK, "docs/archivo/.md"),
    # Las tres siguientes son de la revisión cruzada, rev131: el prefijo casaba y la ruta
    # resolvia al documento vigente. Un prefijo no acota una ruta que puede
    # volver hacia atras.
    ("travesia al vigente",              "v9.8",   HASH_OK, "docs/archivo/../02-protocolo.md"),
    ("travesia desde subdirectorio",     "v9.9",   HASH_OK, "docs/archivo/sub/../../02-protocolo.md"),
    ("barra doble sin nombre",           "v9.10",  HASH_OK, "docs/archivo//.md"),
    ("subdirectorio dentro del archivo", "v9.11",  HASH_OK, "docs/archivo/sub/x.md"),
    ("hash corto",                       "v9.5",   "a" * 63, "docs/archivo/x.md"),
    ("hash no hexadecimal",              "v9.6",   "z" * 64, "docs/archivo/x.md"),
    ("marca con hora 24",                "v9.7",   HASH_OK, "docs/archivo/x.md"),
]


def base() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(DDL.read_text())
    return con


def sembrar(con: sqlite3.Connection, version: str, hsh: str, archivo: str,
            fecha: str = FECHA_OK) -> None:
    con.execute(
        "INSERT INTO protocolo_congelado (version, hash, archivo, congelado_en) "
        "VALUES (?,?,?,?)", (version, hsh, archivo, fecha))


def ciclo_completo(con: sqlite3.Connection, version: str, hsh: str) -> None:
    """Ata un lote al par, lo congela y lo cruza. Este era el ataque de la revisión cruzada."""
    con.execute(
        "INSERT INTO lote_captura "
        "(lote_id, etiqueta, estado, version_protocolo, hash_protocolo) "
        "VALUES (901, 'ataque-catalogo', 'ciego', ?, ?)", (version, hsh))
    con.execute("UPDATE lote_captura SET estado='congelado', congelado_en=? "
                "WHERE lote_id=901", (FECHA_OK,))
    con.execute("UPDATE lote_captura SET estado='cruzado' WHERE lote_id=901")


def main() -> int:
    fallos: list[str] = []

    print("== Estados que deben rechazarse ==")
    for etiqueta, version, hsh, archivo in RECHAZOS:
        fecha = "2026-08-09T24:00:00Z" if "hora 24" in etiqueta else FECHA_OK
        con = base()
        try:
            sembrar(con, version, hsh, archivo, fecha)
        except sqlite3.IntegrityError:
            print("  RECHAZADO  %s" % etiqueta)
        else:
            print("  ENTRA      %s   <-- FALLA" % etiqueta)
            fallos.append(etiqueta)
        finally:
            con.close()

    print()
    print("== Estructura legitima: debe entrar limpia ==")
    con = base()
    try:
        sembrar(con, "v2.9", HASH_OK, "docs/archivo/02-protocolo-v2.9.md")
        ciclo_completo(con, "v2.9", HASH_OK)
        estado = con.execute(
            "SELECT estado FROM lote_captura WHERE lote_id=901").fetchone()[0]
        if estado == "cruzado":
            print("  LIMPIA     entrada valida y lote cerrado")
        else:
            print("  estado inesperado %r   <-- FALLA" % estado)
            fallos.append("lote valido no llego a cruzado")
    except sqlite3.IntegrityError as e:
        print("  RECHAZADA  entrada valida   <-- FALLA (%s)" % e)
        fallos.append("falso positivo sobre entrada valida")
    finally:
        con.close()

    print()
    print("== Limitacion declarada (§25.1): debe seguir entrando ==")
    con = base()
    try:
        # Hash bien formado que no corresponde a ningun archivo del repo, y ruta
        # bajo docs/archivo/ que tampoco existe. SQLite no puede saberlo.
        sembrar(con, "v7.7", "b" * 64, "docs/archivo/02-protocolo-v7.7.md")
        ciclo_completo(con, "v7.7", "b" * 64)
        estado = con.execute(
            "SELECT estado FROM lote_captura WHERE lote_id=901").fetchone()[0]
        if estado == "cruzado":
            print("  ENTRA      lote cerrado contra un protocolo inexistente")
            print("             Es la limitacion declarada, no un defecto nuevo:")
            print("             SQLite no lee el disco ni calcula SHA-256.")
            print("             La garantia plena exige correr")
            print("             scripts/verificar_congelamiento.py")
        else:
            print("  estado inesperado %r" % estado)
    except sqlite3.IntegrityError as e:
        # Si algun dia esto se cierra dentro de la base, la limitacion declarada
        # en §25.1 quedo obsoleta y el protocolo miente por defecto.
        print("  RECHAZADO   <-- el esquema ya cierra esto")
        print("              §25.1 declara una limitacion que ya no existe:")
        print("              corrige el protocolo. (%s)" % e)
        fallos.append("§25.1 declara una limitacion inexistente")
    finally:
        con.close()

    print()
    if fallos:
        print("FALLAN %d comprobaciones:" % len(fallos))
        for f in fallos:
            print("  - %s" % f)
        return 1
    print("Catalogo: todo se comporta como se declara.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
