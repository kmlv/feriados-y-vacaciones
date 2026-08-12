"""Carga las capturas del piloto en una base real y reporta lo que NO puede cargar.

Es la prueba de punta a punta del esquema: hasta ahora se atacaba con estados
inventados, y esto lo somete a las normas de ocho paises tal como se capturaron.

Principio de este guion, y es el que ordena todo el proyecto: **los datos crudos
con procedencia estan en `data/raw/<unidad>/captura.json`, escritos leyendo las
normas; la base es salida derivada y se puede borrar y regenerar**. Nada se edita
a mano en la base.

Lo que no se puede cargar NO se fuerza. Se cuenta y se explica. Una carga que
reporta «8 de 8 unidades» escondiendo que a seis les faltan las fechas es peor
que una que dice la verdad, porque la primera invita a analizar un panel hueco.

Uso:
    python3 scripts/cargar_piloto.py           # construye data/derived/piloto.db
    python3 scripts/cargar_piloto.py --validar # ademas corre las 37 validaciones
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ortografia import cita_correcta, mal_escritos

# LAS RUTAS SE RESUELVEN CONTRA EL ARBOL QUE SE ESTE LEYENDO, y no se
# escriben aqui: en el paquete publicado el esquema, las capturas y los
# datos viven en otro sitio, y este guion tiene que arrancar en los dos.
from rutas import BASE, CAPTURAS, CONGELAMIENTO, ESQUEMA, GUIONES, REPO, VALIDACIONES
DDL, VALID, CRUDO, SALIDA = ESQUEMA, VALIDACIONES, CAPTURAS, BASE

# Nombre de carpeta -> (ISO3, nombre del pais, jurisdiccion de referencia).
#
# LOS NOMBRES VAN ACENTUADOS Y ESTA ES SU FUENTE CANONICA. Durante dias fueron
# ASCII —«Peru», «Mexico», «Berlin»— porque nacieron como eco del nombre de
# carpeta, y de ahi pasaron a la base, a los CSV publicados y a la tabla
# principal del reporte. Un documento en español para un lector peruano cuya
# columna mas visible escribe «Peru» pierde al lector en el primer vistazo.
#
# El nombre del pais es DATO PUBLICABLE, no un derivado del sistema de archivos.
# La carpeta puede seguir en ASCII —es una ruta— y el nombre no.
#
# Y DESDE HOY LLEVA LOS DOS IDIOMAS, por la misma razon con el signo invertido:
# la version inglesa del reporte saldria con «Bélgica», «Países Bajos» y «Perú»
# en su primera columna. No rompe nada, compila, pasa las compuertas, y se ve en
# el primer cuadro que abra el lector — igual que los acentos, del otro lado.
#
# Va como DATO y no como sustitucion en la plantilla inglesa: si se arreglara
# ahi, el CSV publicable seguiria saliendo en castellano y habria dos verdades
# para el mismo hecho.
#
# Procedencia: los paises son el nombre corto ingles de la ISO 3166-1 —de ahi
# «Türkiye» y «Czechia», que son los vigentes y no los antiguos—. Las ciudades
# NO tienen norma equivalente: se usa el exonimo ingles establecido donde existe
# —Vienna, Copenhagen, Warsaw— y el endonimo cuando no —Guayaquil, Managua—.
# Eso es convencion editorial y va dicho, no disfrazado de estandar.
UNIDADES = {
    "peru":        ("PER", "Perú", "Lima", "Peru", "Lima"),
    "guatemala":   ("GTM", "Guatemala", "Ciudad de Guatemala", "Guatemala", "Guatemala City"),
    "el-salvador": ("SLV", "El Salvador", "San Salvador", "El Salvador", "San Salvador"),
    "mexico":      ("MEX", "México", "Ciudad de México", "Mexico", "Mexico City"),
    "alemania":    ("DEU", "Alemania", "Berlín", "Germany", "Berlin"),
    "indonesia":   ("IDN", "Indonesia", "Yakarta", "Indonesia", "Jakarta"),
    "turquia":     ("TUR", "Turquía", "Estambul", "Türkiye", "Istanbul"),
    "canada":      ("CAN", "Canadá", "Toronto", "Canada", "Toronto"),
    # --- Escalado a las 47 del grupo congelado, 2026-08-10 ---------------
    # Las unidades sin archivo de captura se reportan como tales; el
    # cargador no inventa filas por una entrada de esta tabla.
    "argentina":      ("ARG", "Argentina", "Buenos Aires", "Argentina", "Buenos Aires"),
    "australia":      ("AUS", "Australia", "Sídney", "Australia", "Sydney"),
    "austria":        ("AUT", "Austria", "Viena", "Austria", "Vienna"),
    "belgica":        ("BEL", "Bélgica", "Bruselas", "Belgium", "Brussels"),
    "bolivia":        ("BOL", "Bolivia", "Santa Cruz", "Bolivia", "Santa Cruz"),
    "brasil":         ("BRA", "Brasil", "São Paulo", "Brazil", "São Paulo"),
    "bulgaria":       ("BGR", "Bulgaria", "Sofía", "Bulgaria", "Sofia"),
    "chile":          ("CHL", "Chile", "Santiago", "Chile", "Santiago"),
    "colombia":       ("COL", "Colombia", "Bogotá", "Colombia", "Bogotá"),
    "corea-del-sur":  ("KOR", "Corea del Sur", "Seúl", "South Korea", "Seoul"),
    "costa-rica":     ("CRI", "Costa Rica", "San José", "Costa Rica", "San José"),
    "dinamarca":      ("DNK", "Dinamarca", "Copenhague", "Denmark", "Copenhagen"),
    "ecuador":        ("ECU", "Ecuador", "Guayaquil", "Ecuador", "Guayaquil"),
    "eslovaquia":     ("SVK", "Eslovaquia", "Bratislava", "Slovakia", "Bratislava"),
    "espana":         ("ESP", "España", "Madrid", "Spain", "Madrid"),
    "estados-unidos": ("USA", "Estados Unidos", "Nueva York", "United States", "New York"),
    "finlandia":      ("FIN", "Finlandia", "Helsinki", "Finland", "Helsinki"),
    "francia":        ("FRA", "Francia", "París", "France", "Paris"),
    "grecia":         ("GRC", "Grecia", "Atenas", "Greece", "Athens"),
    "honduras":       ("HND", "Honduras", "Tegucigalpa", "Honduras", "Tegucigalpa"),
    "hungria":        ("HUN", "Hungría", "Budapest", "Hungary", "Budapest"),
    "irlanda":        ("IRL", "Irlanda", "Dublín", "Ireland", "Dublin"),
    "israel":         ("ISR", "Israel", "Jerusalén", "Israel", "Jerusalem"),
    "italia":         ("ITA", "Italia", "Roma", "Italy", "Rome"),
    "japon":          ("JPN", "Japón", "Tokio", "Japan", "Tokyo"),
    "nicaragua":      ("NIC", "Nicaragua", "Managua", "Nicaragua", "Managua"),
    "noruega":        ("NOR", "Noruega", "Oslo", "Norway", "Oslo"),
    "nueva-zelanda":  ("NZL", "Nueva Zelanda", "Auckland", "New Zealand", "Auckland"),
    "paises-bajos":   ("NLD", "Países Bajos", "Ámsterdam", "Netherlands", "Amsterdam"),
    "paraguay":       ("PRY", "Paraguay", "Asunción", "Paraguay", "Asunción"),
    "polonia":        ("POL", "Polonia", "Varsovia", "Poland", "Warsaw"),
    "portugal":       ("PRT", "Portugal", "Lisboa", "Portugal", "Lisbon"),
    "reino-unido":    ("GBR", "Reino Unido", "Londres", "United Kingdom", "London"),
    "republica-checa": ("CZE", "República Checa", "Praga", "Czechia", "Prague"),
    "republica-dominicana": ("DOM", "República Dominicana", "Santo Domingo", "Dominican Republic", "Santo Domingo"),
    "rumania":        ("ROU", "Rumanía", "Bucarest", "Romania", "Bucharest"),
    "suecia":         ("SWE", "Suecia", "Estocolmo", "Sweden", "Stockholm"),
    "suiza":          ("CHE", "Suiza", "Zúrich", "Switzerland", "Zurich"),
    "tailandia":      ("THA", "Tailandia", "Bangkok", "Thailand", "Bangkok"),
}

# La captura de cada pais tiene la forma que le impuso su norma, no una comun.
# Eso es deliberado: forzar una forma comun en el crudo habria obligado a decidir
# antes de leer. La normalizacion vive aqui, donde es visible y reversible.
DONDE_ESTAN_LOS_FERIADOS = [
    ("feriados_2026", "lista"),
    ("feriados", "lista"),
    ("feriados", "nacionales"),
    ("feriados", "civiles"),
    ("feriados", "nucleo_comun_16_laender"),
    ("feriados", "lista_ontario"),
]


# Feriados que se suman a la lista principal de una unidad. Alemania y El
# Salvador tienen fechas propias de la jurisdiccion de referencia ademas de las
# nacionales, y omitirlas subestimaria justo la jurisdiccion que el protocolo
# manda medir.
EXTRAS = [("feriados", "propios_de_berlin"), ("feriados", "subnacionales")]


def sqlite():
    import sqlite3
    if SALIDA.exists():
        SALIDA.unlink()          # derivado: se regenera entero, nunca se parchea
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(SALIDA)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(DDL.read_text())
    return con


def es_del_complemento(f: dict) -> bool:
    """¿Esta entrada subnacional pertenece a las jurisdicciones que NO medimos?

    Existe porque El Salvador salia con un feriado de mas. Su articulo 190 es un
    O EXCLUSIVO por jurisdiccion: tres y cinco de agosto EN LA CIUDAD DE SAN
    SALVADOR, «y en el resto de la Republica, el dia principal de la festividad
    mas importante del lugar». El cargador sumaba las dos ramas, asi que San
    Salvador recibia sus dos dias mas el dia local que la norma reserva para
    quien NO es San Salvador. La captura lo decia dos veces: cada entrada trae su
    `jurisdiccion`, y el bloque declara once contra los doce que se publicaban.

    SE EXCLUYE POR LO QUE LA ENTRADA AFIRMA, no por comparar nombres. Mi primera
    version casaba el nombre de la ciudad contra el de la jurisdiccion, y tiro
    ocho feriados suizos: la captura escribe «Kanton Zuerich» y la unidad se
    llama «Zúrich», que no casan ni normalizando acentos porque la `ue` alemana
    no es una `u` con dieresis para una comparacion de cadenas. Adivinar
    identidad por nombre falla en silencio y hacia abajo, que es la peor
    direccion. Reconocer el COMPLEMENTO declarado es una lista corta, explicita y
    que solo puede equivocarse hacia arriba.
    """
    j = (f.get("jurisdiccion") or "").lower()
    return any(t in j for t in ("resto de", "resto del", "rest of", "demas ",
                                "demás ", "otras jurisdicciones"))


def feriados_de(cap: dict, ciudad: str = "") -> list[dict]:
    salida = []
    for clave, sub in DONDE_ESTAN_LOS_FERIADOS:
        if clave in cap and isinstance(cap[clave], dict) and sub in cap[clave]:
            salida = list(cap[clave][sub])
            break
    for clave, sub in EXTRAS:
        if clave in cap and isinstance(cap[clave], dict) and sub in cap[clave]:
            salida += [f for f in cap[clave][sub]
                       if not isinstance(f, dict) or not es_del_complemento(f)]
    return [f for f in salida if isinstance(f, dict)]


def ocurre_en(f: dict, reglas: list, anio: int) -> bool:
    """¿Ocurre este feriado en `anio`? Solo miente quien no evalua la condicion.

    Un feriado cuyas reglas TODAS llevan condicion no existe en los anios en que
    ninguna se cumple — esa es la existencia condicional de §35.2. Si hay al
    menos una regla sin condicion, el feriado ocurre siempre y no hay nada que
    evaluar.

    POR QUE HIZO FALTA ESCRIBIR ESTO. Al codificar los condicionales chilenos el
    esquema ya sabia EXPRESAR la condicion, pero el conteo no la miraba: Chile
    sumaba en 2026 dos feriados que ese anio no existen. Un esquema que dice la
    verdad y un conteo que no la lee dan exactamente el mismo numero equivocado
    que no tener el esquema.

    Solo se evalua lo gregoriano y `propia`, que es lo que el grupo necesita. Lo
    demas devuelve True y se declara: preferimos contar de mas y decirlo a
    inventar un calendario hebreo aqui dentro.
    """
    import datetime
    condiciones = [(cl, ca, co) for cl, ca, co in reglas if co]
    if len(condiciones) != len(reglas):
        return True                      # hay regla por defecto: ocurre siempre
    for clase, campos, cond in condiciones:
        ref = cond.get("referencia")
        dsem = cond.get("dia_semana")
        if ref == "propia" and clase == "fija":
            try:
                if datetime.date(anio, campos["mes"], campos["dia"]).isoweekday() == dsem:
                    return True
            except ValueError:           # 29 de febrero en anio no bisiesto
                continue
        elif ref not in ("propia", "regla_por_defecto"):
            try:
                mes, dia = (int(x) for x in str(ref).split("-"))
                if datetime.date(anio, mes, dia).isoweekday() == dsem:
                    return True
            except (ValueError, TypeError):
                continue
        else:
            return True                  # no evaluable aqui: se cuenta y se declara
    return False


def ocurre_el_anio(f: dict, anio: int) -> bool:
    """¿Cae este feriado PERIODICO en `anio`? Los de periodo 1 caen siempre.

    EL CAMPO EXISTIA Y NADIE LO LEIA. `periodo_anios` esta en el esquema desde
    v2.x con un comentario que dice que se creo justo para esto —«el calculo del
    panel puede excluirlo o anotarlo, en vez de depender de que alguien se
    acuerde»— y `ocurre_en` solo evaluaba la condicion de dia de semana. El
    resultado: el Inauguration Day estadounidense y la transmision sexenal
    mexicana contaban en LOS DOS cortes, y no caen en ninguno. Es exactamente lo
    que el docstring de `ocurre_en` dice de si mismo: un esquema que dice la
    verdad con un conteo que no lo lee da el mismo numero equivocado que no tener
    esquema.

    EL ANCLA ES OBLIGATORIA y por eso esto falla en vez de suponerla. Un periodo
    de cuatro no dice en QUE anios cae: «cada cuarto anio despues de 1965» y
    «cada cuarto anio despues de 1966» tienen el mismo periodo y no comparten
    ningun anio. Deducirla de `desde` habria funcionado para Mexico y dado el
    resultado equivocado para Estados Unidos, que es la peor clase de acierto.
    """
    periodo = f.get("periodo_anios") or 1
    if periodo <= 1:
        return True
    ancla = f.get("ancla_anio")
    if ancla is None:
        raise SystemExit(
            "«%s» declara periodo_anios=%s y no trae `ancla_anio`.\n"
            "  Un periodo no dice en que anios cae sin su anio base: escribelo "
            "en la captura con su literal." % (f.get("nombre", "?"), periodo))
    return (anio - int(ancla)) % int(periodo) == 0


def alcanza_a_la_unidad(f: dict) -> bool:
    """¿Cubre este feriado a la jurisdiccion de referencia?

    La cobertura vivia en una nota de texto libre. El Inauguration Day declaraba
    `cobertura = 'todo_el_pais'` mientras su propia nota decia que solo rige para
    empleados federales del area de Washington — o sea que ni siquiera alcanza a
    los federales de Nueva York, que es la unidad que medimos. Un campo que
    afirma lo contrario de la nota que tiene al lado es peor que un campo vacio.

    Razon INDEPENDIENTE de la periodicidad: aunque el corte cayera en anio de
    investidura, seguiria sin contar para Nueva York.
    """
    return f.get("cobertura") != "area_metropolitana_declarada"


# LA FICHA DE UNA UNIDAD, Y SI NO ESTA SE PARA.
#
# Dos comprobaciones —el descuadre de totales y el delta narrado— resolvian la
# ficha con `CRUDO/carpeta/"captura.json"` y hacian `continue` si no existia.
# Peru guarda las suyas con otro nombre, asi que las dos la SALTABAN EN SILENCIO:
# **la unica unidad exenta del control era el pais del que trata el informe.**
#
# Es la primera forma de la familia —la comprobacion que enmudece— y la peor
# version de ella, porque el hueco no estaba en el borde del conjunto sino en su
# centro. Un `continue` ante un archivo que falta es una exencion concedida por
# accidente y sin registro.
#
# Ahora se prueban los nombres conocidos y, si no hay ninguno, se ABORTA
# nombrando la unidad y lo que si hay en su carpeta. Que falle cuesta un minuto;
# que exima, un pais sin comprobar.
def captura_de(carpeta: str) -> dict:
    d = CRUDO / carpeta
    for nombre in ("captura.json", "captura-feriados.json", "captura-doble.json"):
        ruta = d / nombre
        if ruta.exists():
            return json.loads(ruta.read_text())
    sys.exit("%s no tiene ficha de captura con ninguno de los nombres conocidos.\n"
             "  En su carpeta hay: %s\n"
             "  Antes esto se saltaba en silencio y la unidad quedaba exenta de "
             "las comprobaciones." % (carpeta, ", ".join(
                 sorted(f.name for f in d.glob("*.json")) or ["nada"])))


def evidencia_de_no_cambio(v: dict) -> bool:
    """¿Autoriza el §10 bis codificar `sin_cambio_confirmado` en esta celda?

    DOS RAMAS Y NO UN UMBRAL, que es la correccion. Mi primera version pedia una
    sola cosa —donde se busco, el pasaje, y nivel 3 o mejor— y daba la celda por
    buena. Eso era UNA pantalla con umbral de nivel: no una version relajada de
    la regla de tres del §10, sino OTRA REGLA. Las filas que hubiera admitido no
    estaban autorizadas por ningun protocolo.

    El §10 bis, que el principal adopto sobre el borrador de
    la campaña del corte 2016, dice que para vacaciones la pantalla 1 no tiene
    instrumento —demostrado: un candidato en 45, falso, y ciega al caso israelí—
    y sustituye la regla de tres por:

      (a) pantalla 2 con INDICE OFICIAL de modificaciones, nota de version o
          comparacion de consolidados fechados, a nivel 1 o 2; o bien
      (b) pantalla 2 de nivel 3 o negativo sin indice, Y ADEMAS pantalla 3.

    La rama (a) no pide pantalla 3 porque un indice oficial no es un proxy: es la
    autoridad diciendo que toco el articulo y cuando. La (b) si, porque una
    reproduccion o un «no hallé» necesitan la redundancia que la regla de tres
    existe para dar.

    Y UNA CONDICION QUE VALE PARA LAS DOS: la ausencia solo es evidencia si la
    fuente REGISTRA LAS PRESENCIAS. Por eso `indice_registra_modificaciones` es
    obligatorio en (a): el consolidado en PDF del boletin espanol no anota
    ninguna modificacion en ningun sitio, y su silencio no significaba nada.
    """
    d = v.get("sin_cambio")
    if not isinstance(d, dict):
        return False
    if not (d.get("buscado_en") and d.get("cita")):
        return False
    nivel = d.get("nivel_de_fuente")
    if not isinstance(nivel, int):
        return False
    if nivel <= 2 and d.get("indice_registra_modificaciones") is True:
        return True                                   # rama (a)
    p3 = d.get("pantalla_3")
    return bool(nivel <= 3 and isinstance(p3, dict)
                and p3.get("cita") and p3.get("url"))  # rama (b)


def hasta_fecha(d: dict) -> str | None:
    """Fecha de fin de vigencia, o None. Acepta anio o fecha completa.

    EXISTE PORQUE NO SE PERSISTIA. El `hasta` de la captura se usaba solo para
    saltar la medicion del corte posterior, y nunca llegaba a la base: cero filas
    con fecha de fin. Consecuencia medida: siete celdas del panel publicado no
    reproducen desde `feriados.csv`, y las nueve filas causantes son EXACTAMENTE
    las derogaciones dentro de la ventana — el Karfreitag austriaco, el Store
    bededag danes, los cuatro eslovacos, el Dia de las Culturas costarricense, la
    version vieja del cumpleanos imperial y la transmision mexicana. Lo unico
    irreproducible del paquete eran las reformas, que es de lo que trata el
    proyecto.

    Un anio suelto se cierra el 31 de diciembre: `hasta: 2025` significa que el
    ultimo anio en que rigio fue 2025.
    """
    v = d.get("hasta")
    if v is None:
        return None
    s = str(v)
    return s if len(s) == 10 else "%s-12-31" % s


def desde_fecha(d: dict) -> str:
    """Fecha de entrada en vigor, aceptando anio o fecha completa.

    El grano anual bastaba con ocho unidades y dejo de bastar con Portugal, que
    repuso cuatro feriados el 2 de abril de 2016 — entre los dos cortes no, pero
    SI dentro del anio del corte.
    """
    v = d.get("desde")
    if v is None:
        return "2016-01-01"
    s = str(v)
    if len(s) == 10:
        return s
    # UN ANIO SUELTO SE VOLVIA 1 DE ENERO, que es la fecha mas favorable a entrar
    # en el corte, y eso es un relleno silencioso disfrazado de conversion.
    #
    # §31.2 ya habia registrado este error con Portugal y lo dio por cerrado
    # —«`desde` admite ahora fecha completa»—, pero admitir no es exigir: Colombia
    # y Nicaragua siguieron con grano anual y el cargador metio en el corte de
    # 2026 dos leyes que aun no existian el 1 de enero. La de Colombia se publico
    # el 2 de JUNIO; la de Nicaragua, el 20 de enero, y su propia captura decia
    # que una de las fechas «ya habia pasado al publicarse». Arreglar la
    # instancia y dejar viva la clase.
    #
    # Solo se exige la fecha completa cuando el anio COINCIDE con un corte, que
    # es el unico caso donde el mes cambia el resultado: una ley de 2019 esta
    # vigente el 1-ene-2026 se publicara en marzo o en octubre. Exigirsela a las
    # veinticuatro restantes seria ceremonia sin retorno.
    if s in ("2016", "2026"):
        raise SystemExit(
            "«desde: %s» es grano anual sobre un ANIO DE CORTE, y el mes decide "
            "si entra: %s.\n  Escribe la fecha completa de entrada en vigor."
            % (s, d.get("nombre") or d.get("instrumento") or "?"))
    return "%s-01-01" % s


def clase_y_campos(f: dict) -> tuple[str, dict]:
    """Traduce la clase capturada a la del esquema, o marca que no se puede."""
    cl = f.get("clase_de_regla")
    if cl == "SIN CLASE APLICABLE":
        # Ojo: no todo lo que la captura marca sin clase es el mismo caso. La
        # decision del principal del 2026-08-09 cubre la fecha que fija LA
        # COSTUMBRE LOCAL (Guatemala, El Salvador). El feriado electoral mexicano
        # tambien vino marcado sin clase, y NO es eso: su fecha la fija otra ley,
        # la electoral. La primera version de este cargador lo mapeo igual y le
        # puso una etiqueta falsa en silencio — el codificador habria leido
        # «jurisdiccion local» donde dice «ley electoral federal».
        #
        # Cuando la captura dice que hay una decision pendiente, se OMITE. Forzar
        # una clase para que la fila entre es exactamente lo que este proyecto no
        # hace: el hueco visible vale mas que la etiqueta comoda.
        if "PENDIENTE decidir" in (f.get("nota") or ""):
            return "", {}
        return "delegada_a_jurisdiccion_local", {}
    if cl == "computable":
        regla = f.get("regla", "")
        # El orden importa: `pascua_ortodoxa` va antes que `pascua` porque el
        # segundo es prefijo del primero y lo capturaria por error.
        for anc in ("pascua_ortodoxa", "pascua", "equinoccio_marzo",
                    "equinoccio_septiembre", "solsticio_junio",
                    "solsticio_diciembre", "ano_nuevo_lunar"):
            if regla.startswith(anc):
                # `pascua+0` es Pascua misma: Indonesia la declara como feriado
                # propio, no solo sus derivados.
                resto = regla[len(anc):] or "+0"
                return "relativa", {"ancla": anc, "offset_dias": int(resto)}
        return "", {}
    if cl == "relativa_a_fecha":
        return "relativa_a_fecha", {"mes": f["mes"], "dia": f["dia"],
                                    "dia_semana": f["dia_semana"],
                                    "offset_dias": f["offset_dias"]}
    if cl == "remision_normativa":
        return "remision_normativa", {"instrumento_remitido": f["instrumento_remitido"]}
    if cl == "lunar":
        # Uno de los dos dias, nunca los dos: el esquema lo exige y aqui se
        # respeta pasando solo el que la captura trae.
        campos = {"calendario_lunar": f["calendario_lunar"], "mes_lunar": f["mes_lunar"]}
        if f.get("dia_lunar_desde_fin") is not None:
            campos["dia_lunar_desde_fin"] = f["dia_lunar_desde_fin"]
        else:
            campos["dia_lunar"] = f["dia_lunar"]
        return "lunar", campos
    if cl == "cuota_designada_por_empleador":
        return "cuota_designada_por_empleador", {
            "conjunto_de_referencia": f["conjunto_de_referencia"]}
    if cl == "dependiente_de_proclamacion":
        return "dependiente_de_proclamacion", {}
    if cl == "ordinal":
        # «El primer lunes de febrero». Mexico es la unica del piloto que la
        # ejercita, y la clase existia sin usarse hasta que aparecio.
        return "ordinal", {"ordinal": f["ordinal"], "dia_semana": f["dia_semana"],
                           "mes": f["mes"]}
    if cl == "fija" and f.get("fecha"):
        mes, dia = f["fecha"].split("-")
        return "fija", {"mes": int(mes), "dia": int(dia)}
    return "", {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validar", action="store_true")
    args = ap.parse_args()

    con = sqlite()
    resumen = []

    _ultima = [None]
    con.set_trace_callback(lambda s: _ultima.__setitem__(0, s))

    _n = [0]

    def nid():
        """Identificador unico y global. Antes cada tipo de fila calculaba el suyo
        con una formula distinta, y con 47 unidades esas formulas colisionaron.
        Un contador comun no puede chocar consigo mismo."""
        _n[0] += 1
        return _n[0]

    hecho = 0

    # --- protocolo congelado y lote de captura -------------------------------
    # V7 exigio esto y tenia razon: un hecho sin medicion no dice contra que
    # corte ni bajo que protocolo se capturo, o sea no es auditable. El par
    # version-hash se SIEMBRA DESDE EL REGISTRO, no se escribe aqui: si se
    # escribiera a mano, el vinculo lote->protocolo seria decorativo, que es
    # justo el fallo que la revisión cruzada encontro en v2.9.
    import re
    reg = (CONGELAMIENTO).read_text()
    # LA ETIQUETA ADMITE SUFIJO DE IDIOMA. Desde que una entrada declara los dos
    # —«Archivo (es)» y «Archivo (en)»— esta expresion dejo de reconocer la
    # entrada vigente y `ultima[-1]` se quedaba con la ANTERIOR: el paquete
    # entero salio sellado con v2.23 teniendo el protocolo en v2.24. No fallo —
    # eligio una entrada mas vieja y siguio, que es la forma de esta familia que
    # mas caro sale, porque el resultado es plausible.
    #
    # Lo cazo `verificar_cifras` comparando la version del documento contra la de
    # la exportacion; sin esa comprobacion cruzada habria viajado.
    ultima = re.findall(
        r"## feriados y vacaciones · (v\d+\.\d+)\b.*?"
        r"\| Archivo(?:\s*\((?:es|en)\))? \| `([^`]+)` \|.*?"
        r"\| SHA-256(?:\s*\((?:es|en)\))? \| `([0-9a-f]{64})` \|",
        reg, re.S)
    if not ultima:
        sys.exit("no pude leer una entrada del registro de congelamientos")
    # LA VIGENTE SE LEE DE LA FILA QUE LO DECLARA, no del orden del archivo.
    #
    # Esto tomaba `ultima[-1]` —la ultima entrada por orden de aparicion— y
    # funcionaba porque las entradas se venian anadiendo al final. Al insertar
    # v2.26 arriba, el paquete salio sellado con la version ANTERIOR: portada
    # declarando v2.25 y hash `5fc6cf78`, embarcando el archivo que hashea
    # `822279c6`. Ninguna compuerta lo vio, porque C10 compara el protocolo
    # contra la entrada vigente del registro y las dos eran coherentes entre si
    # — la incoherente era la portada.
    #
    # El registro YA declara cual es la vigente, en su fila `Vigente`. Que el
    # cargador dedujera lo mismo del orden es la figura de siempre: **la decision
    # viviendo fuera del artefacto que la declara.** Ahora se lee esa fila, y si
    # no hay exactamente una vigente se para: cero es un registro sin timon y dos
    # es una ambiguedad que nadie deberia resolver adivinando.
    # SE PARTE EN BLOQUES ANTES DE BUSCAR, y esto tambien costo un intento. Con
    # una sola expresion sobre el archivo entero, el `.*?` cruza de una entrada a
    # otra: caso el encabezado de la PRIMERA version con la fila `Vigente` de la
    # ultima y sello el paquete con v2.0. Un patron que puede saltar de registro
    # a registro no esta leyendo registros.
    bloques = re.split(r"\n(?=## feriados y vacaciones · v)", reg)
    vigentes = []
    for b in bloques:
        if not re.search(r"\| Vigente \| si \|", b):
            continue
        m = re.search(r"## feriados y vacaciones · (v\d+\.\d+)\b", b)
        a = re.search(r"\| Archivo(?:\s*\((?:es|en)\))? \| `([^`]+)` \|", b)
        h = re.search(r"\| SHA-256(?:\s*\((?:es|en)\))? \| `([0-9a-f]{64})` \|", b)
        if m and a and h:
            vigentes.append((m.group(1), a.group(1), h.group(1)))
    if len(vigentes) != 1:
        sys.exit("el registro de congelamiento declara %d versiones vigentes y "
                 "tiene que declarar exactamente una.\n"
                 "  Halladas: %s" % (len(vigentes),
                                     ", ".join(v[0] for v in vigentes) or "ninguna"))
    version, archivo, hash_ = vigentes[0]
    con.execute("INSERT INTO protocolo_congelado (version,hash,archivo,congelado_en) "
                "VALUES (?,?,?,?)", (version, hash_, archivo, "2026-08-09T23:55:00Z"))
    # La etiqueta se DERIVA del numero de unidades, no se escribe. Durante dias
    # dijo 'piloto-ocho-unidades' sobre una base de 47, y esa cadena viajaba al
    # manifiesto del paquete publicado: una etiqueta falsa en el sitio donde
    # alguien la citaria. Cualquier rotulo escrito a mano se queda viejo en
    # cuanto crece lo que rotula.
    con.execute("INSERT INTO lote_captura (lote_id,etiqueta,version_protocolo,"
                "hash_protocolo,estado) VALUES (1,?,?,?,'ciego')",
                ("captura-%d-unidades" % len(UNIDADES), version, hash_))
    # Commit antes del bucle. Sin esto, el rollback de la PRIMERA unidad que
    # falla se lleva por delante el lote y el protocolo, y todas las unidades
    # siguientes revientan por arrastre con «FOREIGN KEY constraint failed».
    # Cuatro unidades aparecian rechazadas por un fallo que era mio y no suyo.
    con.commit()
    print("  lote 1 contra protocolo %s (%s)" % (version, hash_[:12]))
    print()

    # Pares de versiones que no encontraron el evento que los separa. Se acumulan
    # aqui y salen por pantalla al final: enlazar por aproximacion seria peor que
    # no enlazar, porque la fila resultante afirmaria un vinculo que nadie
    # comprobo. Ver el bloque de `reforma_versiones` mas abajo.
    pares_sin_evento = []
    # Versiones anteriores cuyo corte de 2016 se declara `verificado_primaria` sin
    # que la captura diga de que nivel de fuente sale. Ver el bloque de la
    # medicion de 2016 mas abajo.
    niveles_sin_declarar = []

    for carpeta, (iso3, nombre, ciudad, *_en) in UNIDADES.items():
      try:
        con.execute('SAVEPOINT unidad')
        ruta = CRUDO / carpeta / "captura.json"
        if not ruta.exists():
            ruta = CRUDO / carpeta / "captura-feriados.json"
        if not ruta.exists():
            resumen.append((nombre, 0, 0, "sin archivo de captura", ""))
            continue
        cap = json.loads(ruta.read_text())

        jid = len(resumen) + 1
        # `nivel` describe la FILA, y la fila es una ciudad. La primera version
        # ponia 'nacional' en las 47, con lo que la base AFIRMABA que Berlin y
        # Sidney son jurisdicciones nacionales. Lo destapo la exportacion:
        # publicada, esa columna invita a agregar los 47 numeros como cifras de
        # pais, y en un federal sin ley nacional de feriados no existe «el
        # numero del pais».
        #
        # Al corregirlo salto el CHECK `(nivel='nacional') = (padre_id IS NULL)`
        # y el esquema tenia razon: una jurisdiccion subnacional sin padre deja
        # el pais implicito en una cadena ISO, y entonces nada impide que dos
        # unidades del mismo pais queden sin relacion visible. Asi que el pais
        # se materializa como fila. Los ids de pais van desplazados 100 sobre
        # los de ciudad, que van de 1 a 47.
        jid_pais = jid + 100
        pais_en, ciudad_en = (UNIDADES[carpeta] + (None, None))[3:5]
        con.execute("INSERT INTO jurisdicciones VALUES (?,?,?,?,?,?,?,?)",
                    (jid_pais, iso3, nombre, pais_en, "nacional", None,
                     "2000-01-01", None))
        con.execute("INSERT INTO jurisdicciones VALUES (?,?,?,?,?,?,?,?)",
                    (jid, iso3, ciudad, ciudad_en, "subnacional", jid_pais,
                     "2000-01-01", None))

        # --- eventos de reforma ----------------------------------------------
        # La tabla existia con el vocabulario exacto —incluidos `suspension`,
        # `restitucion` y `permanente_o_temporal`— y CERO filas y cero
        # referencias en este cargador: disenada y nunca conectada.
        #
        # Lo que la obligo a existir de verdad fue Eslovaquia. Su corte de 2026
        # cae en el unico ano en que una disposicion transitoria suspende dos
        # feriados, asi que el panel lee cuatro perdidos cuando los permanentes
        # son dos. El dato del panel es correcto y la lectura es falsa: la peor
        # combinacion, porque no hay nada que falle.
        #
        # Cuelga del PAIS y no de la ciudad, como los feriados.
        #
        # ALCANCE DECLARADO, para que no se lea como mas de lo que es: solo
        # entran los eventos que una captura declara en `eventos_reforma`. Las
        # demas describen sus reformas en prosa y con claves distintas cada una;
        # normalizarlas es otra tanda. La tabla es PARCIAL y dice de que.
        eventos_por_fecha = {}
        for ev in cap.get("eventos_reforma") or []:
            cur = con.execute(
                "INSERT INTO eventos_reforma (jurisdiccion_id,tipo,vigencia_desde,"
                "causa,permanente_o_temporal,cita) VALUES (?,?,?,?,?,?)",
                (jid_pais, ev["tipo"], ev["vigencia_desde"], ev.get("que"),
                 ev["permanente_o_temporal"], ev["cita"]))
            # Solo los PERMANENTES son candidatos a separar dos versiones. Una
            # disposicion temporal —el puente israeli de quince dias— no abre un
            # regimen nuevo: manda leer otro numero durante una ventana y decae.
            # Meterla en el indice haria que un par de versiones pudiera
            # engancharse a un evento que por definicion no las separa.
            if ev["permanente_o_temporal"] == "permanente":
                eventos_por_fecha.setdefault(ev["vigencia_desde"], []).append(
                    cur.lastrowid)

        # --- fuentes ---------------------------------------------------------
        # La primera version de este cargador insertaba hechos sin fuente, y las
        # validaciones lo atraparon con 118 violaciones de V1, «hecho sin
        # evidencia». No era un falso positivo: el protocolo exige que todo hecho
        # tenga al menos una fuente, y yo me habia saltado el paso. La red
        # funcionando contra quien la escribio.
        fuentes_id = []
        for clave, f in (cap.get("fuentes") or {}).items():
            fid = nid()
            con.execute(
                "INSERT INTO fuentes (fuente_id,url,version_archivada,autoridad,"
                "jurisdiccion_id,fecha_de_norma,nivel_de_fuente) VALUES (?,?,?,?,?,?,?)",
                (fid, f.get("url") or "sin-url-archivada",
                 # `version_archivada` es NOT NULL a proposito: una URL viva no
                 # basta porque puede cambiar. Cuando la captura no archivo nada,
                 # se dice, en vez de fabricar una referencia inexistente.
                 f.get("version_archivada") or "PENDIENTE DE ARCHIVAR",
                 f.get("cita", clave)[:120], jid,
                 # Solo si es fecha ISO completa. Varias capturas traen «1985» o
                 # «marzo de 2019», y el CHECK las rechazaba tumbando la unidad
                 # entera por un metadato accesorio. La fecha imprecisa vive en
                 # la captura; aqui va nula antes que romper.
                 (lambda x: x if isinstance(x, str) and len(x) == 10
                  and x[4] == x[7] == "-" else None)(
                     f.get("publicacion") or f.get("promulgacion")),
                 int(f.get("nivel_de_fuente", 6))))
            fuentes_id.append(fid)
        estado_2016 = (cap.get("corte_2016") or {}).get("estado", "no_capturado")
        nivel_min = min([int(f.get("nivel_de_fuente", 6))
                         for f in (cap.get("fuentes") or {}).values()] or [6])

        # --- feriados -------------------------------------------------------
        cargados, omitidos, motivos = 0, 0, []
        for f in feriados_de(cap, ciudad):
            hecho = nid()
            clase, campos = clase_y_campos(f)
            if not clase:
                omitidos += 1
                motivos.append(f.get("nombre", "?"))
                continue
            con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                        (hecho, "feriado_version"))
            con.execute(
                "INSERT INTO feriado_version (feriado_version_id,hecho_tipo,feriado_id,"
                "jurisdiccion_id,sector,vigencia_desde,vigencia_hasta,nombre_oficial,"
                "categoria,recurrencia,periodo_anios,regimen,duracion_dias,cobertura,"
                "elegibilidad) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                # `desde` admite anio (2016) o fecha completa (2016-04-02). Antes
                # solo anio, con un comentario mio que decia que dentro del anio
                # daba igual. ES FALSO y Portugal lo demuestra: la Lei 8/2016
                # repone cuatro feriados el 2 de abril, asi que al corte del 1 de
                # enero de 2016 Portugal tenia 9 y no 13. La correccion va aqui,
                # donde estaba el error.
                (hecho, "feriado_version", hecho, jid,
                 f.get("sector", "privado"), desde_fecha(f), hasta_fecha(f),
                 f.get("nombre", "?"),
                 f.get("categoria", "descanso_pagado_obligatorio"),
                 # Recurrencia y periodo se LEEN de la captura. Asumirlos anuales
                 # habria borrado en silencio el feriado sexenal de Mexico, que es
                 # justo el caso para el que se anadio `periodo_anios`.
                 f.get("recurrencia", "recurrente"), f.get("periodo_anios", 1),
                 f.get("regimen", "descanso_obligatorio"),
                 # `dias_que_representa` es para las CUOTAS: una fila que vale
                 # doce dias sin fecha propia. Sin esto Tailandia sumaba dos
                 # —el feriado nombrado y la cuota entera contada como uno— en
                 # vez de trece, y el conteo habria seguido igual de mal despues
                 # de resolver la clase, que es la peor forma de arreglar algo:
                 # la que parece arreglado.
                 float(f.get("dias_que_representa") or f.get("fraccion", 1)),
                 f.get("cobertura", "todo_el_pais"),
                 f.get("elegibilidad", "sin_condicion")))
            rid = nid()
            con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                        (rid, "regla_fecha_version"))
            # Un feriado puede traer VARIAS reglas: la principal y las
            # alternativas condicionales. `reglas_alternativas` las lista con su
            # condicion; la principal es la de la propia entrada, que lleva
            # condicion solo si su existencia es condicional.
            reglas = [(clase, campos, f.get("condicion"))]
            for alt in (f.get("reglas_alternativas") or []):
                clase_alt, campos_alt = clase_y_campos(alt)
                if clase_alt:
                    reglas.append((clase_alt, campos_alt, alt.get("condicion")))
            for clase_i, campos_i, cond in reglas:
                rid_i = rid if clase_i is clase and campos_i is campos else nid()
                if rid_i != rid:
                    con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                                (rid_i, "regla_fecha_version"))
                con.execute(
                    "INSERT INTO regla_fecha_version (regla_fecha_version_id,hecho_tipo,"
                    "feriado_version_id,vigencia_desde,sistema_calendarico,clase_de_regla,"
                    "mes,dia,ancla,offset_dias,ordinal,dia_semana,instrumento_remitido,"
                    "conjunto_de_referencia,calendario_lunar,mes_lunar,dia_lunar,"
                    "dia_lunar_desde_fin,condicion_dia_semana,condicion_referencia) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (rid_i, "regla_fecha_version", hecho,
                     desde_fecha(f), "gregoriano", clase_i,
                     campos_i.get("mes"), campos_i.get("dia"),
                     campos_i.get("ancla"), campos_i.get("offset_dias"),
                     campos_i.get("ordinal"), campos_i.get("dia_semana"),
                     campos_i.get("instrumento_remitido"),
                     campos_i.get("conjunto_de_referencia"),
                     campos_i.get("calendario_lunar"), campos_i.get("mes_lunar"),
                     campos_i.get("dia_lunar"), campos_i.get("dia_lunar_desde_fin"),
                     (cond or {}).get("dia_semana"), (cond or {}).get("referencia")))
                # Cada regla necesita SU evidencia, tambien las alternativas
                # condicionales. La primera version de las reglas multiples solo
                # se la ponia a la principal, y V1 —«hecho sin evidencia»— lo
                # atrapo con doce filas. Un hecho sin fuente no es auditable
                # aunque sea la variante rara de un feriado.
                if fuentes_id and rid_i != rid:
                    con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                                "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                                (rid_i, "regla_fecha_version", fuentes_id[0],
                                 "2026-08-10", "claude"))
            # Evidencia: el hecho se vincula a la primera fuente declarada de la
            # unidad. Es una simplificacion HONESTA y hay que decirla: la captura
            # todavia no asigna fuente por feriado, asi que el vinculo es de
            # unidad y no de fecha. Sin fuentes no cargaria nada; con esta, carga
            # y queda visible que el detalle falta.
            # Medicion: corte 2026, con la fecha efectiva y su banda. Sin esto
            # el hecho no dice contra que corte se capturo. Ver V7.
            # SOLO el feriado, no su regla de fecha: `mediciones.hecho_tipo`
            # admite unicamente los dos constructos que el proyecto MIDE. Lo
            # intente con ambos y el esquema lo rechazo, con razon — una regla de
            # fecha no es una medicion, es la forma de derivar una ocurrencia.
            # Una medicion POR CORTE en el que el hecho estaba vigente. Es lo que
            # hace panel a esto: el conteo de cada corte se DERIVA de la vigencia,
            # no de dos listas escritas a mano que pueden discrepar entre si.
            hasta = hasta_fecha(f)
            for corte in (2016, 2026):
                # Comparacion por FECHA, no por anio: un feriado vigente desde el
                # 2 de abril no estaba vigente el 1 de enero.
                #
                # Y NO SE SALTA LA MEDICION, se emite como `na`. Saltarla dejaba
                # hechos sin ninguna fila —V7, «hecho sin medicion», los cazo en
                # cuanto Colombia y Nicaragua pasaron a estar fuera de los DOS
                # cortes— y sobre todo perdia el resultado: que un feriado no
                # existiera aun en el corte es algo que MEDIMOS, no algo que
                # dejamos de mirar.
                #
                # La causa es `no_cubierto` y no `no_aplicable`, que son cosas
                # distintas y el esquema ya distinguia: `no_aplicable` es haber
                # evaluado la condicion y que no se cumpla; `no_cubierto` es que
                # el hecho cae fuera de la ventana. Mezclarlas habria inflado la
                # cifra publicada de condicionales evaluadas con casos que no lo
                # son.
                if desde_fecha(f) > "%d-01-01" % corte:
                    con.execute(
                        "INSERT INTO mediciones (lote_id,hecho_id,hecho_tipo,corte,"
                        "estado_verificacion,fecha_efectiva_de_medicion,"
                        "dentro_de_banda,causa) "
                        "VALUES (1,?,'feriado_version',?,'na',?,1,'no_cubierto')",
                        (hecho, corte, "%d-01-01" % corte))
                    continue
                # `hasta` cierra la vigencia. Sin esto, la version vieja del
                # feriado sexenal mexicano seguiria contando en 2026 junto con la
                # nueva, y Mexico mostraria un feriado de mas.
                #
                # Y AQUI TAMBIEN SE EMITE `na` EN VEZ DE SALTAR. El comentario de
                # arriba dice «no se salta la medicion, se emite como na» y esta
                # rama no lo cumplia: las nueve filas derogadas dentro de la
                # ventana se quedaban SIN NINGUNA medicion de 2026. El sintoma se
                # ve en el entregable — el D3 de Japon declara en el corte 2016
                # que excluyo y por que, y en el de 2026 la version de diciembre
                # desaparece sin una nota.
                #
                # Misma causa `no_cubierto` que el extremo opuesto: los dos son
                # «el hecho existe y cae fuera de la ventana en este corte», que
                # es distinto de `no_aplicable` —condicion evaluada que no se
                # cumple—. Simetrico y por eso mas facil de razonar.
                if hasta and hasta <= "%d-01-01" % corte:
                    con.execute(
                        "INSERT INTO mediciones (lote_id,hecho_id,hecho_tipo,corte,"
                        "estado_verificacion,fecha_efectiva_de_medicion,"
                        "dentro_de_banda,causa) "
                        "VALUES (1,?,'feriado_version',?,'na',?,1,'no_cubierto')",
                        (hecho, corte, "%d-01-01" % corte))
                    continue
                # Un corte no capturado NO se rellena con el otro. Indonesia fija
                # su calendario por decreto cada anio: copiar el de 2026 en 2016
                # no seria una aproximacion, seria inventar el corte.
                if corte == 2016 and estado_2016 == "no_capturado":
                    continue
                # Existencia condicional. La primera version SALTABA la medicion
                # de los anios en que el feriado no ocurre, y V7 —«hecho sin
                # medicion»— lo atrapo con tres filas. Tenia razon: que hayamos
                # EVALUADO la condicion y salga que no aplica es un resultado, no
                # una ausencia, y merece quedar escrito.
                #
                # Va como `estado_verificacion = 'na'` con `causa = 'no_aplicable'`,
                # que son dos valores que el esquema ya tenia para esto. La fecha
                # efectiva se conserva porque otra restriccion exige que sin fecha
                # la causa sea `sin_fecha_hallada`, y aqui fecha hay: es el dia en
                # que se evaluo. Los conteos excluyen los `na`.
                aplica = (ocurre_en(f, reglas, corte)
                          and ocurre_el_anio(f, corte)
                          and alcanza_a_la_unidad(f))
                con.execute(
                    "INSERT INTO mediciones (lote_id,hecho_id,hecho_tipo,corte,"
                    "estado_verificacion,fecha_efectiva_de_medicion,dentro_de_banda,causa) "
                    "VALUES (1,?,'feriado_version',?,?,?,1,?)",
                    (hecho, corte,
                     ("verificado_primaria" if nivel_min <= 2 else "supuesto")
                     if aplica else "na",
                     "%d-01-01" % corte, None if aplica else "no_aplicable"))
            if fuentes_id:
                for hid, ht in ((hecho, "feriado_version"), (rid, "regla_fecha_version")):
                    con.execute(
                        "INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                        "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                        (hid, ht, fuentes_id[0], "2026-08-09", "claude"))
            cargados += 1

        # --- vacaciones -------------------------------------------------------
        # La otra mitad del proyecto. Se carga solo si la captura sabe el TIPO DE
        # DIA: sin el, el numero es incomparable, y ponerle uno por defecto seria
        # cometer a mano el error de factor dos que el proyecto persigue.
        v = cap.get("vacaciones_normalizado") or {}
        vac_nota = ""
        # Sin regla de colocacion capturada NO se carga la titularidad. V22 lo
        # exige y tiene razon: una titularidad sin saber quien controla el momento
        # no puede producir la banda, que es el constructo propio del proyecto.
        # Rellenarla de oficio la vaciaria de contenido.
        # Una regla de colocacion que cubre solo una PORCION deja el resto sin
        # gobernar, y V23 lo marca con razon. Indonesia declara los 8 dias de cuti
        # bersama como asignacion estatal y no dice quien decide los otros 4.
        # Cargar la porcion sola publicaria una cobertura parcial como si fuera
        # completa; el hallazgo vive en la captura y en las notas hasta cerrarlo.
        if (v.get("colocacion") or {}).get("pendiente_residual"):
            v = dict(v, colocacion=None,
                     pendiente="regla de colocacion parcial: falta el residual")
        if (v.get("tipo") and v["tipo"] != "calendario"
                and v.get("base") is None
                and v.get("base_origen") != "horario_del_trabajador"):
            # El CHECK del esquema lo rechaza igual, pero su mensaje no dice que
            # falta. Nombrar el campo convierte un fallo opaco en un arreglo de
            # una linea para quien capturo.
            v = dict(v, colocacion=None,
                     pendiente="falta `base` (5 o 6 dias) o declarar "
                               "`base_origen: horario_del_trabajador` si la norma "
                               "remite al horario del trabajador; sin una de las "
                               "dos, la unidad %s es inconvertible" % v["tipo"])
        if v.get("dias") is not None and v.get("tipo") and v.get("colocacion"):
            vid = nid()
            con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                        (vid, "vacaciones_version"))
            con.execute(
                "INSERT INTO vacaciones_version (vacaciones_version_id,hecho_tipo,"
                "jurisdiccion_id,sector,vigencia_desde,texto_legal_dias,tipo_de_dia,"
                "base_semanal_dias,base_semanal_origen,"
                "periodo_de_calificacion_meses,base_antiguedad,"
                "imputacion_feriados_a_vacaciones) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (vid, "vacaciones_version", jid, "privado",
                 # Con version anterior, la vigente empieza EL DIA DE LA REFORMA.
                 # Dejarla en 2016 haria que las dos versiones se solaparan, y
                 # ademas afirmaria que el derecho de hoy regia antes de existir.
                 (v.get("version_anterior") or {}).get("hasta") or desde_fecha(v),
                 v["dias"], v["tipo"], v.get("base"),
                 None if v["tipo"] == "calendario"
                 else v.get("base_origen", "norma"),
                 v.get("meses", 12),
                 "servicio_continuo_empleador_actual",
                 v.get("imputacion") or "sin_regla_explicita"))
            if fuentes_id:
                con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                            "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                            (vid, "vacaciones_version", fuentes_id[0], "2026-08-10", "claude"))
            hasta = hasta_fecha(f)
            for corte in (2016, 2026):
                con.execute(
                    "INSERT INTO mediciones (lote_id,hecho_id,hecho_tipo,corte,"
                    "estado_verificacion,fecha_efectiva_de_medicion,dentro_de_banda) "
                    "VALUES (1,?,'vacaciones_version',?,?,?,1)",
                    # EL CORTE 2016 NO HEREDA LA VERIFICACION DEL 2026, y este era
                    # el defecto que el proyecto existe para corregir, reproducido
                    # por nosotros en la variable de vacaciones.
                    #
                    # La version anterior ponia `verificado_primaria` en LOS DOS
                    # cortes cuando la fuente del valor vigente era buena. Pero
                    # que la norma de 2026 este bien citada no dice nada sobre si
                    # en 2016 regia otra: eso es exactamente la «imputacion por
                    # supuesto de persistencia legal» que el README le reprocha al
                    # material importado. Con una sola version por jurisdiccion,
                    # el 2016 era identico al 2026 POR CONSTRUCCION y encima se
                    # declaraba verificado.
                    #
                    # Ahora el corte antiguo va `supuesto` salvo que la captura
                    # traiga una version anterior fechada. Un delta de cero pasa a
                    # significar «no se hallo modificatoria», que es lo que es.
                    #
                    # F0 · Y `sin_cambio_confirmado` DEJA DE SER UN VALOR MUERTO.
                    # Estaba en el CHECK del esquema desde el diseño y nada lo
                    # emitia — el tercer campo declarado y nunca conectado que
                    # aparece hoy, despues de `eventos_reforma` y de
                    # `periodo_anios`.
                    #
                    # La diferencia que transporta es la que este proyecto existe
                    # para no aplastar: `supuesto` es «no se hallo modificatoria»
                    # —o sea, no se busco a fondo— y `sin_cambio_confirmado` es
                    # «se busco y se confirmo que no cambio». Hoy las 43 unidades
                    # del corte antiguo estan en el primero, y sin este valor las
                    # veintiseis que se van a buscar no tendrian donde aterrizar:
                    # el trabajo se haria y el dato seguiria diciendo «supuesto».
                    # EL CORTE ANTIGUO SE GANA SU ESTADO, no lo hereda. Antes
                    # bastaba con que existiera `version_anterior` para que el
                    # 2016 recibiera `verificado_primaria` — y esa version trae
                    # su PROPIO nivel de fuente, que ningun guion leia. Es la
                    # figura que este cargador existe para impedir, una rama mas
                    # alla: el 2016 no heredaba la verificacion del 2026, se la
                    # daba a si mismo.
                    #
                    # Ahora el nivel sale de la version anterior cuando la trae, y
                    # si no la declara cae a `supuesto`. Israel ya declaraba 1;
                    # Mexico lo tenia citado —el decreto del DOF— y le faltaba el
                    # numero, asi que decision del principal: se completa la
                    # captura y nadie baja de estado.
                    # `na` NO ES UN GRADO MAS DE VERIFICACION, es otra cosa.
                    # Estados Unidos no tiene mandato de vacaciones que medir en
                    # ninguno de los dos cortes. Estaba en `supuesto`, que
                    # significa «no se hallo modificatoria» — y eso era falso
                    # sobre nuestro propio trabajo: si se busco, y la respuesta
                    # fue que no existe el derecho. Tampoco vale
                    # `sin_cambio_confirmado`: compararia dos ausencias y daria a
                    # entender que hay un derecho que se mantuvo estable.
                    #
                    # El esquema ya reservaba `na` y la metrica ya lo respeta. La
                    # captura tiene que DECLARARLO con su motivo y donde se
                    # busco: un `na` sin fundamento seria la ausencia disfrazada
                    # de decision. Decision del principal, 2026-08-12.
                    (vid, corte,
                     "na" if v.get("no_aplicable")
                     else ("verificado_primaria"
                      if (nivel_min if corte == 2026
                          else (v.get("version_anterior") or {})
                               .get("nivel_de_fuente", 9)) <= 2
                      else "supuesto")
                     if corte == 2026 or v.get("version_anterior")
                     else "sin_cambio_confirmado" if evidencia_de_no_cambio(v)
                     else "supuesto",
                     "%d-01-01" % corte))
            # LA VERSION ANTERIOR, si la captura la trae con su fecha y su fuente.
            # Sin esto la dimension temporal de vacaciones es plana por
            # construccion: 45 filas, todas vigentes desde el inicio de la
            # ventana, y el corte 2016 no puede diferir del 2026 aunque la ley
            # haya cambiado.
            ant = v.get("version_anterior")
            if ant:
                aid = nid()
                con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                            (aid, "vacaciones_version"))
                con.execute(
                    "INSERT INTO vacaciones_version (vacaciones_version_id,hecho_tipo,"
                    "jurisdiccion_id,sector,vigencia_desde,vigencia_hasta,"
                    "texto_legal_dias,tipo_de_dia,base_semanal_dias,base_semanal_origen,"
                    "periodo_de_calificacion_meses,base_antiguedad,"
                    "imputacion_feriados_a_vacaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (aid, "vacaciones_version", jid, "privado",
                     ant.get("desde", "2016-01-01"), ant["hasta"],
                     ant["dias"], ant.get("tipo", v["tipo"]),
                     ant.get("base", v.get("base")),
                     None if ant.get("tipo", v["tipo"]) == "calendario"
                     else ant.get("base_origen", v.get("base_origen", "norma")),
                     ant.get("meses", v.get("meses", 12)),
                     "servicio_continuo_empleador_actual",
                     ant.get("imputacion", v.get("imputacion") or "sin_regla_explicita")))
                # La medicion de 2016 pasa a esta version, y la actual deja de
                # tenerla: el corte antiguo mide lo que regia entonces.
                con.execute("DELETE FROM mediciones WHERE hecho_id=? AND corte=2016",
                            (vid,))
                # OJO CON ESTE `verificado_primaria`, QUE ESTA A PELO. El corte de
                # 2026 se gana el suyo pasando por `nivel_min <= 2`; el de 2016 lo
                # recibe por el mero hecho de que la captura traiga una version
                # anterior, sin que nadie mire de que fuente sale. Y la version
                # anterior TRAE su propio `nivel_de_fuente` en la captura —Israel
                # declara nivel 1— que ningun guion lee.
                #
                # Es la misma figura que el bloque de arriba existe para impedir,
                # una rama mas alla: alli el 2016 no debia heredar la verificacion
                # del 2026, y aqui no la hereda —simplemente se la da a si mismo.
                #
                # NO LO CAMBIO EN ESTE PASO, y digo por que: exigir el nivel
                # degradaria a Mexico a `supuesto`, porque su version anterior
                # tiene fuente y no tiene numero, y eso mueve el estado de
                # verificacion de una celda ya publicada. Es decision del
                # principal, no mia. Lo que hago es que deje de ser invisible.
                if not isinstance(ant.get("nivel_de_fuente"), int):
                    niveles_sin_declarar.append(nombre)
                con.execute(
                    "INSERT INTO mediciones (lote_id,hecho_id,hecho_tipo,corte,"
                    "estado_verificacion,fecha_efectiva_de_medicion,dentro_de_banda) "
                    "VALUES (1,?,'vacaciones_version',2016,'verificado_primaria',"
                    "'2016-01-01',1)", (aid,))

                # --- EL EVENTO QUE SEPARA LAS DOS VERSIONES --------------------
                # `reforma_versiones` es la tercera tabla del esquema disenada y
                # nunca conectada, despues de `eventos_reforma` y `periodo_anios`.
                # Hasta aqui la base podia tener el evento bien cargado y las dos
                # versiones bien cargadas SIN QUE NADA DIJERA que ese evento es el
                # que las separa. Mexico es el caso testigo del piloto y estaba
                # asi: el molde que vamos a copiar veinte veces, sin enlazar.
                #
                # EL ENLACE ES POR FECHA, y esa es la unica regla. La version
                # anterior cierra el dia en que el nuevo regimen empieza, asi que
                # el evento que las separa es el que rige DESDE ESA MISMA FECHA.
                # No se busca «el evento mas cercano» ni «el unico de vacaciones
                # que hay»: eso enlazaria por plausibilidad y produciria una fila
                # que afirma un vinculo que nadie comprobo.
                #
                # Y CUANDO NO CASA, NO SE ENLAZA Y SE DICE. Israel llega aqui con
                # `hasta` en 2016-12-31 y su propio evento declarando vigencia
                # desde 2017-01-01: la captura se contradice consigo misma en un
                # dia. Enganchar igual habria escondido la contradiccion detras
                # de una fila correcta de aspecto. Sale por pantalla al final.
                frontera = ant["hasta"]
                candidatos = eventos_por_fecha.get(frontera) or []
                if len(candidatos) == 1:
                    for hid, rol in ((aid, "anterior"), (vid, "nuevo")):
                        con.execute(
                            "INSERT INTO reforma_versiones (reforma_id,hecho_id,"
                            "hecho_tipo,rol) VALUES (?,?,'vacaciones_version',?)",
                            (candidatos[0], hid, rol))
                elif not candidatos:
                    pares_sin_evento.append(
                        "%s: las versiones se separan el %s y ningun evento "
                        "permanente del ledger rige desde esa fecha%s"
                        % (nombre, frontera,
                           " (los permanentes rigen desde: %s)"
                           % ", ".join(sorted(eventos_por_fecha))
                           if eventos_por_fecha else " (no declara eventos)"))
                else:
                    pares_sin_evento.append(
                        "%s: %d eventos permanentes rigen desde el %s y no hay "
                        "forma de saber cual separa las versiones"
                        % (nombre, len(candidatos), frontera))
                # V22 exige regla de colocacion en TODA version, y tiene razon:
                # una version sin ella no dice quien decide cuando se toma ese
                # derecho. Se copia la vigente porque la reforma mexicana toca el
                # QUANTUM y la continuidad —arts. 76 y 78—, no el articulo que
                # fija la oportunidad; que no se hallara modificatoria de la
                # colocacion es un supuesto y va escrito en el literal.
                acid = nid()
                con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                            (acid, "regla_colocacion"))
                con.execute(
                    "INSERT INTO regla_colocacion (regla_colocacion_id,hecho_tipo,"
                    "vacaciones_version_id,orden_precedencia,modo_aplicacion,alcance,"
                    "instrumento,iniciativa,veto_empleador,default_ante_silencio,"
                    "resolucion_desacuerdo,literal_normativo) "
                    "VALUES (?,?,?,1,'particion','todo_el_derecho',?,?,?,?,?,?)",
                    (acid, "regla_colocacion", aid, cl["instrumento"], cl["iniciativa"],
                     cl.get("veto"), cl.get("silencio"),
                     cl.get("resolucion_desacuerdo"),
                     "[version anterior] " + cl["literal"][:1900]))
                # La escala de la version anterior, con su tramo cero delante:
                # V12 exige que arranque en cero porque antes del periodo de
                # calificacion el derecho ES cero, y eso es un tramo y no un
                # vacio. Vale igual para las versiones historicas.
                meses_calif = ant.get("meses", v.get("meses", 12))
                tramos_ant = ([(0, meses_calif, 0)] if meses_calif else []) \
                    + list(ant.get("escala") or [])
                for desde, hasta, q in tramos_ant:
                    eaid = nid()
                    con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                                (eaid, "escala_antiguedad"))
                    con.execute(
                        "INSERT INTO escala_antiguedad (escala_id,hecho_tipo,"
                        "vacaciones_version_id,vigencia_desde,desde_meses,"
                        "desde_dias_residuales,hasta_meses,hasta_dias_residuales,"
                        "operador_frontera,literal_normativo,quantum,tipo_de_dia) "
                        "VALUES (?,?,?,?,?,0,?,?,?,?,?,?)",
                        (eaid, "escala_antiguedad", aid, ant.get("desde", "2016-01-01"),
                         desde, hasta, 0 if hasta else None, "tras_completar",
                         (ant.get("literal") or "")[:200], q,
                         ant.get("tipo", v["tipo"])))
                    # V1 vale para los tramos historicos igual que para los
                    # vigentes: todo hecho lleva su fuente. Se me olvido en la
                    # primera version y la validacion lo pillo con dos filas.
                    if fuentes_id:
                        con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,"
                                    "fuente_id,fecha_de_verificacion,revisor) "
                                    "VALUES (?,?,?,?,?)",
                                    (eaid, "escala_antiguedad", fuentes_id[0],
                                     "2026-08-11", "claude"))
                if fuentes_id:
                    con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                                "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                                (aid, "vacaciones_version", fuentes_id[0],
                                 "2026-08-11", "claude"))
                    for h in (acid,):
                        con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,"
                                    "fuente_id,fecha_de_verificacion,revisor) "
                                    "VALUES (?,?,?,?,?)",
                                    (h, "regla_colocacion", fuentes_id[0],
                                     "2026-08-11", "claude"))

            # V12: la escala arranca en cero. Antes del periodo de calificacion
            # el derecho es cero, y eso es un tramo, no un vacio.
            # Un periodo de calificacion de CERO meses es un valor legitimo
            # -Noruega: el derecho a los dias no depende del devengo- y generaba
            # un tramo degenerado (0,0,0) que rechazaba la unidad entera.
            tramos = ([(0, v["meses"], 0)] if v.get("meses") else []) \
                + list(v.get("escala") or [])
            cl = v["colocacion"]
            cid = nid()
            con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                        (cid, "regla_colocacion"))
            con.execute(
                "INSERT INTO regla_colocacion (regla_colocacion_id,hecho_tipo,"
                "vacaciones_version_id,orden_precedencia,modo_aplicacion,alcance,"
                "instrumento,iniciativa,veto_empleador,default_ante_silencio,"
                "resolucion_desacuerdo,"
                "literal_normativo,porcion_dias,porcion_tipo_de_dia) "
                "VALUES (?,?,?,1,'particion',?,?,?,?,?,?,?,?,?)",
                (cid, "regla_colocacion", vid,
                 cl.get("alcance", "todo_el_derecho"),
                 cl["instrumento"], cl["iniciativa"],
                 cl.get("veto"), cl.get("silencio"),
                 cl.get("resolucion_desacuerdo"), cl["literal"],
                 cl.get("porcion_dias"),
                 v["tipo"] if cl.get("porcion_dias") else None))
            if fuentes_id:
                con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                            "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                            (cid, "regla_colocacion", fuentes_id[0], "2026-08-10", "claude"))
            res = v.get("colocacion_residual")
            if res:
                rcid = nid()
                con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                            (rcid, "regla_colocacion"))
                con.execute(
                    "INSERT INTO regla_colocacion (regla_colocacion_id,hecho_tipo,"
                    "vacaciones_version_id,orden_precedencia,modo_aplicacion,alcance,"
                    "instrumento,iniciativa,veto_empleador,default_ante_silencio,"
                    "resolucion_desacuerdo,"
                    "literal_normativo) VALUES (?,?,?,2,'particion','residual',?,?,?,?,?,?)",
                    (rcid, "regla_colocacion", vid, res["instrumento"], res["iniciativa"],
                     res.get("veto"), res.get("silencio"),
                     res.get("resolucion_desacuerdo"), res["literal"]))
                if fuentes_id:
                    con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                                "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                                (rcid, "regla_colocacion", fuentes_id[0], "2026-08-10", "claude"))
            for i, (desde, hasta, q) in enumerate(tramos):
                eid = nid()
                con.execute("INSERT INTO hechos (hecho_id,hecho_tipo) VALUES (?,?)",
                            (eid, "escala_antiguedad"))
                con.execute(
                    "INSERT INTO escala_antiguedad (escala_id,hecho_tipo,"
                    "vacaciones_version_id,vigencia_desde,desde_meses,"
                    "desde_dias_residuales,hasta_meses,hasta_dias_residuales,"
                    "operador_frontera,literal_normativo,quantum,tipo_de_dia) "
                    "VALUES (?,?,?,?,?,0,?,?,?,?,?,?)",
                    (eid, "escala_antiguedad", vid, "2016-01-01", desde,
                     hasta, 0 if hasta else None, "tras_completar",
                     v.get("literal", "")[:200], q, v["tipo"]))
                if fuentes_id:
                    con.execute("INSERT INTO evidencia (hecho_id,hecho_tipo,fuente_id,"
                                "fecha_de_verificacion,revisor) VALUES (?,?,?,?,?)",
                                (eid, "escala_antiguedad", fuentes_id[0], "2026-08-10", "claude"))
            vac_nota = "vac %s %s" % (v["dias"], v["tipo"])
        elif not v.get("colocacion"):
            vac_nota = "VAC SIN CARGAR: %s" % (v.get("pendiente") or
                                               "falta la regla de colocacion")
        else:
            vac_nota = "VAC SIN CARGAR: %s" % (v.get("pendiente") or "sin capturar")

        nota = ""
        if omitidos:
            nota = "%d feriados sin clase resoluble: %s" % (
                omitidos, ", ".join(motivos[:2]) + ("…" if omitidos > 2 else ""))
        if not feriados_de(cap):
            nota = "la captura no trae lista de feriados con fechas"
        # La nota de feriados y la de vacaciones se guardan aparte: juntarlas en
        # una hacia que el contador de unidades completas leyera cualquier nota de
        # vacaciones como si fuera un feriado faltante, y reportaba 0 de 8.
        con.execute('RELEASE unidad')
        resumen.append((nombre, cargados, omitidos, nota, vac_nota))
      except Exception as e:
        # Decir QUE sentencia fallo, no solo que fallo. Perseguir a mano cual de
        # veinte inserts revienta es tiempo perdido cuando SQLite ya lo sabe.
        _ultima[0] = (_ultima[0] or "").replace(chr(10), " ")[:70]
        # Una unidad malformada no tumba las otras 46. Se reporta con su
        # motivo y se sigue; ver el estado del conjunto vale mas que
        # detenerse en el primer tropiezo.
        try:
            con.execute('ROLLBACK TO unidad')
            con.execute('RELEASE unidad')
        except sqlite3.Error:
            pass
        resumen.append((nombre, 0, 0,
                        'RECHAZADA: %s: %s'
                        % (type(e).__name__, str(e).split(chr(10))[0][:60]), ''))

    con.commit()

    print("== Carga del piloto ==\n")
    print("  %-14s %8s %9s  %s" % ("Unidad", "cargados", "omitidos", "por que"))
    print("  " + "-" * 74)
    tot_c = tot_o = 0
    for nombre, c, o, nota, vac in resumen:
        tot_c += c; tot_o += o
        print("  %-14s %8d %9d  %s" % (nombre, c, o, (nota + "  " + vac).strip()))
    print("  " + "-" * 74)
    print("  %-14s %8d %9d" % ("TOTAL", tot_c, tot_o))

    completas = sum(1 for _, c, o, n, _v in resumen if c and not n)
    con_vac = sum(1 for _, _c, _o, _n, v in resumen
                  if v and not v.startswith("VAC SIN"))
    print("\n  %d de %d unidades con la lista de feriados completa."
          % (completas, len(UNIDADES)))
    print("  %d de %d unidades con vacaciones cargadas." % (con_vac, len(UNIDADES)))

    # ORTOGRAFIA DE LOS NOMBRES. De 577, cinco llevaban algun diacritico: las
    # capturas se escribieron en ASCII y eso llego al paquete. En el apendice de
    # verificacion de Peru se leia «Ano Nuevo» y «Navidad del Senor», y en
    # castellano `ano` y `año` son palabras distintas.
    #
    # Falla y no corrige: el nombre correcto pertenece a la captura, que es el
    # dato crudo con procedencia. Un cargador que arregle la ortografia al vuelo
    # deja el crudo mal para siempre y esconde el defecto en un derivado.
    faltas = []
    for carpeta, (iso3, _p, _c, *_en) in UNIDADES.items():
        # `jornada.json` entra tambien: cinco citas suyas seguian en ASCII
        # cuando las de feriados ya estaban limpias, porque la primera pasada
        # solo miro los dos archivos de captura. Vigilar unos archivos y no
        # otros deja el defecto vivo justo donde nadie mira.
        for base in ("captura.json", "captura-feriados.json", "jornada.json"):
            ruta = CRUDO / carpeta / base
            if not ruta.exists():
                continue
            nombres, citas = [], []
            def _rec(n):
                if isinstance(n, dict):
                    if isinstance(n.get("nombre"), str):
                        nombres.append(n["nombre"])
                    # Las citas son transcripcion nuestra del titulo de la norma
                    # y salieron en ASCII igual que los nombres. `literal` NO se
                    # vigila: es el texto citado a la letra y retocarlo seria
                    # falsear la cita.
                    if isinstance(n.get("cita"), str):
                        citas.append(n["cita"])
                    for v in n.values(): _rec(v)
                elif isinstance(n, list):
                    for v in n: _rec(v)
            _rec(json.loads(ruta.read_text()))
            faltas += [(iso3, a, b) for a, b in mal_escritos(nombres, iso3)]
            faltas += [(iso3, c, cita_correcta(c, iso3)) for c in citas
                       if cita_correcta(c, iso3) != c]
    if faltas:
        print("  ORTOGRAFIA: %d nombre(s) de feriado sin la tilde que les toca:"
              % len(faltas))
        for iso3, a, b in faltas[:8]:
            print("     %s  «%s» -> «%s»" % (iso3, a, b))
        print("     Se corrigen en la captura, que es el dato crudo. Este "
              "cargador\n     no los arregla al vuelo a proposito.")
        return 1

    # CONTRASTE CONTRA EL TOTAL QUE LA CAPTURA DECLARA. Diecinueve capturas
    # escriben cuantos feriados deberia haber en su corte y ninguna se comprobaba
    # nunca. Las tres cosas que se arreglaron hoy —El Salvador con un dia de mas
    # por sumar las dos ramas de un o-exclusivo, Colombia con una ley de junio
    # dentro del corte de enero, Nicaragua con cuatro— las habria cazado esto el
    # dia que se escribieron. En los tres casos el numero correcto estaba en la
    # captura, al lado del falso.
    #
    # Las discrepancias legitimas van EN UNA LISTA CON SU RAZON, no en un aviso
    # que se ignora: son cantidades distintas, no errores. Cualquier otra falla.
    EXPLICADAS = {
        ("KOR", 2026): "`total_cargable` es un subconjunto declarado; el nominal "
                       "de la captura es texto porque incluye electorales y "
                       "sustitutos que no son fechas fijas.",
        ("ECU", 2016): "`total_nacional` no incluye el feriado propio de "
                       "Guayaquil, que es la unidad de referencia.",
        ("USA", 2016): "`total_exigible_sector_privado` mide otro constructo: en "
                       "EE. UU. ningun feriado obliga al empleador privado. Los "
                       "de la base son `cierre_sector_publico` y por eso la "
                       "metrica los excluye.",
        ("USA", 2026): "Igual que 2016.",
    }
    import unicodedata as _u
    def _plano(x):
        return "".join(c for c in _u.normalize("NFD", x.lower())
                       if _u.category(c) != "Mn")
    cargado = {}
    for iso, corte, n in con.execute(
            "SELECT j.iso3, m.corte, SUM(f.duracion_dias) FROM mediciones m "
            "  JOIN feriado_version f ON f.feriado_version_id = m.hecho_id "
            "   AND m.hecho_tipo='feriado_version' "
            "  JOIN jurisdicciones j ON j.jurisdiccion_id = f.jurisdiccion_id "
            " WHERE m.estado_verificacion <> 'na' GROUP BY j.iso3, m.corte"):
        cargado[(iso, corte)] = n
    descuadres = []
    for carpeta, (iso3, _p, ciudad, *_en) in UNIDADES.items():
        fe = (captura_de(carpeta).get("feriados") or {})
        if not isinstance(fe, dict):
            continue
        for corte in (2016, 2026):
            cands = {k: v for k, v in fe.items()
                     if k.startswith("total") and str(corte) in k
                     and isinstance(v, (int, float))}
            if not cands:
                continue
            pref = ([k for k in cands if _plano(ciudad).split()[-1] in _plano(k)]
                    or [k for k in cands if "referencia" in _plano(k)]
                    or sorted(cands))
            dice, hay = cands[pref[0]], cargado.get((iso3, corte))
            if hay is None or abs(dice - hay) <= 0.01:
                continue
            if (iso3, corte) in EXPLICADAS:
                continue
            descuadres.append("%s corte %d: la captura declara %g en `%s` y la "
                              "base tiene %g" % (iso3, corte, dice, pref[0], hay))
    if descuadres:
        print("  DESCUADRE contra el total declarado por la captura:")
        for d in descuadres:
            print("     %s" % d)
        print("     El codificador conto y escribio el numero. Si la base dice "
              "otro,\n     o el cargador se equivoca o la captura lo hace: "
              "hay que mirar cual.")
        return 1

    # RECONCILIACION DEL CAMPO QUE NADIE LEIA. 34 capturas declaran su cambio
    # entre cortes en `delta_2016_2026` y ningun guion lo consumia: trabajo del
    # codificador invisible para el sistema, que es exactamente como Israel
    # publico un valor falso teniendo el correcto escrito al lado.
    #
    # No se «carga» —el estado que manda sigue siendo `corte_2016.estado`, que es
    # el que el esquema modela— sino que se CONTRASTA. Una captura que dice haber
    # hallado un cambio de vacaciones y no trae `version_anterior` es una de dos
    # cosas: una reforma sin cargar, o un pendiente. Las dos merecen salir por
    # pantalla; ninguna merece quedarse callada en un JSON.
    import re as _re
    pendientes = []
    for carpeta, (iso3, nombre, _c, *_en) in UNIDADES.items():
        cap = captura_de(carpeta)
        dl = cap.get("delta_2016_2026")
        if not isinstance(dl, dict):
            continue
        dice = str(dl.get("vacaciones", ""))
        cargada = bool((cap.get("vacaciones_normalizado") or {}).get("version_anterior"))
        if dice and not _re.match(r"\s*(0|sin|ninguna|no\b)", dice, _re.I) and not cargada:
            pendientes.append("%s: «%s»" % (nombre, dice[:60]))
    if pendientes:
        print("  AVISO  %d captura(s) declaran cambio de vacaciones sin version "
              "anterior cargada:" % len(pendientes))
        for p in pendientes:
            print("           %s" % p)

    # El otro lado del mismo hueco: la reforma esta cargada Y las versiones
    # tambien, y aun asi la base no dice que una separe a las otras. Un par sin
    # evento no es un fallo de carga —las dos versiones son correctas— sino una
    # contradiccion entre lo que la captura fecha en un sitio y en el otro.
    if pares_sin_evento:
        print("  AVISO  %d par(es) de versiones sin evento de reforma que las "
              "separe:" % len(pares_sin_evento))
        for p in pares_sin_evento:
            print("           %s" % p)

    if niveles_sin_declarar:
        print("  AVISO  %d version(es) anterior(es) fijan el corte 2016 en "
              "`verificado_primaria` sin declarar nivel de fuente: %s"
              % (len(niveles_sin_declarar), ", ".join(niveles_sin_declarar)))

    print("  Base: %s" % SALIDA.relative_to(REPO))

    # LA JORNADA SE CARGA AQUI, y no como paso suelto que hay que acordarse de
    # correr. Este guion BORRA la base y la reconstruye entera, asi que un
    # cargador aparte se perdia en cada reconstruccion — y la metrica no fallaba:
    # caia a su convencion de cinco dias en silencio y daba numeros plausibles y
    # equivocados. Un paso que hay que recordar es un paso que se olvida.
    con.commit()
    con.close()
    import subprocess
    r = subprocess.run([sys.executable, str(GUIONES / "cargar_jornada.py")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("  LA JORNADA NO CARGO:\n%s" % r.stderr.strip()[:400])
        return 1
    print("  Jornada: %s"
          % [l for l in r.stdout.splitlines() if "de 47 unidades" in l][0].strip())

    # Y las validaciones DESPUES de la jornada, no antes: mi primera version puso
    # un `return` aqui y dejo el bloque entero inalcanzable. `--validar` seguia
    # aceptandose en la linea de comandos y no corria nada — la peor forma de
    # romper una comprobacion, porque no falla: enmudece.
    if args.validar:
        print("\n== Validaciones externas ==")
        r = subprocess.run(["sqlite3", str(SALIDA)], stdin=open(VALID),
                           capture_output=True, text=True)
        filas = [l for l in r.stdout.strip().split("\n") if l.strip()]
        if filas:
            print("  %d violaciones:" % len(filas))
            for f in filas[:20]:
                print("    %s" % f)
            return 1
        print("  Las 37 validaciones devuelven cero filas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
