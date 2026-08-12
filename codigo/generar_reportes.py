"""Compila los cuatro entregables contra UN SOLO snapshot, o no compila ninguno.

LOS CUATRO
  D1  reporte principal — prosa humana, cifras por consulta
  D2  apéndice por país — generado entero
  D3  apéndice de verificación por país — generado entero, para lector externo
  D4  el paquete: los tres anteriores más los datos, la licencia y el manifiesto
      de exclusiones

POR QUE LA COMPILACION ES ATOMICA. Si D1 se escribe un martes y los apéndices se
generan un jueves, dicen cosas distintas y nadie se entera hasta que un lector lo
nota. Todos los documentos de una compilación llevan en portada el mismo hash de
base, de protocolo y de generador, y `probar_reportes.py` falla si dos no
coinciden. Es el mismo movimiento que el verificador de congelamiento, un nivel
más arriba.

QUE SE EXCLUYE DEL PAQUETE, y va escrito dentro de él: sólo las transcripciones
de los chats de origen. Un paquete que calla sus exclusiones se lee como completo.

Uso:  python3 scripts/generar_reportes.py [--pdf]
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reportes_nucleo import (BASE, EXPORT, REPO, SALIDA, colofon, construir_registro,
                             cubierta, portada, resolver, sha256_de, snapshot)
from reportes_paises import d2, d3

PLANTILLAS = REPO / "plantillas"

# LOS GENERADORES DE FIGURA SON CODIGO Y VIAJAN COMO CODIGO. Su fuente vive en
# `plantillas/`, junto a las figuras que producen, pero dentro del paquete todo
# lo ejecutable queda junto en `codigo/`. Sin ellos el paquete llevaba cuatro
# imagenes que el lector externo no podia rehacer — y las figuras sacan sus
# cifras del mismo registro que el texto, asi que son un resultado, no un
# adorno: un resultado sin su guion es una afirmacion sin procedencia.


# LA DOBLE CODIFICACION SE QUEDA INTERNA, y por eso hay que quitar CUATRO
# cosas y no una. Decision del principal: la medicion de fiabilidad vive en el
# repositorio privado y en la documentacion interna, y no viaja ni al informe ni
# al repositorio publico.
#
# Retirar solo las tablas del Anexo A dejaria dentro el insumo y la calculadora:
# las ocho segundas lecturas en crudo y el guion que las cruza. Cualquiera
# recomputaria en dos minutos exactamente lo que se decidio no publicar, **y sin
# las salvedades que costo escribir** —entre ellas que en tres unidades la
# independencia solo esta afirmada—. Publicar el insumo y retirar la conclusion
# es peor que publicar las dos cosas.
#
# Y NO SE ARREGLA BORRANDO EL ENLACE. `notes/07` entro al paquete para que el
# enlace del protocolo resolviera, y el protocolo viaja byte a byte porque
# reescribirlo rompe el hash que el propio paquete certifica. Asi que en su sitio
# viaja una NOTA TESTIGO: dice que el ejercicio se hizo, que el material se
# conserva internamente y que las cifras no se publican. El enlace resuelve, la
# certificacion aguanta, y las tasas no salen.
DOBLES_FUERA = "captura-doble.json"
CRUCE_FUERA = "cruzar_doble.py"


def generadores_de_figura() -> list[Path]:
    return sorted(PLANTILLAS.glob("generar_figura_*.py"))


def carpeta_de_generadores() -> str:
    """Donde estan los generadores VISTO DESDE LA RAIZ que se este leyendo.

    En el repositorio es `plantillas/`; en el paquete publicado es `codigo/`.
    El remedio que imprime la compuerta de figuras se deriva de aqui en vez de
    ser una cadena fija: fija seria correcta en un sitio y falsa en el otro, y
    una instruccion falsa con cara de instruccion es peor que no dar ninguna
    —quien la sigue cree haberlo arreglado—. Es la misma leccion que ya obligo
    a derivar del nombre cual de los dos guiones hay que correr.
    """
    return "plantillas" if generadores_de_figura() else "codigo"


def unidades(con) -> list[tuple[str, str, str]]:
    return con.execute(
        "SELECT j.iso3, p.nombre, j.nombre FROM jurisdicciones j "
        "  JOIN jurisdicciones p ON p.jurisdiccion_id = j.padre_id "
        " WHERE j.nivel='subnacional' ORDER BY j.iso3").fetchall()


def escribir(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto if texto.endswith("\n") else texto + "\n", encoding="utf-8")


# --- Que puede existir en el paquete, y NADA MAS --------------------------

def manifiesto_publicable(isos) -> set[str]:
    """Lista BLANCA de rutas relativas que el paquete puede contener.

    DENEGAR POR DEFECTO, y la diferencia con una lista de exclusiones no es de
    estilo. «`coord/` no se publica» es permisivo: manana alguien anade una
    carpeta y se publica salvo que se acuerde de excluirla — es «permitir no es
    exigir» en el sitio donde mas caro sale, que es lo que sale del proyecto.
    Con lista blanca, lo que no esta escrito aqui no viaja.
    Y la comprobacion es de IGUALDAD, no de inclusion: tambien falla si FALTA
    algo. Ese lado importa igual — `EXCLUSIONES.md` prometia las capturas
    crudas, el protocolo y el codigo, y el paquete llevaba solo los CSV; el
    documento que declara lo que se excluye estaba equivocado sobre lo que se
    incluye, y ninguna comprobacion podia verlo porque no habia manifiesto contra
    el que comparar.
    Se DERIVA de la lista de unidades y del contenido real de las carpetas de
    origen: un manifiesto escrito a mano se queda viejo en cuanto crece lo que
    describe, que es la leccion de la etiqueta del lote.
    """
    m = {"D1-reporte-principal.md", "D1-main-report.md",
         "D1-main-report.pdf",
         "EXCLUSIONES.md", "LICENCIA.md", "README.md",
         "CITATION.cff", "LEEME.md", "SNAPSHOT.json",
         "datos/LEEME.md", "datos/MANIFEST.csv",
         "D2-paises/INDICE.md", "D3-verificacion/INDICE.md"}
    m |= {"D2-paises/%s.md" % i for i in isos}
    m |= {"D3-verificacion/%s.md" % i for i in isos}
    m |= {"datos/%s" % f.name for f in EXPORT.iterdir() if f.is_file()}
    # Las figuras sin sufijo de idioma ya no se generan: cada una tiene su `-es`
    # y su `-en`. Si quedan en disco son restos, y el manifiesto no las autoriza
    # — asi la lista blanca las caza en vez de publicarlas por inercia.
    m |= {"figuras/%s" % f.name
          for f in (PLANTILLAS / "figuras").iterdir()
          if f.is_file() and ("-es." in f.name or "-en." in f.name)}
    m |= {"capturas/%s/%s" % (d.name, f.name)
          for d in (REPO / "data/raw").iterdir() if d.is_dir()
          for f in d.glob("*.json") if f.name != DOBLES_FUERA}
    m |= {"codigo/%s" % f.name for f in (REPO / "scripts").glob("*.py")
          if f.name != CRUCE_FUERA}
    m |= {"codigo/%s" % f.name for f in generadores_de_figura()}
    m.add("notes/07-doble-codificacion.md")
    m.add("reproducir.sh")
    m |= {"metodo/protocolo.md", "metodo/protocol.md",
          "metodo/PROTOCOL_FREEZE.md",
          "metodo/esquema.sql", "metodo/validaciones.sql"}
    # El PDF es opcional: solo existe si se compilo con --pdf.
    m.add("D1-reporte-principal.pdf")
    return m


# --- D4: lo que rodea a los documentos ------------------------------------

EXCLUSIONES = [
    ("Transcripciones de los chats exploratorios de origen",
     "Conversaciones de trabajo con asistentes de IA que precedieron al diseño. No "
     "son fuente de ningún dato publicado: el material que produjeron se trató como "
     "insumo y todo valor se recapturó de la norma. Se excluyen porque son "
     "correspondencia de trabajo, no evidencia."),
    ("Las cifras del índice de referencia externo",
     "Las comparaciones aparecen calculadas —nuestro valor, el suyo implícito y la "
     "diferencia— pero **su tabla no se republica**. Quien quiera recomputar el "
     "cruce descarga su conjunto de datos de su fuente original, citada en el "
     "apéndice de cada unidad. Así el cruce es reproducible sin redistribuir dato "
     "de terceros, y el valor externo se mantiene fuera de nuestro registro de "
     "hechos, como manda el protocolo."),
    ("La medición de fiabilidad entre codificadores",
     "Se ejecutó una doble codificación ciega sobre una muestra estratificada de "
     "unidades, y **sus resultados no se publican**: ni las tasas de acuerdo, ni "
     "las segundas lecturas en crudo, ni el programa que las cruza. Se conservan "
     "en la documentación interna del proyecto. Se excluyen enteros y no a "
     "medias a propósito: publicar el insumo y retirar la conclusión permitiría "
     "recomputar la cifra sin las salvedades que la acompañan —entre ellas el "
     "grado en que la independencia entre las dos lecturas está evidenciada—, y "
     "una cifra sin su salvedad es peor que ninguna. La mención de que el "
     "ejercicio se hizo **no debe leerse como afirmación de concordancia alta**."),
    ("La base de datos de trabajo",
     "Es un derivado: se reconstruye entera desde las capturas con un comando, y "
     "publicarla invitaría a tratarla como el original. Lo que se publica son las "
     "capturas crudas con procedencia y los archivos tabulares derivados."),
]


def manifiesto_exclusiones(snap) -> str:
    p = [portada(snap, "Qué NO incluye este paquete, y por qué"),
         "\nUn paquete que calla sus exclusiones se lee como completo. Éstas son "
         "las suyas.\n"]
    for i, (qué, por_qué) in enumerate(EXCLUSIONES, 1):
        p.append("\n## %d. %s\n\n%s\n" % (i, qué, por_qué))
    p.append("\n## Lo que sí incluye\n")
    p.append("Todo lo demás: los datos tabulares, las capturas crudas con su "
             "procedencia, el protocolo de medición con su registro de "
             "congelamiento, el apéndice de país y el apéndice de verificación de "
             "cada unidad, y el código que lo regenera todo.\n")
    return "\n".join(p)


def citacion(snap) -> str:
    return f"""cff-version: 1.2.0
message: "Si usa este conjunto de datos, cítelo así."
title: "Feriados públicos y vacaciones anuales de ley: 47 unidades de referencia, dos cortes"
abstract: >-
  Conjunto de datos de feriados públicos y vacaciones anuales mínimas exigibles
  por ley, construido leyendo las normas, para 47 jurisdicciones de referencia en
  dos cortes temporales. Cada cifra de vacaciones viaja con su unidad de conteo y
  su base semanal en columnas separadas, y cada hecho con su fuente y el nivel de
  ésta.
authors:
  - family-names: "López Vargas"
    given-names: "Kristian"
type: dataset
license: CC-BY-4.0
keywords:
  - feriados públicos
  - vacaciones anuales
  - regulación laboral comparada
  - medición institucional
version: "{snap['protocolo']}"
"""


def licencia() -> str:
    return """# Licencia

## Los datos y los documentos

Los archivos de datos y los documentos de este paquete se publican bajo
**Creative Commons Atribución 4.0 Internacional (CC BY 4.0)**.
Texto completo: <https://creativecommons.org/licenses/by/4.0/deed.es>

Puede copiarlos, redistribuirlos y adaptarlos, incluso comercialmente, siempre que
dé el crédito correspondiente e indique si hizo cambios.

## El código

Los guiones que generan y verifican el paquete se publican bajo **licencia MIT**.

## Lo que NO está cubierto por lo anterior

**Los textos legales citados** pertenecen a sus jurisdicciones. Se reproducen
fragmentos con finalidad de verificación y con la cita de su fuente. La legislación
oficial es de reproducción libre en la mayoría de los ordenamientos, pero el
régimen concreto varía por país y no se afirma aquí uno solo para todos: quien
reutilice un pasaje debe comprobar el de su jurisdicción.

**Las cifras del índice de referencia externo no se redistribuyen.** Este paquete
publica las comparaciones calculadas y la referencia a su fuente original; su tabla
hay que obtenerla de sus autores.
"""


LEEME_EN = """

## What is here

| path | what it is |
|---|---|
| `D1-main-report.md` · `.pdf` | The report in English: the problem, the method in brief, and the results |
| `D1-reporte-principal.md` · `.pdf` | The same report in Spanish. **Not a translation**: both versions are written in parallel against the same query marks, so their figures come from one query and each uses its own numeric convention |
| `D2-paises/<ISO3>.md` | Country appendix: sources, method given those sources, decisions |
| `D3-verificacion/<ISO3>.md` | Verification appendix, **Spanish only**: every number with its verbatim citation and its arithmetic. Whoever checks a figure reads the statute in its original language |
| `datos/` | The tabular files, with a hash manifest |
| `capturas/<unit>/` | The **raw data with provenance**: what was read from each statute, with its verbatim text and source level. Everything else derives from here |
| `metodo/` | The measurement protocol, its freeze registry, the schema and the validations |
| `codigo/` | The scripts that regenerate the whole package from `capturas/` |
| `EXCLUSIONES.md` | What this package does **not** include, and why |
| `LICENCIA.md` | Terms of use, including those we do not control |

## Where to start

For **the argument**, read `D1`. To **use the data**, start at `datos/LEEME.md`.
To **check one number**, go to that unit's `D3`: it is written for someone with
no access to the project repository.

## Three things to know before using the figures

**1. No leave figure is comparable without its unit.** Four different counting
units appear in the statutes. The legal quantity travels next to the type of day
and the weekly base; the converted figure lives in another file and is labelled
as a convention.

**2. Not every public holiday counts.** Filter by regime according to what you
want to measure, and say which one you used. `panel_feriados.csv` carries both
the nominal count and the enforceable subset.

**3. Unverified absence is not absence.** A zero delta between cuts may mean no
reform happened or that none was looked for, and the data distinguishes the two.

## Reproducibility

Everything in this package is derived and regenerates from the raw captures.
**And you can check that right here**, without downloading anything and without
leaving this folder:

```
./reproducir.sh
```

It rebuilds the database from `capturas/`, re-exports the tabular files into
`regenerado/`, and compares them **hash by hash** against those in `datos/`. The
answer is not «it ran»: it is *they match* or *these files do not match*. It
writes to a separate folder on purpose — re-exporting over `datos/` would erase
the only copy there is to compare against.

You need only Python 3. If you edit a capture and run it again it will stop
matching: that is correct, you have measured something else.

The hashes on the cover identify the compilation: two documents with different
hashes do not belong to the same package.
"""


def leeme_paquete(snap, reg, n_unidades, idioma="es") -> str:
    """El LEEME del paquete, en su idioma, y cada uno nombrando al otro.

    LOS DOS SE ENLAZAN EN LA PRIMERA LINEA porque un lector que abra el paquete
    y solo encuentre un idioma no sabe que existe el otro — y eso no lo caza
    ninguna compuerta, porque el archivo que falta no lo referencia nadie. Lo
    vio la revisión de plantillas y es el mismo agujero que el enlace muerto del README:
    lo que no esta enlazado es invisible, y lo invisible no se comprueba.
    """
    otro = ("[Read this in English](README.md)" if idioma == "es"
            else "[Leer en castellano](LEEME.md)")
    titulo = ("Feriados y vacaciones de ley — paquete publicable"
              if idioma == "es"
              else "Statutory holidays and annual leave — publishable package")
    if idioma == "en":
        return (portada(snap, titulo, otro) + LEEME_EN)
    return portada(snap, titulo, otro) + f"""

## Qué hay aquí

| ruta | qué es |
|---|---|
| `D1-reporte-principal.md` | El reporte en castellano: el problema, el método en síntesis y los resultados |
| `D1-main-report.md` | El mismo reporte en inglés. **No es una traducción**: las dos versiones se escriben en paralelo contra las mismas marcas, así que sus cifras salen de la misma consulta y su convención numérica es la de cada idioma |
| `D2-paises/<ISO3>.md` | Apéndice por país: fuentes, metodología dadas esas fuentes, decisiones |
| `D3-verificacion/<ISO3>.md` | Apéndice de verificación: cada número con su cita textual y su aritmética |
| `datos/` | Los archivos tabulares, con manifiesto de hashes |
| `capturas/<unidad>/` | El **dato crudo con procedencia**: lo que se leyó de cada norma, con su literal y su nivel de fuente. Todo lo demás sale de aquí |
| `metodo/` | El protocolo de medición, su registro de congelamiento, el esquema y las validaciones |
| `codigo/` | Los guiones que regeneran el paquete entero desde `capturas/` |
| `figuras/` | Las imágenes que el reporte referencia |
| `EXCLUSIONES.md` | Qué **no** incluye este paquete y por qué |
| `LICENCIA.md` | Condiciones de uso, incluidas las que no controlamos |
| `CITATION.cff` | Cómo citar |

## Por dónde empezar

Si quiere **el argumento**, lea `D1`. Si quiere **usar los datos**, empiece por
`datos/LEEME.md`. Si quiere **comprobar un número concreto**, vaya al `D3` de esa
unidad: está escrito para alguien sin acceso al repositorio del proyecto.

## Las tres cosas que hay que saber antes de usar las cifras

**1. Ningún número de vacaciones es comparable sin su unidad.** {n_unidades} unidades,
cuatro unidades de conteo distintas en las leyes. La cantidad legal va pegada al
tipo de día y a la base semanal; la cifra convertida está en otro archivo y
etiquetada como convención.

**2. No todo día festivo cuenta.** Filtre por régimen según lo que quiera medir, y
diga cuál usó.

**3. Ausencia no verificada no es ausencia.** Un delta de cero entre cortes puede
significar que no hubo reforma o que no se buscó, y los datos distinguen los dos
casos.

## Reproducibilidad

Todo lo de este paquete es derivado y se regenera desde las capturas crudas.
**Y usted puede comprobarlo aquí mismo**, sin descargar nada y sin salir de esta
carpeta:

```
./reproducir.sh
```

Reconstruye la base desde `capturas/`, vuelve a exportar los archivos tabulares
a `regenerado/` y los compara **hash por hash** contra los de `datos/`. La
respuesta no es «ha funcionado»: es *coinciden* o *estas filas no coinciden*.
Sale a una carpeta aparte a propósito — reexportar encima de `datos/` borraría
la única copia contra la que comparar.

Sólo necesita Python 3. Si modifica una captura y vuelve a correrlo, dejará de
coincidir: eso es correcto, ha medido otra cosa.

Los hashes de la portada identifican la compilación: dos documentos con hashes
distintos no pertenecen al mismo paquete.
"""


# --- nota de participación, que el principal pidió como nota al pie -------

NOTA_METODO = """

---

## Nota sobre el método de producción

La captura de las normas, la revisión adversarial del esquema y del protocolo, la
auditoría contra el antecedente externo y la doble codificación ciega las
ejecutaron **asistentes de inteligencia artificial**, bajo un protocolo de
medición versionado y congelado por hash, con adjudicación humana de todas las
decisiones de constructo.

Los roles fueron distintos y conviene distinguirlos, porque la separación es parte
del diseño: **por regla**, quien capturó una unidad no fue quien la auditó, y
quien implementó una parte del esquema no fue quien la atacó. Va con esa reserva
porque no se cumplió en todos los casos, y el Anexo A dice dónde.

La doble codificación se declara ciega, y en parte de los pares esa ceguera
**está afirmada y no acreditada** por nuestro propio registro. **Sus cifras no se
publican** —se conservan en la documentación interna del proyecto, y el motivo
está en `EXCLUSIONES.md`—, así que esta mención no debe leerse como afirmación de
concordancia. Lo que sí se publica de ese ejercicio son las correcciones que
provocó, incluida una que fue contra el segundo lector.

No se nombran modelos ni identificadores internos: un alias de trabajo no
significa nada fuera del proyecto, y un nombre de modelo envejece en meses. Lo que
sí queda registrado, y es lo que permite auditar el proceso, son el protocolo, sus
versiones congeladas y el historial completo de revisiones.
"""

NOTA_METODO_EN = """

---

## Note on the production method

The capture of the statutes, the adversarial review of the schema and the
protocol, the audit against the external benchmark and the blind double coding
were carried out by **artificial-intelligence assistants**, under a versioned
measurement protocol frozen by hash, with human adjudication of every construct
decision.

The roles were distinct and worth distinguishing, because the separation is part
of the design: **as a rule**, whoever captured a unit did not audit it, and
whoever implemented a part of the schema did not attack it. It carries that
reserve because it did not hold in every case, and Annex A says where.

The double coding is declared blind, and in some of the pairs that blindness is
**asserted and not evidenced** by our own record. **Its figures are not
published** —they are kept in the project's internal documentation, and the
reason is in `EXCLUSIONES.md`— so this mention must not be read as a claim of
agreement. What is published from that exercise are the corrections it prompted,
including one that went against the second reader.

No models or internal identifiers are named: a working alias means nothing
outside the project, and a model name ages in months. What is on the record, and
what makes the process auditable, are the protocol, its frozen versions and the
full revision history.
"""

# D1, por idioma. La plantilla, el titulo y la nota de metodo cambian; todo lo
# demas —marcas, colofon, procedencia— lo resuelve el idioma que se pasa.
D1_POR_IDIOMA = {
    "es": ("D1-reporte-principal.md", "D1-reporte-principal.md",
           "Comparación de feriados y vacaciones de ley en Perú, "
           "Iberoamérica y la OCDE", NOTA_METODO),
    "en": ("D1-main-report.md", "D1-main-report.md",
           "Statutory public holidays and annual leave in Peru, Ibero-America "
           "and the OECD", NOTA_METODO_EN),
}


def main() -> int:
    if not BASE.exists():
        sys.exit("no existe la base — corre antes scripts/cargar_piloto.py")
    # LA EXPORTACION TIENE QUE SER MAS NUEVA QUE LA BASE. Los reportes leen los
    # CSV para nombres y agregados, asi que compilar con una exportacion vieja
    # produce un documento coherente consigo mismo y desfasado del dato — que es
    # la peor forma de estar mal. Acaba de pasar: se corrigieron los acentos de
    # los nombres, se regenero el reporte antes que la exportacion, y la tabla
    # principal salio diciendo «Peru».
    if EXPORT.joinpath("unidades.csv").stat().st_mtime < BASE.stat().st_mtime:
        sys.exit("la exportacion es mas vieja que la base: los reportes saldrian "
                 "desfasados.\n  Corre antes: python3 scripts/exportar.py")
    # Y LA MISMA GUARDIA PARA LAS FIGURAS, que no la tenian. La figura de
    # apertura saca sus cifras del mismo registro que el texto, asi que no puede
    # llevar numeros tecleados — pero es un BINARIO que se copia, no se
    # reconstruye aqui. Una figura vieja junto a un texto nuevo es coherente
    # consigo misma y desfasada del dato, que es la forma de estar mal que este
    # proyecto ya conoce. Y en una imagen no la caza ninguna compuerta de texto:
    # solo se ve abriendo la pagina.
    figs = sorted((PLANTILLAS / "figuras").glob("*.p*g")) + \
        sorted((PLANTILLAS / "figuras").glob("*.pdf"))
    viejas = [f.name for f in figs if f.stat().st_mtime < BASE.stat().st_mtime]
    if viejas:
        # EL REMEDIO SE DERIVA DEL NOMBRE, no es una cadena fija. La version
        # anterior mandaba correr `generar_figura_apertura.py` para CUALQUIER
        # figura vieja, incluida la de dispersion — un remedio equivocado con
        # cara de instruccion, que es peor que no dar ninguno: quien lo sigue
        # cree haberlo arreglado.
        # Y LA CARPETA TAMBIEN SE DERIVA, por el mismo motivo un nivel mas
        # arriba: en el paquete publicado los generadores estan en `codigo/`,
        # no en `plantillas/`, y el remedio mandaba a un sitio que alli no
        # existe.
        donde = carpeta_de_generadores()
        guiones = sorted({
            "python3 %s/generar_figura_%s.py%s"
            % (donde, n.split("-")[1], " --ajustes" if "ajustes" in n else "")
            for n in viejas})
        sys.exit("figuras mas viejas que la base: %s\n  Sus cifras salen del "
                 "mismo registro que el texto y se quedarian atras.\n"
                 "  Corre antes:\n    %s"
                 % (", ".join(viejas), "\n    ".join(guiones)))
    con = sqlite3.connect(BASE)
    snap = snapshot(con)
    reg = construir_registro(con)

    if SALIDA.exists():
        shutil.rmtree(SALIDA)          # derivado: se regenera entero
    SALIDA.mkdir(parents=True)

    # D2 y D3 PRIMERO: D1 cita la cobertura de citas de D3, y una cifra que se
    # mide despues de escribir el texto que la cita no puede entrar por consulta.
    us = unidades(con)
    celdas = citadas = 0
    for iso3, pais, ciudad in us:
        escribir(SALIDA / "D2-paises" / ("%s.md" % iso3), d2(con, snap, iso3, pais, ciudad))
        texto, n, cp = d3(con, snap, iso3, pais, ciudad)
        escribir(SALIDA / "D3-verificacion" / ("%s.md" % iso3), texto)
        celdas += n
        citadas += cp
    reg["d3_celdas"] = str(celdas)
    reg["d3_citadas"] = str(citadas)
    reg["d3_cobertura_pct"] = "%.0f" % (100.0 * citadas / celdas)

    # D1 --------------------------------------------------------------------
    for idi, (nombre_plantilla, salida_md, titulo, nota) in D1_POR_IDIOMA.items():
      src = PLANTILLAS / nombre_plantilla
      if not src.exists():
        continue
      plantilla = src.read_text(encoding="utf-8")
    # LAS INSTRUCCIONES DE EDICION NO SE PUBLICAN. La plantilla abre con un
    # bloque de comentario que lleva el contrato de redaccion y los pendientes
    # internos, y salia dentro del entregable. Pandoc lo descarta al hacer el
    # PDF, asi que no se veia ahi — pero el `.md` es entregable por si mismo y
    # cualquiera que lo abra en el repositorio lo lee.
    #
    # Se quita SOLO si el documento EMPIEZA con el, y no «el primero que
    # aparezca»: los bloques `<!-- citado: … -->` que envuelven los valores del
    # antecedente tienen que sobrevivir, porque la compuerta C1 los usa como
    # escape declarado y quitarlos la haria fallar. Anclar al principio es mas
    # estrecho que contar uno: si algun dia el orden cambia, esta regla no se
    # come el bloque equivocado.
      plantilla = re.sub(r"\A\s*<!--.*?-->\s*", "", plantilla, flags=re.S)
      # CADA IDIOMA CON SU REGISTRO, o el ingles saldria con coma decimal.
      reg_idi = reg if idi == "es" else construir_registro(
          sqlite3.connect(BASE), idi)
      cuerpo = resolver(plantilla, reg_idi, "D1·%s" % idi)
    # D1 abre con su argumento, no con una caja de hashes. La procedencia baja
    # al colofón: quien lee un reporte quiere la respuesta primero, y quien
    # audita la compilación sabe dónde buscarla.
      d1 = cubierta(titulo, "Kristian López Vargas") \
          + "\n" + cuerpo + nota + colofon(snap, idi)
      escribir(SALIDA / salida_md, d1)

    # Índices de los dos apéndices, derivados del mismo recorrido -----------
    for carpeta, titulo in (("D2-paises", "Apéndices por país"),
                            ("D3-verificacion", "Apéndices de verificación")):
        idx = [portada(snap, titulo), "\n| unidad | jurisdicción | apéndice |",
               "|---|---|---|"]
        for iso3, pais, ciudad in us:
            idx.append("| %s | %s | [%s](%s.md) |" % (pais, ciudad, iso3, iso3))
        escribir(SALIDA / carpeta / "INDICE.md", "\n".join(idx))

    # D4 --------------------------------------------------------------------
    destino = SALIDA / "datos"
    destino.mkdir(parents=True, exist_ok=True)
    for f in sorted(EXPORT.iterdir()):
        if f.is_file():
            shutil.copy(f, destino / f.name)
    # LAS FIGURAS VIAJAN CON EL DOCUMENTO. Su fuente vive en `plantillas/`, que es
    # de la sesion de plantillas; aqui se COPIAN al paquete. Referenciarlas desde
    # fuera se ve bien en el repositorio y deja un hueco en cuanto el paquete se
    # mueve — y el hueco no rompe nada, que es lo que lo hace peligroso.
    origen_fig = PLANTILLAS / "figuras"
    if origen_fig.is_dir():
        destino_fig = SALIDA / "figuras"
        destino_fig.mkdir(parents=True, exist_ok=True)
        for f in sorted(origen_fig.iterdir()):
            if f.is_file():
                shutil.copy(f, destino_fig / f.name)
        print("  fig %d imagen(es) copiadas al paquete"
              % sum(1 for f in origen_fig.iterdir() if f.is_file()))

    # LO QUE EL PAQUETE PROMETIA Y NO LLEVABA. `EXCLUSIONES.md` decia —dos
    # veces— que se publican «las capturas crudas con procedencia, el protocolo
    # de medicion con su registro de congelamiento y el codigo que lo regenera
    # todo», y el paquete solo llevaba los CSV derivados. El documento que existe
    # para declarar lo que se excluye se equivocaba sobre lo que se incluye, que
    # es la peor pieza posible para tener mal.
    #
    # Se arregla enviandolas, no corrigiendo la frase: sin las capturas el lector
    # externo no puede rehacer nada, y el proyecto entero se apoya en que el dato
    # crudo con procedencia es la fuente y lo demas es derivado.
    crudo = SALIDA / "capturas"
    n_cap = 0
    for d in sorted((REPO / "data/raw").iterdir()):
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            if f.name == DOBLES_FUERA:
                continue
            dst = crudo / d.name / f.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, dst)
            n_cap += 1
    metodo = SALIDA / "metodo"
    metodo.mkdir(parents=True, exist_ok=True)
    for src, nombre in ((REPO / "docs/02-protocolo.md", "protocolo.md"),
                        (REPO / "docs/02-protocol.md", "protocol.md"),
                        # EL REGISTRO VIAJA CON SU NOMBRE, sin traducir. Se llamo
                        # `registro-de-congelamiento.md` un tiempo, que se lee
                        # mejor, y por eso quedo muerto el enlace de §7: el
                        # protocolo lo cita como `PROTOCOL_FREEZE.md` y el
                        # protocolo no se toca (ver abajo). Cuando un documento
                        # inmutable nombra un archivo, el nombre deja de ser
                        # nuestro.
                        # Este viaja REDACTADO, y la redaccion se hace abajo.
                        (REPO / "docs/PROTOCOL_FREEZE.md", "PROTOCOL_FREEZE.md"),
                        (REPO / "schema/draft/001_schema.sql", "esquema.sql"),
                        (REPO / "schema/draft/900_validaciones.sql", "validaciones.sql")):
        if src.exists():
            shutil.copy(src, metodo / nombre)
    # EL PROTOCOLO NO SE REESCRIBE, Y ESTO COSTO ENTENDERLO.
    #
    # El protocolo citaba dos archivos que no viajaban: la nota de doble
    # codificacion, por `../notes/07-doble-codificacion.md`, y su propio registro
    # de congelamiento. Dos enlaces muertos dentro del paquete.
    #
    # El arreglo evidente era reescribir los enlaces al copiar, y estuvo escrito
    # aqui. Rompia algo mucho peor que lo que arreglaba: el paquete embarca el
    # registro que declara el SHA-256 del protocolo, y un protocolo reescrito ya
    # no casa con el. Un lector externo hace exactamente esa comprobacion —
    # hashear el documento que le diste contra el registro que le diste — y un
    # hash que no cuadra no se lee como un renombrado, se lee como manipulacion.
    #
    # Asi que la direccion se invierte: **cuando un documento inmutable nombra un
    # archivo, el nombre deja de ser nuestro.** El protocolo viaja byte a byte y
    # el paquete se pliega a lo que el protocolo cita — `PROTOCOL_FREEZE.md` con
    # su nombre en ingles, y la nota en `notes/`, que es donde resuelve el
    # relativo visto desde `metodo/`. Se pierde el nombre castellano; se gana que
    # el documento certificado sea el certificado.
    #
    # Y se arregla INCLUYENDO, no borrando el enlace: la cifra de fiabilidad es de
    # las que un lector externo querra ver medida, y un protocolo que la cita sin
    # poder mostrarla se lee como una promesa.
    #
    # Lo que antes comprobaba la reescritura —que el enlace siga siendo el que
    # creemos— no desaparece: lo hace ahora la compuerta C10, resolviendo TODO
    # enlace relativo del paquete en vez de vigilar uno solo por su literal.
    notas = SALIDA / "notes"
    notas.mkdir(parents=True, exist_ok=True)
    (notas / "07-doble-codificacion.md").write_text(
        "# Doble codificación ciega — resultado no publicado\n"
        "\n"
        "El protocolo de medición cita este documento desde su sección sobre "
        "fiabilidad. Aquí está lo que se puede decir de él en el paquete "
        "publicado.\n"
        "\n"
        "**Qué se hizo.** Sobre una muestra estratificada de unidades del "
        "conjunto se ejecutó una segunda captura de las mismas normas, "
        "independiente de la primera, para medir el acuerdo entre lecturas. La "
        "muestra se eligió de modo que cada unidad estresara una parte distinta "
        "del constructo.\n"
        "\n"
        "**Qué no está aquí, y por qué se dice.** Ni las tasas de acuerdo, ni las "
        "segundas lecturas en crudo, ni el programa que las cruza. La medición y "
        "su material se conservan en la documentación interna del proyecto y no "
        "forman parte de esta publicación. Se declara en `EXCLUSIONES.md` junto "
        "con el resto de lo que el paquete no trae.\n"
        "\n"
        "**Lo que este documento NO debe leerse como.** No afirma una "
        "concordancia alta ni baja. Un ejercicio de fiabilidad mencionado sin su "
        "cifra no es evidencia de fiabilidad: es constancia de que el "
        "procedimiento se ejecutó. Quien necesite la magnitud tiene que pedirla, "
        "y con ella van las salvedades sobre el grado en que la independencia "
        "entre lecturas está evidenciada.\n",
        encoding="utf-8")

    # EL COMANDO DE UNA LINEA, EN LA RAIZ Y NO DENTRO DE `codigo/`. Quien abre el
    # paquete ve la raiz; un guion escondido entre otros veintiseis no lo
    # encuentra nadie, y una instruccion que no se encuentra equivale a no darla.
    repro = SALIDA / "reproducir.sh"
    repro.write_text(
        '#!/bin/sh\n'
        '# Rehace el dataset desde `capturas/` y lo compara con `datos/`.\n'
        '# Ver la seccion «Reproducibilidad» del LEEME.\n'
        'cd "$(dirname "$0")" && exec python3 codigo/reproducir.py "$@"\n',
        encoding="utf-8")
    repro.chmod(0o755)

    # EL REGISTRO VIAJA REDACTADO EN UNA LINEA, y hay que explicar las dos
    # mitades porque las dos son incomodas.
    #
    # POR QUE SE TOCA. La entrada historica de v2.24 describia su origen citando
    # la tasa de fiabilidad entera, con numerador y denominador. Retiramos el
    # anexo, el insumo y la calculadora, y la cifra seguia publicada — en el
    # PRIMER archivo que abre quien audita, que es el peor sitio posible: el
    # lector que va a comprobar integridad se encontraba el dato que se decidio
    # no publicar.
    #
    # POR QUE SOLO EN LA COPIA. Un registro de congelamiento existe para no
    # borrar nada; reescribir el interno seria destruir un dato historico real
    # del proyecto en el archivo cuya funcion es conservarlo. Asi que el interno
    # queda intacto y la copia que viaja lleva la linea sustituida por una que
    # DICE que se omitio y donde esta el motivo. Omitir en silencio seria peor
    # que publicar.
    #
    # Y no toca ningun hash ni ninguna fecha, asi que la certificacion que C10
    # comprueba sigue funcionando: lo que se redacta es prosa descriptiva.
    # LAS TRES CAPTURAS EXENTAS DEJAN DE SERLO EN LA COPIA QUE VIAJA, y el
    # motivo es que la exencion se quedo sin objeto aqui.
    #
    # Francia, Grecia e Israel llevan el mismo identificador en su captura y en
    # su segunda codificacion, y eso se CONSERVA en el repositorio privado a
    # proposito: es la evidencia de que la independencia entre las dos lecturas
    # esta afirmada y no acreditada, y despersonalizarla la haria invisible.
    #
    # Pero al paquete ya no viaja la segunda codificacion. Aqui no hay dos lados
    # que comparar: queda un handle interno suelto que al lector externo no le
    # dice nada y que no preserva ninguna pregunta, porque la pregunta necesita
    # las dos mitades. Asi que en la copia se mapea por papel como el resto.
    #
    # El campo no lo lee el cargador —comprobado— asi que esto no toca ningun
    # dato derivado, y la reproduccion del paquete lo confirma al ejecutarse.
    for u in ("francia", "grecia", "israel"):
        f = crudo / u / "captura.json"
        if f.exists():
            f.write_text(f.read_text(encoding="utf-8").replace(
                '"capturado_por": "opus5"',  # escape:definicion
                '"capturado_por": "captura · lote 1"'),
                encoding="utf-8")

    reg_ruta = metodo / "PROTOCOL_FREEZE.md"
    txt_reg = reg_ruta.read_text(encoding="utf-8")
    REDACTADO = ("**Tasa de fiabilidad — no publicada.** El resultado de la doble "
                 "codificacion ciega se conserva en la documentacion interna del "
                 "proyecto y no forma parte de este paquete. La omision se declara "
                 "en `EXCLUSIONES.md` con su motivo. Los hashes y las fechas de "
                 "esta entrada no estan tocados.")
    import re as _re
    nuevo_reg, n_red = _re.subn(
        r"\*\*Primera tasa de fiabilidad del proyecto\.\*\*.*?se habia hecho\.",
        REDACTADO, txt_reg, flags=_re.S)
    if n_red != 1:
        sys.exit("la redaccion del registro no encontro su bloque (%d coincidencias).\n"
                 "  O el registro cambio de redaccion y hay que actualizar esto, o "
                 "la tasa ya no esta y sobra la redaccion." % n_red)
    reg_ruta.write_text(nuevo_reg, encoding="utf-8")

    codigo = SALIDA / "codigo"
    codigo.mkdir(parents=True, exist_ok=True)
    guiones_paquete = [f for f in sorted((REPO / "scripts").glob("*.py"))
                       if f.name != CRUCE_FUERA] + generadores_de_figura()
    for f in guiones_paquete:
        shutil.copy(f, codigo / f.name)
    print("  crudo %d capturas, %d guiones y el metodo viajan en el paquete"
          % (n_cap, len(guiones_paquete)))

    escribir(SALIDA / "EXCLUSIONES.md", manifiesto_exclusiones(snap))
    escribir(SALIDA / "LICENCIA.md", licencia())
    escribir(SALIDA / "CITATION.cff", citacion(snap))
    escribir(SALIDA / "LEEME.md", leeme_paquete(snap, reg, reg["unidades"], "es"))
    escribir(SALIDA / "README.md", leeme_paquete(snap, reg, reg["unidades"], "en"))
    escribir(SALIDA / "SNAPSHOT.json", json.dumps(snap, ensure_ascii=False, indent=1))

    # EL README, QUE ERA EL UNICO DOCUMENTO SIN COMPUERTA. C1 vigila D1 desde el
    # principio y aqui no miraba nunca — y era el archivo mas leido del
    # repositorio. Al ir a hacerlo bilingue aparecieron CINCO cifras desfasadas,
    # y una era la primera fila de la tabla que sostiene la tesis del proyecto:
    # decia −0,4 donde el calculo da −0,8, o sea la mitad. Es la cifra que un
    # revisor comprobaria primero.
    #
    # Sale por marca como todo lo demas, y va a la RAIZ y no al paquete: el
    # ingles a `README.md`, que es el que GitHub muestra, y el castellano a
    # `LEEME.md`.
    # CADA IDIOMA CON SU REGISTRO. La primera version emitia el ingles con el
    # registro castellano y salia «−0,8» en la portada de GitHub: la coma
    # decimal de un idioma en el documento del otro. Cablear la emision sin
    # pasar el idioma era peor que no emitir.
    # El apendice de hallazgos va a `docs/` y no al paquete: es material del
    # repositorio que D1 referencia por titulo. Mismo trato que los README —cada
    # idioma con su registro— porque el problema es el mismo.
    for plantilla, destino, idi in (("README-en.md", "README.md", "en"),
                                    ("README-es.md", "LEEME.md", "es"),
                                    ("hallazgos-en.md", "docs/10-findings.md", "en"),
                                    ("hallazgos-es.md", "docs/10-hallazgos.md", "es")):
        src = PLANTILLAS / plantilla
        if src.exists():
            reg_idi = reg if idi == "es" else construir_registro(
                sqlite3.connect(BASE), idi)
            escribir(REPO / destino, resolver(src.read_text(encoding="utf-8"),
                                              reg_idi, plantilla))
    print("  raiz README.md y LEEME.md por marca, ninguna cifra tecleada")

    print("  D1  1 documento")
    print("  D2  %d apéndices de país" % len(us))
    print("  D3  %d apéndices de verificación" % len(us))
    print("  D4  paquete en %s" % SALIDA.relative_to(REPO))
    print("\nsnapshot: protocolo %s · base %s… · generador %s…"
          % (snap["protocolo"], snap["base_sha256"][:12], snap["generador_sha256"][:12]))

    for idi, (_pl, salida_md, _t, _n) in (D1_POR_IDIOMA.items()
                                          if "--pdf" in sys.argv else ()):
      if (SALIDA / salida_md).exists():
        pdf = SALIDA / salida_md.replace(".md", ".pdf")
        r = subprocess.run(
            ["pandoc", str(SALIDA / salida_md), "-o", str(pdf),
             "--pdf-engine=xelatex", "-V", "lang=%s" % idi,
             "-V", "geometry:margin=3cm",
             # SIN INDICE, y no es preferencia de formato. La primera version
             # del PDF abria con dos paginas de indice y el principal la rechazo
             # por eso: la pagina 1 tiene que ser la RESPUESTA. Toda la
             # arquitectura del documento —afirmar en los titulos, procedencia al
             # cierre— existe para eso, y un `--toc` la deshace sin tocar una
             # linea de la plantilla. Si algun dia el documento crece hasta
             # necesitarlo, su sitio es DESPUES del resumen ejecutivo.
             "-V", "mainfont=Helvetica",
             # El encabezado de pagina, por idioma. Iba cableado en castellano
             # dentro de la hoja de estilo y salia asi en todas las paginas del
             # PDF ingles.
             # DEL MISMO TITULO, no de una segunda cadena. Eran dos y decian
             # cosas distintas del mismo documento — el encabezado ingles ya no
             # llevaba los anios y la portada si. El encabezado es el titulo con
             # el «en» sustituido por el punto medio, que es lo que lo hace
             # cabecera y no titulo.
             "-V", "header-includes=\\def\\cabecera{%s}"
                   % D1_POR_IDIOMA[idi][2]
                     .replace(" in Peru,", " · Peru,")
                     .replace(" de ley en Perú,", " de ley · Perú,"),
             # LA HOJA DE ESTILO VA AQUI, y hasta ahora no iba. Existia en
             # `plantillas/estilo-pdf.tex`, decia de si misma que se pasa con
             # --include-in-header, y este comando —que es el canonico— no la
             # pasaba. Habia dos formas de sacar el PDF y una perdia el estilo
             # sin avisar: la figura desbordada, las tablas sin aire, la cabecera
             # sin repetir. Ninguna fallaba.
             "--include-in-header", str(PLANTILLAS / "estilo-pdf.tex"),
             # LAS RUTAS DE IMAGEN SON RELATIVAS AL MARKDOWN, no al directorio
             # desde el que se invoca. Sin esto, `figuras/figura-apertura` se
             # buscaba en la raiz del repositorio y no aparecia.
             "--resource-path", str(SALIDA)],
            capture_output=True, text=True)
        # PANDOC AVISA Y SIGUE, que es la degradacion silenciosa de siempre con
        # otra ropa: ante una imagen que no encuentra escribe «replacing image
        # with description», devuelve codigo CERO y produce un PDF de 18 paginas
        # sin la figura. El generador se tragaba stderr cuando el comando tenia
        # exito, asi que el aviso no llegaba a nadie y el defecto solo se veia
        # abriendo la pagina renderizada.
        avisos = [l for l in r.stderr.splitlines() if "[WARNING]" in l]
        if r.returncode != 0:
            print("  PDF FALLO: %s" % r.stderr.strip()[:200])
            return 1
        if avisos:
            print("  PDF FALLO, pandoc aviso y siguio:")
            for l in avisos[:5]:
                print("     %s" % l.strip())
            return 1
        print("  PDF %s escrito" % idi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
