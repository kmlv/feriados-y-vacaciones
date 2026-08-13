"""Comprueba que las cifras escritas en la documentacion sigan siendo ciertas.

POR QUE EXISTE. En un solo dia el README dijo «Fase 0, importacion de material
previo» sobre un dataset terminado, `00-ESTADO.md` declaro v2.9 cuando el
protocolo iba en v2.18, y la nota de hallazgos afirmo 568 feriados cuando eran
569. Ninguno era mentira cuando se escribio: los tres se quedaron viejos solos.

Un numero a mano en un documento es una copia sin dueño. Este guion le pone
dueno: la exportacion manda, y cualquier documento que diga otra cosa se reporta.

QUE NO HACE, y es deliberado: no corrige. Un guion que reescribe la prosa por su
cuenta cambia afirmaciones que un humano redacto con matices —«44 de 47», «tres
unidades no tienen capturado el corte»— y eso no es sincronizar, es reescribir.
Reporta y para.

Uso:  python3 scripts/verificar_cifras.py
Sale: 0 si todo cuadra, 1 si algo no.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXPORT = REPO / "data/derived/export"


def filas(nombre: str) -> list[dict]:
    with (EXPORT / nombre).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def verdad() -> dict[str, int | str]:
    """La verdad sale de la exportacion, nunca de otro documento."""
    fuentes = filas("fuentes.csv")
    manifiesto = {r["archivo"]: r for r in
                  csv.DictReader((EXPORT / "MANIFEST.csv").open(encoding="utf-8"))}
    return {
        "unidades":    len(filas("unidades.csv")),
        # Feriados DISTINTOS, no filas: desde v2.20 un feriado puede traer varias
        # reglas de fecha y `feriados.csv` tiene una fila por regla. Contar filas
        # inflaria la cifra publicada en cada feriado con alternativa condicional.
        "feriados":    len({f["feriado_id"] for f in filas("feriados.csv")}),
        # Unidades con titularidad, no filas: desde que hay versiones historicas
        # una jurisdiccion con reforma aparece dos veces, y contar filas inflaria
        # la cifra publicada. Mismo cuidado que con los feriados.
        "vacaciones":  len({f["iso3"] for f in filas("vacaciones.csv")}),
        "colocacion":  len(filas("colocacion.csv")),
        "fuentes":     len(fuentes),
        "nivel12":     sum(1 for f in fuentes if int(f["nivel"]) <= 2),
        # EL DESGLOSE, no solo el total. La frase de hallazgos decia «126 de 250
        # fuentes son de nivel 1 o 2. De las 77 restantes, 68 estan en 3-4…» y
        # este guion solo vigilaba el 250: certificaba una frase llena de numeros
        # habiendo leido uno. Y los otros ni siquiera cuadraban entre si —126 mas
        # 77 dan 203—, o sea que el error era visible sin consultar nada.
        "nivel1":      sum(1 for f in fuentes if int(f["nivel"]) == 1),
        "nivel2":      sum(1 for f in fuentes if int(f["nivel"]) == 2),
        "nivel34":     sum(1 for f in fuentes if 3 <= int(f["nivel"]) <= 4),
        "resto_de_fuentes": sum(1 for f in fuentes if int(f["nivel"]) > 2),
        "evidencia":   len(filas("evidencia.csv")),
        "protocolo":   manifiesto["__protocolo__"]["filas"],
    }


# Cada comprobacion es (documento, patron, clave). El patron captura UN numero en
# su grupo 1, y ese numero tiene que coincidir con la clave correspondiente. Se
# escriben con contexto suficiente para que no aticen cualquier digito suelto: un
# patron laxo daria falsas alarmas y en dos dias nadie correria el guion.
# LAS DE `10-hallazgos.md` SE RETIRARON POR LA MISMA RAZON QUE LAS DEL README, y
# el patron ya es reconocible: cada vez que un documento pasa a generarse desde
# plantilla con marcas, sus comprobaciones aqui quedan CIEGAS —el patron deja de
# encontrar su cifra porque la cifra ya no se teclea— y este guion las cuenta y
# sale con error. Retirarlas con la razon escrita es lo contrario de dejarlas
# mudas: la cobertura la toma C1, que vigila ya seis plantillas.
#
# LAS DEL README SE RETIRARON, y el motivo importa: dejaron de casar porque el
# README pasa a generarse desde plantilla con marcas, asi que sus cifras ya no
# se teclean. Una comprobacion que no encuentra su patron NO falla sola —
# enmudece— y este guion las cuenta como «ciegas» y sale con error justo por
# eso. Retirarlas con la razon escrita es lo contrario de dejarlas mudas: la
# cobertura la toma C1, que ahora vigila `plantillas/README-es.md` y `-en.md`.
COMPROBACIONES = [
    ("docs/00-ESTADO.md", r"\| Unidades capturadas \| \*\*(\d+) de 47\*\* \|", "unidades"),
    ("docs/00-ESTADO.md", r"\| Feriados registrados \| (\d+) \|", "feriados"),
    ("docs/00-ESTADO.md", r"\| Titularidades de vacaciones \| (\d+) de 47 \|", "vacaciones"),
    ("docs/00-ESTADO.md", r"\| Fuentes de nivel 1–2 \| (\d+) de \d+ \|", "nivel12"),
    ("docs/00-ESTADO.md", r"\*\*(v[\d.]+) vigente\*\*", "protocolo"),
]


def main() -> int:
    v = verdad()
    print("La exportacion dice:")
    for k, x in v.items():
        print("  %-12s %s" % (k, x))
    print()

    malas, no_halladas = [], []
    for doc, patron, clave in COMPROBACIONES:
        ruta = REPO / doc
        if not ruta.exists():
            no_halladas.append((doc, patron, "el documento no existe"))
            continue
        m = re.search(patron, ruta.read_text(encoding="utf-8"))
        if not m:
            # Un patron que ya no encuentra nada es tan grave como uno que
            # encuentra el numero equivocado: significa que el documento se
            # reescribio y la comprobacion dejo de vigilar sin avisar.
            no_halladas.append((doc, patron, "el patron ya no encuentra nada"))
            continue
        dicho, real = m.group(1), str(v[clave])
        if dicho != real:
            malas.append((doc, clave, dicho, real))

    for doc, clave, dicho, real in malas:
        print("  DESFASADO  %-24s %-12s dice %-8s y son %s" % (doc, clave, dicho, real))
    for doc, patron, motivo in no_halladas:
        print("  SIN VIGILAR %-23s %s" % (doc, motivo))
        print("              patron: %s" % patron)

    if malas or no_halladas:
        print("\n%d cifras desfasadas, %d comprobaciones ciegas."
              % (len(malas), len(no_halladas)))
        return 1
    print("Las %d cifras de la documentacion coinciden con la exportacion."
          % len(COMPROBACIONES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
