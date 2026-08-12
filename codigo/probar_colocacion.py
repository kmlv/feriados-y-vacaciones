#!/usr/bin/env python3
"""Suite adversarial de las reglas de colocacion y del vinculo lote -> protocolo.

Carga el DDL en una base desechable, intenta estados que el protocolo prohibe y
corre las validaciones. Dos mitades, y ninguna basta sola:

  · ADVERSARIAL — cada caso DEBE producir la violacion esperada.
  · FIDELIDAD   — cada estructura legitima DEBE entrar sin ninguna violacion de
                  colocacion. Un falso positivo es tan grave como un falso
                  negativo: empuja a corromper dato bueno para callar la alerta.

Uso:  python3 scripts/probar_colocacion.py
"""
import re
import sqlite3
import sys

ESQUEMA = 'schema/draft/001_schema.sql'
VALIDACIONES = 'schema/draft/900_validaciones.sql'

# Validaciones de colocacion. El resto (V1, V6, V7...) reporta huecos del
# fixture minimo, no del caso, y se ignora deliberadamente.
COLOC = {'V22', 'V23', 'V23b', 'V24', 'V25', 'V26', 'V26b', 'V27', 'V28', 'V30',
         'V31', 'V32', 'V33', 'V34', 'V35', 'V36', 'V37'}

HASH_A = 'a' * 64
HASH_B = 'b' * 64


def base(dias=20, tipo='habil'):
    con = sqlite3.connect(':memory:')
    con.executescript(open(ESQUEMA, encoding='utf-8').read())
    con.execute('PRAGMA foreign_keys = ON')
    con.execute("INSERT INTO jurisdicciones (jurisdiccion_id,iso3,nombre,nivel,padre_id,vigencia_desde,vigencia_hasta) VALUES (1,'XXX','X','nacional',NULL,'2000-01-01',NULL)")
    con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (100,'vacaciones_version')")
    con.execute(
        "INSERT INTO vacaciones_version (vacaciones_version_id,jurisdiccion_id,sector,"
        "vigencia_desde,texto_legal_dias,tipo_de_dia,base_semanal_dias,"
        "base_semanal_origen,"
        "periodo_de_calificacion_meses,"
        "base_antiguedad,imputacion_feriados_a_vacaciones) VALUES "
        "(100,1,'privado','2016-01-01',?,?,?,?,12,'servicio_continuo_empleador_actual','extienden')",
        # La base semanal se exige cuando la unidad se define contra la semana.
        # `base_semanal_origen` acompana a la base desde v2.17.
        (dias, tipo, None if tipo == 'calendario' else 5,
         None if tipo == 'calendario' else 'norma'))
    con.commit()
    return con


def regla(con, rid, **kw):
    kw.setdefault('vacaciones_version_id', 100)
    kw.setdefault('instrumento', 'ley')
    kw.setdefault('iniciativa', 'negociada')
    # `resolucion_desacuerdo` es obligatorio cuando la iniciativa es negociada
    # desde v2.19, y prohibido en el resto. El ayudante lo pone solo para que
    # cada caso siga hablando de lo suyo; los casos que prueban ESA restriccion
    # lo pasan explicito.
    if kw['iniciativa'] == 'negociada':
        kw.setdefault('resolucion_desacuerdo', 'sin_regla')
    kw.setdefault('literal_normativo', 'literal de prueba')
    con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?, 'regla_colocacion')", (rid,))
    cols = ['regla_colocacion_id'] + list(kw)
    con.execute('INSERT INTO regla_colocacion (%s) VALUES (%s)'
                % (','.join(cols), ','.join('?' * len(cols))), [rid] + list(kw.values()))
    con.commit()


def violaciones(con):
    texto = re.sub(r'--[^\n]*', '', open(VALIDACIONES, encoding='utf-8').read())
    vistas = []
    for stmt in texto.split(';'):
        if not stmt.strip() or stmt.strip().startswith('.'):
            continue
        try:
            for fila in con.execute(stmt):
                clave = str(fila[0]).split()[0]
                if clave in COLOC:
                    vistas.append(clave)
        except sqlite3.Error:
            continue
    return sorted(set(vistas))


fallos = []


def caso_adversarial(nombre, con, esperada):
    v = violaciones(con)
    ok = esperada in v
    print('  %s  %-62s %s' % ('OK   ' if ok else 'FALLA', nombre, ','.join(v) or '(ninguna)'))
    if not ok:
        fallos.append('%s: no reporto %s' % (nombre, esperada))


# Contado, no escrito a mano. El literal decia 'las cuatro estructuras fieles'
# cuando ya corrian seis: al agregar casos nadie actualiza la frase, y el resumen
# pasa a mentir sobre su propia cobertura. Es el mismo defecto que la cabecera
# del DDL declarando una version vieja del protocolo.
fieles = []


def caso_fiel(nombre, con):
    fieles.append(nombre)
    v = violaciones(con)
    print('  %s  %-62s %s' % ('OK   ' if not v else 'FALLA', nombre, ','.join(v) or '(limpia)'))
    if v:
        fallos.append('%s: falso positivo %s' % (nombre, ','.join(v)))


def rechaza(con, nombre, sql, args=()):
    try:
        con.execute(sql, args)
        con.commit()
        print('  FALLA  %-62s acepto el estado prohibido' % nombre)
        fallos.append(nombre)
    except sqlite3.Error as e:
        print('  OK     %-62s %s' % (nombre, str(e).split('\n')[0][:40]))


def acepta(con, nombre, sql, args=()):
    try:
        con.execute(sql, args)
        con.commit()
        print('  OK     %-62s' % nombre)
    except sqlite3.Error as e:
        print('  FALLA  %-62s %s' % (nombre, e))
        fallos.append(nombre)


print('ADVERSARIAL · vinculo lote -> protocolo')
con = base()
rechaza(con, 'lote con par inventado (banana + 64 zetas)',
        "INSERT INTO lote_captura (lote_id,etiqueta,version_protocolo,hash_protocolo,estado) "
        "VALUES (1,'L','banana',?, 'ciego')", ('z' * 64,))
rechaza(con, 'catalogo con hash no hexadecimal',
        "INSERT INTO protocolo_congelado VALUES ('v2.8',?, 'docs/archivo/02-protocolo-v2.8.md','2026-08-09T00:00:00Z')", ('z' * 64,))
rechaza(con, 'catalogo con version que no es version',
        "INSERT INTO protocolo_congelado VALUES ('banana',?, 'docs/archivo/02-protocolo-v2.8.md','2026-08-09T00:00:00Z')", (HASH_A,))
rechaza(con, 'catalogo con marca de tiempo imposible',
        "INSERT INTO protocolo_congelado VALUES ('v9.9',?, 'docs/archivo/02-protocolo-v2.8.md','2026-99-99T99:99:99Z')", (HASH_B,))
acepta(con, 'catalogo legitimo',
       "INSERT INTO protocolo_congelado VALUES ('v2.8',?, 'docs/archivo/02-protocolo-v2.8.md','2026-08-09T04:15:00Z')",
       (HASH_A,))
acepta(con, 'lote legitimo contra el catalogo',
       "INSERT INTO lote_captura (lote_id,etiqueta,version_protocolo,hash_protocolo,estado) "
       "VALUES (2,'L',   'v2.8',?, 'ciego')", (HASH_A,))
acepta(con, 'congelar', "UPDATE lote_captura SET estado='congelado',"
       " congelado_en='2026-08-09T05:00:00Z' WHERE lote_id=2")
acepta(con, 'cruzar', "UPDATE lote_captura SET estado='cruzado' WHERE lote_id=2")
rechaza(con, 'mutar el par del lote despues de cruzar',
        "UPDATE lote_captura SET version_protocolo='v9.9' WHERE lote_id=2")
rechaza(con, 'repuntar el archivo de una entrada congelada',
        "UPDATE protocolo_congelado SET archivo='docs/archivo/02-protocolo-v2.7.md' WHERE version='v2.8'")
rechaza(con, 'borrar una entrada de congelamiento',
        "DELETE FROM protocolo_congelado WHERE version='v2.8'")

print()
print('ADVERSARIAL · estructura y aritmetica de colocacion')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='fallback', grupo_fallback=7,
      es_raiz_fallback=1, alcance='residual')
caso_adversarial('fila fallback residual suelta acreditando cobertura', con, 'V33')

con = base()
for i, g in ((1, 1), (2, 1), (3, 2), (4, 2)):
    regla(con, i, orden_precedencia=i, modo_aplicacion='fallback', grupo_fallback=g,
          es_raiz_fallback=1 if i in (1, 3) else 0,
          condicion_fallback=None if i in (1, 3) else 'si_el_anterior_no_fija',
          alcance='todo_el_derecho')
regla(con, 5, orden_precedencia=5, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.5)
caso_adversarial('dos cascadas totales conviviendo con una particion', con, 'V24')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=1, alcance='porcion_definida', porcion_fraccion=0.6)
regla(con, 2, orden_precedencia=2, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=0, condicion_fallback='si_el_anterior_no_fija',
      alcance='porcion_definida', porcion_fraccion=0.6)
regla(con, 3, orden_precedencia=3, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.5)
regla(con, 4, orden_precedencia=4, modo_aplicacion='particion', alcance='residual')
caso_adversarial('cascada 0,6 + particion 0,5 + residual = 1,1 del derecho', con, 'V26')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=1, alcance='porcion_definida', porcion_dias=18, porcion_tipo_de_dia='habil')
regla(con, 2, orden_precedencia=2, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=0, condicion_fallback='si_el_anterior_no_fija',
      alcance='porcion_definida', porcion_dias=18, porcion_tipo_de_dia='habil')
regla(con, 3, orden_precedencia=3, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_dias=14, porcion_tipo_de_dia='habil')
regla(con, 4, orden_precedencia=4, modo_aplicacion='particion', alcance='residual')
caso_adversarial('cascada 18 dias + particion 14 dias sobre un derecho de 20', con, 'V26b')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=1, alcance='porcion_definida', porcion_dias=10, porcion_tipo_de_dia='habil')
regla(con, 2, orden_precedencia=2, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=0, condicion_fallback='si_el_anterior_no_fija',
      alcance='porcion_definida', porcion_dias=10, porcion_tipo_de_dia='habil')
regla(con, 3, orden_precedencia=3, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.5)
regla(con, 4, orden_precedencia=4, modo_aplicacion='particion', alcance='residual')
caso_adversarial('cascada en dias y particion en fraccion, misma version', con, 'V27')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.4)
for i, g in ((2, 1), (3, 1), (4, 2), (5, 2)):
    regla(con, i, orden_precedencia=i, modo_aplicacion='fallback', grupo_fallback=g,
          es_raiz_fallback=1 if i in (2, 4) else 0,
          condicion_fallback=None if i in (2, 4) else 'si_no_hay_acuerdo',
          alcance='residual')
caso_adversarial('dos cascadas residuales reclamando el mismo remanente', con, 'V25')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=1, alcance='residual')
regla(con, 2, orden_precedencia=2, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=0, condicion_fallback='si_el_anterior_no_fija', alcance='residual')
caso_adversarial('residual sin ninguna porcion contra la cual serlo', con, 'V37')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.5)
regla(con, 2, orden_precedencia=2, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.5)
regla(con, 3, orden_precedencia=3, modo_aplicacion='particion', alcance='residual')
caso_adversarial('residual vacio: las porciones ya suman el derecho entero', con, 'V23b')

con = base()
try:
    regla(con, 9, orden_precedencia=1, modo_aplicacion='particion',
          alcance='todo_el_derecho', condicion_fallback='si_no_hay_acuerdo')
    print('  FALLA  %-62s acepto el estado prohibido'
          % 'condicion de cascada en una fila de particion')
    fallos.append('condicion de cascada aceptada en particion')
except sqlite3.Error as e:
    print('  OK     %-62s %s' % ('condicion de cascada en una fila de particion',
                                 str(e).split('\n')[0][:40]))

print()
print('FIDELIDAD · las estructuras legitimas entran limpias')

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.5, instrumento='convenio_colectivo')
regla(con, 2, orden_precedencia=2, modo_aplicacion='particion',
      alcance='porcion_definida', porcion_fraccion=0.5, instrumento='ley')
caso_fiel('Particion exhaustiva 0,5 + 0,5 sin residual', con)

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='particion', alcance='porcion_definida',
      porcion_dias=10, porcion_tipo_de_dia='habil', instrumento='convenio_colectivo')
regla(con, 2, orden_precedencia=2, modo_aplicacion='particion', alcance='porcion_definida',
      porcion_dias=10, porcion_tipo_de_dia='habil', instrumento='ley')
caso_fiel('Particion exhaustiva 10 + 10 dias sobre un derecho de 20', con)

con = base(dias=24)
regla(con, 1, orden_precedencia=1, modo_aplicacion='particion', alcance='todo_el_derecho',
      iniciativa='trabajador', veto_empleador='causal_operativa',
      default_ante_silencio='sin_regla', literal_normativo='BUrlG 7(1)')
caso_fiel('Alemania · regla unica, veto operativo, sin regla de silencio', con)

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='particion', alcance='porcion_definida',
      porcion_dias=5, porcion_tipo_de_dia='habil', instrumento='convenio_colectivo')
regla(con, 2, orden_precedencia=2, modo_aplicacion='particion', alcance='residual',
      iniciativa='trabajador', veto_empleador='causal_operativa',
      default_ante_silencio='aprobado', literal_normativo='BW 7:638(2)')
caso_fiel('Paises Bajos · convenio fija una porcion, el resto residual', con)

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=1, alcance='todo_el_derecho', instrumento='convenio_colectivo')
regla(con, 2, orden_precedencia=2, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=0, condicion_fallback='si_el_anterior_no_fija',
      alcance='todo_el_derecho', instrumento='consejo_de_empresa')
regla(con, 3, orden_precedencia=3, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=0, condicion_fallback='si_no_hay_acuerdo',
      alcance='todo_el_derecho', instrumento='acuerdo_individual', iniciativa='trabajador',
      veto_empleador='causal_operativa', default_ante_silencio='sin_regla')
caso_fiel('Belgica · cascada de tres niveles sobre todo el derecho', con)

con = base()
regla(con, 1, orden_precedencia=1, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=1, alcance='porcion_definida', porcion_fraccion=0.5,
      instrumento='convenio_colectivo')
regla(con, 2, orden_precedencia=2, modo_aplicacion='fallback', grupo_fallback=1,
      es_raiz_fallback=0, condicion_fallback='si_no_hay_acuerdo',
      alcance='porcion_definida', porcion_fraccion=0.5, instrumento='organo_paritario')
regla(con, 3, orden_precedencia=3, modo_aplicacion='particion', alcance='residual',
      iniciativa='trabajador', veto_empleador='causal_operativa',
      default_ante_silencio='aprobado')
caso_fiel('Mixto · cascada gobierna media porcion, el resto residual', con)

print()
print('ADVERSARIAL · resolucion del desacuerdo [v2.19]')
# El campo nace de un colapso real: nueve unidades `negociada` escondian seis
# regimenes opuestos. Las dos restricciones que lo sostienen son simetricas y las
# dos hay que probarlas — una sola dejaria pasar la mitad del defecto.
con = base()
SQL = ("INSERT INTO regla_colocacion (regla_colocacion_id,vacaciones_version_id,"
       "orden_precedencia,modo_aplicacion,alcance,instrumento,iniciativa,"
       "resolucion_desacuerdo,literal_normativo) VALUES "
       "(?,100,1,'particion','todo_el_derecho','ley',?,?,'literal')")
for rid in (900, 901, 902, 903):
    con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,'regla_colocacion')",
                (rid,))
con.commit()
rechaza(con, 'negociada SIN resolucion del desacuerdo', SQL, (900, 'negociada', None))
rechaza(con, 'resolucion en una regla que NO es negociada', SQL,
        (901, 'empleador', 'empleador'))
rechaza(con, 'valor fuera del dominio de resolucion', SQL,
        (902, 'negociada', 'lo_decide_el_azar'))
acepta(con, 'negociada con `sin_regla`: callar es una respuesta, no un hueco', SQL,
       (903, 'negociada', 'sin_regla'))

print()
if fallos:
    print('FALLA la suite:')
    for f in fallos:
        print('  - %s' % f)
    sys.exit(1)
print('Suite completa: todos los casos adversariales se rechazan y las %d '
      'estructuras fieles entran limpias.' % len(fieles))
