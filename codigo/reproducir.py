"""Rehace el dataset desde las capturas crudas y lo compara con el publicado.

QUE AFIRMA EL PAQUETE Y POR QUE ESTE GUION EXISTE. El `LEEME` dice que todo lo
que no sea captura cruda **se regenera desde las capturas**. Durante un tiempo
eso fue falso de una forma incomoda: el paquete embarcaba las capturas, el
esquema y los 25 guiones, y ninguno arrancaba, porque resolvian sus rutas contra
el arbol del repositorio y el paquete tiene otro. La afirmacion estaba impresa y
el primer comando devolvia un error de archivo no encontrado.

Y NO ES SOLO «QUE CORRA». Un guion que termina sin error demuestra poco: podria
haber escrito cualquier cosa. Lo que se comprueba aqui es mas fuerte y es lo que
un tercero querria: se rehace el dataset entero desde el dato crudo y se compara
**hash por hash** contra los CSV que viajan en el paquete. La respuesta no es
«ha corrido», es «coincide» o «estas filas no coinciden».

Por eso la regeneracion sale a una carpeta aparte. Si reexportara encima de los
datos publicados, borraria la unica copia contra la que comparar y el lector se
quedaria con unos archivos y ninguna forma de saber si son los suyos.

Uso:  python3 codigo/reproducir.py        (dentro del paquete)
      python3 scripts/reproducir.py       (en el repositorio; compara consigo mismo)
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rutas import DATOS_PUBLICADOS, EN_PAQUETE, EXPORT, GUIONES, REPO


def sha256_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def paso(titulo: str, guion: str) -> None:
    print("  %s…" % titulo, flush=True)
    r = subprocess.run([sys.executable, str(GUIONES / guion)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        # SE IMPRIME LA SALIDA DEL GUION QUE FALLO, no un resumen nuestro. Quien
        # corre esto es un tercero sin acceso a nuestro repositorio: un «fallo el
        # paso 1» lo deja sin nada que investigar.
        print("\nFALLO EN «%s» (%s):\n%s\n%s"
              % (titulo, guion, r.stdout.strip()[-2000:], r.stderr.strip()[-2000:]))
        sys.exit(1)


def main() -> int:
    print("REPRODUCCION DEL DATASET DESDE LAS CAPTURAS CRUDAS\n")
    print("  arbol: %s" % ("paquete publicado" if EN_PAQUETE else "repositorio"))
    print("  raiz:  %s\n" % REPO)

    paso("Reconstruyendo la base desde las capturas", "cargar_piloto.py")
    paso("Exportando los archivos tabulares", "exportar.py")

    # EL MANIFIESTO PUBLICADO ES EL PATRON. Se compara contra el, y no contra un
    # listado de archivos: si el paquete trajera un CSV que el manifiesto no
    # declara, compararlo archivo por archivo lo daria por bueno.
    manifiesto = DATOS_PUBLICADOS / "MANIFEST.csv"
    if not manifiesto.exists():
        sys.exit("no esta el manifiesto publicado: %s" % manifiesto)

    esperado = {}
    for fila in csv.DictReader(manifiesto.open(encoding="utf-8")):
        nombre = fila["archivo"]
        # `__version_publicada__` no es un archivo: es el sello, y depende de donde se
        # publique, no del dato. Comparar el dato es lo que esta prueba hace.
        if nombre.startswith("__"):
            continue
        esperado[nombre] = fila["sha256"]

    print("\n  Comparando %d archivos contra el manifiesto publicado\n"
          % len(esperado))

    faltan, diferentes, iguales = [], [], 0
    for nombre, sha in sorted(esperado.items()):
        nuevo = EXPORT / nombre
        if not nuevo.exists():
            faltan.append(nombre)
        elif sha256_de(nuevo) != sha:
            diferentes.append(nombre)
        else:
            iguales += 1

    for n in faltan:
        print("  NO SE REGENERO   %s" % n)
    for n in diferentes:
        print("  NO COINCIDE      %s" % n)
    if iguales:
        print("  %d archivo(s) reproducen exactamente su hash publicado" % iguales)

    if faltan or diferentes:
        print("\nLA REPRODUCCION NO COINCIDE con el dataset publicado.")
        print("Si has modificado alguna captura, es lo esperado: has medido otra")
        print("cosa. Si no la has tocado, es un defecto nuestro y queremos saberlo.")
        return 1

    print("\nEL DATASET PUBLICADO SE REPRODUCE ENTERO desde las capturas crudas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
