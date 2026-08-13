"""Dispersión: días de trabajo liberados contra PBI per cápita PPP.

QUE DIBUJA, Y POR QUE ESTA FORMA. Un punto por jurisdicción. En el eje vertical
el desenlace de D1 —días de trabajo liberados y pagados al año, vacaciones más
feriados efectivos con la imputación de §4.2—; en el horizontal el ingreso, en
escala logarítmica porque el conjunto abarca un factor de diecinueve entre la
unidad más pobre y la más rica y en escala lineal el tercio inferior se apelmaza
contra el margen.

EL COLOR CODIFICA PERTENENCIA, Y LA PERTENENCIA NO ES UNA PARTICION. El grupo de
referencia es la UNION de tres componentes, y siete unidades están en dos a la
vez. Un color por unidad obligaría a elegir cuál de sus dos pertenencias mostrar
—que es precisamente la clase de elección escondida que este proyecto denuncia en
otros—. Por eso el círculo se parte: la mitad izquierda dice si la unidad es
iberoamericana y la derecha su situación ante la OCDE. Las dos dimensiones son
independientes y ninguna tapa a la otra. Ninguna unidad está en los tres
componentes —adhesión y membresía se excluyen por construcción—, así que dos
mitades bastan y no hacen falta tercios.

POR QUE PERU NO SE PINTA DE OTRO COLOR. Resaltarlo repintándolo destruiría su
codificación de grupo, que es media figura: Perú es iberoamericano Y está en
adhesión, y ese es el hecho que la imagen tiene que dejar ver. Se resalta por
anillo, tamaño y rótulo —peso, no tono—, que además es la regla general de no
vestir el texto con el color de la serie.

LA PALETA ESTA VALIDADA, NO ELEGIDA A OJO. Los tres tonos pasan las seis
comprobaciones de `validate_palette.js` con la lista de pares COMPLETA, que es la
que corresponde a una dispersión —en una dispersión cualquier par de puntos puede
quedar contiguo, no sólo los vecinos de una leyenda—. Peor par bajo daltonismo
ΔE 9,2 sobre un objetivo de 8. El verde queda por debajo de 3:1 contra el papel:
la mitigación exigida es rótulo visible, y aquí la lleva **cada** punto.

DE DONDE SALEN LAS CIFRAS. El desenlace, de `metrica_descanso.filas_de()`; el
ingreso y la pertenencia, de `grupo_referencia.csv`, que los construyó
`construir_grupos_comparacion.py` desde la API del Banco Mundial. Aquí no nace
ningún número: esto es presentación, y la regla de una sola calculadora se
respeta. La única excepción está declarada abajo y en la propia imagen.

LAS AUSENCIAS, QUE HAY QUE LEER ANTES DE PUBLICAR. El grupo tiene 47 unidades y
aquí se dibujan 46. La que falta es **Bolivia**, y su hueco es una ambigüedad
gramatical de la norma sin resolver —o sea nuestro, no del legislador—, que no es
un cero y no se dibuja como tal.

Estados Unidos **sí entra, y en cero**, desde que `metrica_descanso.py` adjudicó
ese valor. Conviene recordar por qué el cero es un dato y no un hueco: no existe
mandato federal de vacaciones, y sus doce feriados están capturados como cierre
de sector público sin mandato nacional, o sea cero exigible al empleador privado.
Contra el ingreso es la observación más informativa del conjunto —el país más
rico salvo uno, sin derecho garantizado—. Durante un tiempo esta figura fijaba
ese cero por su cuenta, y estuvo mal: dejaba el mismo número definido en dos
sitios. Ahora sale del calculador como cualquier otro y aquí no nace ningún
número.

SALIDA. `figura-dispersion-ppp-es.{pdf,png}` y `-en.{pdf,png}` en
`plantillas/figuras/`. SE EMITEN LOS DOS IDIOMAS POR DEFECTO, sin bandera: si el
ingles fuera opcional, el dia que alguien regenere tras cambiar el dato dejaria
la inglesa vieja junto a la nueva, y una figura desfasada en el otro idioma no la
ve nadie hasta el PDF. Cada plantilla de D1 referencia la suya.

Uso:  python3 plantillas/generar_figura_dispersion.py
"""
from __future__ import annotations

import csv
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import metrica_descanso as M                                   # noqa: E402

SALIDA = REPO / "plantillas" / "figuras"
GRUPOS = REPO / "data/derived/grupos_comparacion/grupo_referencia.csv"
CORTE = 2026

# ---------------------------------------------------------------- paleta
# Trío categórico validado con `--pairs all`, que es el régimen de una
# dispersión. No tocar sin volver a pasar el validador: al oscurecerlos "para
# imprenta" el peor par bajo daltonismo cae de 9,2 a 5,4 y reprueba.
C_IBE = "EB6834"        # Iberoamérica
C_OCDE = "2A78D6"       # OCDE, miembro
C_ADH = "1BAF7A"        # OCDE, en adhesión
TINTA = "0B0B0B"        # texto primario
SEC = "52514E"          # texto secundario
MUDO = "898781"         # rótulos de eje
REJILLA = "E1E0D9"      # línea de rejilla, un tono sobre el papel
EJE = "C3C2B7"          # línea de eje
PAPEL = "FCFCFB"        # superficie

# ---------------------------------------------------------------- geometría
# Alto generoso a propósito. Con 9,2 cm las quince unidades ricas del racimo
# superior derecho se tocaban y media docena de rótulos necesitaba guía; el
# problema no era el ancho —el eje es logarítmico y ya reparte bien— sino que
# once días de desenlace ocupaban tres centímetros.
ANCHO, ALTO = 15.6, 11.3        # cm del área de trazado
R = 0.165                       # cm, radio del marcador
R_PER = 0.225                   # cm, radio de Perú
X_MIN, X_MAX = 6200.0, 155000.0
Y_MIN, Y_MAX = -1.6, 37.0
X_TICKS = [(10000, "10"), (20000, "20"), (50000, "50"), (100000, "100")]
X_REJILLA = [8000, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 150000]
Y_TICKS = [0, 5, 10, 15, 20, 25, 30, 35]


def px(v: float) -> float:
    """Ingreso -> cm. Logarítmica: el eje compara razones, no diferencias."""
    lo, hi = math.log10(X_MIN), math.log10(X_MAX)
    return (math.log10(v) - lo) / (hi - lo) * ANCHO


def py(v: float) -> float:
    return (v - Y_MIN) / (Y_MAX - Y_MIN) * ALTO


def esc(s: str) -> str:
    """Rótulos a LaTeX. Los nombres traen tildes y `&` no aparece, pero por si."""
    return s.replace("&", r"\&").replace("_", r"\_").replace("%", r"\%")


# ---------------------------------------------------------------- datos
def cargar(L: dict) -> tuple[list[dict], dict]:
    metrica = {f["iso"]: f for f in M.filas_de(CORTE)}
    grupos = {r["iso3"]: r for r in csv.DictReader(GRUPOS.open(encoding="utf-8"))}

    puntos, perdidas = [], []
    for iso, g in grupos.items():
        if not g["ppp_promedio_2021_2025"]:
            # Sin ingreso no hay abscisa y la unidad no puede dibujarse. Hoy
            # esta rama está vacía, pero si un día se llena tiene que decirlo:
            # una unidad que la métrica sí emite y la figura calla es una
            # truncación silenciosa, que es el defecto que este proyecto
            # persigue. Se avisa por salida estándar y se cuenta en el pie.
            if iso in metrica:
                perdidas.append(iso)
            continue
        f = metrica.get(iso)
        if f is not None:
            # El centro del intervalo, que es lo mismo que usa el registro de D1
            # para sus medianas. Publicar el extremo bajo aquí y el centro allá
            # daría dos cifras distintas del mismo país en el mismo informe.
            y = (f["lo"] + f["hi"]) / 2
            medido = True
        else:
            # NO SE DIBUJA LO QUE EL CALCULADOR NO EMITE. Aqui hubo una rama que
            # ponia a Estados Unidos en cero desde este archivo. El cero era
            # defendible y el sitio no: dejaba la figura con 46 unidades y el
            # cuerpo con 45, y el mismo numero definido en dos lugares. El dia
            # que el calculador lo emitiera, las medianas se moverian y la
            # figura no. Decision del principal: dibujar las que emite y
            # explicar las ausencias, que es lo que hace `ausentes()`.
            continue
        puntos.append({
            "iso": iso, "pais": g["pais"], "x": float(g["ppp_promedio_2021_2025"]),
            "y": y, "medido": medido,
            "pob": float(g["poblacion_2024"] or 0),
            "ibe": g["comp_iberoamerica"] == "si",
            "ocde": g["comp_ocde"] == "si",
            "adh": g["comp_adhesion"] == "si",
        })
    dibujadas = {p["iso"] for p in puntos}
    faltan = ausentes(grupos, dibujadas, L)
    return puntos, {"filas_metrica": len(metrica), "perdidas": sorted(perdidas),
                    "faltan": faltan}


# ------------------------------------------------------ idioma de la figura
# LOS ROTULOS VAN DENTRO DE LA IMAGEN, Y ESO NO LO CAZA NINGUNA COMPUERTA. Para
# una compuerta de texto una figura es una ruta; que su leyenda este en el idioma
# equivocado es invisible hasta que alguien mira el PDF. D1 se publica en dos
# idiomas, asi que la figura se emite en dos y cada plantilla referencia la suya.
#
# El separador decimal tambien cambia (FORMATO.md §12) y aqui hay que aplicarlo a
# mano, porque estos numeros no pasan por `_fmt`.
IDIOMAS = {
    "es": {
        "eje_y": "Días de trabajo liberados y pagados al año",
        "eje_x": "PBI per cápita PPP — miles de dólares internacionales, "
                 "promedio 2021--2025 (escala logarítmica)",
        "ibe": "Iberoamérica", "ocde": "OCDE, miembro",
        "adh": "OCDE, en adhesión", "dos": "en dos grupos",
        "sin_mandato": "sin mandato legal: cero",
        "peru": "Perú", "decimal": ",",
        "ajuste": "sin Estados Unidos ni Japón",
        "fit_stats": r"n\,%d, pendiente %s, R$^2$ %s",
        "cabecera": r"\textbf{%d jurisdicciones, %d.} Vacaciones más los feriados "
                    r"que caen en día de trabajo, contados en días de trabajo de "
                    r"cada país; no incluye el descanso semanal. En %d países la "
                    r"ley no dice si los feriados que caen dentro de las "
                    r"vacaciones las alargan: ahí se dibuja el centro del rango. "
                    r"Es un valor esperado, no un mínimo garantizado.",
        "ausencias_pre": r"\\[1pt] No aparecen en el gráfico ",
        "ausencias_sep": "; ni ",
        # CONCORDANCIA. El numero de ausencias cambia con el dato —hoy una,
        # ayer dos— y un plural fijo se lee como plantilla sin terminar. Ver
        # FORMATO.md §4.
        "ausencias_post_1": r". La ausencia es el dato y no un cero: dibujarla "
                            r"en cero pondría en la figura un valor que el "
                            r"cálculo no emite.",
        "ausencias_post_n": r". La ausencia es el dato y no un cero: dibujarlas "
                            r"en cero pondría en la figura un valor que el "
                            r"cálculo no emite.",
        "recta": r"\\[1pt] \textbf{La recta deja fuera a Estados Unidos y a "
                 r"Japón:} son los dos que no garantizan feriados al asalariado "
                 r"privado. Siguen dibujados. Con las %d unidades enteras la "
                 r"pendiente es %s en vez de %s. Es descriptiva — el ingreso no "
                 r"explica el derecho.",
        "cautela": r"\\[1pt] \emph{Irlanda y Noruega} tienen el producto por "
                   r"habitante inflado respecto al ingreso de sus residentes, por "
                   r"contabilidad de multinacionales y por renta petrolera.",
        "fuentes": r"\\[1pt] \emph{Fuentes:} derecho vigente, elaboración propia "
                   r"sobre las normas. Ingreso, Banco Mundial, promedio "
                   r"2021--2025.",
        "perdidas": r" \emph{Sin dibujar por falta de serie de ingreso:} ",
        "razon": {
            "USA": "porque no tiene mandato federal de vacaciones pagadas ni de "
                   "feriados exigibles al empleador privado: no hay valor que medir",
            "BOL": "porque su norma tiene una ambig\u00fcedad gramatical sin "
                   "resolver, y ese hueco es nuestro y no del legislador",
        },
    },
    "en": {
        "eje_y": "Paid work days released per year",
        "eje_x": "GDP per capita PPP — thousands of international dollars, "
                 "2021--2025 average (logarithmic scale)",
        "ibe": "Ibero-America", "ocde": "OECD, member",
        "adh": "OECD, acceding", "dos": "in two groups",
        "sin_mandato": "no statutory mandate: zero",
        "peru": "Peru", "decimal": ".",
        "ajuste": "excluding the United States and Japan",
        "fit_stats": r"n\,%d, slope %s, R$^2$ %s",
        "cabecera": r"\textbf{%d jurisdictions, %d.} Annual leave plus the public "
                    r"holidays falling on a work day, counted in each country's "
                    r"work days; weekly rest not included. In %d countries the law "
                    r"does not say whether holidays falling inside the leave "
                    r"period extend it: there the centre of the range is plotted. "
                    r"It is an expected value, not a guaranteed minimum.",
        "ausencias_pre": r"\\[1pt] Not shown in the chart: ",
        "ausencias_sep": "; and ",
        "ausencias_post_1": r". The absence is the datum and not a zero: "
                            r"plotting it at zero would put a value in the "
                            r"figure that the calculation does not emit.",
        "ausencias_post_n": r". The absence is the datum and not a zero: "
                            r"plotting them at zero would put a value in the "
                            r"figure that the calculation does not emit.",
        "recta": r"\\[1pt] \textbf{The line excludes the United States and "
                 r"Japan:} they are the two that guarantee no public holidays to "
                 r"the private employee. Both are still plotted. Over the full "
                 r"%d units the slope is %s rather than %s. The line is "
                 r"descriptive — income does not explain the entitlement.",
        "cautela": r"\\[1pt] \emph{Ireland and Norway} have output per head "
                   r"inflated relative to their residents' income, through "
                   r"multinational accounting and petroleum rent.",
        "fuentes": r"\\[1pt] \emph{Sources:} law in force, authors' coding of the "
                   r"statutes. Income, World Bank, 2021--2025 average.",
        "perdidas": r" \emph{Not plotted for want of an income series:} ",
        "razon": {
            "USA": "because it has no federal mandate of paid leave or of public "
                   "holidays enforceable against the private employer: there is "
                   "no value to measure",
            "BOL": "because its statute has an unresolved grammatical ambiguity, "
                   "and that gap is ours and not the legislature's",
        },
    },
}

# ---------------------------------------------------- ausencias del grupo
# POR QUE ESTO ES UNA TABLA Y NO UNA FRASE. El grupo de referencia tiene mas
# unidades que las que el calculador emite, y la diferencia hay que NOMBRARLA:
# una unidad que desaparece del grafico sin explicacion es truncacion silenciosa.
# Las razones no son intercambiables —una es un hecho de la ley, la otra un hueco
# nuestro— y por eso van una por unidad.
#
# Y falla ruidosamente ante una unidad que no conoce. Si manana el grupo pierde
# una tercera, este archivo se detiene en vez de dibujar un conjunto incompleto
# sin decirlo. Es la misma disciplina que hace que resolver() aborte.


def ausentes(grupos: dict, dibujadas: set, L: dict):
    """Unidades del grupo que no se dibujan, con su nombre y su razon.

    Falla ruidosamente ante una unidad sin razon declarada, EN CUALQUIERA de los
    dos idiomas: una razon que existe en castellano y falta en ingles produce una
    figura inglesa a la que le falta una explicacion, y eso no lo ve nadie.
    """
    falta = [i for i in grupos if i not in dibujadas]
    for cod, otro in IDIOMAS.items():
        sin = [i for i in falta if i not in otro["razon"]]
        if sin:
            raise SystemExit(
                "unidades ausentes sin razon declarada en «%s»: %s\n"
                "Anadala a IDIOMAS[...][\"razon\"] en LOS DOS idiomas, o el pie "
                "omitiria una unidad en silencio." % (cod, ", ".join(sin)))
    return [(grupos[i]["pais"], L["razon"][i]) for i in falta]


# ------------------------------------------------------------- ajustes
# TRES RECTAS, Y VAN EN UNA VARIANTE APARTE A PROPOSITO. El principal las pidió
# para comparar y quedarse con una, no para publicar las tres. Mientras decide,
# la figura del cuerpo sigue sin línea: una nube contra el ingreso ya invita a
# leer una relación, y dibujar tres a la vez invita a leer la que más guste.
#
# QUE SE AJUSTA. Mínimos cuadrados de los días contra el LOGARITMO del ingreso,
# que es la variable del eje. Ajustar contra el ingreso en niveles daría una
# recta que en este eje sale curva, y el lector no podría comprobarla con la
# regla. No hay inferencia aquí: ni error estándar ni contraste, porque estas 46
# unidades no son una muestra de nada — son el grupo entero.
AJUSTES = [
    ("crudo", "las 46", None, None),
    ("ponderado por población", "las 46, peso = habitantes", "pob", None),
    (None, "44 unidades", None, ("USA", "JPN")),   # el nombre lo pone el idioma
]

# LA QUE EL PRINCIPAL ELIGIO, tras ver las tres, y RECONFIRMADA cuando el motivo
# original caducó. El motivo era que ésta es la única que no se apoya en el cero
# de Estados Unidos, que entonces no tenía dueño en el calculador. Ya lo tiene, y
# el criterio que queda en pie es el del pie de figura: fuera quien no garantiza
# nada al asalariado privado, que son esos dos y sólo esos dos.
#
# Y AQUI ESTUVO EL DEFECTO QUE ESTO ARRASTRO, que merece quedar escrito porque no
# lo veia ninguna compuerta. Mientras el calculador no emitia a Estados Unidos,
# excluirlo aqui no hacia nada —no estaba entre los puntos— y el rotulo «sin
# Japon» era CIERTO. El dia que el calculador lo adjudico, esta lista empezo a
# quitar dos y el rotulo siguio diciendo uno. Nada parecio cambiar porque la n se
# quedo en 44 en los dos mundos, por razones distintas. Un cambio ajeno convirtio
# un rotulo correcto en falso sin tocarlo, sin mover su numero y sin fallar nada.
#
# De ahi que el pie CALCULE cuanto mueve la exclusion en vez de afirmarla y ya:
# un lector que ve una pendiente no sabe que le quitaron las dos observaciones que
# mas la contradicen, y aqui se le dice.
#
# Los dos excluidos siguen dibujados: se les quita el voto en la recta, no la
# presencia en la nube.
AJUSTE_ELEGIDO = 2


def recta(puntos, peso=None, fuera=None):
    """(a, b, r2, n) de  y = a + b·log10(x).  Devuelve None si no hay datos."""
    ps = [p for p in puntos if not (fuera and p["iso"] in fuera)]
    if len(ps) < 3:
        return None
    w = [(p["pob"] if peso == "pob" else 1.0) for p in ps]
    xs = [math.log10(p["x"]) for p in ps]
    ys = [p["y"] for p in ps]
    sw = sum(w)
    mx = sum(wi * xi for wi, xi in zip(w, xs)) / sw
    my = sum(wi * yi for wi, yi in zip(w, ys)) / sw
    sxx = sum(wi * (xi - mx) ** 2 for wi, xi in zip(w, xs))
    sxy = sum(wi * (xi - mx) * (yi - my) for wi, xi, yi in zip(w, xs, ys))
    if sxx == 0:
        return None
    b = sxy / sxx
    a = my - b * mx
    syy = sum(wi * (yi - my) ** 2 for wi, yi in zip(w, ys))
    res = sum(wi * (yi - (a + b * xi)) ** 2 for wi, xi, yi in zip(w, xs, ys))
    return a, b, (1 - res / syy if syy else 0.0), len(ps)


def colores(p: dict) -> tuple[str, str | None]:
    """(izquierda, derecha). `None` a la derecha = círculo entero de un color."""
    der = C_OCDE if p["ocde"] else (C_ADH if p["adh"] else None)
    if p["ibe"] and der:
        return C_IBE, der
    if p["ibe"]:
        return C_IBE, None
    return der, None


# ------------------------------------------------------- rótulos sin choques
# Cada punto lleva su código, porque una dispersión donde no se puede identificar
# al país sirve de mucho menos a un lector que quiera discutir un caso — y porque
# el rótulo visible es la mitigación que el validador exige para el verde. Se
# colocan por tanteo: ocho posiciones candidatas por punto, en orden de
# preferencia, y se toma la primera que no pise ni un rótulo ya puesto ni un
# marcador. Lo que no cabe en ninguna se dibuja con una guía corta.
ANCHO_CAR = 0.093       # cm por carácter a \tiny
ALTO_ROT = 0.20         # cm


def caja(p, dx, dy, texto):
    w = len(texto) * ANCHO_CAR
    cx = px(p["x"]) + dx + (w / 2 if dx > 0 else (-w / 2 if dx < 0 else 0))
    cy = py(p["y"]) + dy
    return (cx - w / 2 - 0.03, cy - ALTO_ROT / 2 - 0.02,
            cx + w / 2 + 0.03, cy + ALTO_ROT / 2 + 0.02)


def choca(a, b, hx=0.0, hy=0.0):
    a = (a[0] - hx, a[1] - hy, a[2] + hx, a[3] + hy)
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def dist_a_segmento(cx, cy, x0, y0, x1, y1):
    vx, vy = x1 - x0, y1 - y0
    L = vx * vx + vy * vy
    if L == 0:
        return math.hypot(cx - x0, cy - y0)
    t = max(0.0, min(1.0, ((cx - x0) * vx + (cy - y0) * vy) / L))
    return math.hypot(cx - (x0 + t * vx), cy - (y0 + t * vy))


# UNA GUIA NO PUEDE ROZAR UN MARCADOR AJENO, y este fue el defecto más caro de
# la figura porque no se veía en pantalla: a tamaño de imprenta la guía de
# Portugal moría pegada al marcador de Rumania, y como Rumania es verde
# —adhesión— y Portugal azul —miembro—, la lectura cruzada le cambiaba a
# Portugal su situación ante la OCDE. Un rótulo mal atribuido no es un defecto
# estético: afirma un hecho falso sobre un país.
HOLGURA_GUIA = 0.075


# DOS HOLGURAS DISTINTAS, y confundirlas costó una versión entera. Entre dos
# rótulos hace falta aire —sin él «SVK» y «PRT» no se solapaban pero se leían
# como una sola palabra—, pero aplicar esa misma holgura contra los MARCADORES
# empujaba cada rótulo a un anillo lejano con guía, también en las zonas vacías
# donde no hacía ninguna falta. La holgura es del texto contra el texto.
AIRE_X, AIRE_Y = 0.10, 0.025


def colocar(puntos, L: dict):
    g = R + 0.075
    d = 0.7071
    cand = [(g, 0), (-g, 0), (0, g + 0.06), (0, -g - 0.06),
            (g * .78, g * .78), (-g * .78, g * .78),
            (g * .78, -g * .78), (-g * .78, -g * .78)]
    # Anillos sucesivos con guía: si el punto está en un racimo, el rótulo se
    # aleja en vez de desaparecer. Sin esto, el conjunto denso de la esquina
    # superior derecha perdía tres países y el pie tenía que confesarlo.
    for rad in (0.42, 0.62, 0.86, 1.14):
        for ux, uy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (d, d), (-d, d), (d, -d), (-d, -d)):
            cand.append(((g + rad) * ux, (g + rad) * uy))
    marcadores = [(px(p["x"]) - R - .02, py(p["y"]) - R - .02,
                   px(p["x"]) + R + .02, py(p["y"]) + R + .02) for p in puntos]
    puestas, salida = [], {}

    # Perú primero, y después los puntos más apretados. Quien tiene vecinos
    # cerca se queda sin sitio si llega tarde; quien está solo coloca su rótulo
    # pegado en cualquier orden. Atender primero al que menos opciones tiene es
    # lo que evita que un país del racimo acabe con una guía de centímetro y
    # medio cruzando media figura.
    def apreturas(p):
        return sum(1 for q in puntos if q is not p
                   and math.hypot(px(q["x"]) - px(p["x"]),
                                  py(q["y"]) - py(p["y"])) < 1.25)

    # Y dentro de cada punto, hacia donde hay hueco. Sin esto un rótulo se
    # colocaba en el primer sitio libre aunque ese sitio apuntara hacia el
    # vecino, y «GBR» acababa entre dos marcadores sin decir cuál de los dos era
    # el suyo. Las candidatas se reordenan por lo despejada que está su
    # dirección, conservando la preferencia por las pegadas sobre las de anillo.
    def despeje(p, dx, dy):
        n = math.hypot(dx, dy) or 1
        ux, uy = dx / n, dy / n
        peor = 9.9
        for q in puntos:
            if q is p:
                continue
            vx, vy = px(q["x"]) - px(p["x"]), py(q["y"]) - py(p["y"])
            d = math.hypot(vx, vy)
            if d > 1.9 or d == 0:
                continue
            # Sólo cuentan los vecinos que están en esa dirección.
            if (vx * ux + vy * uy) / d > 0.35:
                peor = min(peor, d)
        return peor

    orden = sorted(puntos, key=lambda p: (p["iso"] != "PER", -apreturas(p)))
    for p in orden:
        texto = L["peru"] if p["iso"] == "PER" else p["iso"]
        rr = R_PER if p["iso"] == "PER" else R
        pegadas = sorted(range(8), key=lambda j: -despeje(p, *cand[j]))
        orden_cand = [cand[j] for j in pegadas] + cand[8:]
        for i, (dx, dy) in enumerate(orden_cand):
            k = (rr - R)
            c = caja(p, dx + (k if dx > 0 else -k if dx < 0 else 0),
                     dy + (k if dy > 0 else -k if dy < 0 else 0), texto)
            if c[0] < -1.5 or c[2] > ANCHO + 1.4 or c[1] < -0.9 or c[3] > ALTO + 0.5:
                continue
            if any(choca(c, q, AIRE_X, AIRE_Y) for q in puestas):
                continue
            if any(choca(c, m) for m in marcadores):
                continue
            if i >= 8:      # lleva guía: comprobar que no roza a nadie
                n_ = math.hypot(dx, dy) or 1
                gx0 = px(p["x"]) + dx / n_ * (rr + 0.03)
                gy0 = py(p["y"]) + dy / n_ * (rr + 0.03)
                gx1, gy1 = px(p["x"]) + dx * 0.86, py(p["y"]) + dy * 0.86
                if any(dist_a_segmento(px(q["x"]), py(q["y"]),
                                       gx0, gy0, gx1, gy1) < R + HOLGURA_GUIA
                       for q in puntos if q is not p):
                    continue
            puestas.append(c)
            salida[p["iso"]] = (dx, dy, texto, i >= 8)
            break
        else:
            salida[p["iso"]] = None      # sin sitio: se omite y se declara
    return salida


# ---------------------------------------------------------------- dibujo
def marcador(p, resaltado=False):
    x, y = px(p["x"]), py(p["y"])
    r = R_PER if resaltado else R
    izq, der = colores(p)
    t = ""
    if not p["medido"]:
        # Hueco: no es un valor medido con la misma cañería que los demás.
        t += (f"  \\draw[c{izq.lower()}, line width=0.9pt] ({x:.3f},{y:.3f}) "
              f"circle ({r:.3f});\n")
        return t
    if der is None:
        t += f"  \\fill[c{izq.lower()}] ({x:.3f},{y:.3f}) circle ({r:.3f});\n"
    else:
        t += (f"  \\fill[c{izq.lower()}] ({x:.3f},{y:.3f}) ++(90:{r:.3f}) "
              f"arc[start angle=90, end angle=270, radius={r:.3f}] -- cycle;\n"
              f"  \\fill[c{der.lower()}] ({x:.3f},{y:.3f}) ++(270:{r:.3f}) "
              f"arc[start angle=270, end angle=450, radius={r:.3f}] -- cycle;\n")
    # Anillo del color del papel: separa los marcadores que se solapan sin
    # dibujarles un borde propio.
    t += (f"  \\draw[cpapel, line width=0.55pt] ({x:.3f},{y:.3f}) "
          f"circle ({r:.3f});\n")
    if resaltado:
        t += (f"  \\draw[ctinta, line width=0.9pt] ({x:.3f},{y:.3f}) "
              f"circle ({r + 0.045:.3f});\n")
    return t


def construir(L: dict, ajustes: bool = False):
    puntos, diag = cargar(L)
    # Los puntos que NO salen del calculador. Todo lo que el pie dice sobre
    # ellos —el párrafo, la entrada de leyenda del marcador hueco— se emite
    # sólo si existen. Antes iba cableado, y la revisión cruzada vio la trampa: el día que
    # `metrica_descanso.py` adjudique Estados Unidos, `cargar()` lo tomaría por
    # la rama medida y el pie seguiría jurando que va en cero con marcador
    # hueco. Un pie que afirma lo contrario de lo que dibuja, sin que nada falle.
    huecos = [p for p in puntos if not p["medido"]]
    faltan = diag["faltan"]
    rot = colocar(puntos, L)
    sin_rotulo = sorted(p["iso"] for p in puntos if rot.get(p["iso"]) is None)

    t = []
    a = t.append

    # --- rejilla, por debajo de todo ---
    for v in X_REJILLA:
        if X_MIN < v < X_MAX:
            a(f"  \\draw[crejilla, line width=0.3pt] ({px(v):.3f},0) -- "
              f"({px(v):.3f},{ALTO:.3f});")
    for v in Y_TICKS:
        a(f"  \\draw[crejilla, line width=0.3pt] (0,{py(v):.3f}) -- "
          f"({ANCHO:.3f},{py(v):.3f});")

    # --- ejes ---
    a(f"  \\draw[ceje, line width=0.5pt] (0,{py(Y_MIN):.3f}) -- "
      f"(0,{ALTO:.3f});")
    a(f"  \\draw[ceje, line width=0.5pt] (0,{py(0):.3f}) -- "
      f"({ANCHO:.3f},{py(0):.3f});")
    for v, etq in X_TICKS:
        a(f"  \\node[anchor=north, font=\\scriptsize, text=cmudo] at "
          f"({px(v):.3f},{py(Y_MIN) - 0.10:.3f}) {{{etq}}};")
    for v in Y_TICKS:
        a(f"  \\node[anchor=east, font=\\scriptsize, text=cmudo] at "
          f"(-0.14,{py(v):.3f}) {{{v}}};")

    # --- títulos de eje ---
    # NI UNA REFERENCIA A OTRA PARTE DEL INFORME, y la razón se demostró sola.
    # Puse aquí «no es mínimo exigible (§G.3)» siguiendo una sugerencia de
    # revisión, y diez minutos después otra sesión movió los anexos al cuerpo y
    # esa numeración dejó de existir. Una figura que apunta a un número de
    # sección envejece con la sección y viaja rota cuando la sacan del documento
    # — y sacarla es lo que siempre acaba pasando. Lo que haya que decir se dice
    # con palabras, en el pie, y en la menor cantidad posible.
    a(f"  \\node[anchor=south west, font=\\scriptsize\\bfseries, text=csec] at "
      f"(-0.55,{ALTO + 1.02:.3f}) "
      "{" + L["eje_y"] + "};")
    a(f"  \\node[anchor=north, font=\\scriptsize, text=csec] at "
      f"({ANCHO / 2:.3f},{py(Y_MIN) - 0.52:.3f}) "
      "{" + L["eje_x"] + "};")

    # --- rectas de ajuste, por debajo de los puntos ---
    # En tinta y distinguidas por trazo, no por color: los tres tonos ya están
    # gastados en la pertenencia, y una cuarta y quinta familia cromática
    # rompería la validación de daltonismo que pasó el trío.
    fits = []
    trazos = ["", "dash pattern=on 5pt off 2.5pt", "dash pattern=on 1.2pt off 2pt"]
    if ajustes:
        cuales = list(zip(AJUSTES, trazos))
    else:
        # La figura del cuerpo lleva UNA recta, la elegida, y en trazo continuo:
        # sin las otras dos al lado, el punteado sólo sugeriría provisionalidad.
        cuales = [(AJUSTES[AJUSTE_ELEGIDO], "")]
    for (nombre, detalle, peso, fuera), trazo in cuales:
        r = recta(puntos, peso, fuera)
        if r is None:
            continue
        aa, bb, r2, n = r
        fits.append((nombre, detalle, aa, bb, r2, n, trazo))
        x0, x1 = X_MIN * 1.02, X_MAX * 0.98
        y0, y1 = aa + bb * math.log10(x0), aa + bb * math.log10(x1)
        # Recorte al marco: una recta que se sale por arriba mentiría sobre
        # el rango en el que se ajustó.
        for _ in range(2):
            if y0 < Y_MIN or y0 > Y_MAX:
                yc = Y_MIN if y0 < Y_MIN else Y_MAX
                x0, y0 = 10 ** ((yc - aa) / bb), yc
            if y1 < Y_MIN or y1 > Y_MAX:
                yc = Y_MIN if y1 < Y_MIN else Y_MAX
                x1, y1 = 10 ** ((yc - aa) / bb), yc
        opts = "ctinta, line width=0.65pt, opacity=0.55"
        a(f"  \\draw[{opts}{', ' + trazo if trazo else ''}] "
          f"({px(x0):.3f},{py(y0):.3f}) -- ({px(x1):.3f},{py(y1):.3f});")

    # --- puntos ---
    for p in sorted(puntos, key=lambda q: (q["iso"] == "PER", q["medido"])):
        a(marcador(p, resaltado=(p["iso"] == "PER")))

    # --- rótulos ---
    for p in puntos:
        r_ = rot.get(p["iso"])
        if r_ is None:
            continue
        dx, dy, texto, lejos = r_
        x, y = px(p["x"]), py(p["y"])
        per = p["iso"] == "PER"
        anc = ("west" if dx > 0 else "east" if dx < 0 else
               "south" if dy > 0 else "north")
        # Tinta secundaria y no la de los ejes: estos rótulos no son cromo, son
        # la identidad de cada punto — y son además la mitigación que el
        # validador exige por el verde, que queda bajo 3:1 contra el papel.
        col = "ctinta" if per else "csec"
        peso = r"\bfseries" if per else ""
        if lejos:
            rr = R_PER if per else R
            ux, uy = (dx, dy)
            n = math.hypot(ux, uy) or 1
            a(f"  \\draw[cmudo, line width=0.3pt] "
              f"({x + ux / n * (rr + 0.03):.3f},{y + uy / n * (rr + 0.03):.3f}) -- "
              f"({x + dx * 0.86:.3f},{y + dy * 0.86:.3f});")
        # Fondo del color del papel bajo cada código. Sin él, una línea de
        # rejilla o una recta de ajuste cruza el texto y lo cambia: con las
        # rectas puestas, «ITA» se leía «LTA» y «IRL» se leía «IBL». Un rótulo
        # que el propio dibujo corrompe es peor que uno ausente, porque el
        # lector no sabe que está leyendo mal.
        a(f"  \\node[anchor={anc}, font=\\tiny{peso}, text={col}, "
          f"fill=cpapel, inner sep=0.7pt, outer sep=0pt] at "
          f"({x + dx:.3f},{y + dy:.3f}) {{{esc(texto)}}};")

    # --- leyenda ---
    # En su propia línea y maquetada por LaTeX. La primera versión calculaba el
    # ancho de cada rótulo a mano —tantos caracteres por tantos centímetros— y
    # los cuatro elementos se montaron unos sobre otros. Medir tipografía a ojo
    # es la misma clase de error que el proyecto persigue en los datos: aquí la
    # medida la hace quien sabe, que es el compositor.
    rp = f"{R * 28.4526:.2f}pt"           # el mismo radio, en unidades de texto

    def bolita(izq, der=None):
        if der is None:
            return (r"\tikz[baseline=-0.55ex]\fill[c" + izq.lower()
                    + r"] (0,0) circle (" + rp + r");")
        return (r"\tikz[baseline=-0.55ex]{\fill[c" + izq.lower()
                + r"] (0,0) ++(90:" + rp + r") arc[start angle=90, "
                r"end angle=270, radius=" + rp + r"] -- cycle;"
                r"\fill[c" + der.lower() + r"] (0,0) ++(270:" + rp
                + r") arc[start angle=270, end angle=450, radius=" + rp
                + r"] -- cycle;}")

    sep = r"\hspace{0.62cm}"
    piezas_ley = [
        bolita(C_IBE) + r"\, " + L["ibe"],
        bolita(C_OCDE) + r"\, " + L["ocde"],
        bolita(C_ADH) + r"\, " + L["adh"],
        # El cuarto enseña la codificación: mitad y mitad = dos componentes. El
        # «p. ej.» lo pidió la revisión cruzada y tiene razón: la muestra sólo puede enseñar
        # una de las dos combinaciones que existen, y sin la abreviatura alguien
        # puede leer naranja-y-verde como una categoría propia.
        bolita(C_IBE, C_ADH) + r"\, " + L["dos"],
    ]
    if huecos:
        # Dos rótulos descartados y por qué, que la lección sirve para el
        # siguiente: «cero verificado» sobreafirmaba —no hay fila de evidencia
        # detrás de ese cero—, y «cero adjudicado, pendiente en el calculador»
        # lo arreglaba metiendo fontanería del repositorio en una figura
        # publicable: al lector no le dice nada que aquí exista un calculador.
        # Lo que es cierto y además le importa es que no hay mandato legal.
        piezas_ley.append(
            r"\tikz[baseline=-0.55ex]\draw[c" + C_OCDE.lower()
            + r", line width=0.9pt] (0,0) circle (" + rp
            + r");\, " + L["sin_mandato"])
    leyenda = sep.join(piezas_ley)
    a(f"  \\node[anchor=south west, font=\\scriptsize, text=csec] at "
      f"(-0.55,{ALTO + 0.40:.3f}) {{{leyenda}}};")

    # --- leyenda de las rectas, sólo en la variante ---
    if fits:
        piezas = []
        for nombre, detalle, aa, bb, r2, n, trazo in fits:
            op = ("ctinta, line width=0.65pt, opacity=0.55"
                  + (", " + trazo if trazo else ""))
            piezas.append(
                r"\tikz[baseline=-0.05em]\draw[" + op
                + r"] (0,0) -- (0.62,0);\, " + (nombre or L["ajuste"])
                + r" \textcolor{cmudo}{("
                + (L["fit_stats"] % (n, f"{bb:+.1f}".replace(".", L["decimal"]),
                                     f"{r2:.2f}".replace(".", L["decimal"])))
                + r")}")
        a(f"  \\node[anchor=north west, font=\\scriptsize, text=csec, "
          f"align=left] at (-0.55,{py(Y_MIN) - 1.02:.3f}) "
          f"{{{r' \\ '.join(piezas)}}};")

    # --- pie ---
    # BREVE Y AUTOCONTENIDO, por instruccion del principal, y las dos cosas
    # tiran en direcciones opuestas: hay que decir lo justo para que la imagen
    # no afirme de mas, y nada mas. Reglas que salieron de ese encargo:
    # sin referencias a secciones del informe —envejecen y viajan rotas—, sin
    # vocabulario interno del proyecto, y nada cableado: si el calculador cambia,
    # el pie cambia con el.
    filas = M.filas_de(CORTE)
    n_iv = sum(1 for f in filas if f["lo"] != f["hi"])
    pie = L["cabecera"] % (len(puntos), CORTE, n_iv)
    if faltan:
        # LAS AUSENCIAS SE NOMBRAN. Cada una con su razon, porque no son la misma
        # cosa: una es un hecho de la ley y la otra un hueco nuestro. Sale de
        # `ausentes()`, que aborta si aparece una unidad cuya razon nadie escribio.
        frases = ["\\textbf{%s}, %s" % (esc(n), r) for n, r in faltan]
        pie += (L["ausencias_pre"] + L["ausencias_sep"].join(frases)
                + L["ausencias_post_1" if len(faltan) == 1 else "ausencias_post_n"])
    if fits and len(fits) == 1:
        # CUANTO MUEVE LA EXCLUSION, calculado y no afirmado. La recta publicada
        # quita las dos unidades sin mandato, que son justo las dos que mas la
        # contradicen, y eso le sube la pendiente. Un lector que solo ve el
        # numero de la leyenda no tiene como saberlo, asi que el pie pone al lado
        # el del conjunto entero. Cablear cualquiera de los dos seria dejar el
        # pie mintiendo el dia que cambie el dato, que es lo que este archivo se
        # prohibe tres parrafos mas arriba.
        entera = recta(puntos)
        pie += L["recta"] % (
            len(puntos),
            f"{entera[1]:+.1f}".replace(".", L["decimal"]) if entera else "n/d",
            f"{fits[0][3]:+.1f}".replace(".", L["decimal"]))
    elif fits:
        pie += (
            r"\\[1pt] \textbf{Las tres rectas son para comparar, no para "
            r"publicarse juntas.} Ninguna afirma una relación: el ingreso no "
            r"explica el derecho. La ponderada cambia de signo por una sola "
            r"observación, Estados Unidos.")
    pie += L["cautela"] + L["fuentes"]
    if diag["perdidas"]:
        pie += (L["perdidas"]
                + ", ".join(diag["perdidas"]) + ".")
    if sin_rotulo:
        pie += r" \emph{Sin rótulo:} " + ", ".join(sin_rotulo) + "."
    y_pie = py(Y_MIN) - (1.10 + 0.44 * len(fits))
    a(f"  \\node[anchor=north west, align=left, text width={ANCHO + 1.5:.2f}cm, "
      f"font=\\scriptsize, text=csec, inner sep=0pt] at "
      f"(-1.5,{y_pie:.3f}) {{{pie}}};")

    cuerpo = "\n".join(t)
    return DOC.replace("%%CUERPO%%", cuerpo), puntos, sin_rotulo, fits, diag


DOC = r"""\documentclass[tikz,border=6pt]{standalone}
\usepackage{fontspec}
\setmainfont{Helvetica}
\usepackage{tikz}
\definecolor{c""" + C_IBE.lower() + r"""}{HTML}{""" + C_IBE + r"""}
\definecolor{c""" + C_OCDE.lower() + r"""}{HTML}{""" + C_OCDE + r"""}
\definecolor{c""" + C_ADH.lower() + r"""}{HTML}{""" + C_ADH + r"""}
\definecolor{ctinta}{HTML}{""" + TINTA + r"""}
\definecolor{csec}{HTML}{""" + SEC + r"""}
\definecolor{cmudo}{HTML}{""" + MUDO + r"""}
\definecolor{crejilla}{HTML}{""" + REJILLA + r"""}
\definecolor{ceje}{HTML}{""" + EJE + r"""}
\definecolor{cpapel}{HTML}{""" + PAPEL + r"""}
\begin{document}
\begin{tikzpicture}
%%CUERPO%%
\end{tikzpicture}
\end{document}
"""


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ajustes", action="store_true",
                    help="variante con las tres rectas, en su propio archivo")
    ap.add_argument("--idioma", choices=sorted(IDIOMAS) + ["ambos"],
                    default="ambos", help="por defecto emite los dos")
    args = ap.parse_args()

    # LOS DOS IDIOMAS POR DEFECTO, Y NO UNA BANDERA QUE HAYA QUE ACORDARSE DE
    # PASAR. Si emitir el ingles fuera opcional, el dia que alguien regenere la
    # figura tras cambiar el dato dejaria la inglesa vieja al lado de la nueva —
    # y una figura desfasada en el otro idioma no la ve nadie hasta el PDF.
    codigos = sorted(IDIOMAS) if args.idioma == "ambos" else [args.idioma]
    salida = 0
    for cod in codigos:
        L = IDIOMAS[cod]
        # Archivo propio por variante, y no una bandera que reescriba el mismo
        # PDF: cambiar una figura debajo de quien la revisa invalida la revision
        # sin que nadie se entere.
        # LA VARIANTE DE INSPECCION NO ESCRIBE EN `figuras/`. El manifiesto
        # publicable se DERIVA de ese directorio, asi que cualquier archivo que
        # se deje ahi o se publica o rompe la compuerta C4. La variante de las
        # tres rectas no es publicable —el principal decidio que no van las
        # tres— y aun asi rompio C4 dos veces: la primera al crearla, la segunda
        # al borrarla, porque el manifiesto ya la prometia.
        #
        # `figuras/` no es un espacio de pruebas. Lo que se inspecciona va a
        # `figuras-inspeccion/`, que ningun manifiesto mira.
        if args.ajustes:
            destino = SALIDA.parent / "figuras-inspeccion"
            nombre = f"figura-dispersion-ppp-ajustes-{cod}"
        else:
            destino = SALIDA
            nombre = f"figura-dispersion-ppp-{cod}"
        tex, puntos, sin_rotulo, fits, diag = construir(L, args.ajustes)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "fig.tex"
            f.write_text(tex, encoding="utf-8")
            r = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", f.name],
                cwd=d, capture_output=True, text=True)
            pdf = Path(d) / "fig.pdf"
            if not pdf.exists():
                err = [l for l in r.stdout.splitlines() if l.startswith("!")][:6]
                raise SystemExit("xelatex fallo (%s):\n%s" % (cod, "\n".join(err)))
            destino.mkdir(exist_ok=True)
            shutil.copy(pdf, destino / f"{nombre}.pdf")
            c = subprocess.run(
                ["magick", "-density", "220", str(destino / f"{nombre}.pdf"),
                 "-background", "white", "-alpha", "remove",
                 str(destino / f"{nombre}.png")], capture_output=True)
            if c.returncode != 0:
                raise SystemExit("magick fallo: " + c.stderr.decode()[:400])

        print("figura escrita:", destino / f"{nombre}.pdf")
        print("  unidades dibujadas: %d  (%d del calculador, %d fijadas aqui)"
              % (len(puntos), sum(1 for p in puntos if p["medido"]),
                 sum(1 for p in puntos if not p["medido"])))
        if sin_rotulo:
            print("  sin rotulo por falta de sitio: " + ", ".join(sin_rotulo))
        for nom, det, aa, bb, r2, n, _ in fits:
            print("  ajuste %-22s n=%2d  pendiente %+6.2f  R2=%.3f  (%s)"
                  % (nom or L["ajuste"], n, bb, r2, det))
        huecos = [p["iso"] for p in puntos if not p["medido"]]
        if huecos:
            print("  AVISO: %s no sale%s del calculador (%d filas); su valor lo "
                  "fija esta figura y hay que declararlo"
                  % (", ".join(huecos), "" if len(huecos) == 1 else "n",
                     diag["filas_metrica"]))
        if diag["perdidas"]:
            print("  AVISO: el calculador emite %s y la figura no las dibuja por "
                  "falta de serie de ingreso" % ", ".join(diag["perdidas"]))
    return salida


if __name__ == "__main__":
    raise SystemExit(main())
