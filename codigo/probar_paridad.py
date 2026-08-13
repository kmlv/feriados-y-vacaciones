"""Paridad ESTRUCTURAL entre las dos lenguas de un documento sin marcas.

POR QUE ESTRUCTURAL Y NO TEXTUAL. Los titulos difieren entre idiomas por
definicion; las estructuras no pueden. Comparar el texto daria un falso positivo
en cada linea y una compuerta que falla siempre acaba aflojada hasta no
comprobar nada.

Y POR QUE ES OBLIGATORIA EN EL PROTOCOLO, que es el argumento de
la revisión de plantillas y el que la hace algo mas que higiene: el registro de
decisiones se CITA por numero. Si «§34.1» no resuelve a la misma regla en los dos
idiomas, las referencias dejan de ser citables — y entonces no hay un protocolo
en dos lenguas, hay dos protocolos.

Lo que compara:

  · el numero de encabezados y su NIVEL, en orden;
  · la numeracion de seccion que cada encabezado declara —«## 12.», «### 34.1»—,
    que es lo que una cita resuelve;
  · que ninguna seccion del original falte en la traduccion, y al reves.

Lo que NO compara: el texto de los titulos, la longitud, ni el cuerpo. Eso es
trabajo de un lector, no de una compuerta.

Uso:  python3 scripts/probar_paridad.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# (castellano, traduccion, etiqueta). Un par cuyo segundo archivo no exista
# todavia se informa y no falla: la traduccion en curso no es un defecto.
PARES = [
    (REPO / "docs/02-protocolo.md", REPO / "docs/02-protocol.md", "protocolo"),
    (REPO / "plantillas/D1-reporte-principal.md",
     REPO / "plantillas/D1-main-report.md", "D1"),
    (REPO / "plantillas/hallazgos-es.md",
     REPO / "plantillas/hallazgos-en.md", "hallazgos"),
    (REPO / "plantillas/README-es.md",
     REPO / "plantillas/README-en.md", "README"),
]

ENCABEZADO = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
# La numeracion que una cita resuelve: «## 12. …», «### 34.1 …», «§34.1».
NUMERO = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")

fallos: list[str] = []


def perfil(ruta: Path):
    """(nivel, numero_declarado) por encabezado, en orden de aparicion."""
    out = []
    for h, texto in ENCABEZADO.findall(ruta.read_text(encoding="utf-8")):
        m = NUMERO.match(texto.strip())
        out.append((len(h), m.group(1) if m else None))
    return out


def marcas(ruta: Path) -> list[str]:
    return re.findall(r"\{\{q:([a-z0-9_]+)\}\}", ruta.read_text(encoding="utf-8"))


def main() -> int:
    print("PARIDAD ESTRUCTURAL ENTRE IDIOMAS\n")
    for es, en, etiqueta in PARES:
        if not en.exists():
            print("  ...     %-11s no hay traduccion todavia; nada que cotejar"
                  % etiqueta)
            continue
        pe, pt = perfil(es), perfil(en)
        problemas = []
        if len(pe) != len(pt):
            problemas.append("%d encabezados contra %d" % (len(pe), len(pt)))
        # LA NUMERACION, que es lo que una cita resuelve. Se compara la SECUENCIA
        # y no el conjunto: dos documentos pueden tener las mismas secciones en
        # otro orden y entonces «§34.1» sigue resolviendo a reglas distintas.
        ne = [n for _, n in pe if n]
        nt = [n for _, n in pt if n]
        if ne != nt:
            faltan = [n for n in ne if n not in nt]
            sobran = [n for n in nt if n not in ne]
            if faltan:
                problemas.append("secciones sin traducir: %s"
                                 % ", ".join(faltan[:8]))
            if sobran:
                problemas.append("secciones que no existen en el original: %s"
                                 % ", ".join(sobran[:8]))
            if not faltan and not sobran:
                problemas.append("mismas secciones en distinto ORDEN")
        # Los niveles, para que «§3» no sea capitulo en una lengua y apartado en
        # la otra.
        if len(pe) == len(pt) and [n for n, _ in pe] != [n for n, _ in pt]:
            problemas.append("el nivel de algun encabezado no coincide")
        # Las marcas, donde las haya: mismo conjunto Y mismos usos. Un conteo
        # distinto pasa la comprobacion de conjunto sin que nadie se entere, y
        # esa fue observacion de la revisión de plantillas.
        me, mt = marcas(es), marcas(en)
        if sorted(me) != sorted(mt):
            problemas.append("las marcas difieren: faltan %s, sobran %s"
                             % (sorted(set(me) - set(mt))[:4] or "—",
                                sorted(set(mt) - set(me))[:4] or "—"))
        # TRADUCCION EN CURSO NO ES DIVERGENCIA, y distinguirlo importa: una
        # compuerta que denuncia el trabajo en vuelo se aprende a ignorar, y
        # entonces no avisa el dia que la divergencia sea real. Es «en curso» si
        # todo lo traducido coincide con el original y lo unico que falta es la
        # COLA — o sea, la traduccion es un prefijo fiel.
        en_curso = ne[:len(nt)] == nt and len(nt) < len(ne)
        if en_curso:
            print("  ...     %-11s traduccion en curso: %d de %d secciones, "
                  "y las %d hechas coinciden una a una"
                  % (etiqueta, len(nt), len(ne), len(nt)))
        elif problemas:
            print("  FALLA   %-11s %s" % (etiqueta, "; ".join(problemas)))
            fallos.append(etiqueta)
        else:
            print("  OK      %-11s %d encabezados, %d secciones numeradas, "
                  "%d marcas" % (etiqueta, len(pe), len(ne), len(me)))

    print("\n%s" % ("Paridad: las estructuras coinciden."
                    if not fallos else "FALLAN %d: %s"
                    % (len(fallos), ", ".join(fallos))))
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
