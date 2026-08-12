#!/bin/sh
# Rehace el dataset desde `capturas/` y lo compara con `datos/`.
# Ver la seccion «Reproducibilidad» del LEEME.
cd "$(dirname "$0")" && exec python3 codigo/reproducir.py "$@"
