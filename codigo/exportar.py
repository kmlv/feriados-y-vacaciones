"""Exporta el dataset a CSV citable — derivado de la base, nunca escrito a mano.

QUE PROBLEMA RESUELVE. Hasta ahora el producto era una base SQLite que se
regenera con un comando. Eso sirve para trabajar y no sirve para citar: quien
quiera usar el dato no va a instalar sqlite ni leer nuestro esquema de 27 tablas.
Este guion produce el paquete que se publica.

LA REGLA QUE ORDENA TODO EL DISENIO, y es la misma que el proyecto le reprocha al
antecedente: **ningun numero viaja sin su unidad**. En `vacaciones.csv` la
columna `dias_texto_legal` va pegada a `tipo_de_dia` y `base_semanal_dias`, y no
hay forma de leer una sin las otras. La cifra convertida a dias de trabajo NO
esta en ese archivo: vive aparte, en `vacaciones_convertido.csv`, porque es una
CONVENCION NUESTRA y mezclarla con el texto legal seria cometer el error que
venimos a medir.

LO QUE EL PAQUETE DECLARA ADEMAS DE LOS DATOS. Cada fila lleva su fuente con
nivel y fecha de verificacion; cada corte lleva su estado de verificacion, que
distingue «no cambio» de «no lo buscamos»; y el manifiesto lleva el hash de cada
archivo, la version del protocolo y el commit. Un dataset sin eso se puede creer
o no creer, pero no se puede auditar.

Uso:  python3 scripts/exportar.py
Sale: data/derived/export/*.csv + LEEME.md + MANIFEST.csv
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

# LAS RUTAS SE RESUELVEN CONTRA EL ARBOL QUE SE ESTE LEYENDO, y no se
# escriben aqui: en el paquete publicado el esquema, las capturas y los
# datos viven en otro sitio, y este guion tiene que arrancar en los dos.
from rutas import BASE, CAPTURAS, EXPORT, GUIONES, REPO
SALIDA = EXPORT

# Cada entrada es (nombre_archivo, glosa_para_el_LEEME, sql). El orden es el de
# publicacion: primero las unidades, luego los dos objetos medidos, luego el
# aparato de procedencia, y al final lo derivado — que va marcado como derivado.
CONSULTAS: list[tuple[str, str, str]] = [
    (
        "unidades.csv",
        "Las 47 unidades de referencia. `jurisdiccion_de_referencia` es la "
        "ciudad concreta que se midio, no el pais: en un pais federal sin ley "
        "nacional de feriados no existe «el numero del pais». Los nombres van en "
        "los dos idiomas: los paises con el nombre corto ingles de la ISO "
        "3166-1 —de ahi «Türkiye» y «Czechia»—, y las ciudades con el exonimo "
        "ingles establecido donde existe y el endonimo cuando no, que es "
        "convencion editorial y se dice.",
        """
        SELECT j.iso3                                        AS pais_iso3,
               p.nombre                                      AS pais,
               j.nombre                                      AS jurisdiccion_de_referencia,
               -- El nombre ingles viaja EN EL DATO, no solo en el documento
               -- ingles. Si viviera en la plantilla, este CSV publicable
               -- seguiria saliendo en castellano y habria dos verdades para el
               -- mismo hecho.
               p.nombre_en                                   AS pais_en,
               j.nombre_en                                   AS jurisdiccion_de_referencia_en,
               COUNT(DISTINCT f.feriado_version_id)          AS feriados_registrados,
               MAX(CASE WHEN v.vacaciones_version_id IS NOT NULL
                        THEN 1 ELSE 0 END)                   AS tiene_vacaciones
          FROM jurisdicciones j
          JOIN jurisdicciones p ON p.jurisdiccion_id = j.padre_id
          LEFT JOIN feriado_version f ON f.jurisdiccion_id = j.jurisdiccion_id
          LEFT JOIN vacaciones_version v ON v.jurisdiccion_id = j.jurisdiccion_id
         WHERE j.nivel = 'subnacional'
         GROUP BY j.iso3, p.nombre, j.nombre
         ORDER BY j.iso3
        """,
    ),
    (
        "feriados.csv",
        "`regla_id` identifica la FILA y `feriado_id` el feriado: para contar "
        "feriados se agrupa por `feriado_id`. Una REGLA DE FECHA por fila, no un feriado: desde v2.20 un feriado puede "
        "tener varias reglas —una por defecto y las alternativas condicionales—, "
        "asi que para contar feriados hay que contar `feriado` distintos por "
        "unidad y no filas. El archivo lo dice aqui porque un CSV que cambia de "
        "grano en silencio es peor que uno mal disenado. "
        "`categoria` y `regimen` son lo que decide si cuenta: no todos los dias "
        "festivos obligan a descanso pagado. OJO con `condicion_dia_semana`: un "
        "feriado puede tener VARIAS filas, una por regla, y si TODAS llevan "
        "condicion, ese feriado no ocurre en los anios en que ninguna se cumple "
        "— es el caso de los tres condicionales chilenos, que estan en el "
        "registro y no en el conteo de 2016 ni de 2026.",
        """
        SELECT r.regla_fecha_version_id                      AS regla_id,
               j.iso3                                        AS iso3,
               j.nombre                                      AS unidad,
               f.feriado_version_id                          AS feriado_id,
               f.nombre_oficial                              AS feriado,
               f.categoria                                   AS categoria,
               f.regimen                                     AS regimen,
               f.duracion_dias                               AS duracion_dias,
               f.recurrencia                                 AS recurrencia,
               f.periodo_anios                               AS periodo_anios,
               r.clase_de_regla                              AS clase_de_fecha,
               r.sistema_calendarico                         AS calendario,
               r.mes                                         AS mes,
               r.dia                                         AS dia,
               r.ordinal                                     AS ordinal,
               r.dia_semana                                  AS dia_semana,
               r.ancla                                       AS ancla,
               r.offset_dias                                 AS offset_dias,
               r.instrumento_remitido                        AS instrumento_remitido,
               r.dia_lunar_desde_fin                         AS dia_lunar_desde_fin,
               r.conjunto_de_referencia                      AS conjunto_de_referencia,
               r.condicion_referencia                        AS condicion_referencia,
               r.condicion_dia_semana                        AS condicion_dia_semana,
               f.vigencia_desde                              AS vigencia_desde,
               f.vigencia_hasta                              AS vigencia_hasta,
               f.cobertura                                   AS cobertura,
               f.elegibilidad                                AS elegibilidad,
               f.sector                                      AS sector
          FROM feriado_version f
          JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
          LEFT JOIN regla_fecha_version r
                 ON r.feriado_version_id = f.feriado_version_id
         ORDER BY j.iso3, r.mes, r.dia, f.nombre_oficial
        """,
    ),
    (
        "vacaciones.csv",
        "Una VERSION de titularidad por fila, no una unidad: desde que el panel "
        "de vacaciones dejo de ser plano, una jurisdiccion con reforma en la "
        "ventana aparece dos veces, con sus `vigencia_desde` y `vigencia_hasta` "
        "distintos. Para contar unidades, cuente `iso3` "
        "distintos. "
        "`dias_texto_legal` NO es comparable entre "
        "filas si `tipo_de_dia` difiere: 30 dias calendario peruanos y 24 "
        "Werktage alemanes no son la misma magnitud. Para comparar, "
        "`vacaciones_convertido.csv`. "
        "LA PROCEDENCIA DEL CORTE ANTIGUO VA EN COLUMNA y no en prosa, porque "
        "una afirmacion que solo se puede comprobar abriendo cuarenta y un "
        "archivos no es comprobable. `estado_2016` dice de donde sale el corte "
        "de 2016 de cada fila: `sin_cambio_confirmado` es «se busco la "
        "modificatoria y se comprobo que no existe o que no toca la cantidad», "
        "`verificado_primaria` es «la reforma esta capturada y fechada», y "
        "`supuesto` es solo «no se hallo» — que NO es evidencia de que no "
        "cambiara. Y `nivel_fuente_2016` con `rama_10bis` dicen CON QUE se "
        "confirmo, porque no vale lo mismo un indice oficial de nivel 1 que una "
        "reproduccion de nivel 3 con una tercera pantalla coincidente: son las "
        "dos ramas del §10 bis del protocolo y se publican separadas en vez de "
        "aplastarse en un unico «confirmado». `buscado_en_2016` nombra el "
        "documento que se consulto. El apendice de verificacion de cada unidad "
        "trae la misma celda con su pasaje citado.",
        """
        SELECT j.iso3                                        AS iso3,
               j.nombre                                      AS unidad,
               v.vacaciones_version_id                       AS version_id,
               v.texto_legal_dias                            AS dias_texto_legal,
               v.tipo_de_dia                                 AS tipo_de_dia,
               v.base_semanal_dias                           AS base_semanal_dias,
               v.base_semanal_origen                         AS base_semanal_origen,
               v.periodo_de_calificacion_meses               AS calificacion_meses,
               v.rango_min                                   AS rango_min,
               v.rango_max                                   AS rango_max,
               v.causa_del_rango                             AS causa_del_rango,
               v.base_antiguedad                             AS base_antiguedad,
               v.imputacion_feriados_a_vacaciones            AS imputacion_feriados,
               v.regla_de_reconocimiento                     AS regla_reconocimiento,
               v.vigencia_desde                              AS vigencia_desde,
               v.vigencia_hasta                              AS vigencia_hasta,
               v.sector                                      AS sector,
               -- LA PROCEDENCIA DEL CORTE 2016, POR CELDA. El informe afirma que
               -- decenas de celdas tienen el no-cambio «buscado y confirmado», y
               -- hasta ahora esa afirmacion no se podia comprobar desde el
               -- paquete: este archivo tenia diecisiete columnas y ninguna decia
               -- de donde sale el corte antiguo. La evidencia viajaba —en el
               -- bloque `sin_cambio` de cada captura— pero en prosa dentro de un
               -- JSON, sin columna y sin indice: para comprobar cuarenta y una
               -- habia que abrir cuarenta y un archivos.
               --
               -- Es la misma asimetria que ya se corrigio del lado de feriados,
               -- donde el panel gano su `estado_2016`. Aqui no habia equivalente
               -- porque hasta ayer no hacia falta: eran todas supuestas y no
               -- habia nada que distinguir. Hoy hay tres estados y el export los
               -- aplanaba.
               (SELECT m.estado_verificacion FROM mediciones m
                 WHERE m.hecho_id = v.vacaciones_version_id
                   AND m.hecho_tipo = 'vacaciones_version'
                   AND m.corte = 2016)                        AS estado_2016,
               -- Y EL NIVEL DE LA FUENTE QUE LO SOSTIENE, porque `confirmado` no
               -- vale lo mismo con un indice oficial de nivel 1 que con una
               -- reproduccion de nivel 3 mas pantalla 3. El §10 bis existe justo
               -- para distinguir esas dos ramas; publicar solo el estado las
               -- volveria a aplastar en el ultimo paso.
               (SELECT m.estado_verificacion FROM mediciones m
                 WHERE m.hecho_id = v.vacaciones_version_id
                   AND m.hecho_tipo = 'vacaciones_version'
                   AND m.corte = 2026)                        AS estado_2026
          FROM vacaciones_version v
          JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id
         ORDER BY j.iso3
        """,
    ),
    (
        "escala_antiguedad.csv",
        "Tramos de antiguedad, donde la titularidad no es un numero unico. "
        "`literal_normativo` guarda la frase de la ley que fija el tramo.",
        """
        SELECT j.iso3                                        AS iso3,
               j.nombre                                      AS unidad,
               e.desde_meses                                 AS desde_meses,
               e.hasta_meses                                 AS hasta_meses,
               e.operador_frontera                           AS operador_frontera,
               e.quantum                                     AS dias,
               e.tipo_de_dia                                 AS tipo_de_dia,
               e.literal_normativo                           AS literal_normativo
          FROM escala_antiguedad e
          JOIN vacaciones_version v
            ON v.vacaciones_version_id = e.vacaciones_version_id
          JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id
         ORDER BY j.iso3, e.desde_meses
        """,
    ),
    (
        "colocacion.csv",
        "Quien decide CUANDO se toman las vacaciones. Un derecho de 30 dias que "
        "fija el empleador sin veto del trabajador no es el mismo bien que 30 "
        "dias de eleccion libre, y el numero solo no lo distingue. "
        "`resolucion_desacuerdo` dice que pasa cuando la negociacion no llega a "
        "acuerdo: sin esa columna, Peru y Grecia parecen iguales y resuelven en "
        "direcciones opuestas.",
        """
        SELECT j.iso3                                        AS iso3,
               j.nombre                                      AS unidad,
               c.orden_precedencia                           AS orden,
               c.modo_aplicacion                             AS modo,
               c.alcance                                     AS alcance,
               c.porcion_dias                                AS porcion_dias,
               c.porcion_fraccion                            AS porcion_fraccion,
               c.iniciativa                                  AS iniciativa,
               c.veto_empleador                              AS veto_empleador,
               c.default_ante_silencio                       AS default_ante_silencio,
               c.resolucion_desacuerdo                       AS resolucion_desacuerdo,
               c.instrumento                                 AS instrumento,
               c.literal_normativo                           AS literal_normativo
          FROM regla_colocacion c
          JOIN vacaciones_version v
            ON v.vacaciones_version_id = c.vacaciones_version_id
          JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id
         ORDER BY j.iso3, c.orden_precedencia
        """,
    ),
    (
        "fuentes.csv",
        "Toda fuente citada, con su nivel. Nivel 1 es gaceta oficial; nivel 4 es "
        "fuente secundaria sin confirmar. El nivel se declara, no se maquilla.",
        """
        SELECT COALESCE(j.iso3, '')                          AS iso3,
               COALESCE(j.nombre, '(sin unidad)')            AS unidad,
               s.autoridad                                   AS autoridad,
               s.nivel_de_fuente                             AS nivel,
               s.fecha_de_norma                              AS fecha_de_norma,
               s.url                                         AS url,
               s.version_archivada                           AS version_archivada
          FROM fuentes s
          LEFT JOIN jurisdicciones j ON j.jurisdiccion_id = s.jurisdiccion_id
         ORDER BY s.nivel_de_fuente, j.iso3
        """,
    ),
    (
        "evidencia.csv",
        "El puente entre cada hecho y la fuente que lo respalda. Es lo que hace "
        "auditable el dataset: cualquier fila de feriados o vacaciones se puede "
        "seguir hasta el documento.",
        """
        SELECT ev.hecho_tipo                                 AS hecho_tipo,
               ev.hecho_id                                   AS hecho_id,
               COALESCE(jf.iso3, jv.iso3, '')                AS iso3,
               COALESCE(f.nombre_oficial, 'vacaciones')      AS hecho,
               s.autoridad                                   AS autoridad,
               s.nivel_de_fuente                             AS nivel_fuente,
               s.url                                         AS url,
               ev.fecha_de_verificacion                      AS verificado_en,
               ev.revisor                                    AS revisor
          FROM evidencia ev
          JOIN fuentes s ON s.fuente_id = ev.fuente_id
          LEFT JOIN feriado_version f
                 ON f.feriado_version_id = ev.hecho_id
                AND ev.hecho_tipo = 'feriado_version'
          LEFT JOIN jurisdicciones jf ON jf.jurisdiccion_id = f.jurisdiccion_id
          LEFT JOIN vacaciones_version v
                 ON v.vacaciones_version_id = ev.hecho_id
                AND ev.hecho_tipo = 'vacaciones_version'
          LEFT JOIN jurisdicciones jv ON jv.jurisdiccion_id = v.jurisdiccion_id
         ORDER BY iso3, ev.hecho_tipo
        """,
    ),
    (
        "panel_feriados.csv",
        "DERIVADO. Conteo por corte, obtenido preguntando a la base que feriados "
        "estaban vigentes en cada fecha. **`estado_2016` es la columna que mas "
        "importa** y durante un tiempo este archivo la prometia sin emitirla: "
        "`verificado` es que las modificatorias de la ventana estan localizadas y "
        "datadas; `verificado_parcial`, que se verifico el conteo y hay cambio de "
        "regla sin cambio de cantidad; `supuesto_sin_cambio`, que NO se hallo "
        "modificatoria — ausencia no verificada, no ausencia; y `no_capturado`, "
        "que ese corte no se leyo y no se rellena con el otro. **`feriados_*` "
        "cuenta TODO dia festivo capturado y `exigibles_*` solo el descanso "
        "pagado obligatorio**, que es lo que la metrica principal usa: para "
        "Estados Unidos son doce y cero, porque sus feriados son cierre del "
        "sector publico y ninguno obliga al empleador privado.",
        """
        SELECT j.iso3                                        AS iso3,
               j.nombre                                      AS unidad,
               SUM(CASE WHEN m.corte = 2016 THEN f.duracion_dias ELSE 0 END)
                                                             AS feriados_2016,
               SUM(CASE WHEN m.corte = 2026 THEN f.duracion_dias ELSE 0 END)
                                                             AS feriados_2026,
               -- EL SUBCONJUNTO EXIGIBLE, en su propia columna. Las tres cosas
               -- que hay que saber del paquete incluyen «no todo dia festivo
               -- cuenta: filtre por regimen» — y este archivo no traia con que
               -- filtrar. Una instruccion que el dato no permite cumplir es peor
               -- que ninguna, porque el lector cree haberla seguido.
               --
               -- Donde mas duele: los doce de Estados Unidos son cierre del
               -- sector publico y ninguno obliga al empleador privado, asi que
               -- la metrica principal le da CERO mientras este panel publicaba
               -- doce. Dos numeros nuestros, en el mismo paquete, diciendo cosas
               -- distintas del mismo pais.
               SUM(CASE WHEN m.corte = 2016
                         AND f.categoria = 'descanso_pagado_obligatorio'
                        THEN f.duracion_dias ELSE 0 END)   AS exigibles_2016,
               SUM(CASE WHEN m.corte = 2026
                         AND f.categoria = 'descanso_pagado_obligatorio'
                        THEN f.duracion_dias ELSE 0 END)   AS exigibles_2026
          FROM mediciones m
          JOIN feriado_version f
            ON f.feriado_version_id = m.hecho_id
           AND m.hecho_tipo = 'feriado_version'
           -- Un feriado condicional que ese anio no ocurre esta medido con
           -- `na`: se evaluo y no aplica. Sumarlo contaria un dia que no hubo.
           AND m.estado_verificacion <> 'na'
          JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
         GROUP BY j.iso3, j.nombre
         ORDER BY j.iso3
        """,
    ),
]

# Conversion a una unidad comun. Es NUESTRA convencion y se publica aparte por
# eso mismo. El factor de calendario a dias de trabajo es 5/7; el de Werktage
# —que excluyen domingo pero incluyen sabado— es 5/6; semanas van a 5 dias.
CONVERSION = """
    SELECT j.iso3                                            AS iso3,
           j.nombre                                          AS unidad,
           v.texto_legal_dias                                AS dias_texto_legal,
           v.tipo_de_dia                                     AS tipo_de_dia,
           -- Va aqui a proposito. Sin esta columna, quien lea SOLO el archivo
           -- convertido no puede distinguir un pais cuya norma declara la base
           -- —Alemania, seis dias— de uno donde la base la ponemos nosotros
           -- —Peru no declara ninguna—. Los dos numeros convertidos se ven
           -- igual de firmes y no lo son.
           COALESCE(v.base_semanal_origen, 'no declarada por la norma')
                                                             AS base_segun,
           ROUND(CASE v.tipo_de_dia
                   WHEN 'habil'      THEN v.texto_legal_dias
                   WHEN 'calendario' THEN v.texto_legal_dias * 5.0 / 7.0
                   WHEN 'werktage'   THEN v.texto_legal_dias * 5.0 / 6.0
                   WHEN 'semanas'    THEN v.texto_legal_dias * 5.0
                 END, 1)                                     AS dias_trabajo_semana5,
           'semana de 5 dias'                                AS supuesto
      FROM vacaciones_version v
      JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id
     WHERE v.tipo_de_dia IS NOT NULL
     ORDER BY j.iso3
"""


def escribir(con: sqlite3.Connection, nombre: str, sql: str) -> tuple[int, str]:
    """Vuelca una consulta a CSV y devuelve (filas, sha256)."""
    cur = con.execute(sql)
    cabecera = [d[0] for d in cur.description]
    ruta = SALIDA / nombre
    filas = 0
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cabecera)
        for fila in cur:
            w.writerow(["" if c is None else c for c in fila])
            filas += 1
    return filas, hashlib.sha256(ruta.read_bytes()).hexdigest()


def version_publicada_() -> str:
    """El commit que sella la exportacion es el del repositorio PUBLICO.

    Esta funcion leia el HEAD de ESTE repositorio y lo escribia en el manifiesto,
    que viaja dentro del paquete. El sello de `SNAPSHOT.json` ya se habia
    corregido para no hacerlo —el repositorio publico arranca con historial
    limpio, asi que el hash privado no resuelve a nada que el lector pueda
    consultar— y esta puerta se quedo abierta. El paquete salia con el
    identificador interno igualmente, un archivo mas alla.

    Es el defecto que este proyecto ya conoce: **se arregla donde se encontro y
    no donde vive.** Por eso el arreglo no es un parche aqui, es la misma regla
    que en el sello, escrita una sola vez y usada en los dos sitios.

    Sin `VERSION_PUBLICA` dice `sin-publicar`, que es la verdad de esa copia, y NO
    repliega al hash privado: el repliegue silencioso volveria a publicarlo con
    la diferencia de que ya nadie estaria mirando.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from reportes_nucleo import version_publicada
    return version_publicada()


def main() -> int:
    if not BASE.exists():
        sys.exit("no existe %s — corre antes scripts/cargar_piloto.py"
                 % BASE.relative_to(REPO))
    SALIDA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(BASE)

    manifiesto: list[tuple[str, int, str]] = []
    glosas: list[tuple[str, str]] = []
    for nombre, glosa, sql in CONSULTAS:
        filas, sha = escribir(con, nombre, sql)
        manifiesto.append((nombre, filas, sha))
        glosas.append((nombre, glosa))
        print("  %-26s %4d filas" % (nombre, filas))

    filas, sha = escribir(con, "vacaciones_convertido.csv", CONVERSION)
    manifiesto.append(("vacaciones_convertido.csv", filas, sha))
    glosas.append(("vacaciones_convertido.csv",
                   "DERIVADO Y CONVENCIONAL. La conversion a dias de trabajo "
                   "sobre semana de 5 la decidimos nosotros, no la ley. Se "
                   "publica aparte para que nadie la confunda con el texto "
                   "legal, y con el supuesto en su propia columna."))
    print("  %-26s %4d filas" % ("vacaciones_convertido.csv", filas))

    # `estado_2016` vive en las capturas y no en la base, asi que el panel salia
    # sin la columna que su propio LEEME declara crucial: sin ella no se puede
    # separar «no hubo reforma» de «no se busco», que es la advertencia que el
    # paquete repite en todas partes. Se anade leyendo el estado con la misma
    # funcion que usa `panel.py`, para que no haya dos definiciones.
    import importlib.util
    spec = importlib.util.spec_from_file_location("pan", GUIONES / "panel.py")
    pan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pan)
    estados = pan.estados_del_corte()
    ruta = SALIDA / "panel_feriados.csv"
    filas_panel = list(csv.DictReader(ruta.open(encoding="utf-8")))
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(list(filas_panel[0]) + ["estado_2016"])
        for f in filas_panel:
            w.writerow(list(f.values()) + [estados.get(f["iso3"], "no_capturado")])
    for i, (nombre, filas_n, _) in enumerate(manifiesto):
        if nombre == "panel_feriados.csv":
            manifiesto[i] = (nombre, filas_n,
                             hashlib.sha256(ruta.read_bytes()).hexdigest())

    # UNA UNIDAD SIN VACACIONES TIENE QUE DECIR POR QUE, y hasta ahora no lo
    # decia. `tiene_vacaciones` valia 0 para dos unidades y el lector no podia
    # distinguir los dos casos, que son opuestos:
    #
    #   Estados Unidos  NO EXISTE el derecho. Se busco —la ley federal de normas
    #                   laborales no exige vacaciones pagadas y ningun estado
    #                   impone un minimo general al sector privado— y la
    #                   respuesta es que no hay cantidad que medir.
    #   Bolivia         SI EXISTE y no lo hemos resuelto: quince dias, pero
    #                   falta decidir si son habiles o calendario, y resolverlo
    #                   mal introduce un error de factor.
    #
    # Un cero que agrupa «no hay derecho» con «no lo sabemos» es la misma
    # confusion que el paquete denuncia en el antecedente externo, cometida por
    # nosotros. Y la distincion ya estaba escrita en las capturas: lo que
    # faltaba era publicarla.
    # EL NIVEL Y LA RAMA DEL §10 BIS, que viven en la captura y no en la base.
    # `estado_2016` ya sale de `mediciones`, pero «confirmado» no dice CON QUE:
    # España se apoya en un índice oficial de nivel 1 y Guatemala en una
    # reproducción de nivel 3 más pantalla 3. Las dos son confirmadas y no valen
    # lo mismo — el §10 bis existe para separarlas, y publicar sólo el estado las
    # volvería a aplastar en el último paso.
    ruta_v = SALIDA / "vacaciones.csv"
    filas_v = list(csv.DictReader(ruta_v.open(encoding="utf-8")))
    ev = {}
    for carpeta in sorted(CAPTURAS.iterdir()):
        if not carpeta.is_dir():
            continue
        for nombre_f in ("captura.json", "captura-feriados.json",
                         "captura-doble.json"):
            f = carpeta / nombre_f
            if not f.exists():
                continue
            cap = json.loads(f.read_text(encoding="utf-8"))
            v = cap.get("vacaciones_normalizado") or cap.get("vacaciones") or {}
            sc = v.get("sin_cambio")
            if isinstance(sc, dict):
                nivel = sc.get("nivel_de_fuente")
                rama = ("a" if (isinstance(nivel, int) and nivel <= 2
                                and sc.get("indice_registra_modificaciones") is True)
                        else "b" if sc.get("pantalla_3") else "")
                ev[cap.get("unidad")] = (nivel if nivel is not None else "",
                                         rama, sc.get("buscado_en", ""))
            break
    with ruta_v.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(list(filas_v[0]) + ["nivel_fuente_2016", "rama_10bis",
                                       "buscado_en_2016"])
        for f in filas_v:
            n, r, b = ev.get(f["iso3"], ("", "", ""))
            w.writerow(list(f.values()) + [n, r, " ".join(str(b).split())])
    for i, (nombre, filas_n, _) in enumerate(manifiesto):
        if nombre == "vacaciones.csv":
            manifiesto[i] = (nombre, filas_n,
                             hashlib.sha256(ruta_v.read_bytes()).hexdigest())

    ruta_u = SALIDA / "unidades.csv"
    filas_u = list(csv.DictReader(ruta_u.open(encoding="utf-8")))
    razones = {}
    for carpeta in sorted((CAPTURAS).iterdir()):
        if not carpeta.is_dir():
            continue
        for nombre_f in ("captura.json", "captura-feriados.json",
                         "captura-doble.json"):
            f = carpeta / nombre_f
            if not f.exists():
                continue
            cap = json.loads(f.read_text(encoding="utf-8"))
            v = cap.get("vacaciones_normalizado") or cap.get("vacaciones") or {}
            iso = cap.get("unidad")
            if v.get("no_aplicable"):
                razones[iso] = ("no_aplicable",
                                v["no_aplicable"].get("motivo", ""))
            elif v.get("pendiente"):
                razones[iso] = ("pendiente", v["pendiente"])
            elif v.get("dias") is None or v.get("tipo") is None:
                razones.setdefault(iso, ("pendiente",
                                         "la captura no resuelve la cantidad o "
                                         "el tipo de día"))
            break
    with ruta_u.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(list(filas_u[0]) + ["vacaciones_ausencia",
                                       "vacaciones_ausencia_motivo"])
        for f in filas_u:
            e, m = ("", "")
            if f["tiene_vacaciones"] in ("0", 0):
                e, m = razones.get(f["pais_iso3"],
                                   ("no_declarado",
                                    "sin fila de vacaciones y sin motivo "
                                    "declarado en la captura"))
            w.writerow(list(f.values()) + [e, " ".join(m.split())])
    for i, (nombre, filas_n, _) in enumerate(manifiesto):
        if nombre == "unidades.csv":
            manifiesto[i] = (nombre, filas_n,
                             hashlib.sha256(ruta_u.read_bytes()).hexdigest())

    protocolo = con.execute(
        "SELECT version, hash FROM protocolo_congelado "
        "ORDER BY congelado_en DESC LIMIT 1").fetchone() or ("desconocida", "")
    lote = con.execute(
        "SELECT etiqueta FROM lote_captura ORDER BY lote_id LIMIT 1").fetchone()
    con.close()

    with (SALIDA / "MANIFEST.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["archivo", "filas", "sha256"])
        for fila in manifiesto:
            w.writerow(fila)
        w.writerow(["__protocolo__", protocolo[0], protocolo[1]])
        w.writerow(["__lote__", "", lote[0] if lote else "sin lote"])
        w.writerow(["__version_publicada__", "", version_publicada_()])

    (SALIDA / "LEEME.md").write_text(leeme(glosas, manifiesto, protocolo),
                                     encoding="utf-8")
    print("\nEscrito en %s — %d archivos + MANIFEST.csv + LEEME.md"
          % (SALIDA.relative_to(REPO), len(manifiesto)))
    return 0


def leeme(glosas, manifiesto, protocolo) -> str:
    filas = {n: f for n, f, _ in manifiesto}
    tabla = "\n".join(
        "### `%s` — %d filas\n\n%s\n" % (n, filas[n], g) for n, g in glosas)
    return f"""# Feriados y vacaciones legales — exportacion

Generado por `scripts/exportar.py` desde `data/derived/piloto.db`.
**No editar a mano.** Cualquier correccion va en la captura de origen
(`data/raw/<unidad>/captura.json`) y se regenera el paquete.

Protocolo **{protocolo[0]}** · commit y hashes en `MANIFEST.csv`.

## Lo que hay que saber antes de usar estos numeros

**1. Ningun numero de vacaciones es comparable sin su unidad.** La ley peruana
concede 30 dias *calendario*; la alemana, 24 *Werktage*; la de Ontario, 2
*semanas*. Son tres magnitudes distintas. Por eso `dias_texto_legal` viaja
siempre pegado a `tipo_de_dia` y `base_semanal_dias`, y por eso la version
convertida esta en otro archivo. Si vas a promediar, usa
`vacaciones_convertido.csv` y **cita el supuesto**.

**2. No todo dia festivo cuenta.** En Francia solo el 1 de mayo obliga por ley a
descanso pagado; los demas dependen del convenio. En Tailandia la ley nombra uno
y deja doce a designacion del empleador. Filtra por `categoria` y `regimen`
segun lo que quieras medir, y di cual usaste.

**3. Ausencia no verificada no es ausencia.** En `panel_feriados.csv`, un delta
de cero entre 2016 y 2026 puede significar que no hubo reforma o que no la
buscamos. La distincion esta declarada y no se rellena por conveniencia.

**4. La unidad de referencia es una jurisdiccion concreta, no un pais.** Para
Alemania medimos Berlin; para Australia, Sidney. En paises federales sin ley
nacional de feriados no existe «el numero del pais», y promediar estados seria
inventar una cifra que ninguna ley concede.

## Archivos

{tabla}
## Como citar una fila

Toma su `iso3` y el hecho, busca en `evidencia.csv` la fuente con su nivel y
fecha de verificacion, y cita esa norma. El dataset no pide que se le crea: pide
que se le siga hasta el documento.
"""


if __name__ == "__main__":
    raise SystemExit(main())
