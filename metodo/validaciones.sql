-- Validaciones que NO son expresables como restricción de tabla.
-- [blocker 6 de codex] El borrador anterior remitía a este archivo y el archivo
-- no existía. Las promesas remitidas a un archivo inexistente son prosa.
--
-- Cada consulta debe devolver CERO filas. Cualquier fila es una violación.
-- Uso:  sqlite3 base.db < 900_validaciones.sql

.headers on
.mode column

-- V1 · Todo hecho versionado tiene al menos un vínculo de evidencia.
SELECT 'V1 hecho sin evidencia' AS violacion, h.hecho_tipo, h.hecho_id
FROM hechos h
LEFT JOIN evidencia e ON e.hecho_id = h.hecho_id AND e.hecho_tipo = h.hecho_tipo
WHERE e.hecho_id IS NULL;

-- V2 · Cada hecho registrado existe en su tabla concreta.
SELECT 'V2 hecho huerfano' AS violacion, h.hecho_tipo, h.hecho_id FROM hechos h
WHERE (h.hecho_tipo='feriado_version'          AND NOT EXISTS (SELECT 1 FROM feriado_version          t WHERE t.feriado_version_id=h.hecho_id))
   OR (h.hecho_tipo='regla_fecha_version'      AND NOT EXISTS (SELECT 1 FROM regla_fecha_version      t WHERE t.regla_fecha_version_id=h.hecho_id))
   OR (h.hecho_tipo='ocurrencia'               AND NOT EXISTS (SELECT 1 FROM ocurrencias              t WHERE t.ocurrencia_id=h.hecho_id))
   OR (h.hecho_tipo='vacaciones_version'       AND NOT EXISTS (SELECT 1 FROM vacaciones_version       t WHERE t.vacaciones_version_id=h.hecho_id))
   OR (h.hecho_tipo='escala_antiguedad'        AND NOT EXISTS (SELECT 1 FROM escala_antiguedad        t WHERE t.escala_id=h.hecho_id))
   OR (h.hecho_tipo='particion_alternativa'    AND NOT EXISTS (SELECT 1 FROM particion_alternativa    t WHERE t.particion_alternativa_id=h.hecho_id))
   OR (h.hecho_tipo='regimen_jornada'          AND NOT EXISTS (SELECT 1 FROM regimen_jornada          t WHERE t.regimen_jornada_id=h.hecho_id))
   OR (h.hecho_tipo='instrumento_supranacional'AND NOT EXISTS (SELECT 1 FROM instrumento_supranacional t WHERE t.instrumento_id=h.hecho_id))
   OR (h.hecho_tipo='evento_compensatorio'     AND NOT EXISTS (SELECT 1 FROM eventos_compensatorios   t WHERE t.evento_compensatorio_id=h.hecho_id))
   OR (h.hecho_tipo='determinacion_fecha'       AND NOT EXISTS (SELECT 1 FROM determinaciones_fecha    t WHERE t.determinacion_id=h.hecho_id));

-- V3 · Escala de antigüedad: sin solapamientos dentro de la misma versión y vigencia.
SELECT 'V3 solapamiento de tramos' AS violacion, a.vacaciones_version_id, a.escala_id, b.escala_id
FROM escala_antiguedad a JOIN escala_antiguedad b
  ON a.vacaciones_version_id = b.vacaciones_version_id
 AND a.vigencia_desde = b.vigencia_desde
 AND a.escala_id < b.escala_id
WHERE (a.desde_meses*31 + a.desde_dias_residuales) < COALESCE(b.hasta_meses*31 + b.hasta_dias_residuales, 1e9)
  AND (b.desde_meses*31 + b.desde_dias_residuales) < COALESCE(a.hasta_meses*31 + a.hasta_dias_residuales, 1e9);

-- V4 · Escala de antigüedad: sin huecos. El tramo n+1 arranca donde termina el n.
SELECT 'V4 hueco en la escala' AS violacion, a.vacaciones_version_id, a.hasta_meses
FROM escala_antiguedad a
WHERE a.hasta_meses IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM escala_antiguedad b
    WHERE b.vacaciones_version_id = a.vacaciones_version_id
      AND b.vigencia_desde = a.vigencia_desde
      AND b.desde_meses = a.hasta_meses
      AND b.desde_dias_residuales = a.hasta_dias_residuales);

-- V5 · Escala de antigüedad: exactamente un tramo abierto por versión y vigencia.
SELECT 'V5 tramos abiertos != 1' AS violacion, vacaciones_version_id, vigencia_desde, COUNT(*) AS abiertos
FROM escala_antiguedad WHERE hasta_meses IS NULL
GROUP BY vacaciones_version_id, vigencia_desde HAVING COUNT(*) <> 1;

-- V6 · Cobertura de la grilla. Se prueban DOS puntos por aniversario: el exacto
--      —el trabajador de referencia de §1.1, doce meses cumplidos— y el
--      inmediatamente posterior, que es como §3.2.1 define la grilla. Con el
--      intervalo normalizado a [desde,hasta) ambos deben caer siempre en algún
--      tramo; si uno no cae, hay hueco.
WITH puntos(m,d) AS (VALUES (12,0),(12,1),(60,0),(60,1),(120,0),(120,1))
SELECT 'V6 punto de grilla sin tramo' AS violacion, v.vacaciones_version_id, p.m, p.d
FROM vacaciones_version v CROSS JOIN puntos p
WHERE NOT EXISTS (
  SELECT 1 FROM escala_antiguedad e
  WHERE e.vacaciones_version_id = v.vacaciones_version_id
    AND (p.m*31 + p.d) >= (e.desde_meses*31 + e.desde_dias_residuales)
    AND ( e.hasta_meses IS NULL
          OR (p.m*31 + p.d) < (e.hasta_meses*31 + e.hasta_dias_residuales) ));

-- V7 · Toda celda medida en un corte tiene medición registrada.
SELECT 'V7 hecho sin medicion' AS violacion, h.hecho_tipo, h.hecho_id
FROM hechos h
WHERE h.hecho_tipo IN ('feriado_version','vacaciones_version')
  AND NOT EXISTS (SELECT 1 FROM mediciones m
                  WHERE m.hecho_id = h.hecho_id AND m.hecho_tipo = h.hecho_tipo);

-- V8 · Una medición verificada necesita AL MENOS UNA fuente admisible (1-5).
--      Corregido tras la [suggestion 6] de codex: la versión anterior daba falso
--      positivo cuando un hecho verificado conservaba, además de su fuente
--      admisible, el vínculo de descubrimiento de nivel 6. Conservar ese vínculo
--      es correcto; lo que hay que prohibir es que sea el único soporte.
SELECT 'V8 verificada sin fuente admisible' AS violacion, m.hecho_tipo, m.hecho_id
FROM mediciones m
WHERE m.estado_verificacion IN ('verificado_primaria','verificado_secundaria')
  AND NOT EXISTS (
    SELECT 1 FROM evidencia e JOIN fuentes f ON f.fuente_id = e.fuente_id
    WHERE e.hecho_id = m.hecho_id AND e.hecho_tipo = m.hecho_tipo
      AND f.nivel_de_fuente BETWEEN 1 AND 5);

-- V9 · Piso supranacional: sólo cuenta si es vinculante Y aplica al privado.
SELECT 'V9 piso no aplicable usado' AS violacion, instrumento_id
FROM instrumento_supranacional
WHERE ratificado_o_vinculante = 'no_vinculante' AND aplicable_al_sector_privado = 1;

-- V10 · Toda alternativa produce al menos un bloque.
--      Antes bastaba con "tener una clase": codex insertó una clase con
--      cardinalidad 0..0, que pasa el test y produce exactamente cero bloques.
SELECT 'V10 alternativa sin bloques posibles' AS violacion, a.particion_alternativa_id
FROM particion_alternativa a
WHERE NOT EXISTS (
  SELECT 1 FROM particion_clase c
  WHERE c.particion_alternativa_id = a.particion_alternativa_id
    AND (c.cardinalidad_max IS NULL OR c.cardinalidad_max > 0));

-- V12 · La escala arranca en cero: sin tramo inicial no hay derecho de entrada.
--      codex insertó [300,500),[500,∞) y V3-V6 no dijeron nada.
SELECT 'V12 escala no arranca en cero' AS violacion, vacaciones_version_id, vigencia_desde
FROM escala_antiguedad
GROUP BY vacaciones_version_id, vigencia_desde
HAVING MIN(desde_meses * 31 + desde_dias_residuales) <> 0;

-- V13 · Determinación de fecha huérfana: existe y ninguna ocurrencia la usa.
SELECT 'V13 determinacion huerfana' AS violacion, d.determinacion_id
FROM determinaciones_fecha d
WHERE NOT EXISTS (SELECT 1 FROM ocurrencias o WHERE o.determinacion_id = d.determinacion_id);

-- V14 · Factibilidad REAL de la partición, con cota DERIVADA de los datos.
--      Historia de esta validación, porque ilustra el modo de fallo:
--        v1 comparaba el quantum contra el intervalo [piso, techo]. codex la
--        rompió con dos casos donde el quantum cae en el intervalo pero ninguna
--        combinación entera lo alcanza.
--        v2 enumeró combinaciones enteras, pero con la cardinalidad tope fijada
--        en 12. codex la rompió al revés: una partición de trece bloques
--        unitarios es factible, pasa el DDL, y v2 la declaraba infactible.
--        Una nota que "declara" una cota no la convierte en restricción del
--        modelo. Un falso positivo es tan grave como un falso negativo.
--        v3 derivaba la cota, pero dejaba dos sentinels de 1000000. codex la
--        rompió otra vez con una partición de 1,000,001 bloques unitarios: el
--        mismo error que el 12, sólo que a otra escala. Un sentinel es un
--        número mágico con mejor disfraz.
--      v4 no tiene sentinels: floor(quantum/tamano_min) siempre existe y sirve
--      de respaldo de cada máximo nulo, y el tope global se expresa NULL-safe.
WITH RECURSIVE
caps AS (
  SELECT c.particion_clase_id AS cid,
         a.particion_alternativa_id AS aid,
         ROW_NUMBER() OVER (PARTITION BY a.particion_alternativa_id ORDER BY c.particion_clase_id) AS k,
         c.cardinalidad_min AS cmin,
         -- Sin sentinel. floor(quantum/tamano_min) SIEMPRE existe porque
         -- tamano_min > 0 está garantizado por CHECK, así que sirve de
         -- respaldo de cada máximo nulo. El 1000000 anterior era el mismo
         -- error que el 12, sólo que a otra escala.
         MIN(COALESCE(c.cardinalidad_max, CAST(v.texto_legal_dias / c.tamano_min AS INTEGER)),
             COALESCE(a.numero_bloques_max, CAST(v.texto_legal_dias / c.tamano_min AS INTEGER)),
             CAST(v.texto_legal_dias / c.tamano_min AS INTEGER)) AS cmax,
         c.tamano_min AS tmin,
         COALESCE(c.tamano_max, c.tamano_min) AS tmax
  FROM particion_clase c
  JOIN particion_alternativa a ON a.particion_alternativa_id = c.particion_alternativa_id
  JOIN vacaciones_version v ON v.vacaciones_version_id = a.vacaciones_version_id),
tope AS (SELECT COALESCE(MAX(cmax), 0) AS m FROM caps),
nums(i) AS (SELECT 0 UNION ALL SELECT i+1 FROM nums WHERE i < (SELECT m FROM tope)),
nclases AS (SELECT aid, MAX(k) AS n FROM caps GROUP BY aid),
comb(aid,k,bloques,smin,smax) AS (
  SELECT aid, 0, 0, 0.0, 0.0 FROM nclases
  UNION ALL
  SELECT c.aid, c.k, comb.bloques + n.i, comb.smin + n.i*c.tmin, comb.smax + n.i*c.tmax
  FROM comb
  JOIN caps c ON c.aid = comb.aid AND c.k = comb.k + 1
  JOIN nums n ON n.i BETWEEN c.cmin AND c.cmax)
SELECT 'V14 particion infactible' AS violacion, a.particion_alternativa_id
FROM particion_alternativa a
JOIN vacaciones_version v ON v.vacaciones_version_id = a.vacaciones_version_id
JOIN nclases nc ON nc.aid = a.particion_alternativa_id
WHERE NOT EXISTS (
  SELECT 1 FROM comb
  WHERE comb.aid = a.particion_alternativa_id
    AND comb.k = nc.n
    AND comb.bloques >= a.numero_bloques_min
    AND (a.numero_bloques_max IS NULL OR comb.bloques <= a.numero_bloques_max)
    AND v.texto_legal_dias BETWEEN comb.smin AND comb.smax);


-- V16 · Una celda verificada no puede sostenerse SÓLO en un instrumento externo.
--      [blocker 1 v24] La versión anterior decidía por `autoridad LIKE '%CBR%'`
--      y codex la rompió por los dos lados: falso negativo con la autoridad
--      escrita completa sin la sigla, y falso positivo con otra entidad cuyo
--      nombre la contiene. Además permitía cargar el instrumento como nivel 1.
--      Ahora decide por la clave foránea a `dataset_externo`, que es identidad,
--      no texto, y el CHECK de `fuentes` fuerza nivel 4.
SELECT 'V16 verificada solo con instrumento externo' AS violacion, m.hecho_tipo, m.hecho_id
FROM mediciones m
WHERE m.estado_verificacion IN ('verificado_primaria','verificado_secundaria')
  AND EXISTS (SELECT 1 FROM evidencia e JOIN fuentes f ON f.fuente_id = e.fuente_id
              WHERE e.hecho_id = m.hecho_id AND e.hecho_tipo = m.hecho_tipo
                AND f.dataset_externo_id IS NOT NULL)
  AND NOT EXISTS (SELECT 1 FROM evidencia e JOIN fuentes f ON f.fuente_id = e.fuente_id
                  WHERE e.hecho_id = m.hecho_id AND e.hecho_tipo = m.hecho_tipo
                    AND f.dataset_externo_id IS NULL
                    AND f.nivel_de_fuente BETWEEN 1 AND 5);

-- V17 · Censura en el tope declarada en el cruce: ahí el valor es cota
--      inferior, y usarlo como medición es el error que la tabla previene.
SELECT 'V17 censura sin causa declarada' AS violacion, cw.crosswalk_id
FROM crosswalk cw JOIN medicion_externa me USING (medicion_externa_id)
WHERE me.censurado_en_tope = 1
  AND NOT EXISTS (SELECT 1 FROM crosswalk_causa c
                  WHERE c.crosswalk_id = cw.crosswalk_id AND c.causa = 'censura');

-- V18 · La causa CONSERVA la categoría de la base normativa.
--      [blocker 3 v24] Antes 'laudo' se satisfacía declarando 'convenio', y
--      'no_determinable' no exigía nada. Eso permitía callar la validación
--      convirtiendo incertidumbre o laudo en convenio.
SELECT 'V18 base normativa sin su causa exacta' AS violacion, cw.crosswalk_id, me.base_normativa
FROM crosswalk cw JOIN medicion_externa me USING (medicion_externa_id)
WHERE me.base_normativa <> 'ley'
  AND NOT EXISTS (
    SELECT 1 FROM crosswalk_causa c
    WHERE c.crosswalk_id = cw.crosswalk_id
      AND c.causa = CASE me.base_normativa
                      WHEN 'convenio' THEN 'convenio'
                      WHEN 'laudo' THEN 'laudo'
                      WHEN 'mixta' THEN 'mixta'
                      WHEN 'no_determinable' THEN 'base_no_determinable'
                    END);

-- V19 · Igual para la regla subnacional: 'no_determinable' no se reduce
--      semánticamente a 'subnacional'.
SELECT 'V19 regla subnacional sin su causa exacta' AS violacion, cw.crosswalk_id, me.regla_subnacional_efectiva
FROM crosswalk cw JOIN medicion_externa me USING (medicion_externa_id)
WHERE me.regla_subnacional_efectiva <> 'nacional_uniforme'
  AND NOT EXISTS (
    SELECT 1 FROM crosswalk_causa c
    WHERE c.crosswalk_id = cw.crosswalk_id
      AND c.causa = CASE me.regla_subnacional_efectiva
                      WHEN 'no_determinable' THEN 'subnacional_no_determinable'
                      ELSE 'subnacional'
                    END);

-- V20 · Cobertura POR MEDICIÓN en todo lote cruzado.
--      [blocker 4 rev93] La versión anterior sólo reportaba un lote cruzado con
--      CERO cruces; un lote con dos mediciones y un solo cruce pasaba limpio.
--      La validación defensiva tiene que igualar la invariante del cierre, no
--      una versión débil de ella: si un trigger se deshabilita o el dato llega
--      importado, esto es lo único que queda.
SELECT 'V20 medicion sin cruce en lote cruzado' AS violacion, m.lote_id, m.hecho_tipo, m.hecho_id, m.corte
FROM mediciones m JOIN lote_captura l ON l.lote_id = m.lote_id
WHERE l.estado = 'cruzado'
  AND NOT EXISTS (SELECT 1 FROM crosswalk cw
                  WHERE cw.hecho_id = m.hecho_id AND cw.hecho_tipo = m.hecho_tipo
                    AND cw.corte = m.corte);

-- V21 · Desfase de año declarado. El trigger de cierre ya lo exige, pero si el
--      dato llega importado o el trigger se deshabilita, esta es la red.
SELECT 'V21 anio externo distinto del corte sin causa vintage' AS violacion,
       cw.crosswalk_id, me.anio, cw.corte
FROM crosswalk cw JOIN medicion_externa me USING (medicion_externa_id)
WHERE me.anio <> cw.corte
  AND NOT EXISTS (SELECT 1 FROM crosswalk_causa c
                  WHERE c.crosswalk_id = cw.crosswalk_id AND c.causa = 'vintage');


-- V22 · Toda versión de vacaciones tiene al menos una regla de colocación.
SELECT 'V22 version sin regla de colocacion' AS violacion, vv.vacaciones_version_id
FROM vacaciones_version vv
WHERE NOT EXISTS (SELECT 1 FROM regla_colocacion r
                  WHERE r.vacaciones_version_id = vv.vacaciones_version_id);

-- V23 · El derecho queda cubierto por completo. Tres maneras legítimas, y la
--      tercera faltaba: alcance total, residual que recoge lo no asignado, o
--      porciones que ya suman EXACTAMENTE el derecho.
--      [blocker 3 rev119] Reconocer sólo las dos primeras hacía irrepresentable
--      una partición exhaustiva: `0,5 + 0,5` sin residual cubre el 100% y se
--      reportaba como derecho sin cobertura. Un falso positivo empuja a inventar
--      un residual vacío para callar la alerta, que es corromper dato bueno.
SELECT 'V23 derecho sin cobertura de colocacion' AS violacion, vv.vacaciones_version_id
FROM vacaciones_version vv
WHERE EXISTS (SELECT 1 FROM asignacion_colocacion a
              WHERE a.vacaciones_version_id = vv.vacaciones_version_id)
  AND NOT EXISTS (SELECT 1 FROM asignacion_colocacion a
                  WHERE a.vacaciones_version_id = vv.vacaciones_version_id
                    AND a.alcance IN ('todo_el_derecho','residual'))
  -- ¿suman exacto en fracción?
  AND NOT (SELECT COALESCE(SUM(a.porcion_fraccion), -1) BETWEEN 1.0 - 1e-9 AND 1.0 + 1e-9
             FROM asignacion_colocacion a
            WHERE a.vacaciones_version_id = vv.vacaciones_version_id)
  -- ¿o exacto en días del derecho de la versión?
  AND NOT (SELECT COALESCE(SUM(a.porcion_dias), -1)
                    BETWEEN vv.texto_legal_dias - 1e-9 AND vv.texto_legal_dias + 1e-9
             FROM asignacion_colocacion a
            WHERE a.vacaciones_version_id = vv.vacaciones_version_id);

-- V23b · Y al revés: si las porciones ya suman el derecho entero, un residual
--      no recoge nada. Un residual vacío es una regla que no gobierna ningún
--      día y finge cobertura.
SELECT 'V23b residual vacio: las porciones ya suman el derecho' AS violacion,
       vv.vacaciones_version_id
FROM vacaciones_version vv
WHERE EXISTS (SELECT 1 FROM asignacion_colocacion a
              WHERE a.vacaciones_version_id = vv.vacaciones_version_id
                AND a.alcance = 'residual')
  AND ((SELECT COALESCE(SUM(a.porcion_fraccion), -1)
          FROM asignacion_colocacion a
         WHERE a.vacaciones_version_id = vv.vacaciones_version_id) >= 1.0 - 1e-9
    OR (SELECT COALESCE(SUM(a.porcion_dias), -1)
          FROM asignacion_colocacion a
         WHERE a.vacaciones_version_id = vv.vacaciones_version_id)
              >= vv.texto_legal_dias - 1e-9);

-- V24 a V27 cuentan UNIDADES DE ASIGNACIÓN, no filas: una fila por cada regla
-- de partición y una unidad por cada grupo de cascada, porque los niveles de una
-- cascada compiten por fijar la MISMA porción. Ver la vista
-- `asignacion_colocacion` en el esquema.
-- [blocker 1 rev113, residuo] Mientras filtraban por `modo_aplicacion =
-- 'particion'`, declarar una regla `fallback` la eximía de toda la aritmética:
-- 0,6 en cascada más 0,5 en partición más residual sumaban 1,1 del derecho con
-- cero violaciones. La red aritmética existía y era evadible por etiqueta.

-- V24 · Una unidad de alcance total no convive con ninguna otra unidad, sea del
--      modo que sea. Dos cascadas totales, o una total más una partición, son
--      dos reclamos sobre el mismo derecho.
SELECT 'V24 alcance total conviviendo con otra unidad' AS violacion, a.vacaciones_version_id
FROM asignacion_colocacion a
WHERE a.alcance = 'todo_el_derecho'
  AND (SELECT COUNT(*) FROM asignacion_colocacion a2
       WHERE a2.vacaciones_version_id = a.vacaciones_version_id) > 1;

-- V25 · Como máximo una unidad residual por versión. El remanente es uno solo:
--      dos residuales independientes reclaman los dos lo mismo.
SELECT 'V25 mas de una unidad residual' AS violacion, vacaciones_version_id, COUNT(*) AS n
FROM asignacion_colocacion WHERE alcance = 'residual'
GROUP BY vacaciones_version_id HAVING COUNT(*) > 1;

-- V26 · Aritmética de las porciones. [blocker 3 rev109] Dos porciones de 0,8
--      más una residual sumaban 160% y nadie decía nada: la residual acreditaba
--      cobertura por mera presencia.
SELECT 'V26 porciones en fraccion suman mas de uno' AS violacion,
       vacaciones_version_id, SUM(porcion_fraccion) AS suma
FROM asignacion_colocacion
WHERE porcion_fraccion IS NOT NULL
GROUP BY vacaciones_version_id HAVING SUM(porcion_fraccion) > 1.0 + 1e-9;

SELECT 'V26b porciones en dias exceden el derecho' AS violacion,
       a.vacaciones_version_id, SUM(a.porcion_dias) AS suma, vv.texto_legal_dias
FROM asignacion_colocacion a JOIN vacaciones_version vv USING (vacaciones_version_id)
WHERE a.porcion_dias IS NOT NULL
GROUP BY a.vacaciones_version_id
HAVING SUM(a.porcion_dias) > vv.texto_legal_dias + 1e-9;

-- V27 · Unidades no mezclables sin base de conversión: sobre una misma versión,
--      o todo en días o todo en fracción. Vale entre modos, no sólo dentro de
--      la partición: una cascada en días y una partición en fracción tampoco
--      son sumables.
SELECT 'V27 la version mezcla dias y fraccion' AS violacion, vacaciones_version_id
FROM asignacion_colocacion
GROUP BY vacaciones_version_id
HAVING SUM(porcion_dias IS NOT NULL) > 0 AND SUM(porcion_fraccion IS NOT NULL) > 0;

-- V28 · Y si son días, el tipo de día debe coincidir con el de la versión: 20
--      hábiles y 20 calendario no son la misma porción.
SELECT 'V28 tipo de dia de la porcion discrepa' AS violacion, r.regla_colocacion_id
FROM regla_colocacion r JOIN vacaciones_version vv USING (vacaciones_version_id)
WHERE r.porcion_tipo_de_dia IS NOT NULL AND r.porcion_tipo_de_dia <> vv.tipo_de_dia;

-- V29 · Toda regla de colocación tiene evidencia propia. [blocker 4 rev109]
SELECT 'V29 regla de colocacion sin evidencia' AS violacion, r.regla_colocacion_id
FROM regla_colocacion r
WHERE NOT EXISTS (SELECT 1 FROM evidencia e
                  WHERE e.hecho_id = r.regla_colocacion_id
                    AND e.hecho_tipo = 'regla_colocacion');


-- V30 · Cada grupo de cascada tiene exactamente una raíz. Sin raíz no hay regla
--      primaria y la cascada no gobierna nada; con dos, no se sabe cuál manda.
SELECT 'V30 grupo de cascada sin raiz unica' AS violacion,
       vacaciones_version_id, grupo_fallback, SUM(es_raiz_fallback) AS raices
FROM regla_colocacion WHERE modo_aplicacion = 'fallback'
GROUP BY vacaciones_version_id, grupo_fallback HAVING SUM(es_raiz_fallback) <> 1;

-- V31 · La raíz es la de menor precedencia dentro de su grupo.
SELECT 'V31 raiz de cascada fuera de orden' AS violacion, r.regla_colocacion_id
FROM regla_colocacion r
WHERE r.modo_aplicacion = 'fallback' AND r.es_raiz_fallback = 1
  AND EXISTS (SELECT 1 FROM regla_colocacion r2
              WHERE r2.vacaciones_version_id = r.vacaciones_version_id
                AND r2.grupo_fallback = r.grupo_fallback
                AND r2.orden_precedencia < r.orden_precedencia);

-- V32 · Todas las filas de un grupo de cascada gobiernan el MISMO objetivo:
--      compiten por fijar lo mismo, así que su alcance y porción coinciden.
SELECT 'V32 grupo de cascada con objetivo inconsistente' AS violacion,
       vacaciones_version_id, grupo_fallback
FROM regla_colocacion WHERE modo_aplicacion = 'fallback'
GROUP BY vacaciones_version_id, grupo_fallback
HAVING COUNT(DISTINCT alcance) > 1
    OR COUNT(DISTINCT COALESCE(porcion_dias,-1)) > 1
    OR COUNT(DISTINCT COALESCE(porcion_fraccion,-1)) > 1;

-- V33 · Un grupo de cascada de un solo nivel no es cascada: es una regla
--      simple mal etiquetada. Antes una fila suelta acreditaba cobertura.
SELECT 'V33 cascada de un solo nivel' AS violacion, vacaciones_version_id, grupo_fallback
FROM regla_colocacion WHERE modo_aplicacion = 'fallback'
GROUP BY vacaciones_version_id, grupo_fallback HAVING COUNT(*) < 2;

-- V34 · No se mezcla partición con cascada sobre la misma versión sin que la
--      cascada declare qué porción gobierna. Si hay ambos modos, ningún grupo
--      de cascada puede reclamar el derecho entero.
SELECT 'V34 cascada de alcance total conviviendo con particion' AS violacion,
       r.vacaciones_version_id
FROM regla_colocacion r
WHERE r.modo_aplicacion = 'fallback' AND r.alcance = 'todo_el_derecho'
  AND EXISTS (SELECT 1 FROM regla_colocacion r2
              WHERE r2.vacaciones_version_id = r.vacaciones_version_id
                AND r2.modo_aplicacion = 'particion');

-- V35 · Dos grupos de cascada no pueden reclamar los dos el derecho entero.
SELECT 'V35 dos cascadas reclaman todo el derecho' AS violacion, vacaciones_version_id
FROM (SELECT DISTINCT vacaciones_version_id, grupo_fallback FROM regla_colocacion
      WHERE modo_aplicacion = 'fallback' AND alcance = 'todo_el_derecho')
GROUP BY vacaciones_version_id HAVING COUNT(*) > 1;

-- V36 · Cobertura, corregida. [blocker 1 rev113] V23 aceptaba una fila fallback
--      residual suelta como cobertura completa. Ahora la cobertura por cascada
--      exige que el grupo sea válido, y eso lo garantizan V30 a V33.
SELECT 'V36 cobertura acreditada por cascada invalida' AS violacion, r.vacaciones_version_id
FROM regla_colocacion r
WHERE r.modo_aplicacion = 'fallback'
  AND r.alcance IN ('todo_el_derecho','residual')
  AND (SELECT COUNT(*) FROM regla_colocacion r2
       WHERE r2.vacaciones_version_id = r.vacaciones_version_id
         AND r2.grupo_fallback = r.grupo_fallback) < 2;

-- V37 · Un residual se define CONTRA algo. Una versión cuya única cobertura es
--      residual —sin ninguna porción definida— no está declarando un remanente:
--      está declarando el derecho entero por la puerta de atrás, y esquiva la
--      exclusividad de V24. Un derecho gobernado por una sola regla se declara
--      `todo_el_derecho`, que sí es excluyente.
SELECT 'V37 residual sin porcion definida contra la cual serlo' AS violacion,
       a.vacaciones_version_id
FROM asignacion_colocacion a
WHERE a.alcance = 'residual'
  AND NOT EXISTS (SELECT 1 FROM asignacion_colocacion a2
                  WHERE a2.vacaciones_version_id = a.vacaciones_version_id
                    AND a2.alcance = 'porcion_definida');
