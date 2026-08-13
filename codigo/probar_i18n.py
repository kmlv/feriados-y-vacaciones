"""Comprueba que el juego de cadenas ingles cuadre con el castellano.

POR QUE ES MECANICO Y NO A OJO. Son ciento y pico cadenas con interpolaciones, y
una que falte revienta la compilacion mientras que una de mas o en otro orden
formatea mal SIN reventar — que es peor. Revisarlo leyendo es exactamente donde
se pierde uno.

Y EL CATALOGO PUEDE MENTIR SOBRE SI MISMO. La primera version del extractor usaba
`%[-\\d.]*[sdgf%]`, que NO coge la bandera de signo `%+d`: el campo
`interpolaciones` de `describe_fecha.02` declaraba dos donde hay tres, asi que una
traduccion que perdiera la tercera habria pasado la validacion. Lo encontro
la revisión de plantillas escribiendo su propio extractor a proposito distinto y
comparando clave por clave — con la misma expresion, los dos habriamos dicho que
estaba bien. Por eso esta suite **no confia en el campo declarado**: lo recalcula
del texto y de paso comprueba que el catalogo se describa bien a si mismo.

Uso:  python3 scripts/probar_i18n.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
I18N = REPO / "plantillas/i18n"
INTERP = re.compile(r"%[-+ #0]*\d*(?:\.\d+)?[sdgfeEG%]")

fallos: list[str] = []


def ok(cond, etiqueta, detalle=""):
    print("  %-6s %s%s" % ("OK" if cond else "FALLA", etiqueta,
                           "" if cond else "\n            " + detalle))
    if not cond:
        fallos.append(etiqueta)


def main() -> int:
    es = json.loads((I18N / "cadenas-es.json").read_text(encoding="utf-8"))
    ruta_en = I18N / "cadenas-en.json"
    if not ruta_en.exists():
        print("  AVISO  no hay juego ingles todavia; nada que cotejar")
        return 0
    en = json.loads(ruta_en.read_text(encoding="utf-8"))
    ces, cen = es["cadenas"], en["cadenas"]

    print("COTEJO DE LOS JUEGOS DE CADENAS\n")

    # 1 · EL CATALOGO CONTRA SI MISMO, antes que nada. Si el campo declarado no
    #     coincide con lo que la cadena tiene, todo lo que venga despues estaria
    #     comprobando contra una declaracion falsa.
    mentira = [k for k, v in ces.items()
               if INTERP.findall(v["es"]) != v.get("interpolaciones")]
    ok(not mentira, "el catalogo declara sus propias interpolaciones sin error",
       "mal declaradas: %s" % ", ".join(mentira[:6]))

    # 2 · Mismas claves, en los dos sentidos.
    faltan, sobran = sorted(set(ces) - set(cen)), sorted(set(cen) - set(ces))
    ok(not faltan and not sobran, "las claves coinciden en los dos juegos",
       "faltan en el ingles: %s · sobran: %s"
       % (", ".join(faltan[:5]) or "—", ", ".join(sobran[:5]) or "—"))

    # 3 · Interpolaciones: mismo juego Y MISMO ORDEN. El orden importa porque
    #     `%s` y `%d` no son intercambiables y el formateo es posicional.
    malas = []
    for k in sorted(set(ces) & set(cen)):
        t = str(cen.get(k) or "").strip()
        if not t:
            continue                      # vacias declaradas: se revisan aparte
        a, b = INTERP.findall(ces[k]["es"]), INTERP.findall(t)
        if a != b:
            malas.append("%s: es=%s en=%s" % (k, a, b))
    ok(not malas, "cada traduccion conserva sus interpolaciones y su orden",
       "; ".join(malas[:4]))

    # 4 · Las vacias tienen que estar DECLARADAS con su razon. Una traduccion
    #     que falta y una que se decidio no hacer se ven igual en el archivo, y
    #     esa es justo la diferencia que hay que poder leer.
    # Las razones viven en un bloque aparte y no campo por campo. Es la forma
    # que eligio la revisión de plantillas y es mejor: agrupa por MOTIVO, asi que se lee
    # «estas seis y por estas dos razones» en vez de seis notas sueltas.
    declaradas = set()
    for grupo in (en.get("_sin_traducir_a_proposito") or {}).values():
        if isinstance(grupo, dict):
            declaradas.update(grupo.get("claves") or [])
    vacias = sorted(k for k in cen if not str(cen.get(k) or "").strip())
    sin_razon = [k for k in vacias if k not in declaradas]
    ok(not sin_razon,
       "las %d cadenas sin traducir declaran por que" % len(vacias),
       "sin razon escrita: %s" % ", ".join(sin_razon[:6]))

    # 5 · El formateo tiene que EJECUTARSE, no solo parecerse. Una cadena que
    #     declara `%d` y recibe texto revienta en compilacion, no aqui.
    def cebo(spec):
        return 1 if spec[-1] in "dgfeEG" else "x"
    revientan = []
    for k in sorted(set(ces) & set(cen)):
        t = str(cen.get(k) or "").strip()
        if not t:
            continue
        args = tuple(cebo(s) for s in INTERP.findall(t) if s != "%%")
        try:
            t % args
        except Exception as e:
            revientan.append("%s (%s)" % (k, type(e).__name__))
    ok(not revientan, "las traducciones aceptan los argumentos que declaran",
       "; ".join(revientan[:4]))

    print("\n%s" % ("Cadenas: los dos juegos cuadran."
                    if not fallos else "FALLAN %d: %s" % (len(fallos),
                                                          ", ".join(fallos))))
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
