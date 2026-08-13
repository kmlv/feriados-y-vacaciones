"""Construye el repositorio PUBLICO desde el paquete, con historial nuevo.

QUE HACE Y QUE NO. Deja un repositorio git completo en una carpeta aparte, con
UN SOLO commit y una etiqueta de version, conteniendo exactamente el arbol de
`reportes/` y nada mas. **No crea nada en ningun servidor y no empuja.** Empujar
es una decision del principal y una accion que no se deshace; este guion la deja
lista y para.

POR QUE HISTORIAL NUEVO Y NO UN SUBARBOL DEL PRIVADO. El repositorio de trabajo
lleva dentro la coordinacion entre sesiones, las notas internas, los borradores y
las transcripciones. Un `git subtree` o un filtrado arrastra objetos y mensajes
de commit de todo eso, y un objeto que no se referencia sigue siendo recuperable.
La unica forma limpia de publicar un subconjunto es un arbol nuevo sin pasado.

LA VERSION SE SELLA ANTES DE COMMITEAR, y ese orden es el arreglo de un problema
real. El sello tenia que llevar el commit publico, y el commit publico es el que
CONTIENE el paquete: un artefacto no puede declarar el identificador que lo
contiene. Con una ETIQUETA el circulo se rompe, porque la etiqueta se decide
antes y se aplica despues. Por eso aqui se regenera el paquete con
`VERSION_PUBLICA` puesta, se commitea, y se etiqueta con ese mismo nombre — de
modo que lo que el paquete dice de si mismo y lo que el repositorio dice de el
son la misma cadena.

Uso:  python3 scripts/publicar.py v1.0 [--salida <carpeta>]
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
PAQUETE = REPO / "reportes"


def corre(cmd: list[str], cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("fallo `%s`:\n%s" % (" ".join(cmd), (r.stdout + r.stderr).strip()))
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="etiqueta de publicacion, por ejemplo v1.0")
    ap.add_argument("--salida", default=str(REPO.parent / "Feriados-Vacaciones-publico"))
    a = ap.parse_args()
    if not a.version.startswith("v"):
        sys.exit("la etiqueta empieza por «v»: v1.0, v1.1…")
    salida = Path(a.salida).resolve()

    print("REPOSITORIO PUBLICO\n")
    print("  etiqueta: %s" % a.version)
    print("  salida:   %s\n" % salida)

    # 1 · REGENERAR CON EL SELLO PUESTO. No se copia el paquete que hay en disco:
    # ese dice «sin-publicar». Se vuelve a compilar entero con la etiqueta, para
    # que el sello del documento y la etiqueta del repositorio sean la misma
    # cadena y no dos que alguien tenga que creerse iguales.
    print("  Regenerando el paquete con la version sellada…")
    env = dict(os.environ, VERSION_PUBLICA=a.version)
    # LAS FIGURAS TAMBIEN SON DERIVADAS Y ENTRAN EN LA CADENA. La primera version
    # de este guion regeneraba la exportacion y los documentos, y el generador se
    # nego —con razon— porque las figuras habian quedado mas viejas que la base:
    # sacan sus cifras del mismo registro que el texto, asi que son un resultado
    # y no un adorno. El orden es exportar, dibujar, componer; saltarse el paso
    # de en medio publica un documento cuyas imagenes dicen otra cosa.
    cadena = [(REPO / "scripts/exportar.py", []),
              (REPO / "plantillas/generar_figura_apertura.py", []),
              (REPO / "plantillas/generar_figura_dispersion.py", []),
              (REPO / "scripts/generar_reportes.py", ["--pdf"])]
    for guion, extra in cadena:
        r = subprocess.run([sys.executable, str(guion)] + extra,
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            sys.exit("fallo al regenerar (%s):\n%s"
                     % (guion.name, (r.stdout + r.stderr).strip()[-2000:]))

    # 2 · LAS COMPUERTAS, DESPUES DE SELLAR Y NO ANTES. Regenerar cambia el
    # paquete; comprobarlo antes seria comprobar otro. Es la misma leccion que la
    # compilacion atomica: lo que se verifica tiene que ser lo que sale.
    print("  Pasando las compuertas sobre el paquete sellado…")
    r = subprocess.run([sys.executable, str(REPO / "scripts/probar_reportes.py")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("las compuertas NO pasan sobre el paquete sellado:\n%s"
                 % r.stdout.strip()[-2000:])
    print("    %s" % r.stdout.strip().splitlines()[-1])

    # 3 bis · EL MARCADOR NO PUEDE VIAJAR PUBLICADO. `sin-publicar` es la verdad
    # de una copia de trabajo y es **falso dentro de la cosa publicada**: dice
    # «esto no se ha publicado» en la cabecera del LEEME, que es lo primero que
    # se lee. Y es de los fallos caros porque el paquete se ve completo.
    #
    # Vive en tres sitios —el sello, la fila del manifiesto y el colofon de los
    # dos idiomas— asi que se comprueba en todo el arbol y no en uno.
    from reportes_nucleo import SIN_PUBLICAR
    con_marcador = [str(f.relative_to(PAQUETE))
                    for f in PAQUETE.rglob("*")
                    if f.is_file() and f.suffix in (".md", ".json", ".csv")
                    and SIN_PUBLICAR in f.read_text(encoding="utf-8", errors="ignore")]
    if con_marcador:
        sys.exit("el paquete sellado sigue llevando el marcador «%s» en:\n  %s\n"
                 "  Regenerar con VERSION_PUBLICA puesta deberia haberlo sustituido; "
                 "que quede es senal de que un sitio no lee el sello."
                 % (SIN_PUBLICAR, "\n  ".join(con_marcador)))

    # 4 · Y LA REPRODUCCION, que es la afirmacion mas fuerte del LEEME.
    print("  Comprobando que el paquete se reproduzca a si mismo…")
    r = subprocess.run([sys.executable, str(REPO / "scripts/reproducir.py")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("el paquete no se reproduce:\n%s" % r.stdout.strip()[-2000:])

    # 5 · EL ARBOL NUEVO. Se borra y se rehace: este directorio es derivado
    # entero, igual que `reportes/`, y conservar restos de una publicacion
    # anterior es como se acaba publicando un archivo que ya nadie referencia.
    if salida.exists():
        if not (salida / ".git").exists():
            sys.exit("%s existe y no es un repositorio git; no lo toco." % salida)
        shutil.rmtree(salida)
    shutil.copytree(PAQUETE, salida)

    # 6 · UNA COMPROBACION MAS, sobre el arbol copiado y no sobre el original.
    # Lo que se publica es esto.
    fugas = []
    for f in salida.rglob("*"):
        if f.is_file() and (".git" not in f.parts):
            rel = str(f.relative_to(salida))
            if rel.startswith("regenerado/") or rel.endswith(".db"):
                fugas.append(rel)
    if fugas:
        sys.exit("el arbol a publicar lleva derivados de una ejecucion previa:\n  %s"
                 % "\n  ".join(fugas[:10]))

    corre(["git", "init", "-q", "-b", "main"], salida)
    corre(["git", "add", "-A"], salida)
    corre(["git", "-c", "user.name=Kristian Lopez Vargas",
           "-c", "user.email=klopezva@ucsc.edu",
           "commit", "-q", "-m",
           "Feriados y vacaciones anuales — dataset y reporte, %s\n\n"
           "Conjunto de datos citable de feriados publicos y vacaciones anuales\n"
           "legales en 47 jurisdicciones de referencia, en dos cortes.\n\n"
           "El paquete se regenera y se comprueba a si mismo: `./reproducir.sh`\n"
           "rehace el dataset desde las capturas crudas y lo compara hash por\n"
           "hash con los archivos publicados." % a.version], salida)
    corre(["git", "tag", "-a", a.version, "-m",
           "Publicacion %s" % a.version], salida)

    n = len([f for f in salida.rglob("*") if f.is_file() and ".git" not in f.parts])
    print("\n  %d archivos, un commit, etiqueta %s" % (n, a.version))
    print("  commit: %s" % corre(["git", "rev-parse", "HEAD"], salida)[:12])
    print("\nEL REPOSITORIO PUBLICO ESTA LISTO Y NO SE HA EMPUJADO.")
    print("Para publicarlo, desde %s:" % salida)
    print("  gh repo create <nombre> --public --source=. --push")
    print("  git push origin %s" % a.version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
