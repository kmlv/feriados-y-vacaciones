-- Esquema borrador. NO declara versión ni hash de protocolo: una cabecera se
-- desincroniza y ya se desincronizó una vez. El vínculo vive en
-- `lote_captura` contra el catálogo `protocolo_congelado`, con FK e inmutabilidad.
-- SQLite. BORRADOR: se congela recién después del piloto.
--
-- Reescrito tras el review de codex, que EJECUTÓ el borrador anterior y aceptó
-- estados que el protocolo prohíbe: `NTH:cualquier:cosa:99`, evidencia de un
-- hecho inexistente, y la fecha `2026-99-99`. "Ejecuta limpio" sólo probaba
-- sintaxis. Este archivo va acompañado de `900_validaciones.sql` con lo que no
-- es expresable en DDL.

PRAGMA foreign_keys = ON;

-- =====================================================================
-- 0 · Registro común de hechos  [blocker 5 de codex]
-- =====================================================================
-- La identificación polimórfica de v2.3 §5.1 no tenía integridad referencial:
-- `hecho_id` podía no existir en ninguna tabla. Ahora todo hecho versionado
-- nace aquí, y las tablas de la capa común usan claves foráneas COMPUESTAS.

CREATE TABLE hechos (
  hecho_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  hecho_tipo TEXT NOT NULL CHECK (hecho_tipo IN (
               'feriado_version','regla_fecha_version','ocurrencia',
               'vacaciones_version','escala_antiguedad','particion_alternativa',
               'regimen_jornada','instrumento_supranacional','evento_compensatorio',
               'determinacion_fecha','regla_colocacion')),
  UNIQUE (hecho_id, hecho_tipo)          -- destino de las FK compuestas
);

-- Fecha ISO real, no cualquier texto.  [blocker 8]
-- Uso: CHECK (es_fecha(x)) no existe en SQLite; se expande inline.
--   date(x) IS NOT NULL AND date(julianday(x)) IS NOT NULL AND date(julianday(x)) = x

-- =====================================================================
-- 1 · Capa común
-- =====================================================================

CREATE TABLE jurisdicciones (
  jurisdiccion_id  INTEGER PRIMARY KEY,
  iso3             TEXT NOT NULL,
  nombre           TEXT NOT NULL,
  -- El nombre en ingles es DATO y no formato. Sin esta columna, la version
  -- inglesa del reporte sacaria «Bélgica» y «Países Bajos» en su primera
  -- columna, y arreglarlo en la plantilla inglesa dejaria el CSV publicable en
  -- castellano: dos verdades para el mismo hecho.
  --
  -- Columna y no tabla de traducciones a proposito. El proyecto publica en dos
  -- idiomas, no en N, y una tabla generica seria estructura para un caso que no
  -- existe todavia — este repositorio ya ha pagado dos veces por cosas
  -- declaradas y nunca conectadas. Si llega un tercer idioma, ESE es el momento.
  nombre_en        TEXT,
  nivel            TEXT NOT NULL CHECK (nivel IN ('nacional','subnacional')),
  padre_id         INTEGER REFERENCES jurisdicciones(jurisdiccion_id),
  vigencia_desde   TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta   TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde),
  CHECK ((nivel = 'nacional') = (padre_id IS NULL))
);

-- [blocker 1 v24] Identidad del instrumento externo, no substring del nombre.
-- El LIKE anterior tenía falso negativo (autoridad escrita completa, sin la
-- sigla), falso positivo (otra entidad cuyo nombre la contiene) y evasión por
-- nivel (cargarlo como nivel 1). Un booleano tampoco basta: perdería dataset y
-- versión, que son lo que hace citable la divergencia.
CREATE TABLE dataset_externo (
  dataset_externo_id INTEGER PRIMARY KEY,
  nombre             TEXT NOT NULL,
  version_doi        TEXT NOT NULL,
  UNIQUE (nombre, version_doi)
);

CREATE TABLE fuentes (
  fuente_id         INTEGER PRIMARY KEY,
  -- No nulo sólo cuando la fuente ES un instrumento externo.
  dataset_externo_id INTEGER REFERENCES dataset_externo(dataset_externo_id),
  url               TEXT NOT NULL,
  version_archivada TEXT NOT NULL,
  autoridad         TEXT NOT NULL,
  jurisdiccion_id   INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  fecha_de_norma    TEXT CHECK (fecha_de_norma IS NULL OR date(julianday(fecha_de_norma)) IS NOT NULL AND date(julianday(fecha_de_norma)) = fecha_de_norma),
  nivel_de_fuente   INTEGER NOT NULL CHECK (nivel_de_fuente BETWEEN 1 AND 6),
  -- Un instrumento externo es nivel 4 por definición. Cierra la evasión de
  -- cargarlo como nivel 1 citando la frase "fuente T1" de la nota de prior art.
  CHECK (dataset_externo_id IS NULL OR nivel_de_fuente = 4)
);

CREATE TABLE evidencia (
  hecho_id              INTEGER NOT NULL,
  hecho_tipo            TEXT NOT NULL,
  fuente_id             INTEGER NOT NULL REFERENCES fuentes(fuente_id),
  fecha_de_verificacion TEXT NOT NULL CHECK (date(julianday(fecha_de_verificacion)) IS NOT NULL AND date(julianday(fecha_de_verificacion)) = fecha_de_verificacion),
  revisor               TEXT NOT NULL,
  PRIMARY KEY (hecho_id, hecho_tipo, fuente_id),
  FOREIGN KEY (hecho_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo)
);

CREATE TABLE eventos_reforma (
  reforma_id            INTEGER PRIMARY KEY,
  jurisdiccion_id       INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  tipo                  TEXT NOT NULL CHECK (tipo IN (
                          'creacion','abolicion','suspension','restitucion',
                          'sustitucion','extension_de_cobertura',
                          'cambio_de_escala_de_antiguedad',
                          'reforma_de_reglas_sin_cambio_de_quantum')),
  fecha_anuncio         TEXT CHECK (fecha_anuncio IS NULL OR date(julianday(fecha_anuncio)) IS NOT NULL AND date(julianday(fecha_anuncio)) = fecha_anuncio),
  fecha_promulgacion    TEXT CHECK (fecha_promulgacion IS NULL OR date(julianday(fecha_promulgacion)) IS NOT NULL AND date(julianday(fecha_promulgacion)) = fecha_promulgacion),
  vigencia_desde        TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  causa                 TEXT,
  permanente_o_temporal TEXT NOT NULL CHECK (permanente_o_temporal IN ('permanente','temporal')),
  cita                  TEXT NOT NULL
);

CREATE TABLE reforma_versiones (
  reforma_id INTEGER NOT NULL REFERENCES eventos_reforma(reforma_id),
  hecho_id   INTEGER NOT NULL,
  hecho_tipo TEXT NOT NULL,
  rol        TEXT NOT NULL CHECK (rol IN ('anterior','nuevo')),
  PRIMARY KEY (reforma_id, hecho_id, hecho_tipo, rol),
  FOREIGN KEY (hecho_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo)
);

-- [blocker 8] Estado, causa y fecha separados. La fecha es NULL cuando el
-- estado es 'na' — §1.5 manda representar el fuera de banda como NA con causa,
-- no rechazarlo. Y la banda de ±1 año corresponde a cada ancla.
-- [blocker 2 v24] Lote de captura. §23.2 exige capturar ANTES de ver el valor
-- externo. La base no puede probar qué vio una persona, pero sí puede hacer
-- cumplir el ORDEN: nada se cruza hasta que el lote se congela, y nada se
-- modifica después de congelado.
-- [blocker 2 rev113] Dos textos editables no son un vínculo. Antes se aceptaba
-- version 'banana' con 64 letras z, y después de cruzar se podía reescribir el
-- par entero. Ahora hay catálogo, FK compuesta e inmovilización.
-- La FK cerró el par inventado desde el lote, pero el catálogo seguía siendo
-- sembrable: aceptaba `version = 'banana'` y `congelado_en = '2026-99-99T99:99:99Z'`,
-- y dejaba reescribir `archivo` de una entrada ya referenciada. Un registro de
-- congelamiento que se puede repuntar a otro archivo no reconstruye nada.
CREATE TABLE protocolo_congelado (
  -- Forma exacta `vN.N`. La version anterior de este CHECK admitia la 'v' en
  -- cualquier posicion y cualquier cantidad de puntos, asi que `v2v.8`, `v2.8v`
  -- y `v2.8.1` entraban. Ahora: empieza en 'v', despues de la 'v' solo digitos
  -- y puntos, y exactamente un punto.
  version       TEXT NOT NULL CHECK (
                  version GLOB 'v[0-9]*.[0-9]*'
                  AND substr(version,1,1) = 'v'
                  AND substr(version,2) NOT GLOB '*[^0-9.]*'
                  AND length(version) - length(replace(version,'.','')) = 1),
  hash          TEXT NOT NULL CHECK (
                  length(hash) = 64
                  AND hash GLOB '[0-9a-f]*'
                  AND hash NOT GLOB '*[^0-9a-f]*'),
  -- La regla de §26 —una entrada congelada apunta a su copia inmutable, nunca al
  -- documento vigente— era prosa, y `archivo = ''` entraba sin queja. Como la
  -- regla es de PREFIJO DE RUTA, si es expresable en SQL, y aqui se expresa.
  -- Lo que SQLite no puede hacer es comprobar que el archivo exista y que su
  -- contenido reproduzca `hash`: no lee el disco ni calcula SHA-256. Esa parte
  -- queda como limitacion declarada del dataset; ver §25.1.
  --
  -- El prefijo por si solo NO basta, y codex lo rompio: `docs/archivo/../02-
  -- protocolo.md` casa con el GLOB y resuelve al documento vigente, que es
  -- exactamente lo que la regla prohibe. Tambien entraban `docs/archivo//.md` y
  -- la travesia a cualquier profundidad. Un prefijo de ruta no es una ruta
  -- acotada mientras la ruta pueda volver hacia atras.
  --
  -- El cierre no es enumerar travesias, que es una carrera que se pierde: el
  -- archivo de protocolos es PLANO, asi que lo que sigue al prefijo no puede
  -- contener ninguna barra. Eso mata `..`, `//` y los subdirectorios de una vez.
  archivo       TEXT NOT NULL CHECK (
                  archivo GLOB 'docs/archivo/*.md'
                  AND substr(archivo, length('docs/archivo/') + 1) NOT GLOB '*/*'
                  AND archivo NOT GLOB '*..*'
                  AND length(archivo) > length('docs/archivo/.md')),
  -- Mismo rigor que `lote_captura.congelado_en`, y por el mismo motivo: la marca
  -- de auditoría de la entrada del catálogo no puede ser más laxa que la del
  -- lote que la cita. Sin esto el catálogo aceptaba el mes 99 y la hora 99.
  congelado_en  TEXT NOT NULL CHECK (
                  strftime('%Y-%m-%dT%H:%M:%SZ', substr(congelado_en,1,19)) IS NOT NULL
                  AND strftime('%Y-%m-%dT%H:%M:%SZ', substr(congelado_en,1,19)) = congelado_en
                  AND date(julianday(substr(congelado_en,1,10))) IS NOT NULL
                  AND date(julianday(substr(congelado_en,1,10))) = substr(congelado_en,1,10)
                  AND substr(congelado_en,12,2) BETWEEN '00' AND '23'
                  AND substr(congelado_en,15,2) BETWEEN '00' AND '59'
                  AND substr(congelado_en,18,2) BETWEEN '00' AND '59'),
  PRIMARY KEY (version, hash),
  UNIQUE (version)
);

-- El catálogo es un REGISTRO de congelamiento: se escribe una vez. La FK ya
-- impedía cambiar `version`/`hash` de una entrada citada por un lote, pero
-- `archivo` quedaba libre y una entrada sin citar todavía se podía borrar.
CREATE TRIGGER trg_catalogo_protocolo_inmutable
BEFORE UPDATE ON protocolo_congelado
BEGIN
  SELECT RAISE(ABORT, 'el catalogo de protocolos congelados es de solo escritura inicial');
END;

CREATE TRIGGER trg_catalogo_protocolo_sin_borrado
BEFORE DELETE ON protocolo_congelado
BEGIN
  SELECT RAISE(ABORT, 'una entrada de congelamiento no se borra');
END;

CREATE TABLE lote_captura (
  lote_id  INTEGER PRIMARY KEY,
  etiqueta TEXT NOT NULL,
  -- [blocker rev103 y 5 rev109] Vínculo reconstruible lote → protocolo. Un
  -- comentario de cabecera se desincroniza; esto no.
  version_protocolo      TEXT NOT NULL,
  hash_protocolo         TEXT NOT NULL,
  estado   TEXT NOT NULL CHECK (estado IN ('ciego','congelado','cruzado')),
  -- [blocker 3 rev90] Antes era texto libre y mutable: en un lote ya cruzado se
  -- podía reescribir el momento del congelamiento a 2099. El estado no podía
  -- retroceder, pero la marca de auditoría sí se podía falsear.
  -- [blocker 3 rev93] La versión anterior validaba la FORMA y la fecha, no la
  -- hora: aceptaba '2026-08-08T99:99:99Z'. Ahora hay ida y vuelta por strftime,
  -- que rechaza cualquier componente fuera de rango.
  -- OJO con la lógica de tres valores: `strftime` devuelve NULL ante una hora
  -- imposible, y un CHECK que evalúa a NULL PASA. Hay que exigir explícitamente
  -- que no sea nulo. Es el mismo error que hacía fallar abierta la
  -- compatibilidad semántica, reproducido aquí.
  -- Hacen falta DOS comprobaciones y ninguna basta sola:
  --  · el ida y vuelta por strftime rechaza hora y mes imposibles, pero NO
  --    normaliza el día — devuelve '2026-02-31' tal cual;
  --  · el ida y vuelta por julianday sí normaliza el día, y delata el 31 de
  --    febrero porque vuelve como 3 de marzo.
  -- Y ambas exigen IS NOT NULL explícito: un CHECK que evalúa a NULL PASA.
  congelado_en TEXT CHECK (congelado_en IS NULL OR (
                 strftime('%Y-%m-%dT%H:%M:%SZ', substr(congelado_en,1,19)) IS NOT NULL
                 AND strftime('%Y-%m-%dT%H:%M:%SZ', substr(congelado_en,1,19)) = congelado_en
                 AND date(julianday(substr(congelado_en,1,10))) IS NOT NULL
                 AND date(julianday(substr(congelado_en,1,10))) = substr(congelado_en,1,10)
                 -- Y rangos explícitos de reloj. `strftime` CONSERVA la hora 24
                 -- —es fin de día válido en ISO-8601— así que las dos idas y
                 -- vueltas la dejaban pasar. Se comprueban los tres componentes,
                 -- no sólo el que se coló, porque el comportamiento del motor
                 -- ante los otros dos no es algo en lo que convenga apoyarse.
                 AND substr(congelado_en,12,2) BETWEEN '00' AND '23'
                 AND substr(congelado_en,15,2) BETWEEN '00' AND '59'
                 AND substr(congelado_en,18,2) BETWEEN '00' AND '59')),
  CHECK ((estado = 'ciego') = (congelado_en IS NULL)),
  FOREIGN KEY (version_protocolo, hash_protocolo)
    REFERENCES protocolo_congelado(version, hash)
);

-- Hueco que encontré yo al probar lo anterior: la máquina de estados sólo
-- gobernaba UPDATE, así que un lote podía NACER congelado o cruzado y saltarse
-- la fase ciega entera. Todo lote empieza en ciego.
CREATE TRIGGER trg_lote_nace_ciego
BEFORE INSERT ON lote_captura
WHEN NEW.estado <> 'ciego'
BEGIN
  SELECT RAISE(ABORT, 'todo lote nace ciego');
END;

CREATE TABLE mediciones (
  lote_id                    INTEGER NOT NULL REFERENCES lote_captura(lote_id),
  hecho_id                   INTEGER NOT NULL,
  -- Mismo cierre: la medición con corte y fecha efectiva aplica a las dos
  -- titularidades medidas. Los hechos auxiliares llevan procedencia por
  -- `evidencia`, no por `mediciones`. Sin esto, un hecho auxiliar medido en un
  -- lote congelado quedaba mutable, porque la inmutabilidad sólo cubre esas dos.
  hecho_tipo                 TEXT NOT NULL CHECK (hecho_tipo IN ('vacaciones_version','feriado_version')),
  corte                      INTEGER NOT NULL CHECK (corte IN (2016, 2026)),
  estado_verificacion        TEXT NOT NULL CHECK (estado_verificacion IN (
                               'verificado_primaria','verificado_secundaria',
                               'sin_cambio_confirmado','supuesto','na')),
  -- [blocker 4 rev55] La fecha NO se pierde. §1.5 manda registrarla siempre para
  -- auditar la banda y publicar la distribución de desviaciones. La versión
  -- anterior la borraba en 'na' y además RECHAZABA la fecha fuera de banda, que
  -- es justo la que hay que poder mostrar. Sólo es NULL cuando no se halló
  -- ninguna fecha, y eso es una causa distinta de estar fuera de banda.
  fecha_efectiva_de_medicion TEXT
                             CHECK (fecha_efectiva_de_medicion IS NULL
                                    OR date(julianday(fecha_efectiva_de_medicion)) IS NOT NULL
                                   AND date(julianday(fecha_efectiva_de_medicion)) = fecha_efectiva_de_medicion),
  dentro_de_banda            INTEGER CHECK (dentro_de_banda IN (0,1)),
  causa                      TEXT CHECK (causa IS NULL OR causa IN (
                               'sin_fecha_hallada','fuera_de_banda','fuente_en_conflicto',
                               'no_aplicable','no_cubierto')),
  PRIMARY KEY (hecho_id, hecho_tipo, corte),
  FOREIGN KEY (hecho_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  -- La bandera de banda existe si y sólo si hay fecha, y tiene que decir la verdad.
  CHECK ((fecha_efectiva_de_medicion IS NULL) = (dentro_de_banda IS NULL)),
  CHECK (fecha_efectiva_de_medicion IS NULL OR dentro_de_banda =
    CASE WHEN (corte = 2016 AND fecha_efectiva_de_medicion BETWEEN '2015-01-01' AND '2017-01-01')
           OR (corte = 2026 AND fecha_efectiva_de_medicion BETWEEN '2026-01-01' AND '2026-12-31')
         THEN 1 ELSE 0 END),
  -- [blocker 2 rev60] Las causas no pueden mentir sobre la fecha guardada.
  -- 'sin_fecha_hallada' si y sólo si NO hay fecha.
  CHECK ((causa = 'sin_fecha_hallada') = (fecha_efectiva_de_medicion IS NULL)),
  -- 'fuera_de_banda' si y sólo si hay fecha Y la bandera dice que está fuera.
  CHECK ((causa = 'fuera_de_banda')
         = (fecha_efectiva_de_medicion IS NOT NULL AND dentro_de_banda = 0)),
  CHECK (dentro_de_banda IS NULL OR dentro_de_banda = 1
         OR estado_verificacion = 'na'),
  CHECK (estado_verificacion <> 'na' OR causa IS NOT NULL)
);

-- =====================================================================
-- 2 · Módulo feriados
-- =====================================================================

CREATE TABLE feriado_version (
  feriado_version_id INTEGER PRIMARY KEY,
  hecho_tipo         TEXT NOT NULL DEFAULT 'feriado_version' CHECK (hecho_tipo = 'feriado_version'),
  feriado_id         INTEGER NOT NULL,
  jurisdiccion_id    INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  sector             TEXT NOT NULL,
  vigencia_desde     TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta     TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  nombre_oficial     TEXT NOT NULL,
  categoria          TEXT NOT NULL CHECK (categoria IN (
                       'descanso_pagado_obligatorio','descanso_obligatorio_no_pagado',
                       'cierre_sector_publico','feriado_bancario',
                       'observancia_optativa','conmemorativo_sin_descanso')),
  recurrencia        TEXT NOT NULL CHECK (recurrencia IN ('recurrente','one_off')),
  -- Periodo en anios [decision del principal, piloto 2026-08-09]. Mexico concede
  -- el 1 de octubre CADA SEIS ANIOS, por transmision del Poder Ejecutivo. Con dos
  -- cortes puede caer en uno y no en el otro, y un codificador que solo mire los
  -- cortes registraria un delta QUE NO ES UNA REFORMA. Con el periodo explicito el
  -- calculo del panel puede excluirlo o anotarlo, en vez de depender de que
  -- alguien se acuerde. 1 = anual; NULL solo para one_off.
  periodo_anios      INTEGER CHECK (periodo_anios IS NULL OR periodo_anios >= 1),
  regimen            TEXT NOT NULL CHECK (regimen IN (
                       'descanso_obligatorio','descanso_salvo_requerimiento_con_recargo',
                       'sin_mandato_de_pago','sin_mandato_nacional')),
  tasa_recargo       REAL CHECK (tasa_recargo IS NULL OR tasa_recargo >= 0),
  duracion_dias      REAL NOT NULL CHECK (duracion_dias > 0),
  cobertura          TEXT NOT NULL,
  elegibilidad       TEXT NOT NULL,
  UNIQUE (feriado_id, jurisdiccion_id, sector, vigencia_desde),
  FOREIGN KEY (feriado_version_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde),
  CHECK (regimen = 'descanso_salvo_requerimiento_con_recargo' OR tasa_recargo IS NULL),
  -- [suggestion 10] categoría y régimen tienen que ser compatibles.
  CHECK (NOT (categoria = 'descanso_pagado_obligatorio' AND regimen = 'sin_mandato_de_pago')),
  -- El periodo acompania a la recurrencia y no puede contradecirla. Va como
  -- restriccion de tabla porque relaciona dos columnas.
  CHECK ((recurrencia = 'recurrente' AND periodo_anios IS NOT NULL)
      OR (recurrencia = 'one_off'    AND periodo_anios IS NULL))
);

-- [blocker 4] Gramática canónica ESTRUCTURADA, no comodines.
-- El borrador anterior aceptaba `NTH:cualquier:cosa:99`. Aquí cada clase habilita
-- exactamente su juego de columnas y prohíbe las demás.
CREATE TABLE regla_fecha_version (
  regla_fecha_version_id INTEGER PRIMARY KEY,
  hecho_tipo         TEXT NOT NULL DEFAULT 'regla_fecha_version' CHECK (hecho_tipo = 'regla_fecha_version'),
  feriado_version_id INTEGER NOT NULL REFERENCES feriado_version(feriado_version_id),
  vigencia_desde     TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta     TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  sistema_calendarico TEXT NOT NULL,
  -- `delegada_a_jurisdiccion_local` [decision del principal, piloto 2026-08-09].
  -- Guatemala concede «el dia de la festividad de la localidad» y El Salvador «la
  -- festividad mas importante del lugar, SEGUN LA COSTUMBRE». El feriado existe
  -- con certeza a nivel nacional y su fecha NO es determinable a ese nivel: es
  -- propiedad de la jurisdiccion local. No es fija, no es computable, y meterlo
  -- en `dependiente_de_proclamacion` obligaria a inventar una proclamacion
  -- inexistente para satisfacer el esquema.
  -- `relativa_a_fecha` y `remision_normativa` [decision del principal 2026-08-10].
  -- El piloto trajo dos casos que no eran ninguna de las clases previas, y que
  -- se separan a proposito porque NO son el mismo problema:
  --
  --   Ontario: «the Monday preceding May 25» (Victoria Day). Es determinista y
  --   computable, asi que puede generar ocurrencias. No es `ordinal` —no es el
  --   enesimo lunes del mes— ni `relativa`, cuyo ancla es una fiesta MOVIL.
  --   Aqui el ancla es una FECHA del calendario.
  --
  --   Mexico: «el que determinen las leyes federales y locales electorales».
  --   La fecha existe, pero vive en OTRO cuerpo normativo. No es computable
  --   desde esta norma, y tampoco es costumbre local. Exige citar a que remite.
  --
  -- Meterlos en una sola clase habria escondido que el primero SI es calculable.
  clase_de_regla     TEXT NOT NULL CHECK (clase_de_regla IN (
                       'fija','ordinal','relativa','lunar','dependiente_de_proclamacion',
                       'delegada_a_jurisdiccion_local',
                       'relativa_a_fecha','remision_normativa',
                       'cuota_designada_por_empleador')),
  -- fija
  mes                INTEGER CHECK (mes IS NULL OR mes BETWEEN 1 AND 12),
  dia                INTEGER CHECK (dia IS NULL OR dia BETWEEN 1 AND 31),
  -- ordinal: "2º lunes de octubre"; ordinal = -1 significa el último
  ordinal            INTEGER CHECK (ordinal IS NULL OR ordinal IN (-1,1,2,3,4,5)),
  dia_semana         INTEGER CHECK (dia_semana IS NULL OR dia_semana BETWEEN 1 AND 7),
  -- relativa: ancla móvil + desplazamiento
  -- `pascua_ortodoxa` y `equinoccio_septiembre` [hallazgo de la carga de las 47].
  -- Dos lotes distintos encontraron el mismo hueco y lo resolvieron al reves:
  -- uno codifico los feriados ortodoxos rumanos como `pascua` -que produce una
  -- fecha equivocada EN SILENCIO, porque las dos pascuas difieren hasta cinco
  -- semanas- y el otro omitio los griegos. Un ancla sin distinguir el computo no
  -- es un ancla. `equinoccio_septiembre` faltaba y Japon lo necesita.
  -- `solsticio_junio` y `solsticio_diciembre` [decision del principal 2026-08-10].
  -- Chile concede «el dia del solsticio de invierno de cada anio en el hemisferio
  -- sur», que cae entre el 20 y el 22 de junio. Es la misma clase de objeto que
  -- los equinoccios que ya estaban: una efemeride astronomica determinista. Se
  -- anaden los dos y no solo el de junio, porque un catalogo con tres de los
  -- cuatro puntos cardinales del anio invita a la siguiente omision.
  ancla              TEXT CHECK (ancla IS NULL OR ancla IN (
                       'pascua','pascua_ortodoxa','equinoccio_marzo',
                       'equinoccio_septiembre','solsticio_junio','solsticio_diciembre',
                       'ano_nuevo_lunar')),
  offset_dias        INTEGER,
  -- lunar
  calendario_lunar   TEXT,
  mes_lunar          INTEGER CHECK (mes_lunar IS NULL OR mes_lunar BETWEEN 1 AND 13),
  dia_lunar          INTEGER CHECK (dia_lunar IS NULL OR dia_lunar BETWEEN 1 AND 30),
  -- [decision del principal 2026-08-10] Dia contado DESDE EL FIN del mes lunar;
  -- 1 es el ultimo dia. Corea concede la vispera del Anio Nuevo lunar, que su
  -- decreto define como «음력 12월 말일», el ultimo dia del mes 12 — que es el 29
  -- o el 30 segun el anio. Con `dia_lunar` solo no se puede escribir sin mentir
  -- en la mitad de los anios. Se descarto el centinela -1 en `dia_lunar`: un
  -- numero que significa otra cosa que un numero es un truco que nadie recuerda
  -- dos meses despues.
  dia_lunar_desde_fin INTEGER CHECK (dia_lunar_desde_fin IS NULL
                       OR dia_lunar_desde_fin BETWEEN 1 AND 30),
  -- A que norma remite. Obligatorio en `remision_normativa` y prohibido en el
  -- resto: una remision sin destino no es una remision, es un hueco con nombre.
  instrumento_remitido TEXT,
  -- Conjunto del que el empleador designa los dias de una cuota. Obligatorio en
  -- `cuota_designada_por_empleador` y prohibido en el resto.
  conjunto_de_referencia TEXT,
  -- CONDICION DE APLICACION [decision del principal 2026-08-10]. Un feriado
  -- puede tener VARIAS reglas de fecha, cada una con la condicion bajo la que
  -- rige, y como maximo una sin condicion — la que rige por defecto.
  --
  -- Resuelve dos cosas que parecian distintas y son la misma:
  --
  --   EXISTENCIA CONDICIONAL. Chile declara feriado el 2 de enero SOLO en los
  --   anios en que cae lunes, y el 17 de septiembre solo cuando el 18 y el 19
  --   caen fin de semana. Un feriado cuyas reglas TODAS llevan condicion no
  --   ocurre en los anios en que ninguna se cumple, y eso no necesita un campo
  --   propio: la ausencia de regla por defecto ES la existencia condicional.
  --
  --   REGLA DISYUNTIVA. Santa Brigida en Irlanda es el primer lunes de febrero
  --   SALVO cuando el 1 de febrero cae viernes, y entonces es el 1 de febrero.
  --   Yom HaAtzmaut en Israel desplaza el 5 de Iyar de tres maneras distintas
  --   segun el dia de la semana en que caiga. Son dos y cuatro reglas del
  --   catalogo alternandose, no una clase nueva.
  --
  -- `condicion_referencia` dice QUE fecha se examina, y hacen falta las tres:
  --
  --   `propia`             la fecha que esta misma regla computa. Chile: el 2 de
  --                        enero es feriado cuando el 2 de enero cae lunes.
  --   `regla_por_defecto`  la fecha de la regla SIN condicion del mismo feriado.
  --                        Israel: las tres alternativas producen el 3, el 4 y el
  --                        6 de Iyar, pero la condicion se examina sobre el 5,
  --                        que es la regla por defecto. Con `propia` se estaria
  --                        preguntando por el dia de la semana del resultado en
  --                        vez del de la base, que es otra cosa.
  --   `MM-DD`              una fecha fija distinta. Irlanda: se examina el 1 de
  --                        febrero mientras la regla por defecto produce el
  --                        primer lunes del mes.
  condicion_dia_semana INTEGER CHECK (condicion_dia_semana IS NULL
                        OR condicion_dia_semana BETWEEN 1 AND 7),
  condicion_referencia TEXT CHECK (condicion_referencia IS NULL
                        OR condicion_referencia IN ('propia','regla_por_defecto')
                        OR condicion_referencia GLOB '[0-1][0-9]-[0-3][0-9]'),
  regla_de_traslado_aplicable TEXT,
  -- La clave incluye la condicion: sin eso, dos reglas del mismo feriado con
  -- condiciones distintas chocarian y el mecanismo entero seria inutilizable.
  UNIQUE (feriado_version_id, vigencia_desde, condicion_referencia, condicion_dia_semana),
  FOREIGN KEY (regla_fecha_version_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde),
  -- Exactamente las columnas de su clase, y ninguna otra.
  CHECK (
    (clase_de_regla = 'fija' AND mes IS NOT NULL AND dia IS NOT NULL
       AND ordinal IS NULL AND dia_semana IS NULL AND ancla IS NULL
       AND offset_dias IS NULL AND calendario_lunar IS NULL
       AND mes_lunar IS NULL AND dia_lunar IS NULL
       AND dia_lunar_desde_fin IS NULL)
 OR (clase_de_regla = 'ordinal' AND ordinal IS NOT NULL AND dia_semana IS NOT NULL
       AND mes IS NOT NULL AND dia IS NULL AND ancla IS NULL
       AND offset_dias IS NULL AND calendario_lunar IS NULL
       AND mes_lunar IS NULL AND dia_lunar IS NULL
       AND dia_lunar_desde_fin IS NULL)
 OR (clase_de_regla = 'relativa' AND ancla IS NOT NULL AND offset_dias IS NOT NULL
       AND mes IS NULL AND dia IS NULL AND ordinal IS NULL AND dia_semana IS NULL
       AND calendario_lunar IS NULL AND mes_lunar IS NULL AND dia_lunar IS NULL
       AND dia_lunar_desde_fin IS NULL)
 OR (clase_de_regla = 'relativa_a_fecha'
       -- mes+dia son el ANCLA, dia_semana el objetivo, y el signo de offset_dias
       -- la direccion: negativo = el anterior, positivo = el siguiente.
       AND mes IS NOT NULL AND dia IS NOT NULL AND dia_semana IS NOT NULL
       AND offset_dias IS NOT NULL AND offset_dias <> 0
       AND ordinal IS NULL AND ancla IS NULL AND calendario_lunar IS NULL
       AND mes_lunar IS NULL AND dia_lunar IS NULL
       AND dia_lunar_desde_fin IS NULL)
 OR (clase_de_regla = 'remision_normativa'
       AND instrumento_remitido IS NOT NULL
       AND mes IS NULL AND dia IS NULL AND ordinal IS NULL AND dia_semana IS NULL
       AND ancla IS NULL AND offset_dias IS NULL AND calendario_lunar IS NULL
       AND mes_lunar IS NULL AND dia_lunar IS NULL
       AND dia_lunar_desde_fin IS NULL)
 OR (clase_de_regla = 'delegada_a_jurisdiccion_local'
       AND mes IS NULL AND dia IS NULL AND ordinal IS NULL AND dia_semana IS NULL
       AND ancla IS NULL AND offset_dias IS NULL AND calendario_lunar IS NULL
       AND mes_lunar IS NULL AND dia_lunar IS NULL
       AND dia_lunar_desde_fin IS NULL)
 OR (clase_de_regla = 'lunar' AND calendario_lunar IS NOT NULL
       AND mes_lunar IS NOT NULL
       -- Exactamente uno de los dos: el dia contado desde el principio del mes
       -- lunar o el contado desde su fin. Los dos a la vez serian dos fechas.
       AND ((dia_lunar IS NOT NULL) <> (dia_lunar_desde_fin IS NOT NULL))
       AND mes IS NULL AND dia IS NULL AND ordinal IS NULL AND dia_semana IS NULL
       AND ancla IS NULL AND offset_dias IS NULL)
 OR (clase_de_regla = 'cuota_designada_por_empleador'
       -- Tailandia: la ley nombra UN feriado y deja doce dias a designacion del
       -- empleador dentro de un conjunto tradicional de referencia. No hay fecha
       -- que escribir, y omitirlo dejaba el conteo tailandes en 1 contra los 13
       -- del antecedente. El conjunto es obligatorio: una cuota sin conjunto no
       -- se puede auditar, solo creer.
       AND conjunto_de_referencia IS NOT NULL
       AND mes IS NULL AND dia IS NULL AND ordinal IS NULL AND dia_semana IS NULL
       AND ancla IS NULL AND offset_dias IS NULL AND calendario_lunar IS NULL
       AND mes_lunar IS NULL AND dia_lunar IS NULL AND dia_lunar_desde_fin IS NULL)
 OR (clase_de_regla = 'dependiente_de_proclamacion'
       AND mes IS NULL AND dia IS NULL AND ordinal IS NULL AND dia_semana IS NULL
       AND ancla IS NULL AND offset_dias IS NULL
       -- [blocker 2 rev55] esta rama no prohibía las columnas lunares.
       AND calendario_lunar IS NULL AND mes_lunar IS NULL AND dia_lunar IS NULL
       AND dia_lunar_desde_fin IS NULL)
  ),
  -- [blocker 2 rev55] El par mes-día tiene que existir: 31 de febrero no es
  -- una fecha. El 29 de febrero SÍ se conserva representable como regla
  -- recurrente — la regla existe aunque el año no sea bisiesto.
  CHECK (mes IS NULL OR dia IS NULL OR
    CASE mes
      WHEN 2 THEN dia <= 29
      WHEN 4 THEN dia <= 30
      WHEN 6 THEN dia <= 30
      WHEN 9 THEN dia <= 30
      WHEN 11 THEN dia <= 30
      ELSE dia <= 31
    END),
  -- La remision solo existe en su clase. Sin esto, cualquier fila podria llevar
  -- un destino que nadie usa, y el campo dejaria de significar algo.
  CHECK (clase_de_regla = 'remision_normativa' OR instrumento_remitido IS NULL),
  -- Una condicion a medias no es una condicion: sin saber que fecha se examina,
  -- «rige cuando cae en viernes» no dice cuando rige.
  CHECK ((condicion_dia_semana IS NULL) = (condicion_referencia IS NULL)),
  CHECK (clase_de_regla = 'cuota_designada_por_empleador'
         OR conjunto_de_referencia IS NULL)
);

-- COMO MAXIMO UNA REGLA SIN CONDICION por feriado y vigencia. Va como indice
-- parcial y no como UNIQUE de tabla porque SQLite trata los NULL como
-- distintos: sin esto, la clave de arriba dejaria meter dos reglas por defecto
-- y el feriado tendria dos fechas el mismo anio sin que nada lo notara.
CREATE UNIQUE INDEX ux_regla_fecha_por_defecto
  ON regla_fecha_version (feriado_version_id, vigencia_desde)
  WHERE condicion_dia_semana IS NULL;

-- [blocker 3 rev55] La determinación es un hecho con evidencia propia — §6 se
-- la atribuye — y la cardinalidad es 0..1 : 1: como máximo una ocurrencia la usa
-- (UNIQUE abajo, en `ocurrencias`), y no puede quedar huérfana (V13).
CREATE TABLE determinaciones_fecha (
  determinacion_id       INTEGER PRIMARY KEY,
  hecho_tipo             TEXT NOT NULL DEFAULT 'determinacion_fecha' CHECK (hecho_tipo = 'determinacion_fecha'),
  fecha_legal_original   TEXT NOT NULL,
  calendario             TEXT NOT NULL,
  era                    TEXT,
  fecha_gregoriana_local TEXT NOT NULL CHECK (date(julianday(fecha_gregoriana_local)) IS NOT NULL AND date(julianday(fecha_gregoriana_local)) = fecha_gregoriana_local),
  zona_horaria           TEXT NOT NULL,
  metodo_de_conversion   TEXT NOT NULL CHECK (metodo_de_conversion IN (
                           'determinista','proclamacion_contemporanea','estimada')),
  certeza                TEXT NOT NULL CHECK (certeza IN ('alta','media','baja')),
  autoridad              TEXT,
  proclamacion_id        TEXT,
  FOREIGN KEY (determinacion_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (metodo_de_conversion <> 'proclamacion_contemporanea' OR proclamacion_id IS NOT NULL)
);

-- [§16.4] `anio_calendario` separado de `corte`: una ocurrencia de 2027 puede
-- servir al estimando del corte 2026 cuando el período cruza el 31 de diciembre.
CREATE TABLE ocurrencias (
  ocurrencia_id            INTEGER PRIMARY KEY,
  hecho_tipo               TEXT NOT NULL DEFAULT 'ocurrencia' CHECK (hecho_tipo = 'ocurrencia'),
  feriado_version_id       INTEGER NOT NULL REFERENCES feriado_version(feriado_version_id),
  corte                    INTEGER NOT NULL CHECK (corte IN (2016, 2026)),
  anio_calendario          INTEGER NOT NULL CHECK (anio_calendario BETWEEN 2015 AND 2027),
  indice_en_periodo        INTEGER NOT NULL CHECK (indice_en_periodo >= 1),
  fecha_nominal            TEXT NOT NULL CHECK (date(julianday(fecha_nominal)) IS NOT NULL AND date(julianday(fecha_nominal)) = fecha_nominal),
  fecha_observada          TEXT NOT NULL CHECK (date(julianday(fecha_observada)) IS NOT NULL AND date(julianday(fecha_observada)) = fecha_observada),
  base_de_sustitucion      TEXT,
  duracion_horas_estado    TEXT NOT NULL CHECK (duracion_horas_estado IN ('derivada','explicita','na')),
  duracion_horas           REAL CHECK (duracion_horas IS NULL OR duracion_horas > 0),
  cayo_en_descanso_semanal INTEGER NOT NULL CHECK (cayo_en_descanso_semanal IN (0,1)),
  overlap_group            INTEGER,
  origen                   TEXT NOT NULL CHECK (origen IN (
                             'derivada_de_regla','proclamada','por_decreto')),
  determinacion_id         INTEGER REFERENCES determinaciones_fecha(determinacion_id),
  UNIQUE (feriado_version_id, anio_calendario, indice_en_periodo),
  -- [blocker 3 rev55] una determinación no se comparte entre ocurrencias.
  UNIQUE (determinacion_id),
  FOREIGN KEY (ocurrencia_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (origen = 'derivada_de_regla' OR determinacion_id IS NOT NULL),
  CHECK ((duracion_horas_estado = 'explicita') = (duracion_horas IS NOT NULL)),
  -- El año de la fecha sólo puede ser el del corte o el siguiente.
  CHECK (anio_calendario IN (corte, corte + 1)),
  CHECK (CAST(strftime('%Y', fecha_observada) AS INTEGER) = anio_calendario)
);

CREATE TABLE regimen_jornada (
  regimen_jornada_id    INTEGER PRIMARY KEY,
  hecho_tipo            TEXT NOT NULL DEFAULT 'regimen_jornada' CHECK (hecho_tipo = 'regimen_jornada'),
  jurisdiccion_id       INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  sector                TEXT NOT NULL,
  vigencia_desde        TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta        TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  dias_descanso_semanal TEXT NOT NULL,
  -- [v2.21] Cuantos dias de descanso semanal garantiza la ley. Es REAL y no
  -- entero porque hay medios: Austria da el domingo entero mas el sabado desde
  -- las 13:00, y Argentina, Espana y Republica Dominicana cierran la semana al
  -- mediodia. Y es NULLABLE porque hay ordenamientos donde la ley no garantiza
  -- ninguno —Australia y Estados Unidos—, que es un estado distinto de «uno».
  dias_descanso_semanal_n REAL CHECK (dias_descanso_semanal_n IS NULL
                          OR (dias_descanso_semanal_n > 0 AND dias_descanso_semanal_n <= 7)),
  -- [v2.21] La jornada, tal como la escribe la norma.
  --
  -- `horas_semanales_max` va NULLABLE, y el nulo es informacion: Estados Unidos
  -- no tiene techo semanal —sus cuarenta horas son el umbral a partir del cual
  -- la hora se encarece, que no es lo mismo— y Paises Bajos solo tiene topes con
  -- extras incluidas. Poner el tope de Paises Bajos como jornada lo dejaria como
  -- la jornada mas larga del grupo siendo de las mas cortas.
  horas_semanales_max   REAL CHECK (horas_semanales_max IS NULL OR horas_semanales_max > 0),
  horas_diarias_max     REAL CHECK (horas_diarias_max IS NULL OR horas_diarias_max > 0),
  umbral_horas_extra    REAL CHECK (umbral_horas_extra IS NULL OR umbral_horas_extra > 0),
  -- Dias ordinarios de trabajo por semana. REAL por los 5,5 de Argentina y
  -- Republica Dominicana, cuya ley cierra la semana al mediodia del sabado.
  dias_ordinarios       REAL CHECK (dias_ordinarios IS NULL
                        OR (dias_ordinarios > 0 AND dias_ordinarios <= 7)),
  -- DE DONDE SALE ESE NUMERO, y las cuatro respuestas son distintas:
  --
  --   `declarado`         la norma lo escribe. Hungria: «cinco dias, de lunes a
  --                       viernes».
  --   `derivado`          sale de dividir el techo semanal entre el diario, y
  --                       por eso NO es lo mismo que leerlo. Alemania es el
  --                       caso: su ley de jornada no escribe ninguna cifra
  --                       semanal, y el 48 es ocho horas por seis Werktage.
  --   `alternativa_legal` la ley NO elige y dice entre que valores. Chile fija
  --                       un rango de cinco a seis; Colombia e Indonesia nombran
  --                       los dos numeros y dejan la eleccion al acuerdo.
  --                       Nombrar y no elegir es un acto legal.
  --   `no_declarado`      silencio: la distribucion va al contrato o al
  --                       convenio. Callar es otro acto legal distinto.
  dias_ordinarios_origen TEXT NOT NULL CHECK (dias_ordinarios_origen IN (
                          'declarado','derivado','alternativa_legal','no_declarado')),
  -- QUE PASA CUANDO UN FERIADO CAE EN EL DESCANSO SEMANAL. Siete valores, y los
  -- siete estan atestiguados en el grupo — colapsarlos seria el error que este
  -- proyecto mide:
  --
  --   `traslada`            Belgica: el feriado en domingo o en dia de
  --                         inactividad se sustituye por un dia habil.
  --   `compensa_en_dinero`  Italia: no se mueve nada, se paga de mas.
  --   `compensa_a_eleccion` Irlanda: el empleador satisface con dia o con
  --                         dinero, a su eleccion.
  --   `anade_dia`           Australia en Navidad y Anio Nuevo: no sustituye, SUMA
  --                         un dia. No es lo mismo que trasladar.
  --   `regla_sin_efecto`    Honduras: la ley resuelve la coincidencia y no
  --                         entrega nada, porque ese pago ya va en el salario.
  --                         Un cero con norma detras no es un cero por omision.
  --   `sin_regla`           Suecia: silencio.
  --   `no_aplicable`        Paises Bajos y Dinamarca: no puede haber regla
  --                         porque NO EXISTE feriado legal pagado.
  regla_traslado_defecto TEXT CHECK (regla_traslado_defecto IS NULL
                          OR regla_traslado_defecto IN (
                          'traslada','compensa_en_dinero','compensa_a_eleccion',
                          'anade_dia','reduce_cuota_de_horas','regla_sin_efecto',
                          'se_pierde','sin_regla','no_aplicable')),
  -- Y SEPARADO DEL MECANISMO, SU EFECTO. Son dos preguntas distintas y mezclarlas
  -- fue mi primer diseno: el mecanismo describe lo que hace la norma —trasladar,
  -- pagar, reducir una cuota de horas—, y el efecto dice lo unico que necesita
  -- quien mida descanso, que es si el trabajador acaba con un dia libre o no.
  --
  -- Polonia lo justifica solo: su norma no traslada nada, reduce en ocho horas la
  -- cuota del periodo. Mecanismo raro, efecto identico al de un traslado. Y al
  -- reves, Italia tiene un mecanismo comodo de entender y efecto CERO en dias.
  --
  -- `indeterminado` existe por Nicaragua, cuyo art. 68 dice que el dia «sera
  -- compensado» sin decir con que. Elegir por ella seria imputar.
  efecto_traslado       TEXT CHECK (efecto_traslado IS NULL OR efecto_traslado IN (
                          'dia_libre','dinero','dia_o_dinero_a_eleccion',
                          'ninguno','indeterminado')),
  literal_normativo     TEXT,
  horas_lun REAL, horas_mar REAL, horas_mie REAL, horas_jue REAL,
  horas_vie REAL, horas_sab REAL, horas_dom REAL,
  UNIQUE (jurisdiccion_id, sector, vigencia_desde),
  FOREIGN KEY (regimen_jornada_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde)
);

CREATE TABLE eventos_compensatorios (
  evento_compensatorio_id INTEGER PRIMARY KEY,
  hecho_tipo       TEXT NOT NULL DEFAULT 'evento_compensatorio' CHECK (hecho_tipo = 'evento_compensatorio'),
  jurisdiccion_id  INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  anio_calendario  INTEGER NOT NULL,
  fecha            TEXT NOT NULL CHECK (date(julianday(fecha)) IS NOT NULL AND date(julianday(fecha)) = fecha),
  compensa_ocurrencia_id INTEGER REFERENCES ocurrencias(ocurrencia_id),
  compensable      INTEGER NOT NULL CHECK (compensable IN (0,1)),
  UNIQUE (jurisdiccion_id, fecha),
  FOREIGN KEY (evento_compensatorio_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo)
);

-- =====================================================================
-- 3 · Módulo vacaciones
-- =====================================================================

CREATE TABLE vacaciones_version (
  vacaciones_version_id INTEGER PRIMARY KEY,
  hecho_tipo       TEXT NOT NULL DEFAULT 'vacaciones_version' CHECK (hecho_tipo = 'vacaciones_version'),
  jurisdiccion_id  INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  sector           TEXT NOT NULL,
  vigencia_desde   TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta   TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  texto_legal_dias REAL NOT NULL CHECK (texto_legal_dias >= 0),
  -- [decision del principal, piloto 2026-08-09] El dominio de dos valores no
  -- alcanzaba. Alemania concede «24 WERKTAGE», que incluyen el sabado y excluyen
  -- domingos y feriados, sobre semana de seis dias: codificarlos como habiles
  -- sobreestima el derecho aleman en 20%. Ontario concede «2 SEMANAS», y guardar
  -- «10 dias» seria presentar una conversion NUESTRA como si fuera el texto legal,
  -- que es justo lo que este campo existe para impedir.
  tipo_de_dia      TEXT NOT NULL CHECK (tipo_de_dia IN (
                     'calendario','habil','werktage','semanas')),
  -- Base semanal SOBRE LA QUE ESTA ESCRITA LA NORMA. Sin ella la conversion es
  -- imposible y el numero legal es incomparable. Se exige cuando la unidad se
  -- define contra la semana; para dias calendario es NULL y la conversion usa
  -- `regimen_jornada`, que es propiedad del trabajador y no de la norma.
  base_semanal_dias INTEGER CHECK (base_semanal_dias IS NULL
                                   OR base_semanal_dias BETWEEN 1 AND 7),
  -- QUIEN fija la base semanal [hallazgo del escalado a 47]. Exigir la base sin
  -- mas fue correcto para Alemania —cuya ley se escribe sobre semana de seis—
  -- pero ocho unidades definen el derecho contra el horario DEL TRABAJADOR y no
  -- contra una semana legal: Nueva Zelanda dice «what genuinely constitutes a
  -- working week for the employee», los Paises Bajos «vier maal de overeengekomen
  -- arbeidsduur per week». Ahi no hay base que leer, y exigirla obligaba a
  -- inventarla — el mismo error de factor dos, por la otra puerta.
  --
  -- Se declara el ORIGEN. Si lo fija la norma, la base es obligatoria; si lo fija
  -- el horario del trabajador, va nula y la conversion usa `regimen_jornada`. Lo
  -- que sigue prohibido es omitirla en silencio.
  base_semanal_origen TEXT CHECK (base_semanal_origen IS NULL
                                  OR base_semanal_origen IN (
                                    'norma','horario_del_trabajador')),
  periodo_de_calificacion_meses INTEGER NOT NULL CHECK (periodo_de_calificacion_meses >= 0),
  rango_min        REAL, rango_max REAL,
  causa_del_rango  TEXT CHECK (causa_del_rango IS NULL OR causa_del_rango IN ('federal','antiguedad','sector')),
  base_antiguedad  TEXT NOT NULL CHECK (base_antiguedad IN (
                     'servicio_continuo_empleador_actual',
                     'servicio_reconocido_empleadores_previos',
                     'experiencia_laboral_total')),
  regla_de_reconocimiento TEXT,
  imputacion_feriados_a_vacaciones TEXT NOT NULL CHECK (
                     imputacion_feriados_a_vacaciones IN (
                       'se_computan_contra','extienden','sin_regla_explicita')),
  UNIQUE (jurisdiccion_id, sector, vigencia_desde),
  FOREIGN KEY (vacaciones_version_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde),
  CHECK ((rango_min IS NULL) = (rango_max IS NULL)),
  CHECK (rango_max IS NULL OR rango_max >= rango_min),
  CHECK ((rango_min IS NULL) = (causa_del_rango IS NULL)),
  -- [suggestion 10] la regla de reconocimiento sólo aplica si la base la admite.
  CHECK (base_antiguedad = 'servicio_continuo_empleador_actual'
         OR regla_de_reconocimiento IS NOT NULL),
  -- La base semanal se exige exactamente cuando la unidad se define contra la
  -- semana. Va como restriccion de tabla porque relaciona dos columnas.
  -- `IS` y no `=`. Con `=`, un `base_semanal_origen` NULO hace que las tres
  -- ramas evaluen a NULL, la disyuncion entera valga NULL, y un CHECK que
  -- evalua a NULL PASA. Omitir el origen en silencio era exactamente lo que
  -- esta restriccion existe para impedir, y lo dejaba pasar.
  --
  -- Es la TERCERA vez que la logica de tres valores muerde en este esquema: dos
  -- veces con codex en las compatibilidades de clase, y esta. Queda como regla:
  -- en un CHECK que discrimina por un campo anulable, `IS` siempre.
  CHECK ((tipo_de_dia = 'calendario'
            AND base_semanal_dias IS NULL AND base_semanal_origen IS NULL)
      OR (tipo_de_dia <> 'calendario' AND base_semanal_origen IS 'norma'
            AND base_semanal_dias IS NOT NULL)
      OR (tipo_de_dia <> 'calendario'
            AND base_semanal_origen IS 'horario_del_trabajador'
            AND base_semanal_dias IS NULL))
);

-- [blocker 7] Tramos VERSIONADOS, y frontera normalizada en días además del
-- literal: `desde_meses = 60` más "más de cinco años" dejaba ambigua la
-- derivación exactamente en 60.
-- [blocker 1 y 2 rev106] Las reglas de colocación son una TABLA HIJA, no tres
-- escalares en la fila padre. Mi corrección anterior mejoró el vocabulario pero
-- repitió la misma clase de error que ya habíamos cometido con la escala de
-- antigüedad: aplanar estructura en un escalar.
--
-- Un mismo derecho puede estar gobernado por reglas CONCURRENTES, RESIDUALES o
-- JERÁRQUICAS. El art. 7:638(2) neerlandés dice que la regla
-- trabajador→objeción→silencio opera sólo sobre lo NO fijado ya por acuerdo
-- escrito, convenio colectivo, órgano competente o ley. La fuente oficial belga
-- describe una cascada de cuatro niveles. Una sola `iniciativa` obligatoria
-- aplana exactamente esas capas.
--
-- Además `veto_empleador` y `default_ante_silencio` NO son atributos
-- universales: son CONDICIONALES de una regla de solicitud del trabajador.
-- Obligarlos a NOT NULL fabricaba valores donde el concepto no aplica — un
-- calendario fijo por ley no tiene "veto del empleador".
CREATE TABLE regla_colocacion (
  regla_colocacion_id   INTEGER PRIMARY KEY,
  -- [blocker 4 rev109] Es un hecho evidenciable: las capas provienen de
  -- instrumentos distintos, así que colgar una fuente global de la versión
  -- padre no resuelve procedencia.
  hecho_tipo            TEXT NOT NULL DEFAULT 'regla_colocacion' CHECK (hecho_tipo = 'regla_colocacion'),
  vacaciones_version_id INTEGER NOT NULL REFERENCES vacaciones_version(vacaciones_version_id),
  orden_precedencia     INTEGER NOT NULL CHECK (orden_precedencia >= 1),
  -- [blocker 1 rev109] `alcance` mezclaba dos relaciones distintas. Partición y
  -- cascada NO son la misma estructura: en Países Bajos el convenio fija una
  -- PORCIÓN y el resto es residual; en Bélgica varios niveles intentan fijar el
  -- MISMO derecho en orden, y el siguiente opera si el anterior no resolvió.
  -- Representar la cascada como porciones exigía inventar días que la norma no
  -- contiene.
  modo_aplicacion       TEXT NOT NULL CHECK (modo_aplicacion IN ('particion','fallback')),
  -- [blocker 1 rev113] La cascada necesita RAÍZ y OBJETIVO, no sólo un grupo.
  -- Antes una sola fila fallback residual con condición de texto libre pasaba
  -- por cascada completa, y dos grupos superpuestos más una partición convivían
  -- sin que nada lo notara.
  grupo_fallback        INTEGER,          -- reglas del mismo grupo compiten en orden
  es_raiz_fallback      INTEGER CHECK (es_raiz_fallback IN (0,1)),
  condicion_fallback    TEXT CHECK (condicion_fallback IS NULL OR condicion_fallback IN (
                          'si_el_anterior_no_fija','si_no_hay_acuerdo','si_no_aplica_el_instrumento')),
  alcance               TEXT NOT NULL CHECK (alcance IN (
                          'todo_el_derecho','porcion_definida','residual')),
  porcion_dias          REAL CHECK (porcion_dias IS NULL OR porcion_dias > 0),
  porcion_tipo_de_dia   TEXT CHECK (porcion_tipo_de_dia IS NULL OR porcion_tipo_de_dia IN ('calendario','habil')),
  porcion_fraccion      REAL CHECK (porcion_fraccion IS NULL OR (porcion_fraccion > 0 AND porcion_fraccion <= 1)),
  instrumento           TEXT NOT NULL CHECK (instrumento IN (
                          'ley','convenio_colectivo','acuerdo_individual',
                          'organo_paritario','consejo_de_empresa','decision_empresa')),
  -- `asignacion_estatal` [decision del principal, piloto 2026-08-09]. Indonesia:
  -- los 8 dias de «cuti bersama» que fija por decreto un colegio de tres
  -- ministros NO son feriados que se suman — son PARTE del derecho a vacaciones,
  -- con la fecha puesta por un tercero, y descuentan del saldo de 12 dias. Con
  -- esta iniciativa la cota accesible al trabajador cae sola de 12 a 4 sin
  -- necesidad de un campo nuevo, porque la aritmetica de porciones ya existe.
  -- Se distingue de `cierre_colectivo`, que lo decide el empleador.
  iniciativa            TEXT NOT NULL CHECK (iniciativa IN (
                          'trabajador','empleador','negociada',
                          'calendario_fijo_legal','cierre_colectivo',
                          'asignacion_estatal')),
  -- [blocker 2 rev109] `sin_regla` restaurado. Es un estado SUSTANTIVO dentro de
  -- una regla de solicitud —Alemania no tiene regla de silencio, y eso no es lo
  -- mismo que "el silencio no aprueba"—. NULL queda reservado para "no aplica".
  veto_empleador        TEXT CHECK (veto_empleador IS NULL OR veto_empleador IN (
                          'ninguno','causal_operativa','causal_tasada_umbral_alto','discrecional')),
  default_ante_silencio TEXT CHECK (default_ante_silencio IS NULL OR default_ante_silencio IN (
                          'aprobado','no_aprobado','sin_regla')),
  -- [decision del principal, 2026-08-10, tras la doble codificacion ciega]
  -- Quien decide cuando la NEGOCIACION FRACASA. No cabia en `veto_empleador`,
  -- que por restriccion de tabla pertenece a las reglas de solicitud del
  -- trabajador — y con razon: un veto solo existe contra una solicitud. Pero eso
  -- dejaba sin sitio un hecho sustantivo, y nueve unidades colapsadas bajo
  -- `negociada` escondian CUATRO regimenes opuestos:
  --
  --   `empleador`            Peru art. 14 D.Leg. 713 y Portugal 241.º n.º 2:
  --                          «a falta de acuerdo decidira el empleador». Francia
  --                          L3141-16 hace lo mismo.
  --   `limite_razonabilidad` Australia s.88(2) y Nueva Zelanda s.18(4): el
  --                          empleador puede negarse, pero no «unreasonably».
  --   `trabajador_prevalece` Grecia art. 224: el empleador queda OBLIGADO a
  --                          conceder lo que el trabajador pide.
  --   `tercero_dirime`       Grecia art. 4 §2 con su comision tripartita
  --                          —inspector, empleador y representante del
  --                          personal—, y Espana con su procedimiento sumario y
  --                          preferente. Le retiran el desempate al empleador.
  --   `remitido_a_convenio`  Indonesia art. 79(4): la ejecucion se regula en el
  --                          contrato, el reglamento interno o el convenio. La
  --                          ley no calla, DELEGA, y son cosas distintas.
  --   `sin_regla`            Israel: la ley calla. Es un estado, no un hueco.
  --
  -- Sin este campo, Peru y Grecia salian identicos en los campos estructurados
  -- resolviendo el desacuerdo en direcciones opuestas. Colapsar estructuras
  -- legales distintas bajo una etiqueta es exactamente lo que este proyecto le
  -- reprocha al antecedente, y lo estabamos haciendo en la variable de
  -- colocacion.
  resolucion_desacuerdo TEXT CHECK (resolucion_desacuerdo IS NULL OR resolucion_desacuerdo IN (
                          'empleador','trabajador_prevalece','limite_razonabilidad',
                          'tercero_dirime','remitido_a_convenio','sin_regla')),
  literal_normativo     TEXT NOT NULL,
  UNIQUE (vacaciones_version_id, orden_precedencia),
  FOREIGN KEY (regla_colocacion_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  -- La cascada exige grupo y condición; la partición no los admite.
  CHECK ((modo_aplicacion = 'fallback') = (grupo_fallback IS NOT NULL)),
  CHECK ((modo_aplicacion = 'fallback') = (es_raiz_fallback IS NOT NULL)),
  -- La raíz es incondicional; los sucesores exigen condición. Antes se exigía
  -- condición también a la primera, que no tiene nivel anterior.
  CHECK (es_raiz_fallback IS NULL OR (es_raiz_fallback = 1) = (condicion_fallback IS NULL)),
  -- [blocker 4 rev119] El comentario decía que la partición no admite condición
  -- y nada lo hacía cumplir: una fila de partición con
  -- `condicion_fallback = 'si_no_hay_acuerdo'` entraba y ninguna validación la
  -- veía. Una condición de cascada en una partición no significa nada.
  CHECK (modo_aplicacion = 'fallback' OR condicion_fallback IS NULL),
  -- [blocker 3 rev109] Unidad declarada: una porción en días dice de qué días.
  CHECK ((porcion_dias IS NOT NULL) = (porcion_tipo_de_dia IS NOT NULL)),
  CHECK ((alcance = 'porcion_definida') = (porcion_dias IS NOT NULL OR porcion_fraccion IS NOT NULL)),
  CHECK (NOT (porcion_dias IS NOT NULL AND porcion_fraccion IS NOT NULL)),
  -- Condicionales de una regla de solicitud del trabajador.
  CHECK ((iniciativa = 'trabajador') = (veto_empleador IS NOT NULL)),
  CHECK ((iniciativa = 'trabajador') = (default_ante_silencio IS NOT NULL)),
  -- Condicional de una regla NEGOCIADA, y obligatorio ahi. Va con `=` y no con
  -- una implicacion en un solo sentido a proposito: si fuera opcional, el
  -- codificador con prisa lo dejaria en null y volveriamos al colapso que este
  -- campo viene a deshacer. `sin_regla` existe para el caso de Israel, donde la
  -- ley calla — y decir «la ley calla» es una respuesta, no una omision.
  CHECK ((iniciativa = 'negociada') = (resolucion_desacuerdo IS NOT NULL)),
  -- [blocker 2 rev109] Estado incoherente que rev106 ya había señalado y seguía
  -- pasando: si nadie tiene veto, no hay quien deba aprobar, así que el silencio
  -- no puede dejar de aprobar.
  CHECK (NOT (veto_empleador = 'ninguno' AND default_ante_silencio = 'no_aprobado'))
);

-- La UNIDAD DE ASIGNACIÓN no es la fila: es la porción de derecho que alguien
-- reclama. Una partición reclama una porción por fila; una cascada reclama UNA
-- porción por grupo, porque sus niveles compiten por fijar lo mismo (V32).
--
-- Sin esta distinción toda la aritmética se podía evadir declarando `fallback`:
-- V25 a V27 filtraban por `modo_aplicacion = 'particion'`, así que una cascada
-- de 0,6 conviviendo con una partición de 0,5 más residual sumaba 1,1 del
-- derecho sin una sola violación, una cascada en días y una partición en
-- fracción convivían sin base de conversión, y dos cascadas residuales
-- independientes reclamaban las dos el remanente. Las validaciones cuentan
-- unidades, no filas.
CREATE VIEW asignacion_colocacion AS
  SELECT vacaciones_version_id,
         'r' || regla_colocacion_id AS unidad,
         'particion'                AS modo,
         alcance, porcion_dias, porcion_tipo_de_dia, porcion_fraccion
    FROM regla_colocacion
   WHERE modo_aplicacion = 'particion'
   UNION ALL
  SELECT vacaciones_version_id,
         'g' || grupo_fallback,
         'fallback',
         -- Idénticos dentro del grupo por V32; se toma el mínimo para no
         -- depender de qué fila devuelva el motor.
         MIN(alcance), MIN(porcion_dias), MIN(porcion_tipo_de_dia), MIN(porcion_fraccion)
    FROM regla_colocacion
   WHERE modo_aplicacion = 'fallback'
   GROUP BY vacaciones_version_id, grupo_fallback;

CREATE TABLE escala_antiguedad (
  escala_id             INTEGER PRIMARY KEY,
  hecho_tipo            TEXT NOT NULL DEFAULT 'escala_antiguedad' CHECK (hecho_tipo = 'escala_antiguedad'),
  vacaciones_version_id INTEGER NOT NULL REFERENCES vacaciones_version(vacaciones_version_id),
  vigencia_desde        TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta        TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  -- [blocker 1 rev55] Antigüedad CALENDARIO, no días. Un aniversario dura 365 o
  -- 366 días según bisiestos, así que "cinco años" no es un número fijo de días:
  -- la versión anterior sustituyó 60 meses ambiguos por días no equivalentes.
  -- Se almacena como (meses, días residuales); la comparación es lexicográfica.
  -- Las fronteras submensuales viven en el residual.
  desde_meses           INTEGER NOT NULL CHECK (desde_meses >= 0),
  desde_dias_residuales INTEGER NOT NULL DEFAULT 0 CHECK (desde_dias_residuales BETWEEN 0 AND 30),
  hasta_meses           INTEGER,
  hasta_dias_residuales INTEGER CHECK (hasta_dias_residuales IS NULL OR hasta_dias_residuales BETWEEN 0 AND 30),
  -- [blocker 1 rev60] El intervalo almacenado es SIEMPRE [desde, hasta), inclusivo
  -- por la izquierda. Mi intento anterior de hacer semántico el operador con una
  -- bandera de inclusividad abría un hueco: `[0,24)` seguido de `(24,∞)` dejaba
  -- exactamente el mes 24 sin tramo, y todas las validaciones pasaban.
  -- Ahora `mas_de X` se NORMALIZA al día siguiente —(24,1)— al cargar. El operador
  -- y el literal se conservan como procedencia, no como modificadores del intervalo.
  operador_frontera     TEXT NOT NULL CHECK (operador_frontera IN (
                          'al_cumplir','tras_completar','a_partir_de','mas_de')),
  literal_normativo     TEXT NOT NULL,
  quantum               REAL NOT NULL CHECK (quantum >= 0),
  -- Mismo dominio que `vacaciones_version.tipo_de_dia`. En v2.13 se extendio
  -- alli y NO aqui, y la carga del piloto lo encontro: la escala canadiense
  -- cuenta en SEMANAS y no cabia. Un dominio que significa lo mismo y difiere
  -- entre tablas es un error silencioso esperando su turno.
  tipo_de_dia           TEXT NOT NULL CHECK (tipo_de_dia IN (
                     'calendario','habil','werktage','semanas')),
  UNIQUE (vacaciones_version_id, vigencia_desde, desde_meses, desde_dias_residuales),
  FOREIGN KEY (escala_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde),
  CHECK ((hasta_meses IS NULL) = (hasta_dias_residuales IS NULL)),
  CHECK (hasta_meses IS NULL
         OR (hasta_meses > desde_meses)
         OR (hasta_meses = desde_meses AND hasta_dias_residuales > desde_dias_residuales)),
  -- Normalización obligatoria: 'mas_de X' se carga con el inicio ya avanzado al
  -- día siguiente, así que su residual no puede ser cero cuando el tramo arranca
  -- en un aniversario exacto. Es lo que garantiza la partición total del dominio.
  CHECK (operador_frontera <> 'mas_de' OR desde_dias_residuales >= 1
         OR (desde_meses = 0 AND desde_dias_residuales = 0))
);

-- [blocker 9] Conjunto factible de verdad: una alternativa de partición agrupa
-- varias clases de bloque. Sin el padre no se podían expresar particiones
-- alternativas y el optimizador no tenía sobre qué optimizar.
CREATE TABLE particion_alternativa (
  particion_alternativa_id INTEGER PRIMARY KEY,
  hecho_tipo            TEXT NOT NULL DEFAULT 'particion_alternativa' CHECK (hecho_tipo = 'particion_alternativa'),
  vacaciones_version_id INTEGER NOT NULL REFERENCES vacaciones_version(vacaciones_version_id),
  vigencia_desde        TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta        TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  etiqueta              TEXT NOT NULL,
  requiere_consentimiento INTEGER NOT NULL CHECK (requiere_consentimiento IN (0,1)),
  -- [blocker 5 rev55] Límites globales de bloques: sin ellos la alternativa
  -- podía producir cero bloques y seguir pareciendo válida.
  numero_bloques_min    INTEGER NOT NULL CHECK (numero_bloques_min >= 1),
  numero_bloques_max    INTEGER CHECK (numero_bloques_max IS NULL OR numero_bloques_max >= 1),
  FOREIGN KEY (particion_alternativa_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde),
  CHECK (numero_bloques_max IS NULL OR numero_bloques_max >= numero_bloques_min)
);

CREATE TABLE particion_clase (
  particion_clase_id       INTEGER PRIMARY KEY,
  particion_alternativa_id INTEGER NOT NULL REFERENCES particion_alternativa(particion_alternativa_id),
  etiqueta_clase           TEXT NOT NULL,
  cardinalidad_min         INTEGER NOT NULL CHECK (cardinalidad_min >= 0),
  cardinalidad_max         INTEGER,
  tamano_min               REAL NOT NULL CHECK (tamano_min > 0),
  tamano_max               REAL,
  -- Mismo dominio que `vacaciones_version.tipo_de_dia`. En v2.13 se extendio
  -- alli y NO aqui, y la carga del piloto lo encontro: la escala canadiense
  -- cuenta en SEMANAS y no cabia. Un dominio que significa lo mismo y difiere
  -- entre tablas es un error silencioso esperando su turno.
  tipo_de_dia              TEXT NOT NULL CHECK (tipo_de_dia IN (
                     'calendario','habil','werktage','semanas')),
  UNIQUE (particion_alternativa_id, etiqueta_clase),
  CHECK (cardinalidad_max IS NULL OR cardinalidad_max >= cardinalidad_min),
  CHECK (tamano_max IS NULL OR tamano_max >= tamano_min)
);

CREATE TABLE instrumento_supranacional (
  instrumento_id   INTEGER PRIMARY KEY,
  hecho_tipo       TEXT NOT NULL DEFAULT 'instrumento_supranacional' CHECK (hecho_tipo = 'instrumento_supranacional'),
  instrumento      TEXT NOT NULL,
  jurisdiccion_id  INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  vigencia_desde   TEXT NOT NULL CHECK (date(julianday(vigencia_desde)) IS NOT NULL AND date(julianday(vigencia_desde)) = vigencia_desde),
  vigencia_hasta   TEXT CHECK (vigencia_hasta IS NULL OR date(julianday(vigencia_hasta)) IS NOT NULL AND date(julianday(vigencia_hasta)) = vigencia_hasta),
  piso_dias        REAL NOT NULL CHECK (piso_dias >= 0),
  -- Mismo dominio que `vacaciones_version.tipo_de_dia`. En v2.13 se extendio
  -- alli y NO aqui, y la carga del piloto lo encontro: la escala canadiense
  -- cuenta en SEMANAS y no cabia. Un dominio que significa lo mismo y difiere
  -- entre tablas es un error silencioso esperando su turno.
  tipo_de_dia      TEXT NOT NULL CHECK (tipo_de_dia IN (
                     'calendario','habil','werktage','semanas')),
  ratificado_o_vinculante TEXT NOT NULL CHECK (
                     ratificado_o_vinculante IN ('ratificado','vinculante_por_tratado','no_vinculante')),
  aplicable_al_sector_privado INTEGER NOT NULL CHECK (aplicable_al_sector_privado IN (0,1)),
  UNIQUE (instrumento, jurisdiccion_id, vigencia_desde),
  FOREIGN KEY (instrumento_id, hecho_tipo) REFERENCES hechos(hecho_id, hecho_tipo),
  CHECK (vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde)
);

-- =====================================================================
-- 4 · Mediciones externas  [blocker de fable5 sobre el hallazgo CBR]
-- =====================================================================
-- Principio: NINGÚN valor de un instrumento externo entra jamás a una tabla de
-- hechos. Antes de estas tablas el esquema no tenía dónde ponerlo, y eso no era
-- una virtud sino un riesgo: sin lugar legítimo, el valor del antecedente
-- terminaría de contrabando en `vacaciones_version.texto_legal_dias`.
--
-- Estas tablas quedan DELIBERADAMENTE FUERA del registro `hechos`. No son
-- hechos del proyecto: son observaciones de otro instrumento, con otro
-- estimando. Por eso tampoco pueden ser referenciadas por `evidencia`,
-- `reforma_versiones` ni `mediciones`.

CREATE TABLE medicion_externa (
  medicion_externa_id  INTEGER PRIMARY KEY,
  -- [blocker 2 rev86] Antes eran texto libre sin FK, así que el registro
  -- versionado que cierra identidad en `fuentes` no gobernaba las observaciones,
  -- y el UNIQUE omitía la versión: dos versiones del mismo dataset no podían
  -- coexistir. Nombre y DOI se DERIVAN del registro.
  dataset_externo_id   INTEGER NOT NULL REFERENCES dataset_externo(dataset_externo_id),
  jurisdiccion_id      INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  variable             TEXT NOT NULL CHECK (variable IN ('vacaciones','feriados')),
  anio                 INTEGER NOT NULL,
  puntaje_publicado    REAL NOT NULL,
  -- Derivado por función versionada. En el CBR: 30 días → 1.0 en vacaciones,
  -- 18 días → 1.0 en feriados.
  valor_dias_convertido REAL,
  -- En el tope el índice es COTA INFERIOR, no medición. 8% de las celdas.
  censurado_en_tope    INTEGER NOT NULL CHECK (censurado_en_tope IN (0,1)),
  -- El índice da el mismo puntaje a la ley y al convenio colectivo.
  base_normativa       TEXT NOT NULL CHECK (base_normativa IN (
                         'ley','convenio','laudo','mixta','no_determinable')),
  -- Las cuatro reglas federales que el índice aplica sin exponerlas pasan a
  -- ser DATO en vez de prosa narrativa en el codebook ajeno.
  regla_subnacional_efectiva TEXT NOT NULL CHECK (regla_subnacional_efectiva IN (
                         'nacional_uniforme','promedio_no_ponderado',
                         'solo_nivel_federal','moda_subnacional','mezcla',
                         'no_determinable')),
  -- No es nuestro estimando: 'normal length' ≠ 'tras doce meses de servicio'.
  estimando_externo    TEXT NOT NULL,
  -- El índice no declara tipo de día. El dominio propio es calendario|habil y
  -- NO debe relajarse: por eso esta tabla es aparte y admite 'no_declarado'.
  tipo_de_dia_externo  TEXT NOT NULL CHECK (tipo_de_dia_externo IN (
                         'calendario','habil','no_declarado')),
  cita_normativa_externa TEXT,
  UNIQUE (dataset_externo_id, jurisdiccion_id, variable, anio),
  CHECK (censurado_en_tope = 0 OR valor_dias_convertido IS NOT NULL)
);

-- Semilla de la pantalla 2, no hechos. Alimenta candidatos con cita.
CREATE TABLE reforma_externa (
  reforma_externa_id INTEGER PRIMARY KEY,
  dataset_externo_id INTEGER NOT NULL REFERENCES dataset_externo(dataset_externo_id),
  jurisdiccion_id    INTEGER NOT NULL REFERENCES jurisdicciones(jurisdiccion_id),
  variable           TEXT NOT NULL CHECK (variable IN ('vacaciones','feriados')),
  anio_cambio        INTEGER NOT NULL,
  cita               TEXT,
  UNIQUE (dataset_externo_id, jurisdiccion_id, variable, anio_cambio)
);

-- Cruce DERIVADO, nunca capturado. Es la versión con tres fuentes del hallazgo
-- del 24%, y es publicable por sí mismo: mide la cuña entre lo que el
-- antecedente llama derecho y lo que este proyecto mide.
-- [blocker 2 v24] El cruce enlaza LOS DOS LADOS. La versión anterior sólo
-- apuntaba al externo, así que una observación país-año quedaba ambiguamente
-- unida a varias versiones y sectores.
CREATE TABLE crosswalk (
  crosswalk_id        INTEGER PRIMARY KEY,
  medicion_externa_id INTEGER NOT NULL REFERENCES medicion_externa(medicion_externa_id),
  hecho_id            INTEGER NOT NULL,
  -- [blocker 2 rev93] Falla CERRADO. Los CASE de compatibilidad devolvían NULL
  -- para cualquier otro tipo, y en SQL `x <> NULL` es NULL: el trigger no
  -- disparaba y el cruce pasaba sin comprobación. Se restringe el dominio.
  hecho_tipo          TEXT NOT NULL CHECK (hecho_tipo IN ('vacaciones_version','feriado_version')),
  corte               INTEGER NOT NULL,
  UNIQUE (medicion_externa_id, hecho_id, hecho_tipo, corte),
  FOREIGN KEY (hecho_id, hecho_tipo, corte)
    REFERENCES mediciones(hecho_id, hecho_tipo, corte)
);

-- [blocker 3 v24] La causa CONSERVA la categoría. Antes 'laudo' se satisfacía
-- declarando 'convenio', y 'no_determinable' no exigía nada: la validación se
-- podía callar convirtiendo incertidumbre en convenio.
CREATE TABLE crosswalk_causa (
  crosswalk_id INTEGER NOT NULL REFERENCES crosswalk(crosswalk_id),
  causa TEXT NOT NULL CHECK (causa IN (
    'convenio','laudo','mixta','base_no_determinable',
    'subnacional','subnacional_no_determinable',
    'normal_length_vs_referencia','tipo_de_dia','censura','vintage')),
  PRIMARY KEY (crosswalk_id, causa)
);

-- =====================================================================
-- Máquina de estados e inmutabilidad  [blocker 1 y 3 rev86]
-- =====================================================================
-- La versión anterior sólo tenía triggers sobre UPDATE de las dos tablas de
-- versión. Codex mostró que la invariante anunciada no se cumplía: se podía
-- saltar de ciego a cruzado, mover la medición a otro lote ciego para que el
-- trigger dejara de verla congelada, y mutar el estado de verificación después
-- del cruce.

-- Transición monotónica: ciego -> congelado -> cruzado. Nada más.
CREATE TRIGGER trg_lote_transicion_monotonica
BEFORE UPDATE OF estado ON lote_captura
WHEN NOT ((OLD.estado = 'ciego'     AND NEW.estado IN ('ciego','congelado'))
       OR (OLD.estado = 'congelado' AND NEW.estado IN ('congelado','cruzado'))
       OR (OLD.estado = 'cruzado'   AND NEW.estado = 'cruzado'))
BEGIN
  SELECT RAISE(ABORT, 'transicion de lote invalida: solo ciego->congelado->cruzado');
END;

-- Pasar a `cruzado` es una operación CERRADA: exige cobertura total.
-- [blocker 3 rev90] La marca de congelamiento se fija una vez y no se reescribe.
-- El par de protocolo es parte de la identidad auditada del lote: se fija al
-- crearlo y no se toca nunca, ni siquiera mientras el lote sigue ciego.
CREATE TRIGGER trg_protocolo_inmutable
BEFORE UPDATE ON lote_captura
WHEN NEW.version_protocolo IS NOT OLD.version_protocolo
  OR NEW.hash_protocolo IS NOT OLD.hash_protocolo
BEGIN
  SELECT RAISE(ABORT, 'el par de protocolo es inmutable');
END;

CREATE TRIGGER trg_congelado_en_inmutable
BEFORE UPDATE ON lote_captura
WHEN OLD.estado <> 'ciego' AND NEW.congelado_en IS NOT OLD.congelado_en
BEGIN
  SELECT RAISE(ABORT, 'marca de congelamiento inmutable');
END;

-- [blocker 2 rev90] El cierre exige las causas ANTES de volverlas inmutables.
-- Si no, un lote se puede cerrar para siempre con una violación declarada que
-- ya no se puede arreglar.
CREATE TRIGGER trg_cierre_exige_vintage
BEFORE UPDATE OF estado ON lote_captura
WHEN NEW.estado = 'cruzado' AND OLD.estado <> 'cruzado'
 AND EXISTS (SELECT 1 FROM mediciones m
               JOIN crosswalk cw ON cw.hecho_id = m.hecho_id AND cw.hecho_tipo = m.hecho_tipo AND cw.corte = m.corte
               JOIN medicion_externa me ON me.medicion_externa_id = cw.medicion_externa_id
             WHERE m.lote_id = OLD.lote_id AND me.anio <> cw.corte
               AND NOT EXISTS (SELECT 1 FROM crosswalk_causa c
                               WHERE c.crosswalk_id = cw.crosswalk_id AND c.causa = 'vintage'))
BEGIN
  SELECT RAISE(ABORT, 'cierre bloqueado: anio externo distinto del corte sin causa vintage');
END;

CREATE TRIGGER trg_cierre_exige_causas_declaradas
BEFORE UPDATE OF estado ON lote_captura
WHEN NEW.estado = 'cruzado' AND OLD.estado <> 'cruzado'
 AND EXISTS (SELECT 1 FROM mediciones m
               JOIN crosswalk cw ON cw.hecho_id = m.hecho_id AND cw.hecho_tipo = m.hecho_tipo AND cw.corte = m.corte
               JOIN medicion_externa me ON me.medicion_externa_id = cw.medicion_externa_id
             WHERE m.lote_id = OLD.lote_id
               AND ( (me.censurado_en_tope = 1
                      AND NOT EXISTS (SELECT 1 FROM crosswalk_causa c WHERE c.crosswalk_id = cw.crosswalk_id AND c.causa = 'censura'))
                  OR (me.base_normativa <> 'ley'
                      AND NOT EXISTS (SELECT 1 FROM crosswalk_causa c WHERE c.crosswalk_id = cw.crosswalk_id
                                        AND c.causa = CASE me.base_normativa WHEN 'convenio' THEN 'convenio' WHEN 'laudo' THEN 'laudo'
                                                        WHEN 'mixta' THEN 'mixta' WHEN 'no_determinable' THEN 'base_no_determinable' END))
                  OR (me.regla_subnacional_efectiva <> 'nacional_uniforme'
                      AND NOT EXISTS (SELECT 1 FROM crosswalk_causa c WHERE c.crosswalk_id = cw.crosswalk_id
                                        AND c.causa = CASE me.regla_subnacional_efectiva WHEN 'no_determinable' THEN 'subnacional_no_determinable' ELSE 'subnacional' END)) ))
BEGIN
  SELECT RAISE(ABORT, 'cierre bloqueado: hay causas de divergencia sin declarar');
END;

CREATE TRIGGER trg_lote_cruzado_exige_cobertura
BEFORE UPDATE OF estado ON lote_captura
WHEN NEW.estado = 'cruzado' AND OLD.estado <> 'cruzado'
 AND EXISTS (SELECT 1 FROM mediciones m
             WHERE m.lote_id = OLD.lote_id
               AND NOT EXISTS (SELECT 1 FROM crosswalk cw
                               WHERE cw.hecho_id = m.hecho_id
                                 AND cw.hecho_tipo = m.hecho_tipo
                                 AND cw.corte = m.corte))
BEGIN
  SELECT RAISE(ABORT, 'cobertura incompleta: hay mediciones sin cruce en el lote');
END;

-- Mediciones: inmóviles una vez congelado el lote. Cubre INSERT, UPDATE
-- —incluido mover la fila a otro lote— y DELETE.
CREATE TRIGGER trg_medicion_no_insertar_en_lote_cerrado
BEFORE INSERT ON mediciones
WHEN (SELECT estado FROM lote_captura WHERE lote_id = NEW.lote_id) <> 'ciego'
BEGIN
  SELECT RAISE(ABORT, 'lote cerrado: no admite mediciones nuevas');
END;

CREATE TRIGGER trg_medicion_inmutable_tras_congelar
BEFORE UPDATE ON mediciones
WHEN (SELECT estado FROM lote_captura WHERE lote_id = OLD.lote_id) <> 'ciego'
  OR (SELECT estado FROM lote_captura WHERE lote_id = NEW.lote_id) <> 'ciego'
BEGIN
  SELECT RAISE(ABORT, 'medicion congelada: no se muta ni se reasigna de lote');
END;

CREATE TRIGGER trg_medicion_no_borrar_tras_congelar
BEFORE DELETE ON mediciones
WHEN (SELECT estado FROM lote_captura WHERE lote_id = OLD.lote_id) <> 'ciego'
BEGIN
  SELECT RAISE(ABORT, 'medicion congelada: no se borra');
END;

-- Hechos: ni mutación ni borrado una vez congelado el lote que los mide.
CREATE TRIGGER trg_no_mutar_vacaciones_tras_congelar
BEFORE UPDATE ON vacaciones_version
WHEN EXISTS (SELECT 1 FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
             WHERE m.hecho_id = OLD.vacaciones_version_id
               AND m.hecho_tipo = 'vacaciones_version' AND l.estado <> 'ciego')
BEGIN
  SELECT RAISE(ABORT, 'hecho congelado: no se muta tras congelar el lote');
END;

CREATE TRIGGER trg_no_borrar_vacaciones_tras_congelar
BEFORE DELETE ON vacaciones_version
WHEN EXISTS (SELECT 1 FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
             WHERE m.hecho_id = OLD.vacaciones_version_id
               AND m.hecho_tipo = 'vacaciones_version' AND l.estado <> 'ciego')
BEGIN
  SELECT RAISE(ABORT, 'hecho congelado: no se borra tras congelar el lote');
END;

CREATE TRIGGER trg_no_mutar_feriado_tras_congelar
BEFORE UPDATE ON feriado_version
WHEN EXISTS (SELECT 1 FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
             WHERE m.hecho_id = OLD.feriado_version_id
               AND m.hecho_tipo = 'feriado_version' AND l.estado <> 'ciego')
BEGIN
  SELECT RAISE(ABORT, 'hecho congelado: no se muta tras congelar el lote');
END;

CREATE TRIGGER trg_no_borrar_feriado_tras_congelar
BEFORE DELETE ON feriado_version
WHEN EXISTS (SELECT 1 FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
             WHERE m.hecho_id = OLD.feriado_version_id
               AND m.hecho_tipo = 'feriado_version' AND l.estado <> 'ciego')
BEGIN
  SELECT RAISE(ABORT, 'hecho congelado: no se borra tras congelar el lote');
END;

-- Cruce: SÓLO con el lote exactamente `congelado`. Antes el trigger rechazaba
-- únicamente 'ciego', así que se podía insertar un cruce nuevo con el lote ya
-- cruzado — o sea, el cierre no cerraba el grafo.  [blocker 1 rev90]
CREATE TRIGGER trg_crosswalk_insert_solo_congelado
BEFORE INSERT ON crosswalk
WHEN (SELECT l.estado FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE m.hecho_id = NEW.hecho_id AND m.hecho_tipo = NEW.hecho_tipo
        AND m.corte = NEW.corte) <> 'congelado'
BEGIN
  SELECT RAISE(ABORT, 'cruce solo con lote congelado');
END;

CREATE TRIGGER trg_crosswalk_update_solo_congelado
BEFORE UPDATE ON crosswalk
WHEN (SELECT l.estado FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE m.hecho_id = OLD.hecho_id AND m.hecho_tipo = OLD.hecho_tipo
        AND m.corte = OLD.corte) <> 'congelado'
   OR (SELECT l.estado FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE m.hecho_id = NEW.hecho_id AND m.hecho_tipo = NEW.hecho_tipo
        AND m.corte = NEW.corte) <> 'congelado'
BEGIN
  SELECT RAISE(ABORT, 'cruce inmutable fuera del estado congelado');
END;

CREATE TRIGGER trg_crosswalk_delete_solo_congelado
BEFORE DELETE ON crosswalk
WHEN (SELECT l.estado FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE m.hecho_id = OLD.hecho_id AND m.hecho_tipo = OLD.hecho_tipo
        AND m.corte = OLD.corte) <> 'congelado'
BEGIN
  SELECT RAISE(ABORT, 'cruce no borrable fuera del estado congelado');
END;

-- Las causas también son artefactos del cruce: mismas compuertas.
CREATE TRIGGER trg_causa_insert_solo_congelado
BEFORE INSERT ON crosswalk_causa
WHEN (SELECT l.estado FROM crosswalk cw
        JOIN mediciones m ON m.hecho_id = cw.hecho_id AND m.hecho_tipo = cw.hecho_tipo AND m.corte = cw.corte
        JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE cw.crosswalk_id = NEW.crosswalk_id) <> 'congelado'
BEGIN
  SELECT RAISE(ABORT, 'causa solo con lote congelado');
END;

-- [blocker 1 rev93] Comprobaba sólo OLD, así que una causa creada en un lote
-- congelado se podía MOVER a un cruce de un lote ya cerrado.
CREATE TRIGGER trg_causa_update_solo_congelado
BEFORE UPDATE ON crosswalk_causa
WHEN (SELECT l.estado FROM crosswalk cw
        JOIN mediciones m ON m.hecho_id = cw.hecho_id AND m.hecho_tipo = cw.hecho_tipo AND m.corte = cw.corte
        JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE cw.crosswalk_id = OLD.crosswalk_id) <> 'congelado'
   OR (SELECT l.estado FROM crosswalk cw
        JOIN mediciones m ON m.hecho_id = cw.hecho_id AND m.hecho_tipo = cw.hecho_tipo AND m.corte = cw.corte
        JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE cw.crosswalk_id = NEW.crosswalk_id) <> 'congelado'
BEGIN
  SELECT RAISE(ABORT, 'causa inmutable fuera del estado congelado');
END;

CREATE TRIGGER trg_causa_delete_solo_congelado
BEFORE DELETE ON crosswalk_causa
WHEN (SELECT l.estado FROM crosswalk cw
        JOIN mediciones m ON m.hecho_id = cw.hecho_id AND m.hecho_tipo = cw.hecho_tipo AND m.corte = cw.corte
        JOIN lote_captura l ON l.lote_id = m.lote_id
      WHERE cw.crosswalk_id = OLD.crosswalk_id) <> 'congelado'
BEGIN
  SELECT RAISE(ABORT, 'causa no borrable fuera del estado congelado');
END;

-- La observación externa y su identidad quedan congeladas al cerrarse el lote
-- que las referencia: si no, un cruce cerrado se vuelve semánticamente falso
-- cambiando lo que hay del otro lado.  [blocker 1 rev90]
CREATE TRIGGER trg_medicion_externa_congelada
BEFORE UPDATE ON medicion_externa
WHEN EXISTS (SELECT 1 FROM crosswalk cw
               JOIN mediciones m ON m.hecho_id = cw.hecho_id AND m.hecho_tipo = cw.hecho_tipo AND m.corte = cw.corte
               JOIN lote_captura l ON l.lote_id = m.lote_id
             WHERE cw.medicion_externa_id = OLD.medicion_externa_id AND l.estado = 'cruzado')
BEGIN
  SELECT RAISE(ABORT, 'observacion externa congelada: referenciada por un lote cruzado');
END;

CREATE TRIGGER trg_medicion_externa_no_borrar
BEFORE DELETE ON medicion_externa
WHEN EXISTS (SELECT 1 FROM crosswalk cw
               JOIN mediciones m ON m.hecho_id = cw.hecho_id AND m.hecho_tipo = cw.hecho_tipo AND m.corte = cw.corte
               JOIN lote_captura l ON l.lote_id = m.lote_id
             WHERE cw.medicion_externa_id = OLD.medicion_externa_id AND l.estado = 'cruzado')
BEGIN
  SELECT RAISE(ABORT, 'observacion externa congelada: no se borra');
END;

CREATE TRIGGER trg_dataset_externo_congelado
BEFORE UPDATE ON dataset_externo
WHEN EXISTS (SELECT 1 FROM medicion_externa me
               JOIN crosswalk cw ON cw.medicion_externa_id = me.medicion_externa_id
               JOIN mediciones m ON m.hecho_id = cw.hecho_id AND m.hecho_tipo = cw.hecho_tipo AND m.corte = cw.corte
               JOIN lote_captura l ON l.lote_id = m.lote_id
             WHERE me.dataset_externo_id = OLD.dataset_externo_id AND l.estado = 'cruzado')
BEGIN
  SELECT RAISE(ABORT, 'identidad de dataset congelada: hay un lote cruzado que la cita');
END;

-- Compatibilidad semántica: en INSERT y también en UPDATE. Antes sólo corría en
-- INSERT, y bastaba con reapuntar `medicion_externa_id` para romperla.
CREATE TRIGGER trg_crosswalk_compatible_insert
BEFORE INSERT ON crosswalk
WHEN (SELECT me.jurisdiccion_id FROM medicion_externa me WHERE me.medicion_externa_id = NEW.medicion_externa_id)
     <> (CASE NEW.hecho_tipo
           WHEN 'vacaciones_version' THEN (SELECT jurisdiccion_id FROM vacaciones_version WHERE vacaciones_version_id = NEW.hecho_id)
           WHEN 'feriado_version'    THEN (SELECT jurisdiccion_id FROM feriado_version    WHERE feriado_version_id = NEW.hecho_id) END)
  OR (SELECT me.variable FROM medicion_externa me WHERE me.medicion_externa_id = NEW.medicion_externa_id)
     <> (CASE NEW.hecho_tipo WHEN 'vacaciones_version' THEN 'vacaciones' WHEN 'feriado_version' THEN 'feriados' END)
BEGIN
  SELECT RAISE(ABORT, 'cruce incompatible: jurisdiccion o variable no coinciden');
END;

CREATE TRIGGER trg_crosswalk_compatible_update
BEFORE UPDATE ON crosswalk
WHEN (SELECT me.jurisdiccion_id FROM medicion_externa me WHERE me.medicion_externa_id = NEW.medicion_externa_id)
     <> (CASE NEW.hecho_tipo
           WHEN 'vacaciones_version' THEN (SELECT jurisdiccion_id FROM vacaciones_version WHERE vacaciones_version_id = NEW.hecho_id)
           WHEN 'feriado_version'    THEN (SELECT jurisdiccion_id FROM feriado_version    WHERE feriado_version_id = NEW.hecho_id) END)
  OR (SELECT me.variable FROM medicion_externa me WHERE me.medicion_externa_id = NEW.medicion_externa_id)
     <> (CASE NEW.hecho_tipo WHEN 'vacaciones_version' THEN 'vacaciones' WHEN 'feriado_version' THEN 'feriados' END)
BEGIN
  SELECT RAISE(ABORT, 'cruce incompatible tras actualizar');
END;