"""Ataque al catalogo de reglas de fecha, y en particular a lo que anadio v2.20.

POR QUE EXISTE. Las cuatro decisiones de §35 tocaron la tabla que decide CUANDO
ocurre cada feriado: dos anclas nuevas, un dia lunar contado desde el fin del
mes, una clase de cuota y —la de fondo— varias reglas por feriado con condicion.
Un cambio de esa envergadura sin casos adversariales no es un cambio, es una
apuesta.

LO QUE MAS IMPORTA PROBAR, y por eso va primero: que **como maximo una regla por
defecto** por feriado. Ese invariante lo sostiene un indice unico PARCIAL y no un
UNIQUE de tabla, porque SQLite trata los NULL como distintos — un UNIQUE con la
condicion dentro habria dejado meter dos reglas sin condicion y el feriado
tendria dos fechas el mismo anio sin que nada lo notara. Es exactamente la clase
de fallo silencioso que este proyecto ya cometio tres veces con la logica de
tres valores.

Salida cero si todo se comporta como se declara.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DDL = REPO / "schema/draft/001_schema.sql"

fallos: list[str] = []
_id = [1000]


def base() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(DDL.read_text())
    con.execute("INSERT INTO jurisdicciones (jurisdiccion_id,iso3,nombre,nivel,padre_id,vigencia_desde,vigencia_hasta) VALUES (1,'XXX','Prueba','nacional',NULL,"
                "'2000-01-01',NULL)")
    con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (1,'feriado_version')")
    con.execute(
        "INSERT INTO feriado_version (feriado_version_id,feriado_id,jurisdiccion_id,"
        "sector,vigencia_desde,nombre_oficial,categoria,recurrencia,periodo_anios,"
        "regimen,duracion_dias,cobertura,elegibilidad) VALUES "
        "(1,1,1,'privado','2016-01-01','Prueba','descanso_pagado_obligatorio',"
        "'recurrente',1,'descanso_obligatorio',1,'todo_el_pais','todos')")
    con.commit()
    return con


def regla(con, **kw):
    """Inserta una regla de fecha. Devuelve la excepcion, o None si entro."""
    _id[0] += 1
    rid = _id[0]
    kw.setdefault("feriado_version_id", 1)
    kw.setdefault("vigencia_desde", "2016-01-01")
    kw.setdefault("sistema_calendarico", "gregoriano")
    cols = ["regla_fecha_version_id"] + list(kw)
    try:
        con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,'regla_fecha_version')",
                    (rid,))
        con.execute("INSERT INTO regla_fecha_version (%s) VALUES (%s)"
                    % (",".join(cols), ",".join("?" * len(cols))), [rid] + list(kw.values()))
        con.commit()
        return None
    except sqlite3.Error as e:
        con.rollback()
        return e


def rechaza(con, nombre, **kw):
    e = regla(con, **kw)
    if e is None:
        print("  FALLA  %-58s acepto el estado prohibido" % nombre)
        fallos.append(nombre)
    else:
        print("  OK     %-58s %s" % (nombre, str(e).split("\n")[0][:34]))


def acepta(con, nombre, **kw):
    e = regla(con, **kw)
    if e is None:
        print("  OK     %-58s" % nombre)
    else:
        print("  FALLA  %-58s %s" % (nombre, e))
        fallos.append(nombre)


FIJA = dict(clase_de_regla="fija", mes=1, dia=2)
LUNAR = dict(clase_de_regla="lunar", calendario_lunar="lunisolar_coreano", mes_lunar=12)

print("ADVERSARIAL · la regla por defecto es unica [v2.20]")
con = base()
acepta(con, "primera regla sin condicion", **FIJA)
rechaza(con, "SEGUNDA regla sin condicion para el mismo feriado",
        clase_de_regla="ordinal", ordinal=1, dia_semana=1, mes=2)
acepta(con, "una alternativa condicional junto a la de por defecto",
       clase_de_regla="fija", mes=2, dia=1,
       condicion_referencia="02-01", condicion_dia_semana=5)
rechaza(con, "dos alternativas con la MISMA condicion",
        clase_de_regla="fija", mes=3, dia=1,
        condicion_referencia="02-01", condicion_dia_semana=5)
acepta(con, "otra alternativa con condicion distinta",
       clase_de_regla="fija", mes=3, dia=1,
       condicion_referencia="propia", condicion_dia_semana=5)

print()
print("ADVERSARIAL · la condicion, entera o ninguna")
con = base()
rechaza(con, "dia de la semana sin decir que fecha se examina",
        condicion_dia_semana=5, **FIJA)
rechaza(con, "referencia sin dia de la semana",
        condicion_referencia="propia", **FIJA)
rechaza(con, "dia de la semana fuera de rango",
        condicion_referencia="propia", condicion_dia_semana=8, **FIJA)
rechaza(con, "referencia que no es ni `propia` ni una fecha",
        condicion_referencia="cuando toque", condicion_dia_semana=5, **FIJA)
acepta(con, "referencia a la regla por defecto",
       condicion_referencia="regla_por_defecto", condicion_dia_semana=6, **FIJA)

print()
print("ADVERSARIAL · dia lunar desde el fin del mes")
con = base()
acepta(con, "ultimo dia del mes lunar", dia_lunar_desde_fin=1, **LUNAR)
rechaza(con, "los DOS dias lunares a la vez: serian dos fechas",
        dia_lunar=30, dia_lunar_desde_fin=1,
        condicion_referencia="propia", condicion_dia_semana=1, **LUNAR)
rechaza(con, "clase lunar sin ninguno de los dos dias",
        condicion_referencia="propia", condicion_dia_semana=2, **LUNAR)
rechaza(con, "dia desde el fin en una regla que NO es lunar",
        clase_de_regla="fija", mes=1, dia=2, dia_lunar_desde_fin=1,
        condicion_referencia="propia", condicion_dia_semana=3)

print()
print("ADVERSARIAL · cuota designada por el empleador")
con = base()
rechaza(con, "cuota sin conjunto de referencia: no se puede auditar",
        clase_de_regla="cuota_designada_por_empleador")
acepta(con, "cuota con su conjunto",
       clase_de_regla="cuota_designada_por_empleador",
       conjunto_de_referencia="dias tradicionales de observancia reconocida")
rechaza(con, "conjunto de referencia en una clase que no es cuota",
        clase_de_regla="fija", mes=5, dia=1,
        conjunto_de_referencia="lo que sea",
        condicion_referencia="propia", condicion_dia_semana=4)

print()
print("ADVERSARIAL · las anclas nuevas, y las que no existen")
con = base()
acepta(con, "solsticio de junio", clase_de_regla="relativa",
       ancla="solsticio_junio", offset_dias=0)
acepta(con, "solsticio de diciembre", clase_de_regla="relativa",
       ancla="solsticio_diciembre", offset_dias=0,
       condicion_referencia="propia", condicion_dia_semana=1)
rechaza(con, "ancla inventada", clase_de_regla="relativa",
        ancla="solsticio_de_marte", offset_dias=0,
        condicion_referencia="propia", condicion_dia_semana=2)

print()
if fallos:
    print("FALLA la suite:")
    for f in fallos:
        print("  - %s" % f)
    sys.exit(1)
print("Catalogo de reglas de fecha: todo se comporta como se declara.")
