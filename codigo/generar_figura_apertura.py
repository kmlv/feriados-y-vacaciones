"""Genera la figura de apertura de D1 desde las marcas ya registradas.

QUE DIBUJA. Dos paneles, que es la forma que fijaron dos revisiones independientes al converger:

  Izquierda · el NIVEL — dias de trabajo liberados de Peru contra las dos medianas
             de referencia. Es la afirmacion de la primera plana, en una imagen.
  Derecha   · la COMPOSICION de Peru — vacaciones y feriados por separado.

POR QUE NO ES UNA BARRA APILADA. Peru computa los feriados CONTRA el periodo
vacacional, asi que las dos componentes no se suman mecanicamente: apilarlas
invitaria al lector a leer un total que no es el publicado. Van una al lado de la
otra, y el total va en el panel izquierdo, donde si esta bien calculado.

DE DONDE SALEN LAS CIFRAS. De `construir_registro`, las mismas marcas que alimentan
los cuadros. No se teclea ninguna y no se calcula ninguna: si el dato cambia, la
figura cambia con el. Esto NO es calculo, es presentacion — la regla de una sola
calculadora se respeta porque aqui no nace ningun numero.

SALIDA. `figura-apertura-es.{pdf,png}` y `figura-apertura-en.{pdf,png}` en
`plantillas/figuras/`. Cada plantilla de idioma referencia la suya, CON extension
—referenciarla sin extension fue una de las causas encadenadas de que la figura
no saliera en el PDF.

POR QUE AQUI Y NO EN reportes/. `reportes/` se borra y se reconstruye entero en
cada compilacion, asi que cualquier figura escrita ahi desaparece en la siguiente.
La fuente vive en `plantillas/figuras/` y el generador la copia a
`reportes/figuras/` al compilar. C4 comprueba que la figura viaje con el
documento: una referencia a una imagen que no se empaqueta no rompe nada —el
Markdown se ve bien en el repositorio— y deja un hueco solo cuando alguien recibe
el paquete suelto.

Uso:  python3 plantillas/generar_figura_apertura.py
"""
import re, shutil, sqlite3, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import reportes_nucleo as N

SALIDA = REPO / "plantillas" / "figuras"

# LA FIGURA TIENE IDIOMA, Y ES FACIL NO VERLO. Los rotulos van DENTRO de la
# imagen, asi que un D1 ingles que referencie la figura castellana sale con
# «Perú», «Vacaciones» y «Feriados efectivos» incrustados en el grafico. No lo
# caza ninguna compuerta de texto: para ellas la figura es una ruta.
#
# Se emiten las dos y cada plantilla referencia la suya. FORMATO.md §12 dice que
# el separador decimal tambien cambia, y aqui hay que aplicarlo a mano porque
# estos rotulos no pasan por `_fmt`.
IDIOMAS = {
    "es": dict(
        titulo_izq="Días de trabajo liberados al año",
        titulo_der="De qué se compone el total peruano",
        peru="Perú", ocde="Mediana OCDE", ibe="Mediana Iberoamérica",
        vac="Vacaciones", fer="Feriados efectivos",
        decimal=",",
        # LA CLAUSULA DEL MINIMO EXIGIBLE. La revisión cruzada la pidió para la figura de
        # dispersion y aplica igual aqui: §4.3 del cuerpo retira la expresion
        # «minimo exigible» y la rebaja a valor esperado bajo un supuesto
        # nuestro de colocacion uniforme. Quien solo mire la figura —que es el
        # destino de toda figura— recuperaria la afirmacion retirada.
        pie=("Perú: {per} días, el {pct}\\,\\% de su año laboral. "
             "Las dos componentes no se suman: los feriados dentro del período "
             "vacacional se computan contra él. El total es un valor esperado, "
             "no un mínimo exigible."),
    ),
    "en": dict(
        titulo_izq="Paid work days released per year",
        titulo_der="What the Peruvian total is made of",
        peru="Peru", ocde="OECD median", ibe="Ibero-American median",
        vac="Annual leave", fer="Effective public holidays",
        decimal=".",
        pie=("Peru: {per} days, {pct}\\,\\% of its working year. "
             "The two components do not add: holidays inside the leave period "
             "are counted against it. The total is an expected value, "
             "not an enforceable minimum."),
    ),
}


def num(s):
    """«34,3» -> 34.3. Las marcas vienen en formato español."""
    return float(str(s).replace("−", "-").replace(",", "."))


reg = N.construir_registro(sqlite3.connect(REPO / "data/derived/piloto.db"))

per   = num(reg["per_descanso"])
ocde  = num(reg["ocde_mediana"])
ibe   = num(reg["ibe_mediana"])
vac   = num(reg["per_conv"])            # vacaciones de Perú en días de trabajo
fer   = num(reg["per_fer_efectivos"])   # feriados efectivos esperados
pct   = reg["per_pct_ano"]

esc = 0.16                               # cm por día, panel izquierdo


def barra(y, valor, etiqueta, dec, focal=False):
    color = "focal" if focal else "neutro"
    peso = r"\bfseries" if focal else ""
    return (
        f"  \\node[anchor=east, font=\\small{peso}] at (0,{y}) {{{etiqueta}}};\n"
        f"  \\fill[{color}] (0.15,{y-0.22}) rectangle ({0.15+valor*esc},{y+0.22});\n"
        f"  \\node[anchor=west, font=\\small{peso}] at ({0.15+valor*esc+0.12},{y}) "
        f"{{{str(valor).replace('.', dec)}}};\n"
    )

def construir(L):
    """Arma el TikZ completo para un idioma. Un solo sistema de coordenadas:
    el panel derecho va en un `scope` desplazado, no en un segundo dibujo."""
    dec = L["decimal"]
    izq = (barra(0.0,   per,  L["peru"], dec, True)
           + barra(-0.85, ocde, L["ocde"], dec)
           + barra(-1.70, ibe,  L["ibe"],  dec))
    der = (barra(0.0,   vac, L["vac"], dec, True)
           + barra(-0.85, fer, L["fer"], dec, True))
    pie = L["pie"].format(per=str(per).replace(".", dec), pct=str(pct).replace(",", dec))
    return (r"""\documentclass[tikz,border=4pt]{standalone}
\usepackage{fontspec}
\setmainfont{Helvetica}
\usepackage{tikz}
\definecolor{focal}{HTML}{9C2A2A}
\definecolor{neutro}{HTML}{B8B8B4}
\definecolor{tinta}{HTML}{1A1A1A}
\definecolor{gris}{HTML}{6B6B6B}
\begin{document}
\begin{tikzpicture}
  % ---- panel izquierdo: nivel ----
  \node[anchor=west, font=\small\bfseries, text=tinta] at (-3.6,1.15)
    {""" + L["titulo_izq"] + r"""};
""" + izq + r"""  % ---- separador ----
  \draw[gris!40] (7.6,1.3) -- (7.6,-2.15);
  % ---- panel derecho: composicion de Peru ----
  \node[anchor=west, font=\small\bfseries, text=tinta] at (8.3,1.15)
    {""" + L["titulo_der"] + r"""};
  \begin{scope}[xshift=11.6cm]
""" + der + r"""  \end{scope}
  \node[anchor=west, font=\footnotesize, text=gris] at (-3.6,-2.6)
    {""" + pie + r"""};
\end{tikzpicture}
\end{document}
""")


SALIDA.mkdir(exist_ok=True)
for cod, L in IDIOMAS.items():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "fig.tex"
        f.write_text(construir(L), encoding="utf-8")
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", f.name],
                           cwd=d, capture_output=True, text=True)
        pdf = Path(d) / "fig.pdf"
        if not pdf.exists():
            err = [l for l in r.stdout.splitlines() if l.startswith("!")][:4]
            raise SystemExit("xelatex fallo (%s):\n%s" % (cod, "\n".join(err)))
        base = SALIDA / ("figura-apertura-%s" % cod)
        shutil.copy(pdf, base.with_suffix(".pdf"))
        subprocess.run(["magick", "-density", "200", str(base.with_suffix(".pdf")),
                        "-background", "white", "-alpha", "remove",
                        str(base.with_suffix(".png"))], capture_output=True)
        print("figura escrita:", base.with_suffix(".pdf").name)

print("  Peru %s · OCDE %s · Iberoamerica %s · composicion %s + %s"
      % (reg["per_descanso"], reg["ocde_mediana"], reg["ibe_mediana"],
         reg["per_conv"], reg["per_fer_efectivos"]))
