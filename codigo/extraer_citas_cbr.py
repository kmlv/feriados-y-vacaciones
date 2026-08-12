"""Extrae del CBR SOLO las citas legales, nunca los valores codificados.

Por que existe este guion, y por que separa las dos cosas con tanto cuidado.

§23.1 del protocolo distingue lo que el antecedente externo PUEDE hacer de lo
que NO puede:

  PUEDE  ·  localizar la norma aplicable, aportar candidatos a reforma con cita
  NO PUEDE  ·  aportar el valor, ni eximir de leer la norma

El problema operativo es que el documento del CBR se llama «Codes AND Sources»:
el valor codificado y la cita legal viven en el mismo parrafo. Leerlo a ojo para
sacar solo las citas es exactamente la situacion en la que la captura deja de
ser ciega sin que uno lo note.

Asi que la separacion se hace por maquina y no por fuerza de voluntad: este
guion **elimina** toda linea con forma de codigo —`1970: 0.67`, `2005: 1`— y
devuelve unicamente la prosa que cita normas. Lo que sale es una lista de que
leer, no una lista de cuanto vale.

Uso:
    python3 scripts/extraer_citas_cbr.py Peru Mexico Germany ...
    python3 scripts/extraer_citas_cbr.py --piloto      # las ocho del piloto

Salida: data/derived/citas_cbr/<pais>.md
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PDF = REPO / ("data/raw/bibliografia/cbr-cambridge_A_20260808/"
              "cbr-labour-regulation-index-2023-codes-and-sources.pdf")
SALIDA = REPO / "data/derived/citas_cbr"

# Las dos variables del proyecto. El resto del CBR no nos concierne.
VARIABLES = {
    "9": "Annual leave entitlements",
    "10": "Public holiday entitlements",
}

# Unidades del piloto, con el nombre tal como lo escribe el CBR.
PILOTO = ["Peru", "Mexico", "Germany", "Indonesia", "Turkey", "Canada"]
SIN_COBERTURA = ["Guatemala", "El Salvador"]

# Una linea de CODIGO: anio, dos puntos, numero. Es lo que hay que tirar.
CODIGO = re.compile(r"^\s*\d{4}\s*:\s*[\d.]+\s*$")
# El indice del PDF: lineas de puntos suspensivos con numero de pagina.
INDICE = re.compile(r"\.{5,}\s*\d+\s*$")

# Forma de una cita normativa. Se acepta el instrumento, su numero, su anio y
# el articulo si viene pegado. NO se acepta la frase que lo rodea: ahi es donde
# viaja el valor, y el valor esta prohibido como punto de partida.
CITA = re.compile(
    r"(?:[A-Z][A-Za-z’'()\-]*\s+){0,5}"
    r"(?:Act|Law|Code|Decree|Decreto|Ley|Regulation|Ordinance|Statute|Constitution|"
    r"Convention|Directive|FLL|LFT|CRA|ACB|BUrlG|Gesetz|Kanun|Undang|Standards?)"
    r"(?:\s+(?:No\.?|n°|Nº|N\.?º)?\s*[\dIVXLC/\-]+)?"
    r"(?:\s+(?:of|de)?\s*\d{4})?"
    r"(?:\s*,?\s*(?:Art|Arts|Article|Articles|Sec|Section|s\.)\.?\s*[\d]+"
    r"(?:\s*\(\d+\))?(?:\s*(?:and|,)\s*[\d]+)*)?")


def texto_del_pdf() -> str:
    if not PDF.exists():
        sys.exit("no esta el PDF del CBR en %s" % PDF.relative_to(REPO))
    return subprocess.run(["pdftotext", str(PDF), "-"],
                          capture_output=True, text=True, check=True).stdout


def seccion_de(texto: str, pais: str) -> str | None:
    """Trozo del documento que corresponde a un pais.

    El encabezado de pais es una linea con solo el nombre. Se descarta la
    aparicion en el indice, que lleva puntos suspensivos.
    """
    lineas = texto.split("\n")
    inicios = [i for i, l in enumerate(lineas)
               if l.strip() == pais and not INDICE.search(l)]
    if not inicios:
        return None
    # La ultima aparicion suelta es el encabezado real; las previas pueden ser
    # menciones dentro de otra seccion.
    inicio = inicios[-1] if len(inicios) == 1 else inicios[0]
    # Termina donde empieza la variable 42 (la ultima) o 3000 lineas despues.
    fin = min(inicio + 3000, len(lineas))
    return "\n".join(lineas[inicio:fin])


def citas_de_variable(seccion: str, numero: str, titulo: str) -> list[str]:
    """Prosa de una variable, con las lineas de codigo eliminadas."""
    m = re.search(r"^%s\.\s*%s" % (re.escape(numero), re.escape(titulo)),
                  seccion, re.M | re.I)
    if not m:
        # El titulo a veces se parte en dos lineas por el maquetado.
        m = re.search(r"^%s\.\s*%s" % (re.escape(numero),
                                       re.escape(titulo.split()[0])),
                      seccion, re.M | re.I)
        if not m:
            return []
    resto = seccion[m.end():]
    # Hasta el encabezado de la variable siguiente.
    fin = re.search(r"^\d{1,2}\.\s+[A-Z]", resto, re.M)
    bloque = resto[:fin.start()] if fin else resto[:2000]

    limpio = " ".join(l.strip() for l in bloque.split("\n")
                      if l.strip() and not CODIGO.match(l.strip())
                      and not l.strip().isdigit())
    # Devolver la prosa entera NO sirve: el valor viaja dentro de la frase
    # («6 days after their first year…»), asi que quitar las lineas de codigo
    # deja pasar el numero igual. Se extraen solo los TOKENS con forma de cita
    # normativa y se descarta todo lo demas, incluida la frase que los rodea.
    citas = []
    for m in CITA.finditer(limpio):
        c = " ".join(m.group(0).split())
        if c not in citas:
            citas.append(c)
    return citas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="*")
    ap.add_argument("--piloto", action="store_true")
    args = ap.parse_args()

    paises = args.paises or (PILOTO if args.piloto else [])
    if not paises:
        sys.exit("nombra paises o pasa --piloto")

    texto = texto_del_pdf()
    SALIDA.mkdir(parents=True, exist_ok=True)

    for pais in paises:
        seccion = seccion_de(texto, pais)
        if seccion is None:
            print("  %-14s NO APARECE en el CBR" % pais)
            continue
        out = ["# Citas legales del CBR — %s\n" % pais,
               "**Solo citas. Los valores codificados se eliminaron por maquina**, "
               "no a ojo: el documento del CBR mezcla codigo y fuente en el mismo "
               "parrafo, y §23.1 permite la cita pero prohibe el valor.\n",
               "Esto dice **que leer**, no cuanto vale. La norma se lee y el valor "
               "se deriva bajo nuestro constructo.\n"]
        vacio = True
        for numero, titulo in VARIABLES.items():
            lineas = citas_de_variable(seccion, numero, titulo)
            out.append("\n## %s. %s\n" % (numero, titulo))
            if lineas:
                vacio = False
                out.append("\n".join(lineas))
            else:
                out.append("*No se pudo aislar la seccion — revisar a mano.*")
            out.append("")
        destino = SALIDA / ("%s.md" % pais.lower().replace(" ", "-"))
        destino.write_text("\n".join(out) + "\n")
        print("  %-14s %s%s" % (pais, destino.relative_to(REPO),
                                "   (vacio: revisar)" if vacio else ""))

    if SIN_COBERTURA:
        print("\nSin cobertura del CBR, por definicion (son las dos que faltan "
              "de las 47): %s" % ", ".join(SIN_COBERTURA))


if __name__ == "__main__":
    main()
