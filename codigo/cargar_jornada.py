"""Normaliza las 47 capturas de jornada y las carga en `regimen_jornada`.

POR QUE EXISTE APARTE DEL CARGADOR PRINCIPAL. La jornada se capturó en cinco
lotes con una plantilla que dejé con ejemplos en vez de con dominios cerrados, y
cada lote la extendió de forma razonable y distinta. La normalización vive aquí,
en un solo sitio y a la vista, **y no reescribiendo las capturas ajenas**:
uniformar el archivo de otro borra la razón por la que lo escribió así.

LAS DOS DECISIONES DE CARGA, declaradas:

1 · SE CARGA EL VALOR VIGENTE AL 1 DE ENERO DEL AÑO DEL CORTE. México y Chile
    cambian de jornada a mitad de 2026 —Chile pasa a 42 el 26 de abril— y
    Colombia venía de una escalera. La fecha no se elige aquí: es la que el
    proyecto ya usa en `mediciones.fecha_efectiva_de_medicion`, y usar otra haría
    que la jornada y los feriados se midieran en momentos distintos del mismo
    corte. La escalera completa se conserva en la captura.

2 · MECANISMO Y EFECTO SON DOS CAMPOS. Qué hace la norma cuando un feriado cae en
    el descanso semanal, y qué acaba recibiendo el trabajador, son preguntas
    distintas. Polonia no traslada nada: reduce en ocho horas la cuota del
    período, mecanismo raro y efecto idéntico al de un traslado. Italia tiene un
    mecanismo fácil de entender y efecto cero en días.

NADA SE INFIERE EN SILENCIO. Toda unidad que no case con una regla explícita se
reporta al final; el guion no la mete en un valor por defecto sin decirlo.

Uso:  python3 scripts/cargar_jornada.py [--corte 2026]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# LAS RUTAS SE RESUELVEN CONTRA EL ARBOL QUE SE ESTE LEYENDO, y no se
# escriben aqui: en el paquete publicado el esquema, las capturas y los
# datos viven en otro sitio, y este guion tiene que arrancar en los dos.
from rutas import BASE, CAPTURAS, GUIONES, REPO
CRUDO = CAPTURAS

# Cinco vocabularios a cuatro. El mapeo se escribe, no se adivina.
ORIGEN = {
    "norma": "declarado", "declarado_en_la_ley": "declarado",
    "derivado_de_topes": "derivado", "derivado": "derivado",
    "rango_legal": "alternativa_legal", "alternativa_legal": "alternativa_legal",
    "bifurcacion_expresa": "alternativa_legal",
    "no_declarado": "no_declarado", None: "no_declarado",
}

# (mecanismo, efecto) por unidad, leído del literal de cada captura. Va como
# tabla explícita y no como heurística sobre el texto libre: una heurística que
# clasifique mal a un país lo hace en silencio, y aquí cada fila se puede
# discutir contra su literal.
TRASLADO = {
    # Dan un día libre.
    "BEL": ("traslada", "dia_libre"), "BOL": ("traslada", "dia_libre"),
    "BGR": ("traslada", "dia_libre"), "CAN": ("traslada", "dia_libre"),
    "COL": ("traslada", "dia_libre"), "KOR": ("traslada", "dia_libre"),
    "ECU": ("traslada", "dia_libre"), "ESP": ("traslada", "dia_libre"),
    "JPN": ("traslada", "dia_libre"), "NZL": ("traslada", "dia_libre"),
    "GBR": ("traslada", "dia_libre"), "THA": ("traslada", "dia_libre"),
    # Australia SUMA un día en Navidad, Boxing Day y Año Nuevo, y sustituye en el
    # Día de Australia. Añadir no es trasladar y por eso lleva valor propio.
    "AUS": ("anade_dia", "dia_libre"),
    # Polonia no mueve nada: el art. 130 §2 reduce en ocho horas la cuota del
    # período por cada feriado que caiga en día distinto del domingo. LIMITE
    # DECLARADO: por eso el sábado sí da día y el domingo no, y esta columna
    # guarda un solo valor por jurisdicción.
    "POL": ("reduce_cuota_de_horas", "dia_libre"),
    # Dan dinero, o el empleador elige.
    "ITA": ("compensa_en_dinero", "dinero"),
    "IRL": ("compensa_a_eleccion", "dia_o_dinero_a_eleccion"),
    # Hay regla y no entrega nada. Un cero con norma detrás no es un cero por
    # omisión, y por eso no se confunde con el silencio.
    "HND": ("regla_sin_efecto", "ninguno"),
    # La pérdida está ESCRITA, no se deduce del silencio. Los cuatro tienen
    # anclaje textual negativo: la norma dice expresamente que ahí no hay nada.
    "PER": ("se_pierde", "ninguno"),   # art. 7: «se celebrarán en la fecha respectiva»
    "DOM": ("se_pierde", "ninguno"),   # art. 165: «salvo que coincidan con el descanso»
    "DEU": ("se_pierde", "ninguno"),   # ArbZG §11(3) compensa sólo el feriado «en día laborable»
    "CHE": ("se_pierde", "ninguno"),   # LTr art. 21 QUITA el medio día libre en semanas con feriado
    # La ley dice que se compensa y no dice con qué. Elegir por ella sería imputar.
    "NIC": ("compensa_a_eleccion", "indeterminado"),
    # No puede haber regla porque no existe feriado legal pagado.
    "NLD": ("no_aplicable", "ninguno"), "DNK": ("no_aplicable", "ninguno"),
    "USA": ("no_aplicable", "ninguno"),
}
POR_DEFECTO = ("sin_regla", "ninguno")     # silencio, y se reporta cuál cayó aquí

# RECLASIFICACION DEL ORIGEN, leyendo los literales uno por uno. El principal
# pregunto si Peru «de verdad trabaja seis dias por ley», y al leer las nueve
# unidades de seis salio un patron que ninguna captura habia visto entera:
#
#   NINGUNA norma de este grupo manda trabajar seis dias. Todas fijan TECHOS
#   —ocho horas diarias y cuarenta y ocho semanales— o un ritmo de descanso
#   —«un dia por cada seis de trabajo continuo»—, y de ahi alguien dedujo el
#   seis. Un techo dice cuanto se PUEDE, no cuanto se trabaja, y «descanso tras
#   seis dias consecutivos» prohibe el septimo: tampoco obliga al sexto.
#
# Y la asimetria es la parte publicable: las que legislan semana de cinco LO
# DICEN con esas palabras —Bulgaria «la semana de trabajo es de cinco dias»,
# Hungria «de lunes a viernes», Polonia, Chequia, Rumania, Eslovaquia—. El seis
# nunca esta escrito; el cinco si.
#
# Es la MISMA leccion que ya me mordio dos veces: la base de la norma de
# vacaciones no es la semana real, el descanso minimo garantizado tampoco, y
# ahora el maximo legal de dias tampoco. Un limite no describe una practica.
CEILING = {
    "PER": "art. 25: «ocho horas diarias O cuarenta y ocho semanales, como maximo». "
           "La disyuntiva la marco la propia captura y aun asi el campo decia norma.",
    "DEU": "la ArbZG no escribe cifra semanal; el 48 y el 6 salen de multiplicar "
           "ocho horas por los Werktage que el § 9 deja disponibles.",
    "BOL": "48 sobre un tope de 8 exigen seis; el art. 41 solo excluye el domingo.",
    "MEX": "el art. 59 fija horas; el seis sale de 48 entre 8.",
    "PRY": "declarado derivado por la propia captura: 48 entre 8.",
    "THA": "declarado derivado por la propia captura; la seccion 28 fija el "
           "intervalo MAXIMO entre descansos, que es otro techo.",
    "CRI": "el art. 59 constitucional fija «un dia de descanso despues de seis dias "
           "consecutivos»: prohibe el septimo, no obliga al sexto.",
    "NIC": "el art. 64 dice «por cada seis dias de trabajo continuo» — mismo techo.",
    "HND": "el art. 338 dice «por cada seis (6) de trabajo», y ademas 44 entre 6 da "
           "7,33 horas: la practica reparte cinco jornadas y medio sabado.",
}

# Horas semanales al 1 de enero del corte, donde la captura trae la escalera en
# PROSA dentro de `reformas_en_la_ventana` y su cifra de portada es la de hoy.
# Va como tabla y no parseando el texto: extraer números de prosa libre es
# frágil de una forma que no avisa cuando falla, y aquí cada entrada se puede
# contrastar con la nota de su propia captura.
HORAS_AL_CORTE = {
    2026: {
        # «Las 42 horas rigen desde el 15 de julio de 2026. Al corte del 1 de
        # enero de 2026 el tope era de 44» — nota de la propia captura.
        "COL": (44.0, "Ley 2101 de 2021: 44 desde el 15-jul-2025, 42 desde el 15-jul-2026"),
    },
}


def carpeta_por_iso3() -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("c", GUIONES / "cargar_piloto.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return {v[0]: k for k, v in m.UNIDADES.items()}


def vigente_al_corte(cap: dict, corte: int):
    """Horas semanales vigentes el 1 de enero del año del corte.

    Cuando la captura trae escalera fechada se lee de ella; si no, se usa el
    valor de portada. La escalera es lo que hace que Chile y México no mientan:
    los dos cambian a mitad de 2026 y su cifra «de 2026» sería ambigua.
    """
    etapas = cap.get("horas_semanales_por_etapa") or cap.get("etapas") or []
    limite = "%d-01-01" % corte
    mejor, fecha_mejor = None, None
    for e in etapas if isinstance(etapas, list) else []:
        desde = str(e.get("desde") or e.get("vigencia_desde") or "")
        horas = e.get("horas") or e.get("horas_semanales_max")
        if len(desde) == 10 and desde <= limite and horas is not None:
            if fecha_mejor is None or desde > fecha_mejor:
                mejor, fecha_mejor = horas, desde
    if mejor is not None:
        return float(mejor), fecha_mejor
    j = cap.get("jornada") or {}
    return (float(j["horas_semanales_max"])
            if j.get("horas_semanales_max") is not None else None), None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", type=int, default=2026)
    args = ap.parse_args()
    con = sqlite3.connect(BASE)
    con.execute("PRAGMA foreign_keys = ON")

    # Repetible: se limpia antes de cargar. Sin esto, correrlo dos veces —lo que
    # pasa en cuanto alguien lo invoca a mano despues de `cargar_piloto.py`, que
    # ya lo llama— revienta por clave duplicada en vez de rehacer el trabajo.
    # Un cargador de datos derivados que no se puede repetir invita a parchear.
    con.execute("DELETE FROM evidencia WHERE hecho_tipo='regimen_jornada'")
    con.execute("DELETE FROM regimen_jornada")
    con.execute("DELETE FROM hechos WHERE hecho_tipo='regimen_jornada'")

    juris = {i: j for i, j in con.execute(
        "SELECT iso3, jurisdiccion_id FROM jurisdicciones WHERE nivel='subnacional'")}
    siguiente = (con.execute("SELECT COALESCE(MAX(hecho_id),0) FROM hechos").fetchone()[0])

    cargadas, sin_archivo, por_defecto, escalonadas = [], [], [], []
    for iso3, carpeta in sorted(carpeta_por_iso3().items()):
        ruta = CRUDO / carpeta / "jornada.json"
        if not ruta.exists():
            sin_archivo.append(iso3)
            continue
        cap = json.loads(ruta.read_text())
        j = cap.get("jornada") or {}
        d = cap.get("descanso_semanal") or {}
        t = cap.get("traslado_por_defecto") or {}

        horas_sem, fecha_etapa = vigente_al_corte(cap, args.corte)
        forzado = HORAS_AL_CORTE.get(args.corte, {}).get(iso3)
        if forzado:
            horas_sem, fecha_etapa = forzado[0], forzado[1]
        if fecha_etapa:
            escalonadas.append((iso3, horas_sem, fecha_etapa))
        origen_crudo = j.get("dias_ordinarios_origen")
        if origen_crudo not in ORIGEN:
            print("  vocabulario no previsto en %s: %r" % (iso3, origen_crudo))
            return 1
        origen = ORIGEN[origen_crudo]
        if iso3 in CEILING:
            # Lo capturado es el MAXIMO que la ley tolera, no la semana ordinaria.
            origen = "derivado"
        mecanismo, efecto = TRASLADO.get(iso3, POR_DEFECTO)
        if iso3 not in TRASLADO:
            por_defecto.append(iso3)

        siguiente += 1
        con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,'regimen_jornada')",
                    (siguiente,))
        con.execute("""
            INSERT INTO regimen_jornada
              (regimen_jornada_id, jurisdiccion_id, sector, vigencia_desde,
               dias_descanso_semanal, dias_descanso_semanal_n,
               horas_semanales_max, horas_diarias_max, umbral_horas_extra,
               dias_ordinarios, dias_ordinarios_origen,
               regla_traslado_defecto, efecto_traslado, literal_normativo)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (siguiente, juris[iso3], "privado", "%d-01-01" % args.corte,
             d.get("cuales") or "la ley no garantiza ninguno",
             d.get("dias"), horas_sem, j.get("horas_diarias_max"),
             j.get("umbral_horas_extra_semanal") or cap.get("umbral_horas_extra_semanal"),
             j.get("dias_ordinarios"), origen, mecanismo, efecto,
             (j.get("literal") or "")[:2000] or None))
        # Evidencia: la primera fuente declarada de la captura de jornada.
        fuentes = cap.get("fuentes") or {}
        if fuentes:
            clave = sorted(fuentes)[0]
            f = fuentes[clave]
            # La fecha de norma solo entra si es una fecha completa. Los lotes
            # escribieron desde «2003-06-10» hasta «1974» y hasta prosa; el
            # esquema exige ISO y tiene razon. Lo que no es fecha se descarta
            # AQUI y no se fuerza: media fecha en una columna de fechas es peor
            # que ninguna, porque se ordena y se compara como si fuera entera.
            pub = str(f.get("publicacion") or "")
            fecha_norma = pub if (len(pub) == 10 and pub[4] == "-" and pub[7] == "-"
                                  and pub[:4].isdigit()) else None
            fid = con.execute("SELECT COALESCE(MAX(fuente_id),0)+1 FROM fuentes").fetchone()[0]
            con.execute(
                "INSERT INTO fuentes (fuente_id,url,version_archivada,autoridad,"
                "jurisdiccion_id,fecha_de_norma,nivel_de_fuente) VALUES (?,?,?,?,?,?,?)",
                (fid, f.get("url") or "sin-url-archivada", "PENDIENTE DE ARCHIVAR",
                 (f.get("cita") or clave)[:120], juris[iso3],
                 fecha_norma, int(f.get("nivel_de_fuente", 6))))
            con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                        "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                        (siguiente, "regimen_jornada", fid, "2026-08-11", "captura-jornada"))
        cargadas.append(iso3)
    con.commit()

    print("\nJORNADA CARGADA · corte %d\n" % args.corte)
    print("  %d de %d unidades" % (len(cargadas), len(juris)))
    if sin_archivo:
        print("  SIN CAPTURA: %s" % ", ".join(sin_archivo))
    if escalonadas:
        print("\n  Con escalera fechada, se tomó lo vigente al 1 de enero:")
        for iso, h, f in escalonadas:
            print("    %-4s %g horas, escalón de %s" % (iso, h, f))
    print("\n  %d unidades cayeron en el valor por defecto de traslado (silencio):"
          % len(por_defecto))
    print("    %s" % ", ".join(por_defecto))
    print("\n  Ninguna se clasificó por heurística sobre texto libre: las %d con regla"
          % len(TRASLADO))
    print("  están en una tabla explícita, leídas de su literal.")

    print("\nREPARTO DEL EFECTO, que es lo que la métrica usa:\n")
    for efecto, n in con.execute(
            "SELECT efecto_traslado, COUNT(*) FROM regimen_jornada "
            "GROUP BY 1 ORDER BY 2 DESC"):
        print("  %-26s %d" % (efecto, n))
    print("\n  %d unidades reclasificadas a `derivado`: lo que su norma fija es un"
          % len(CEILING))
    print("  TECHO de dias, no la semana ordinaria. Ninguna de las nueve que")
    print("  contaban seis dias lo tiene escrito; las que legislan cinco si.")
    print("\nORIGEN DE LOS DIAS ORDINARIOS:\n")
    for o, n in con.execute(
            "SELECT dias_ordinarios_origen, COUNT(*) FROM regimen_jornada "
            "GROUP BY 1 ORDER BY 2 DESC"):
        print("  %-26s %d" % (o, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
