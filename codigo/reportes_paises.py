"""Genera D2 —apéndice por país— y D3 —apéndice de verificación— desde la base.

LOS DOS SON DERIVADOS ENTEROS. Ninguna frase se escribe a mano aquí: lo que
parece prosa es plantilla rellenada con lo que la base y la captura dicen. Si un
hecho no está, la sección **se omite**; nunca se emite «no aplica». Prosa vacía
es el falso positivo de los reportes — dice que hay contenido donde no lo hay.

D2 contesta: qué fuentes hay para este país, qué se hizo con ellas, y qué se
decidió. Criterio de suficiencia: que alguien pueda re-derivar la mayor parte de
los valores con esto y las fuentes que cita.

D3 contesta, para un verificador externo **sin acceso al repositorio**: de dónde
sale exactamente cada número. Por eso lleva la cita textual dentro del propio
documento y no un enlace a una consulta. Va en dos niveles físicos —índice de una
línea por celda, y el desarrollo completo debajo— y el índice se **deriva** del
mismo recorrido que el cuerpo, porque un índice escrito aparte se desincroniza.

De dónde sale la cita textual: de `data/raw/<unidad>/captura*.json`, que es el
dato crudo con procedencia del proyecto. La base guarda los valores; la captura
guarda el pasaje del que salieron. D3 se genera de las dos.
"""

from __future__ import annotations

import json
import sqlite3

from reportes_nucleo import (_fmt, captura_de, carpeta_de_iso3, portada,
                             temporales_al_corte, vuelve_en)

# Regla del protocolo que gobierna cada constructo. Se mapea aquí, en un solo
# sitio y de forma determinista, en vez de guardarse por celda: una columna con
# la referencia se desincroniza del protocolo en cuanto este se renumera, y
# derivarla es barato.
REGLA_DE = {
    "feriado": ("§2", "Definición de feriado público y su régimen: qué cuenta como "
                      "descanso pagado obligatorio y qué no."),
    "clase_fecha": ("§2.4", "Clase de regla de fecha, y §35 para las reglas "
                            "condicionales y la cuota designada."),
    "vacaciones": ("§3", "Titularidad de vacaciones anuales: cantidad, unidad de "
                         "conteo leída de la norma y base semanal."),
    # LA PROCEDENCIA DEL CORTE ANTIGUO TIENE SU PROPIA REGLA, y no es la de la
    # celda de al lado. La primera version de esta celda reutilizo la etiqueta de
    # `vacaciones` —«§3, cantidad y unidad de conteo»— mientras su valor hablaba
    # de las ramas del §10 bis. En Mexico era mas visible: el valor no menciona
    # cantidad, menciona vigencia.
    #
    # En un apendice cuyo proposito entero es decir QUE REGLA produjo cada celda,
    # este campo es el unico que el lector usa para ir al protocolo a
    # comprobarnos. Apuntar a la seccion equivocada lo manda a un sitio donde no
    # esta lo que busca, y la celda se desmiente a si misma en la linea
    # siguiente. La etiqueta se hereda sola cuando se copia una celda vecina; por
    # eso cada una lleva la suya declarada.
    "procedencia_2016": ("§10 bis", "Las pantallas en la variable de vacaciones: "
                         "cuando un par unidad-corte se codifica «sin cambio "
                         "confirmado», y las dos ramas que lo autorizan."),
    "conversion": ("§3.1", "Conversión a unidad común. La unidad común son semanas "
                           "de derecho; la cifra en días de trabajo es semanas × 5."),
    "imputacion": ("§4", "Imputación de feriados al período vacacional: si lo "
                         "extienden o se computan contra él."),
    "colocacion": ("§5", "Reglas de colocación en capas, y §34.2 para la resolución "
                         "del desacuerdo cuando la colocación es negociada."),
    "fuente": ("§6", "Nivel de fuente y evidencia: todo hecho lleva al menos una."),
}

NIVEL = {
    1: "gaceta oficial",
    2: "portal gubernamental",
    3: "secundarias concordantes",
    4: "una sola secundaria",
    5: "terciaria",
    6: "no consta",
}

FACTOR = {"habil": 1.0, "calendario": 5 / 7, "werktage": 5 / 6, "semanas": 5.0}


def _lit(x, corte=400):
    """Un literal de la captura, recortado y con las comillas que le tocan."""
    if not x:
        return None
    t = " ".join(str(x).split())
    return t if len(t) <= corte else t[:corte].rsplit(" ", 1)[0] + "…"


def _buscar_literales(cap: dict) -> dict:
    """Recoge todo pasaje citado de la captura, indexado por la clave que lo tenía.

    Recorre el árbol entero en vez de mirar rutas fijas porque las capturas no
    tienen forma común: cada país la tomó de su norma. Buscar por nombre de clave
    encuentra los literales dondequiera que el codificador los pusiera.
    """
    out: dict[str, list] = {}
    def rec(nodo, ruta):
        if isinstance(nodo, dict):
            for k, v in nodo.items():
                if isinstance(v, str) and any(
                        s in k.lower() for s in ("literal", "cita", "texto", "verbatim")):
                    out.setdefault(ruta or "raiz", []).append((k, v))
                else:
                    rec(v, "%s.%s" % (ruta, k) if ruta else k)
        elif isinstance(nodo, list):
            for i, v in enumerate(nodo):
                rec(v, "%s[%d]" % (ruta, i))
    rec(cap, "")
    return out


def fuentes_de(con, iso3) -> list[dict]:
    filas = con.execute(
        "SELECT s.autoridad, s.nivel_de_fuente, s.url, s.fecha_de_norma, "
        "       s.version_archivada "
        "  FROM fuentes s JOIN jurisdicciones j ON j.jurisdiccion_id = s.jurisdiccion_id "
        " WHERE j.iso3 = ? AND j.nivel = 'subnacional' "
        " ORDER BY s.nivel_de_fuente, s.autoridad", (iso3,)).fetchall()
    return [{"autoridad": a, "nivel": n, "url": u, "fecha": f, "archivo": v}
            for a, n, u, f, v in filas]


def feriados_de(con, iso3) -> list[dict]:
    filas = con.execute("""
        SELECT f.feriado_version_id, f.nombre_oficial, f.categoria, f.regimen,
               f.duracion_dias, r.clase_de_regla, r.mes, r.dia, r.ancla,
               r.offset_dias, r.ordinal, r.dia_semana, r.calendario_lunar,
               r.mes_lunar, r.dia_lunar, r.dia_lunar_desde_fin,
               r.instrumento_remitido, r.conjunto_de_referencia,
               r.condicion_referencia, r.condicion_dia_semana, f.vigencia_desde
          FROM feriado_version f
          JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
          LEFT JOIN regla_fecha_version r
                 ON r.feriado_version_id = f.feriado_version_id
         WHERE j.iso3 = ?
         ORDER BY f.nombre_oficial, r.condicion_dia_semana""", (iso3,)).fetchall()
    cols = ("id nombre categoria regimen duracion clase mes dia ancla offset ordinal "
            "dia_semana cal_lunar mes_lunar dia_lunar dia_desde_fin remitido conjunto "
            "cond_ref cond_dia desde").split()
    return [dict(zip(cols, f)) for f in filas]


def vacaciones_de(con, iso3):
    f = con.execute("""
        SELECT v.vacaciones_version_id, v.texto_legal_dias, v.tipo_de_dia,
               v.base_semanal_dias, v.base_semanal_origen,
               v.periodo_de_calificacion_meses, v.imputacion_feriados_a_vacaciones
          FROM vacaciones_version v
          JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id
         WHERE j.iso3 = ?""", (iso3,)).fetchone()
    if not f:
        return None
    return dict(zip("id dias tipo base origen meses imputacion".split(), f))


def colocacion_de(con, iso3) -> list[dict]:
    filas = con.execute("""
        SELECT c.orden_precedencia, c.alcance, c.iniciativa, c.veto_empleador,
               c.default_ante_silencio, c.resolucion_desacuerdo, c.instrumento,
               c.literal_normativo
          FROM regla_colocacion c
          JOIN vacaciones_version v ON v.vacaciones_version_id = c.vacaciones_version_id
          JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id
         WHERE j.iso3 = ? ORDER BY c.orden_precedencia""", (iso3,)).fetchall()
    return [dict(zip("orden alcance iniciativa veto silencio resolucion instrumento "
                     "literal".split(), f)) for f in filas]


def escala_de(con, iso3) -> list[dict]:
    filas = con.execute("""
        SELECT e.desde_meses, e.hasta_meses, e.quantum, e.tipo_de_dia,
               e.literal_normativo
          FROM escala_antiguedad e
          JOIN vacaciones_version v ON v.vacaciones_version_id = e.vacaciones_version_id
          JOIN jurisdicciones j ON j.jurisdiccion_id = v.jurisdiccion_id
         WHERE j.iso3 = ? ORDER BY e.desde_meses""", (iso3,)).fetchall()
    return [dict(zip("desde hasta quantum tipo literal".split(), f)) for f in filas]


def panel_de(con, iso3) -> dict:
    filas = con.execute("""
        SELECT m.corte, SUM(f.duracion_dias)
          FROM mediciones m
          JOIN feriado_version f ON f.feriado_version_id = m.hecho_id
           AND m.hecho_tipo = 'feriado_version'
          JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
         WHERE j.iso3 = ? AND m.estado_verificacion <> 'na'
         GROUP BY m.corte""", (iso3,)).fetchall()
    return {c: v for c, v in filas}


def describe_fecha(h: dict) -> str:
    """La regla de fecha en castellano, derivada de sus campos."""
    c = h["clase"]
    if c == "fija":
        return "fecha fija, %02d-%02d" % (h["mes"], h["dia"])
    if c == "ordinal":
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        orden = {-1: "último", 1: "primer", 2: "segundo", 3: "tercer", 4: "cuarto",
                 5: "quinto"}.get(h["ordinal"], str(h["ordinal"]))
        return "%s %s del mes %d" % (orden, dias[h["dia_semana"] - 1], h["mes"])
    if c == "relativa":
        return "%s%+d días" % (h["ancla"].replace("_", " "), h["offset"])
    if c == "relativa_a_fecha":
        return "relativa al %02d-%02d, desplazamiento %+d" % (h["mes"], h["dia"], h["offset"])
    if c == "lunar":
        if h["dia_desde_fin"]:
            return ("calendario %s, mes %s, día %s contado desde el fin del mes"
                    % (h["cal_lunar"], h["mes_lunar"], h["dia_desde_fin"]))
        return "calendario %s, mes %s día %s" % (h["cal_lunar"], h["mes_lunar"], h["dia_lunar"])
    if c == "remision_normativa":
        return "remite a: %s" % h["remitido"]
    if c == "cuota_designada_por_empleador":
        return "cuota de %s días designados por el empleador de: %s" % (
            h["duracion"], h["conjunto"])
    if c == "delegada_a_jurisdiccion_local":
        return "fecha fijada por la costumbre de la jurisdicción local"
    if c == "dependiente_de_proclamacion":
        return "fecha fijada por proclamación anual"
    return c or "sin regla registrada"


def condicion_txt(h: dict) -> str | None:
    if not h["cond_dia"]:
        return None
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    ref = {"propia": "la fecha que esta regla produce",
           "regla_por_defecto": "la fecha de la regla por defecto"}.get(
               h["cond_ref"], "el %s" % h["cond_ref"])
    return "rige sólo cuando %s cae en %s" % (ref, dias[h["cond_dia"] - 1])


# =====================================================================
# D2 · Apéndice por país
# =====================================================================

def d2(con, snap, iso3, pais, ciudad) -> str:
    cap = captura_de(carpeta_de_iso3()[iso3]) or {}
    fs, fer = fuentes_de(con, iso3), feriados_de(con, iso3)
    vac, col, esc = vacaciones_de(con, iso3), colocacion_de(con, iso3), escala_de(con, iso3)
    panel = panel_de(con, iso3)
    p = [portada(snap, "%s — apéndice de país" % pais,
                 "Jurisdicción de referencia: **%s**  ·  código ISO3: `%s`" % (ciudad, iso3))]

    p.append("\n## 1. Qué se midió aquí\n")
    p.append("La unidad de referencia no es el país: es **%s**, la jurisdicción "
             "concreta donde vive el trabajador de referencia. En un país sin ley "
             "nacional única de feriados, «el número del país» no existe, y "
             "promediar jurisdicciones fabricaría una cifra que ninguna norma "
             "concede.\n" % ciudad)
    filas = ["| variable | valor |", "|---|---|"]
    if 2016 in panel or 2026 in panel:
        for corte in (2016, 2026):
            v = panel.get(corte)
            filas.append("| feriados, corte %d | %s |"
                         % (corte, _fmt(v, 1) if v is not None else "no capturado"))
    if vac:
        filas.append("| vacaciones, texto legal | %s %s |"
                 % (_fmt(vac["dias"], 1), vac["tipo"]))
        filas.append("| base semanal | %s |" % (
            "%s días, declarada por la norma" % vac["base"] if vac["base"]
            else "no declarada por la norma"))
        filas.append("| imputación de feriados | %s |" % vac["imputacion"])
    p.append("\n".join(filas) + "\n")

    # EL AVISO QUE LE FALTABA A LA TABLA DE ARRIBA. Si una medida temporal está
    # viva en el año del corte, la cifra es correcta y la lectura obvia no lo es:
    # invita a leer como permanente una caída que no lo es. Se dice aquí, pegado
    # a la cifra, y no en el apéndice de verificación, que es donde estaba y
    # donde no lo ve quien sólo consulta el país.
    temps = temporales_al_corte(con, iso3, 2026)
    if temps:
        vuelta = vuelve_en(con, iso3)
        p.append("\n> **El corte de 2026 cae en un año con una medida temporal "
                 "vigente.** La cifra de arriba es la que la norma concede ese "
                 "año, pero **no describe el estado permanente del derecho**:\n>")
        for t in temps:
            p.append("> - %s — %s desde %s. Fundamento: %s"
                     % (t["que"], t["tipo"], t["desde"], t["cita"]))
        if vuelta:
            p.append(">\n> La restitución está fechada: **%s**. Leer la variación "
                     "entre cortes como reforma permanente sobrestima el cambio "
                     "en tantos días como suspende la medida." % vuelta)
        p.append("")

    p.append("\n## 2. Fuentes disponibles para esta unidad\n")
    if fs:
        p.append("El **nivel** dice qué clase de documento es, no cuánto se le cree: "
                 "el nivel 1 es la gaceta oficial y el 4 es una sola fuente "
                 "secundaria. El nivel se declara fila por fila y no se promedia.\n")
        p.append("| nivel | autoridad | fecha de la norma | localización |")
        p.append("|---|---|---|---|")
        for f in fs:
            p.append("| %d · %s | %s | %s | %s |"
                     % (f["nivel"], NIVEL.get(f["nivel"], "?"), f["autoridad"],
                        f["fecha"] or "—",
                        ("<%s>" % f["url"]) if f["url"].startswith("http") else f["url"]))
        peor = max(f["nivel"] for f in fs)
        if peor >= 3:
            p.append("\n**Límite declarado.** La fuente de peor nivel de esta unidad "
                     "es de nivel %d. Los valores que dependan sólo de ella tienen "
                     "el respaldo que ese nivel indica, ni más ni menos.\n" % peor)
    else:
        p.append("_Sin fuentes registradas para esta unidad._\n")

    p.append("\n## 3. Qué metodología se siguió, dadas esas fuentes\n")
    reglas = [REGLA_DE["feriado"], REGLA_DE["fuente"]]
    if vac:
        reglas += [REGLA_DE["vacaciones"], REGLA_DE["imputacion"]]
        if vac["tipo"] != "habil":
            reglas.append(REGLA_DE["conversion"])
    if col:
        reglas.append(REGLA_DE["colocacion"])
    if any(h["cond_dia"] or h["clase"] in
           ("cuota_designada_por_empleador", "remision_normativa") for h in fer):
        reglas.append(REGLA_DE["clase_fecha"])
    for ref, txt in dict.fromkeys(reglas):
        p.append("- **%s** — %s" % (ref, txt))
    p.append("")

    if vac and vac["tipo"] != "habil":
        semanas = (vac["dias"] / 7 if vac["tipo"] == "calendario"
                   else vac["dias"] if vac["tipo"] == "semanas"
                   else vac["dias"] / (vac["base"] or 6))
        p.append("**Conversión a unidad común.** El texto legal concede %s %s. "
                 "En semanas de derecho son %s, y esa cifra no depende de ningún "
                 "supuesto: %s. Expresada en días de trabajo sobre semana de cinco "
                 "son %s, que es la anterior multiplicada por cinco — un cambio "
                 "de rótulo, no un supuesto.\n"
                 % (_fmt(vac["dias"], 1), vac["tipo"], _fmt(semanas, 2),
                    "treinta días corridos son treinta séptimos de semana se trabaje "
                    "lo que se trabaje" if vac["tipo"] == "calendario"
                    else "la norma declara la base semanal" if vac["base"]
                    else "la norma cuenta en semanas directamente",
                    _fmt(semanas * 5, 1)))

    p.append("\n## 4. Lo más importante que se decidió sobre esta unidad\n")
    decisiones = []
    if vac and not vac["base"] and vac["tipo"] in ("habil", "werktage"):
        decisiones.append(
            "La norma cuenta en días de trabajo y **no declara cuántos tiene la "
            "semana**. La base queda en nulo: es información, no un hueco, y "
            "cualquier conversión a días de trabajo de esta unidad descansa en un "
            "supuesto que no es de la ley.")
    if vac and vac["tipo"] == "calendario":
        decisiones.append(
            "El derecho se cuenta en **días calendario**, que incluyen los descansos "
            "semanales. Compararlo sin convertir con un derecho en días hábiles "
            "sobreestima esta unidad — es el sesgo que este proyecto mide.")
    for h in fer:
        if h["cond_dia"]:
            decisiones.append(
                "**%s** tiene existencia o fecha condicional: %s. Un feriado cuyas "
                "reglas todas llevan condición no ocurre en los años en que ninguna "
                "se cumple." % (h["nombre"], condicion_txt(h)))
        if h["clase"] == "cuota_designada_por_empleador":
            decisiones.append(
                "**%s**: la ley fija la cantidad y deja las fechas a designación del "
                "empleador dentro de un conjunto de referencia. Se registra la "
                "cantidad y el conjunto, sin fechas." % h["nombre"])
        if h["clase"] == "delegada_a_jurisdiccion_local":
            decisiones.append(
                "**%s**: la norma remite a la costumbre local y ningún instrumento "
                "fija la fecha. Se registra el feriado sin fecha." % h["nombre"])
    if col:
        c = col[0]
        quien = {"trabajador": "la pide el trabajador", "empleador": "la señala el empleador",
                 "negociada": "se fija de común acuerdo",
                 "asignacion_estatal": "el Estado fija parte del derecho",
                 "cierre_colectivo": "por cierre colectivo",
                 "calendario_fijo_legal": "por calendario fijo de la ley"}.get(
                     c["iniciativa"], c["iniciativa"])
        extra = ""
        if c["resolucion"]:
            extra = (" Cuando no hay acuerdo, %s." % {
                "empleador": "decide el empleador",
                "trabajador_prevalece": "el empleador queda obligado a conceder lo pedido",
                "limite_razonabilidad": "el empleador puede negarse pero no sin motivo",
                "tercero_dirime": "el desempate sale de las partes",
                "remitido_a_convenio": "la ley remite al contrato o al convenio",
                "sin_regla": "la ley calla"}.get(c["resolucion"], c["resolucion"]))
        elif c["veto"]:
            extra = " El empleador puede oponerse con carácter %s." % c["veto"]
        decisiones.append("**Colocación**: %s.%s Un derecho de N días que fija el "
                          "empleador no es el mismo bien que N días de elección "
                          "libre, y el número solo no lo distingue." % (quien, extra))
    if len(esc) > 1:
        decisiones.append(
            "La titularidad **progresa con la antigüedad**: %d tramos registrados. La "
            "cifra de portada es la del trabajador de referencia, con doce meses "
            "exactos de servicio continuo." % len(esc))
    if not panel.get(2016):
        decisiones.append(
            "**El corte 2016 no se capturó.** El calendario de esta unidad se fija "
            "por decreto cada año, así que el de 2016 es otro documento; copiar el "
            "de 2026 no sería una aproximación sino una invención.")
    p.append("\n".join("%d. %s" % (i, d) for i, d in enumerate(decisiones, 1))
             if decisiones else "_Sin decisiones específicas registradas._")

    p.append("\n\n## 5. Cómo re-derivar estos valores\n")
    p.append("Tome las fuentes de la sección 2, aplique las reglas de la sección 3 y "
             "tenga en cuenta las decisiones de la sección 4. El apéndice de "
             "verificación de esta misma unidad trae, para cada número, la cita "
             "textual de la que sale y la aritmética completa.\n")
    return "\n".join(p)


# =====================================================================
# D3 · Apéndice de verificación
# =====================================================================

def _fer_en_captura(cap: dict) -> dict:
    """nombre del feriado -> su entrada cruda en la captura, para sacar el literal."""
    out = {}
    for clave in ("feriados", "feriados_2026"):
        bloque = cap.get(clave)
        listas = ([bloque] if isinstance(bloque, list) else
                  [v for v in bloque.values() if isinstance(v, list)]
                  if isinstance(bloque, dict) else [])
        for ls in listas:
            for h in ls:
                if isinstance(h, dict) and h.get("nombre"):
                    out.setdefault(h["nombre"], h)
    return out


def _celda(num, titulo, valor, regla, pasajes, aritmetica=None, notas=()):
    """Una celda de D3, con todo lo que un verificador sin repositorio necesita."""
    p = ["\n### V%d · %s\n" % (num, titulo),
         "**Valor publicado:** %s\n" % valor,
         "**Regla aplicada:** %s — %s\n" % regla]
    if pasajes:
        p.append("**Pasaje o pasajes de los que sale:**\n")
        for etiqueta, texto in pasajes:
            p.append("> _%s_\n>\n> «%s»\n" % (etiqueta, _lit(texto, 700)))
    else:
        p.append("**Pasaje textual:** _la captura no registró un pasaje literal para "
                 "esta celda._ El valor descansa en las fuentes de la sección 2 del "
                 "apéndice de país; un verificador tiene que ir a la norma. Es un "
                 "hueco declarado, no un descuido oculto.\n")
    if aritmetica:
        p.append("**Aritmética:**\n\n```\n%s\n```\n" % aritmetica)
    for n in notas:
        p.append("**Nota:** %s\n" % n)
    return "\n".join(p)


def d3(con, snap, iso3, pais, ciudad) -> str:
    cap = captura_de(carpeta_de_iso3()[iso3]) or {}
    crudos = _fer_en_captura(cap)
    fs = fuentes_de(con, iso3)
    fer, vac = feriados_de(con, iso3), vacaciones_de(con, iso3)
    col, esc, panel = colocacion_de(con, iso3), escala_de(con, iso3), panel_de(con, iso3)

    cuerpo, indice, n = [], [], 0

    con_pasaje = [0]

    def add(titulo, valor, regla, pasajes, aritmetica=None, notas=()):
        nonlocal n
        n += 1
        if pasajes:
            con_pasaje[0] += 1
        indice.append("| V%d | %s | %s |" % (n, titulo, valor))
        cuerpo.append(_celda(n, titulo, valor, regla, pasajes, aritmetica, notas))

    # --- feriados, uno por uno -------------------------------------------
    vistos = set()
    for h in fer:
        if h["id"] in vistos:
            continue
        vistos.add(h["id"])
        reglas_h = [x for x in fer if x["id"] == h["id"]]
        crudo = crudos.get(h["nombre"], {})
        pasajes = []
        for k in ("literal", "literal_relevante", "cita", "instrumento"):
            if crudo.get(k):
                pasajes.append(("captura, campo «%s»" % k, crudo[k]))
        desc = " ; ".join(
            describe_fecha(x) + (" (%s)" % condicion_txt(x) if condicion_txt(x) else "")
            for x in reglas_h)
        notas = []
        if crudo.get("nota"):
            notas.append(_lit(crudo["nota"], 900))
        if len(reglas_h) > 1:
            notas.append("Este feriado tiene %d reglas de fecha. %s"
                         % (len(reglas_h),
                            "Todas llevan condición, así que no ocurre en los años en "
                            "que ninguna se cumple."
                            if all(x["cond_dia"] for x in reglas_h)
                            else "Una rige por defecto y las demás bajo condición."))
        add("Feriado · %s" % h["nombre"],
            "%s, %s día(s), régimen «%s»"
            % (h["categoria"], _fmt(h["duracion"], 1), h["regimen"]),
            REGLA_DE["clase_fecha"] if (h["cond_dia"] or h["clase"] in
                                        ("cuota_designada_por_empleador",
                                         "remision_normativa"))
            else REGLA_DE["feriado"],
            pasajes,
            "clase de fecha: %s" % desc, notas)

    # --- conteo por corte, con su aritmética ------------------------------
    for corte in (2016, 2026):
        if corte in panel:
            piezas = con.execute("""
                SELECT f.nombre_oficial, f.duracion_dias
                  FROM mediciones m
                  JOIN feriado_version f ON f.feriado_version_id = m.hecho_id
                   AND m.hecho_tipo='feriado_version'
                  JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
                 WHERE j.iso3=? AND m.corte=? AND m.estado_verificacion<>'na'
                 ORDER BY f.nombre_oficial""", (iso3, corte)).fetchall()
            suma = "\n".join("%-52s %5g" % (nm[:52], d) for nm, d in piezas)
            excl = con.execute("""
                SELECT f.nombre_oficial FROM mediciones m
                  JOIN feriado_version f ON f.feriado_version_id = m.hecho_id
                   AND m.hecho_tipo='feriado_version'
                  JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id
                 WHERE j.iso3=? AND m.corte=? AND m.estado_verificacion='na'""",
                (iso3, corte)).fetchall()
            notas = []
            if excl:
                notas.append("Excluidos de este corte por condición no cumplida: %s. "
                             "Están en el registro con su norma; lo que no existe ese "
                             "año es la ocurrencia, no el derecho."
                             % ", ".join(e[0] for e in excl))
            add("Conteo de feriados, corte %d" % corte, _fmt(panel[corte], 1),
                REGLA_DE["feriado"], [],
                "%s\n%s\n%-52s %5g" % (suma, "-" * 58, "TOTAL", panel[corte]), notas)

    # --- vacaciones -------------------------------------------------------
    if vac:
        vcap = cap.get("vacaciones_normalizado") or cap.get("vacaciones") or {}
        pasajes = [("captura, campo «%s»" % k, vcap[k])
                   for k in ("literal", "imputacion_literal", "literal_imputacion")
                   if vcap.get(k)]
        add("Vacaciones · cantidad y unidad de conteo",
            "%s días de tipo «%s»" % (_fmt(vac["dias"], 1), vac["tipo"]),
            REGLA_DE["vacaciones"], pasajes, None,
            ["La unidad de conteo **no se infiere**: se lee de la norma. Sin ella el "
             "número no es comparable con el de otra unidad."])
        # LA PROCEDENCIA DEL CORTE 2016, CELDA POR CELDA. El informe manda al
        # lector a este apendice para comprobar cada numero, y tenia celda para
        # el conteo de feriados de 2016 y NINGUNA para el corte de 2016 de
        # vacaciones. Con las celdas casi todas supuestas eso no se notaba: no
        # habia nada que ensenar. Desde que decenas se ganan un
        # `sin_cambio_confirmado`, la afirmacion mas fuerte del documento —«se
        # busco y se confirmo que no cambio»— era la unica que el apendice no
        # dejaba verificar. La evidencia viajaba en la captura, en prosa dentro
        # de un JSON; comprobar cuarenta y una pedia abrir cuarenta y un
        # archivos.
        sc = vcap.get("sin_cambio")
        ant = vcap.get("version_anterior")
        if isinstance(sc, dict):
            nivel = sc.get("nivel_de_fuente")
            rama = ("(a) índice oficial de modificaciones, nivel de fuente %s"
                    % nivel) if (isinstance(nivel, int) and nivel <= 2
                                 and sc.get("indice_registra_modificaciones") is True) \
                else ("(b) reproducción de nivel %s más pantalla 3" % nivel)
            p3 = sc.get("pantalla_3") or {}
            pasajes_sc = [("captura, «buscado_en»", sc.get("buscado_en", "")),
                          ("captura, pasaje citado", sc.get("cita", ""))]
            if p3.get("cita"):
                pasajes_sc.append(("captura, pantalla 3", p3["cita"]))
            quien = (p3.get("ejecutada_por") or "").strip()
            add("Vacaciones · procedencia del corte 2016",
                "sin cambio, buscado y confirmado — rama %s" % rama,
                REGLA_DE["procedencia_2016"],
                [(t, v) for t, v in pasajes_sc if v], None,
                ["**Confirmado no es lo mismo que supuesto**, y el paquete los "
                 "distingue: aquí se buscó la modificatoria y se comprobó que no "
                 "existe o que no toca la cantidad. Un «supuesto» sólo dice que "
                 "no se halló."]
                # SE IMPRIME EL NOMBRE, no se remite al campo. Esta celda existe
                # para poner el pasaje delante del lector en vez de mandarlo a
                # buscarlo; decir «el campo lo dice» justo aqui era la unica
                # linea que rompia esa regla, y es el dato que motivo la
                # atribucion en primer lugar.
                + (["La pantalla 3 la ejecutó **%s**, que puede no ser quien "
                    "capturó la unidad ni quien la cargó." % quien]
                   if quien else []))
        elif ant:
            add("Vacaciones · procedencia del corte 2016",
                "reforma capturada y fechada; rige hasta %s"
                % (ant.get("hasta") or "—"),
                REGLA_DE["procedencia_2016"],
                [("captura, versión anterior", ant.get("instrumento", ""))], None,
                ["El corte antiguo no hereda la verificación del vigente: se "
                 "gana la suya por el nivel de fuente que la versión anterior "
                 "declara (%s)." % (ant.get("nivel_de_fuente") or "sin declarar")])
        else:
            add("Vacaciones · procedencia del corte 2016",
                "supuesto — no se halló norma modificatoria",
                REGLA_DE["procedencia_2016"], [], None,
                ["**Esto no es evidencia de que no cambiara.** Es la ausencia de "
                 "una búsqueda positiva, y se declara como tal."])

        add("Vacaciones · base semanal",
            ("%s días, declarada por la norma (%s)" % (vac["base"], vac["origen"]))
            if vac["base"] else "no declarada por la norma",
            REGLA_DE["vacaciones"], [], None,
            [] if vac["base"] else
            ["El nulo es información: la norma no fija semana laboral. Cualquier "
             "conversión de esta unidad a días de trabajo descansa en un supuesto que "
             "no es de la ley."])
        if vac["tipo"] != "habil":
            base = vac["base"] or 7
            if vac["tipo"] == "calendario":
                sem, arit = vac["dias"] / 7, ("%s días calendario / 7 días por semana"
                                              " = %s semanas de derecho"
                                              % (_fmt(vac["dias"], 1),
                                                 _fmt(vac["dias"] / 7, 4)))
            elif vac["tipo"] == "semanas":
                sem = vac["dias"]
                arit = ("%s semanas, tal como las concede la norma"
                        % _fmt(vac["dias"], 1))
            else:
                sem = vac["dias"] / base
                arit = ("%s Werktage / %s días de trabajo por semana declarados"
                        " = %s semanas de derecho"
                        % (_fmt(vac["dias"], 1), _fmt(base, 1), _fmt(sem, 4)))
            add("Vacaciones · conversión a unidad común",
                "%s semanas de derecho, o %s días de trabajo sobre semana de cinco"
                % (_fmt(sem, 2), _fmt(sem * 5, 1)), REGLA_DE["conversion"], [],
                "%s\n%s semanas x 5 días = %s días de trabajo (semana de cinco)"
                % (arit, _fmt(sem, 4), _fmt(sem * 5, 2)),
                ["Las semanas de derecho **no tienen parámetro libre**. Pasar a días "
                 "de trabajo sobre semana de cinco es multiplicar por cinco: un "
                 "cambio de rótulo, no un supuesto."])
        add("Vacaciones · imputación de feriados", vac["imputacion"],
            REGLA_DE["imputacion"],
            [("captura, campo «imputacion_literal»", vcap["imputacion_literal"])]
            if vcap.get("imputacion_literal") else [], None,
            ["Decide si un feriado dentro del período vacacional lo extiende o se "
             "computa contra él. En un derecho contado en días calendario, la "
             "diferencia puede valer varios días."])

    # --- colocación y escala ---------------------------------------------
    for c in col:
        add("Colocación · regla %d (%s)" % (c["orden"], c["alcance"]),
            "iniciativa «%s»%s" % (c["iniciativa"],
                                   ", desacuerdo: «%s»" % c["resolucion"]
                                   if c["resolucion"] else ""),
            REGLA_DE["colocacion"],
            [("literal registrado en la base", c["literal"])] if c["literal"] else [])
    if len(esc) > 1:
        arit = "\n".join(
            "desde el mes %3s hasta %-6s -> %s días %s"
            % (e["desde"], e["hasta"] if e["hasta"] is not None else "sin fin",
               e["quantum"], e["tipo"]) for e in esc)
        add("Escala de antigüedad", "%d tramos" % len(esc), REGLA_DE["vacaciones"],
            [("literal del primer tramo", esc[0]["literal"])] if esc[0]["literal"] else [],
            arit, ["El trabajador de referencia tiene doce meses exactos de servicio "
                   "continuo; la cifra de portada es la de su tramo."])

    p = [portada(snap, "%s — apéndice de verificación" % pais,
                 "Jurisdicción de referencia: **%s**  ·  código ISO3: `%s`" % (ciudad, iso3))]
    p.append("""
## Para qué sirve este documento

Está escrito para alguien **ajeno al proyecto y sin acceso a su repositorio** que
quiera comprobar los números uno por uno. Por eso cada celda trae dentro, y no por
enlace, el pasaje del que sale el valor, la regla que se le aplicó y la aritmética
completa.

Se lee en dos niveles: el índice de abajo da una línea por celda, y el cuerpo
desarrolla cada una. El índice **se deriva del mismo recorrido que el cuerpo**, así
que no puede desincronizarse de él.

Cuando una celda no tiene pasaje textual registrado, este documento **lo dice**. Un
hueco visible vale más que una cita inventada.

**Cobertura de citas en esta unidad: COBERTURA.** El resto de las celdas remite a
las fuentes listadas abajo, que hay que consultar en su origen. Es la limitación
principal de este apéndice y se declara arriba, no en una nota final.

## Índice de celdas

| celda | qué verifica | valor |
|---|---|---|""")
    p.extend(indice)
    p.append("\n## Fuentes citadas en este documento\n")
    p.append("| nivel | autoridad | localización |")
    p.append("|---|---|---|")
    for f in fs:
        p.append("| %d · %s | %s | %s |" % (f["nivel"], NIVEL.get(f["nivel"], "?"),
                                            f["autoridad"], f["url"]))
    p.append("\n## Desarrollo, celda por celda")
    p.extend(cuerpo)
    texto = "\n".join(p).replace(
        "COBERTURA", "%s de %s celdas traen el pasaje textual dentro del documento (%s %%)"
        % (con_pasaje[0], n, _fmt(100.0 * con_pasaje[0] / n if n else 0.0, 0)))
    return texto, n, con_pasaje[0]
