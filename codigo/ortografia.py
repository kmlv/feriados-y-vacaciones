"""Ortografia castellana de los nombres de feriado. Tabla curada, no algoritmo.

POR QUE EXISTE. De 577 nombres, CINCO llevaban algun diacritico: las capturas se
escribieron en ASCII de punta a punta y eso llego al paquete publicado. En el
apendice de verificacion de Peru —el documento que un tercero abre para
comprobar nuestros numeros uno por uno— se leia «Ano Nuevo», «Navidad del
Senor», «Dia de la Fuerza Aerea». En castellano `ano` y `año` son palabras
distintas y la primera significa otra cosa; `Senor` no es una palabra.

NO ES UN ALGORITMO Y NO PUEDE SERLO. Acentuar por regla en un corpus multilingue
rompe mas de lo que arregla: «Ano Novo» y «Dia do Trabalho» son CORRECTOS en
portugues, «Ascension» lo es en frances. Una regla castellana los estropearia, y
un nombre con tilde de mas es tan falso como uno sin la que le toca. Por eso es
una lista escrita a mano, revisada palabra por palabra, y por eso solo se aplica
donde el texto es castellano NUESTRO: nombres de las unidades hispanohablantes, y
glosas entre parentesis en cualquier unidad.

Y LA TABLA ES TAMBIEN LA COMPROBACION. `mal_escritos()` no lleva una lista aparte
de palabras prohibidas —esa se desincronizaria de esta— sino que aplica la tabla
y mira si cambia algo. Si cambiaria un nombre, el nombre esta mal.
"""

import re
TILDES = {
    "Abolicion": "Abolición", "Accion": "Acción", "Aerea": "Aérea",
    "Amazonico": "Amazónico", "Americas": "Américas", "Anexion": "Anexión",
    "Angeles": "Ángeles", "Ano": "Año", "ano": "año",
    "Ascension": "Ascensión", "Asuncion": "Asunción",
    "Boqueron": "Boquerón", "Boyaca": "Boyacá", "Caacupe": "Caacupé",
    "Caidos": "Caídos", "Chiquinquira": "Chiquinquirá",
    "Concepcion": "Concepción", "Conmemoracion": "Conmemoración",
    "Constitucion": "Constitución", "Corazon": "Corazón",
    "Creacion": "Creación", "Cumpleanos": "Cumpleaños",
    "Dia": "Día", "dia": "día", "dias": "días", "Dias": "Días",
    "articulo": "artículo", "Articulo": "Artículo",
    "Codigo": "Código", "codigo": "código",
    "modificacion": "modificación", "Modificacion": "Modificación",
    "Politica": "Política", "politica": "política",
    "Republica": "República", "republica": "república",
    "ultima": "última", "Ultima": "Última",
    "eleccion": "elección", "Eleccion": "Elección",
    "septimo": "séptimo", "Septimo": "Séptimo",
    "version": "versión", "Version": "Versión",
    "Efemeride": "Efeméride", "Ejercito": "Ejército", "Epifania": "Epifanía",
    "Espana": "España", "Espanola": "Española", "Evangelicas": "Evangélicas",
    "Fundacion": "Fundación", "Guemes": "Güemes", "Guzman": "Guzmán",
    "Heroes": "Héroes", "Indigenas": "Indígenas", "Jesus": "Jesús",
    "Jose": "José", "Junin": "Junín", "Liberacion": "Liberación",
    "Maria": "María", "Martin": "Martín", "Mayoria": "Mayoría",
    "Montana": "Montaña", "Morazanica": "Morazánica", "Nino": "Niño",
    "Oracion": "Oración", "Otono": "Otoño", "Pentecostes": "Pentecostés",
    "Peru": "Perú", "Restauracion": "Restauración", "Revolucion": "Revolución",
    "Sabado": "Sábado", "Santamaria": "Santamaría", "Senor": "Señor",
    "Senora": "Señora", "Soberania": "Soberanía",
    "Transmision": "Transmisión", "vispera": "víspera",
}

# Unidades cuyos nombres estan escritos EN CASTELLANO fuera de parentesis.
# Las romances no castellanas quedan fuera a proposito: en portugues «Ano Novo»
# y «Dia do Trabalho» son correctos, y en frances «Ascension» tambien.
CASTELLANO = {"PER", "GTM", "SLV", "MEX", "ARG", "BOL", "CHL", "COL", "CRI",
              "DOM", "ECU", "ESP", "HND", "NIC", "PRY", "KOR", "ISR", "THA"}

# Unidades que ponen su glosa castellana TRAS UNA RAYA en vez de entre
# parentesis: «Uudenvuodenpaiva — Año Nuevo». Va declarado por unidad y no
# deducido de la sintaxis, porque la raya no significa lo mismo en todas:
# Francia la usa DENTRO de su nombre frances —«14 juillet — Fête nationale»— y
# leerla como glosa castellana le aplicaria reglas de otro idioma. Italia igual.
GLOSA_TRAS_RAYA = {"FIN", "GRC", "HUN", "JPN"}

# Unidades donde la tabla castellana NO se aplica a la prosa: las romances no
# castellanas. En portugues «Dia» y «Ano» son correctos, en frances «Ascension»
# lo es, y en italiano «Maria» tambien. Sus citas siguen en ASCII y eso es un
# hueco DECLARADO: arreglarlas exige una tabla por idioma, que es otra tanda.
# Meterles la castellana les pondria tildes de otro idioma, y una tilde de mas
# es tan falsa como la que falta.
SIN_TABLA_CASTELLANA = {"BRA", "PRT", "FRA", "ITA"}


def acentua(t: str) -> str:
    return re.sub(r"[A-Za-z]+", lambda m: TILDES.get(m.group(0), m.group(0)), t)


def correcto(nombre: str, iso3: str) -> str:
    """El nombre como deberia estar escrito, dada la lengua de su unidad."""
    if iso3 in CASTELLANO:
        return acentua(nombre)
    # Fuera del castellano solo se toca la GLOSA, que es texto nuestro y no el
    # nombre que la norma escribe en su idioma.
    out = re.sub(r"\(([^)]*)\)", lambda m: "(%s)" % acentua(m.group(1)), nombre)
    if iso3 in GLOSA_TRAS_RAYA and " — " in out:
        cabeza, _, cola = out.partition(" — ")
        out = "%s — %s" % (cabeza, acentua(cola))
    return out


def mal_escritos(nombres, iso3: str) -> list[tuple[str, str]]:
    """(tal como esta, como deberia) para los que la tabla corregiria."""
    return [(n, correcto(n, iso3)) for n in nombres
            if isinstance(n, str) and correcto(n, iso3) != n]


def cita_correcta(cita: str, iso3: str) -> str:
    """Las CITAS tambien son transcripcion nuestra, y tambien salieron en ASCII.

    «Ley 31788 — Ley que declara Feriado Nacional el 7 de junio en conmemoracion
    de la Batalla de Arica y del Dia de la Bandera» es el titulo real de una ley
    peruana, y en el Diario Oficial lleva sus tildes. Acentuarla la acerca al
    original, no lo contrario.

    No se toca `literal`, que es el texto de la norma citado a la letra: ahi
    cualquier retoque nuestro seria falsear la cita.
    """
    if iso3 in SIN_TABLA_CASTELLANA:
        return cita
    return acentua(cita)
