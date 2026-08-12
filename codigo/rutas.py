"""Donde vive cada cosa, VISTO DESDE EL ARBOL QUE SE ESTE LEYENDO.

POR QUE EXISTE ESTE MODULO. El paquete publicado embarca las capturas crudas, el
esquema, las validaciones y los 25 guiones, y su `LEEME` afirma que todo lo
demas **se regenera desde las capturas**. No se podia: los guiones resolvian sus
rutas contra el arbol del REPOSITORIO —`schema/draft/001_schema.sql`,
`data/raw/`— y el paquete tiene otro —`metodo/esquema.sql`, `capturas/`—. Los 25
guiones viajaban y ninguno arrancaba. Un tercero que lo intentara se llevaba un
`FileNotFoundError` en el primer comando.

Ninguna compuerta lo veia, y no por descuido: **todas comprobaban que el paquete
CONTUVIERA lo que promete, ninguna que lo que promete FUNCIONE.** La
comprobacion llegaba al borde del artefacto y se paraba ahi. Es el sintoma de la
familia entera — no falla nada; falla solo para el lector, y solo si lo intenta.

LA RAIZ NO HACIA FALTA ARREGLARLA. Los 23 guiones la calculan igual, subiendo un
nivel desde su propia carpeta, y eso ya acierta en los dos arboles: en el
repositorio `scripts/` sube a la raiz del repositorio, y en el paquete `codigo/`
sube a la raiz del paquete. Lo que difiere son las SUB-RUTAS, y estan aqui.

Y NO SE ADIVINA LA DISPOSICION POR DESCARTE. Se exige una marca de cada arbol y
se aborta si hay dos o si no hay ninguna. Un modulo de rutas que ante la duda
elige una es la version de rutas de «permitir no es exigir»: acertaria casi
siempre y el dia que fallara devolveria una ruta plausible en vez de un error.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

_MARCA_REPOSITORIO = REPO / "schema/draft/001_schema.sql"
_MARCA_PAQUETE = REPO / "metodo/esquema.sql"

if _MARCA_REPOSITORIO.exists() and _MARCA_PAQUETE.exists():
    sys.exit("no se puede saber que arbol es este: estan la marca del "
             "repositorio (%s) y la del paquete (%s) a la vez."
             % (_MARCA_REPOSITORIO.relative_to(REPO),
                _MARCA_PAQUETE.relative_to(REPO)))
if not _MARCA_REPOSITORIO.exists() and not _MARCA_PAQUETE.exists():
    sys.exit("este arbol no es ni el repositorio ni el paquete: falta el "
             "esquema, que se esperaba en %s o en %s.\n"
             "  Raiz deducida: %s"
             % (_MARCA_REPOSITORIO.relative_to(REPO),
                _MARCA_PAQUETE.relative_to(REPO), REPO))

EN_PAQUETE = _MARCA_PAQUETE.exists()


def _r(en_repositorio: str, en_paquete: str) -> Path:
    return REPO / (en_paquete if EN_PAQUETE else en_repositorio)


# Las cinco que cambian de sitio. Cada una con los dos nombres a la vista, que es
# la unica forma de que un cambio de nombre en el paquete se vea aqui y no se
# descubra al ejecutarlo.
ESQUEMA = _r("schema/draft/001_schema.sql", "metodo/esquema.sql")
VALIDACIONES = _r("schema/draft/900_validaciones.sql", "metodo/validaciones.sql")
CAPTURAS = _r("data/raw", "capturas")
CONGELAMIENTO = _r("docs/PROTOCOL_FREEZE.md", "metodo/PROTOCOL_FREEZE.md")

# LA REGENERACION NO ESCRIBE ENCIMA DE LO QUE VIAJA, y esto no es prudencia: es
# lo que convierte «se puede correr» en «se puede COMPROBAR». Si el paquete
# reexportara sobre `datos/`, el lector obtendria unos CSV y ninguna forma de
# saber si son los mismos que le entregamos — habria borrado la unica copia
# contra la que comparar. Saliendo aparte, la regeneracion produce una respuesta
# y no solo unos archivos: coinciden o no coinciden, hash por hash.
EXPORT = _r("data/derived/export", "regenerado")

# LA CARPETA DE GUIONES, que es como se llaman entre si por subproceso.
GUIONES = Path(__file__).resolve().parent

# LA BASE ES DERIVADA Y SE ESCRIBE. En el repositorio vive donde siempre; en el
# paquete va con lo regenerado, por el mismo motivo.
BASE = _r("data/derived/piloto.db", "regenerado/piloto.db")

# LOS DATOS QUE VIAJAN, que en el repositorio son la propia exportacion y en el
# paquete son la copia sellada contra la que se compara.
DATOS_PUBLICADOS = _r("data/derived/export", "datos")
