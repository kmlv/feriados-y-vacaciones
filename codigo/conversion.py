"""La conversion de vacaciones a semanas de derecho. UNA SOLA VEZ, y aqui.

POR QUE EXISTE ESTE MODULO. La misma conversion estaba escrita dos veces: en
Python dentro de la metrica y en SQL dentro del exportador. Las dos versiones
divergieron, y no en un caso de borde:

    Colombia   15 dias habiles sobre semana legal de 6   ->  informe 12,5   CSV 15,0
    Tailandia   6 dias habiles sobre semana legal de 6   ->  informe  5,0   CSV  6,0

El SQL cableaba una base de CINCO para `habil` y una de SEIS para `werktage`,
cuando las dos etiquetas describen la misma situacion —un dia de trabajo segun
la norma— y las dos tienen que leer `base_semanal_dias`. Alemania convertia y
Colombia no, siendo el mismo caso.

**Dos salidas nuestras decian cosas distintas del mismo pais**, que es
exactamente el defecto que este paquete existe para impedir y que le reprocha al
antecedente. Lo encontro una evaluacion externa del paquete ya publicado.

El arreglo no es corregir el SQL: es que no haya dos sitios. Esta funcion la usan
la metrica y el exportador, y `probar_metrica.py` comprueba que el CSV publicado
sea exactamente lo que ella devuelve, fila por fila.
"""

from __future__ import annotations

# Cuando la norma no declara los dias ordinarios de la semana. No es una medida:
# es una convencion nuestra, y por eso el CSV publica aparte de que base salio
# cada fila — quien lea el numero convertido tiene que poder distinguir una base
# leida de la norma de una puesta por nosotros.
BASE_POR_DEFECTO = 5


def semanas_de_derecho(dias: float, tipo: str, base_norma) -> float:
    """Vacaciones en SEMANAS de derecho, que es la magnitud sin parametro libre.

    Treinta dias corridos son treinta septimos de semana se trabaje lo que se
    trabaje. La semana solo entra cuando la norma cuenta en dias DE TRABAJO
    —`habil` y `werktage`—, y entonces entra la que la norma declara.
    """
    d = float(dias)
    if tipo == "calendario":
        return d / 7.0
    if tipo == "semanas":
        return d
    if tipo in ("habil", "werktage"):
        return d / float(base_norma or BASE_POR_DEFECTO)
    raise ValueError("tipo de dia desconocido: %r" % (tipo,))


def dias_en_semana_de_cinco(dias: float, tipo: str, base_norma) -> float:
    """La cifra comparable del CSV: semanas de derecho sobre una semana de cinco."""
    return round(semanas_de_derecho(dias, tipo, base_norma) * 5.0, 1)
