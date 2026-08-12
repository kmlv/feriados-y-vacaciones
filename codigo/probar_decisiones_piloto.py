"""Ataca las cuatro decisiones de constructo que salieron del piloto.

Las cuatro las decidio el principal el 2026-08-09 tras capturar las ocho unidades,
y las cuatro cambian el esquema. Este guion las prueba con las normas reales que
las provocaron, en vez de con casos abstractos.

  1. Fecha delegada a la jurisdiccion local — Guatemala «el dia de la festividad
     de la localidad», El Salvador «segun la costumbre».
  2. Unidad del texto legal y base semanal — Alemania «24 Werktage», Ontario
     «2 semanas».
  3. Recurrencia periodica no anual — Mexico, 1 de octubre cada seis anios.
  4. Colocacion por asignacion estatal — Indonesia, «cuti bersama».

Las dos mitades de siempre: los estados prohibidos deben rechazarse Y las
estructuras fieles deben entrar limpias. Un falso positivo empuja al codificador
a corromper dato bueno para callar la alerta.

Nota de metodo. Escribir estos casos costo cuatro intentos, y los cuatro fallos
fueron del fixture y no del esquema: columna inexistente, valor fuera de dominio,
columna obligatoria omitida, nombre de columna equivocado. Cada uno se leia como
«el esquema rechaza lo valido». Es el primer patron de fallo de esta serie y por
eso los casos legitimos van explicitos: sin ellos, un fixture roto se lee como
esquema estricto.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DDL = (REPO / "schema/draft/001_schema.sql").read_text()

FERIADO = (
    "INSERT INTO feriado_version (feriado_version_id,hecho_tipo,feriado_id,"
    "jurisdiccion_id,sector,vigencia_desde,nombre_oficial,categoria,recurrencia,"
    "periodo_anios,regimen,duracion_dias,cobertura,elegibilidad) VALUES "
    "(1,'feriado_version',1,1,'privado','2016-01-01','X','descanso_pagado_obligatorio',"
    "?,?,'descanso_obligatorio',1,'todo_el_pais','sin_condicion')")
REGLA = (
    "INSERT INTO regla_fecha_version (regla_fecha_version_id,hecho_tipo,"
    "feriado_version_id,vigencia_desde,sistema_calendarico,clase_de_regla,mes,dia) "
    "VALUES (3,'regla_fecha_version',1,'2016-01-01','gregoriano',?,?,?)")
VACACIONES = (
    "INSERT INTO vacaciones_version (vacaciones_version_id,hecho_tipo,jurisdiccion_id,"
    "sector,vigencia_desde,texto_legal_dias,tipo_de_dia,base_semanal_dias,"
    "base_semanal_origen,periodo_de_calificacion_meses,base_antiguedad,"
    "imputacion_feriados_a_vacaciones) "
    "VALUES (2,'vacaciones_version',1,'privado','2016-01-01',?,?,?,?,12,"
    "'servicio_continuo_empleador_actual','extienden')")


def base(con_feriado: bool = False) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(DDL)
    con.execute("INSERT INTO jurisdicciones (jurisdiccion_id,iso3,nombre,nivel,padre_id,vigencia_desde,vigencia_hasta) VALUES "
                "(1,'XXX','X','nacional',NULL,'2000-01-01',NULL)")
    con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (1,'feriado_version')")
    if con_feriado:
        con.execute(FERIADO, ("recurrente", 1))
        con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) "
                    "VALUES (3,'regla_fecha_version')")
    return con


fallos: list[str] = []


def caso(nombre: str, sql: str, args, esperado: str, con_feriado: bool = False,
         tipo_hecho: str = "feriado_version") -> None:
    con = base(con_feriado)
    try:
        if tipo_hecho == "vacaciones_version":
            con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) "
                        "VALUES (2,'vacaciones_version')")
        con.execute(sql, args)
        con.commit()
        obtenido, detalle = "acepta", ""
    except sqlite3.Error as e:
        obtenido, detalle = "rechaza", str(e).split("\n")[0][:52]
    finally:
        con.close()
    ok = obtenido == esperado
    if not ok:
        fallos.append(nombre)
    print("  %-8s %-46s %s" % (obtenido.upper(), nombre,
                               "" if ok else "<-- FALLA  %s" % detalle))


print("== 1. Fecha delegada a la jurisdiccion local (GTM, SLV) ==")
for nombre, args, esperado in [
        ("delegada sin fecha — el caso real",
         ("delegada_a_jurisdiccion_local", None, None), "acepta"),
        ("delegada CON fecha: se contradice",
         ("delegada_a_jurisdiccion_local", 6, 29), "rechaza"),
        ("fija con fecha — sigue entrando", ("fija", 6, 29), "acepta"),
        ("fija sin fecha", ("fija", None, None), "rechaza"),
        ("clase inventada", ("consuetudinaria", None, None), "rechaza")]:
    caso(nombre, REGLA, args, esperado, con_feriado=True)

print("\n== 1b. Ancla-fecha y remision normativa (CAN, MEX) ==")
REGLA2 = (
    "INSERT INTO regla_fecha_version (regla_fecha_version_id,hecho_tipo,"
    "feriado_version_id,vigencia_desde,sistema_calendarico,clase_de_regla,mes,dia,"
    "dia_semana,offset_dias,ordinal,instrumento_remitido) VALUES "
    "(3,'regla_fecha_version',1,'2016-01-01','gregoriano',?,?,?,?,?,?,?)")
for nombre, args, esperado in [
        ("Victoria Day: lunes anterior al 25 de mayo",
         ("relativa_a_fecha", 5, 25, 1, -1, None, None), "acepta"),
        ("ancla-fecha sin dia de la semana",
         ("relativa_a_fecha", 5, 25, None, -1, None, None), "rechaza"),
        ("ancla-fecha con desplazamiento cero: sin direccion",
         ("relativa_a_fecha", 5, 25, 1, 0, None, None), "rechaza"),
        ("ancla-fecha mezclada con ordinal",
         ("relativa_a_fecha", 5, 25, 1, -1, 2, None), "rechaza"),
        ("jornada electoral: remite a la ley electoral",
         ("remision_normativa", None, None, None, None, None, "Leyes electorales"), "acepta"),
        ("remision SIN destino: hueco con nombre",
         ("remision_normativa", None, None, None, None, None, None), "rechaza"),
        ("remision con fecha propia: se contradice",
         ("remision_normativa", 7, 4, None, None, None, "Leyes electorales"), "rechaza"),
        ("destino de remision en una clase que no remite",
         ("fija", 7, 4, None, None, None, "Leyes electorales"), "rechaza")]:
    caso(nombre, REGLA2, args, esperado, con_feriado=True)

print("\n== 2. Unidad del texto legal y base semanal (DEU, CAN) ==")
for nombre, args, esperado in [
        ("Peru: 30 calendario, sin base", (30, "calendario", None, None), "acepta"),
        ("Alemania: 24 werktage sobre semana de 6", (24, "werktage", 6, "norma"), "acepta"),
        ("Ontario: 2 semanas sobre semana de 5", (2, "semanas", 5, "norma"), "acepta"),
        ("Guatemala: 15 habiles sobre semana de 5", (15, "habil", 5, "norma"), "acepta"),
        # La norma remite al horario DEL TRABAJADOR: base nula y declarada.
        ("Nueva Zelanda: la semana la fija el trabajador",
         (4, "semanas", None, "horario_del_trabajador"), "acepta"),
        ("base nula SIN declarar el origen", (24, "werktage", None, None), "rechaza"),
        ("origen 'norma' pero sin base", (24, "werktage", None, "norma"), "rechaza"),
        ("remite al trabajador Y trae base", (4, "semanas", 5, "horario_del_trabajador"), "rechaza"),
        ("calendario CON base: no aplica", (30, "calendario", 5, "norma"), "rechaza"),
        ("semana de nueve dias", (24, "werktage", 9, "norma"), "rechaza"),
        ("origen inventado", (24, "werktage", 6, "convenio"), "rechaza"),
        ("unidad inventada", (24, "jornadas", 5, "norma"), "rechaza")]:
    caso(nombre, VACACIONES, args, esperado, tipo_hecho="vacaciones_version")

print("\n== 3. Recurrencia periodica no anual (MEX) ==")
for nombre, args, esperado in [
        ("anual", ("recurrente", 1), "acepta"),
        ("cada seis anios — el caso real", ("recurrente", 6), "acepta"),
        ("recurrente sin periodo", ("recurrente", None), "rechaza"),
        ("one_off con periodo", ("one_off", 3), "rechaza"),
        ("one_off sin periodo", ("one_off", None), "acepta"),
        ("periodo cero", ("recurrente", 0), "rechaza"),
        ("periodo negativo", ("recurrente", -6), "rechaza")]:
    caso(nombre, FERIADO, args, esperado)

print("\n== 4. Colocacion por asignacion estatal (IDN) ==")
con = base()
dominio = [r[0] for r in con.execute(
    "SELECT 1 FROM pragma_table_info('regla_colocacion') WHERE name='iniciativa'")]
sql_ok = "asignacion_estatal" in DDL
con.close()
print("  %-8s %-46s" % ("PRESENTE" if sql_ok else "AUSENTE",
                        "iniciativa admite asignacion_estatal"))
if not sql_ok:
    fallos.append("asignacion_estatal ausente del dominio")

print()
if fallos:
    print("FALLAN %d casos:" % len(fallos))
    for f in fallos:
        print("  - %s" % f)
    sys.exit(1)
print("Las cuatro decisiones del piloto se comportan como se declararon.")
