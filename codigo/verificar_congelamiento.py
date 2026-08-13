#!/usr/bin/env python3
"""Verifica `docs/PROTOCOL_FREEZE.md` recalculando cada hash declarado.

Un registro de integridad que no se ejecuta es prosa. Este script recorre las
entradas del registro, resuelve el archivo que cada una declara y compara el
SHA-256 real contra el declarado. Sale con codigo 1 si algo no cuadra.

TRES CLASES DE FALLO ABIERTO, encontradas por revision adversarial y cerradas
aqui. Van juntas porque son la misma idea vista desde tres alturas:

  1. Un hash malformado hacia DESAPARECER el bloque en vez de fallar (la revisión cruzada,
     rev137). Causa: se exigia el hash bien formado para *reconocer* la entrada.

  2. La entrada entera podia desaparecer y nadie lo notaba (la revisión cruzada, rev140).
     Registro vacio: «0 entradas verificadas, todas reproducen», salida 0. Una
     entrada borrada: 13 en vez de 14, salida 0. Homoglifos cirilicos en las
     etiquetas de la tabla: el bloque se vuelve invisible, salida 0.
     Causa: **el conjunto esperado no estaba anclado a nada**. Verificar lo que
     el registro dice contener no dice nada sobre lo que deberia contener.

  3. El titulo nunca se parseaba (la revisión cruzada, rev140), asi que una version duplicada
     o apocrifa pasaba con salida 0. La funcion declarada del registro —version
     a hash unico— no se verificaba.

EL ANCLA. Toda copia de protocolo en `docs/archivo/` debe tener exactamente una
entrada, y toda entrada debe apuntar a una copia existente. Es una biyeccion, y
por eso las tres formas de hacer desaparecer una entrada fallan ahora: el archivo
queda huerfano. Las copias que legitimamente no son versiones congeladas se
declaran en el propio registro, en una tabla que este script lee; una excepcion
declarada es visible, una excepcion implicita es un agujero.

Uso:  python3 scripts/verificar_congelamiento.py
"""
import glob
import hashlib
import subprocess
import os
import re
import sys

REGISTRO = 'docs/PROTOCOL_FREEZE.md'
VIGENTE = 'docs/02-protocolo.md'
ESQUEMA = ['schema/draft/001_schema.sql', 'schema/draft/900_validaciones.sql']
COPIAS = 'docs/archivo/02-protocolo*.md'
# Una copia con nombre `…-vN.N.md` es una VERSION CONGELADA. Es el patron que la
# tabla de excepciones no puede cubrir; ver `excepciones_declaradas`.
COPIA_DE_VERSION = re.compile(r'-v\d+\.\d+\.md$')
# El bloque cuyos hashes se comprueban contra los archivos reales se declara CON
# UNA MARCA, no por su titulo. Dos intentos fallidos antes de llegar aqui, y los
# dos instructivos:
#
#   Por titulo exacto: al congelar el esquema se renombro el bloque y el chequeo
#   dejo de correr EN SILENCIO. Una comprobacion que depende de como este
#   redactado un encabezado no es una comprobacion.
#
#   Por prefijo: entonces alcanzo tambien a un bloque HISTORICO, que declara un
#   hash viejo con toda razon, y lo reporto como error. Afinar el prefijo seria
#   volver a atar la comprobacion a la redaccion.
#
# La marca es explicita y vive en el registro, igual que la tabla de excepciones.
MARCA_VIGENTE = re.compile(r'^\|\s*Vigente\s*\|\s*si\s*\|\s*$', re.M | re.I)
TITULO_EXCEPCIONES = 'Copias archivadas sin entrada propia'

FILA_SHA = re.compile(r'^\|\s*SHA-256(?:\s*\((?:es|en)\))?\s*\|(.*?)\|\s*$', re.M)
FILA_ARCHIVO = re.compile(r'^\|\s*Archivo(?:\s*\((?:es|en)\))?\s*\|(.*?)\|\s*$', re.M)
HEX64 = re.compile(r'^\s*`([0-9a-f]{64})`\s*$')
VERSION = re.compile(r'·\s*(v\d+\.\d+)(?![\d.])')
FILA_RUTA_HASH = re.compile(r'^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|\s*$', re.M)


def sha256(ruta):
    with open(ruta, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def bloques(texto):
    """Todo bloque que PRETENDE ser una entrada, este o no bien formado.

    Separar «pretende ser entrada» de «esta bien formada» es lo que cierra el
    fallo de clase 1: lo primero decide si se examina, lo segundo si pasa.
    """
    for bloque in re.split(r'\n## ', texto):
        titulo = bloque.split('\n')[0].strip()
        # La tabla de excepciones tiene una columna llamada «Archivo», asi que se
        # autodetectaba como entrada. Se excluye por titulo y no confiando en que
        # el nombre de la columna no choque: eso ultimo se rompe al editar el
        # registro y falla de forma confusa.
        if titulo.startswith(TITULO_EXCEPCIONES):
            continue
        shas = FILA_SHA.findall(bloque)
        archivos = FILA_ARCHIVO.findall(bloque)
        if not shas and not archivos:
            continue          # nota o seccion de prosa, no pretende ser entrada
        yield titulo, archivos, shas


def _ruta_de(celda):
    m = re.search(r'`([^`]+)`', celda)
    return m.group(1).strip() if m else None


def entradas(texto):
    """Entradas bien formadas, UNA POR IDIOMA: (titulo, archivo, hash).

    Una entrada del registro puede declarar dos idiomas —dos archivos, dos
    hashes— y aqui se rinde como dos pares, porque cada copia archivada se
    verifica por separado contra el suyo. La union en una sola entrada es lo que
    impide que una traduccion se quede atras sin que nadie lo vea; la separacion
    aqui es solo para comprobarlas.
    """
    for titulo, archivos, shas in bloques(texto):
        if not (1 <= len(shas) <= 2) or len(archivos) != len(shas):
            continue
        for archivo, sha in zip(archivos, shas):
            m_hash = HEX64.match(sha)
            ruta = _ruta_de(archivo)
            if m_hash and ruta:
                yield titulo, ruta, m_hash.group(1)


def malformadas(texto):
    """Bloques que pretenden ser entrada y no lo consiguen. Cada uno es un fallo."""
    for titulo, archivos, shas in bloques(texto):
        # UNA ENTRADA POR VERSION, UNO O DOS IDIOMAS. Desde que el protocolo se
        # publica en dos lenguas, una entrada puede declarar dos archivos con
        # dos hashes — pero en UNA fila, no en dos entradas.
        #
        # Dos entradas separadas permitirian un registro completo y consistente
        # con una traduccion que se quedo atras: cada entrada verdadera por
        # separado, nada falla, y solo se veria comparando fechas que nadie
        # compara. Con una, la desviacion es estructuralmente indecible.
        if not 1 <= len(shas) <= 2:
            yield ('%s · declara %d filas de SHA-256, debe declarar una o dos'
                   % (titulo, len(shas)))
            continue
        # Y TIENEN QUE EMPAREJAR. Dos archivos con un solo hash dejaria la
        # traduccion sin certificar, que es exactamente el hueco que la entrada
        # unica existe para impedir.
        if len(archivos) != len(shas):
            yield ('%s · declara %d archivo(s) y %d hash(es): cada idioma tiene '
                   'que llevar el suyo' % (titulo, len(archivos), len(shas)))
            continue
        malo = next((h for h in shas if not HEX64.match(h)), None)
        if malo is not None:
            yield ('%s · SHA-256 ausente o malformado: %r (64 hex en minuscula)'
                   % (titulo, malo.strip()))
            continue
        if not all(_ruta_de(a) for a in archivos):
            yield '%s · alguna fila de Archivo no lleva una ruta entre comillas' % titulo


def excepciones_declaradas(texto):
    """Copias archivadas que el registro declara que NO son versiones congeladas.

    Se leen del propio registro en vez de codificarse aqui: una excepcion que
    vive en el script es invisible para quien lee el registro.
    """
    for bloque in re.split(r'\n## ', texto):
        if not bloque.split('\n')[0].strip().startswith(TITULO_EXCEPCIONES):
            continue
        return {m for m in re.findall(r'^\|\s*`([^`]+)`\s*\|', bloque, re.M)}
    return set()


def excepciones_invalidas(declaradas):
    """Excepciones que la tabla no tiene derecho a declarar.

    La tabla de excepciones es la UNICA salida del conjunto anclado, y estaba sin
    autenticar: cualquiera podia sacar del ancla una version congelada anadiendo
    una fila. la revisión cruzada lo ejecuto y la version quedaba des-congelada en silencio,
    con su archivo sin volver a hashear.

    Una copia con nombre `…-vN.N.md` es una version congelada por construccion, y
    ninguna razon la exime de tener entrada. La excepcion legitima que existe hoy
    —la correccion editorial de v2.3— no casa ese patron, asi que sigue valiendo.
    """
    for ruta in sorted(declaradas):
        if COPIA_DE_VERSION.search(ruta):
            yield ('excepcion invalida: %s tiene nombre de version congelada y '
                   'no puede declararse excepcion' % ruta)


def version_del_vigente(ruta=None):
    # `ruta=VIGENTE` fijaba el valor por defecto AL DEFINIR la funcion, asi que
    # sustituir el modulo-constante despues del import no surtia efecto. La
    # prueba F —«bajar la version del encabezado no debe mover el ancla»—
    # escribia un vigente falso en un temporal, apuntaba ahi, y esta funcion
    # seguia leyendo el real: llevaba tiempo pasando por el motivo equivocado y
    # solo se vio al subir a v2.23, cuando los demas mensajes cambiaron.
    #
    # Es la familia del arreglo atado al orden: un valor por defecto se liga una
    # vez y no vuelve a mirar. Leerlo en la LLAMADA no depende de cuando se
    # importo el modulo.
    ruta = ruta or VIGENTE
    """Version que el documento vigente declara en su propio encabezado.

    ESTE ES EL ANCLA EXTERNA, y es la pieza que faltaba. La biyeccion de v2.12
    comprueba que las entradas y las copias coincidan ENTRE SI, y la revisión cruzada mostro
    que eso no basta: borrando la entrada Y sacando su archivo del escaneo, los
    dos conjuntos quedan mas pequenos pero igual de balanceados, y el verificador
    anuncia salud con salida 0.

    Yo mismo lo habia escrito en v2.12 —«verificar lo que un registro dice
    contener no dice nada sobre lo que deberia contener»— e implemente un ancla
    interna, que es lo mismo que no anclar.

    El vigente declara su version en su primera linea, y ese hecho vive FUERA del
    registro. Si la cadena de entradas no llega hasta el, falta al menos una.
    """
    try:
        cab = open(ruta, encoding='utf-8').readline()
    except OSError:
        return None
    m = re.search(r'·\s*v(\d+)\.(\d+)\s*$', cab.strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def copias_segun_git(patron=COPIAS):
    """Toda copia de protocolo que ALGUNA VEZ se anadio, segun el historial.

    ESTE ES EL ANCLA BUENA, y llega tras dos intentos fallidos que conviene dejar
    escritos porque cada uno enseña algo:

      1. Biyeccion interna (v2.12): comprueba que entradas y copias en disco
         coincidan ENTRE SI. la revisión cruzada la rompio borrando los dos lados a la vez —
         los conjuntos quedan mas pequenos pero balanceados.

      2. Cadena hasta la version del vigente (v2.15): ancla a un hecho externo al
         registro, pero insuficiente por dos motivos que la revisión cruzada ejecuto. Solo
         cubre la serie mayor del vigente, asi que la serie v1 quedaba libre. Y el
         ancla misma es EDITABLE: bajando el encabezado del vigente de v2.15 a
         v2.1 se podia borrar la entrada v2.15 y su archivo con salida 0.

    El historial de git no tiene esos dos problemas. Es externo al registro y al
    disco, y cubre todas las series.

    CORRECCION, y va aqui porque aqui estaba el error. Escribi que «para borrar
    una copia del historial hay que reescribirlo, que es ruidoso y deja rastro».
    **Es falso, y la revisión cruzada lo ejecuto.** El conjunto anclado se calcula restando las
    excepciones declaradas, y la tabla de excepciones no estaba autenticada: bastaba
    anadirle una fila para sacar una copia historica del ancla. Combinado con
    borrar su entrada, una version congelada quedaba des-congelada en silencio y su
    archivo no se volvia a hashear nunca — comprobado con el archivo corrompido en
    disco, que pasaba verde.

    La puerta se cierra en `excepciones_declaradas`: una excepcion NO puede cubrir
    una copia con nombre de version. El ancla es monotono solo si su unica salida
    tambien lo es.

    Si git no esta disponible se DEVUELVE None y el llamador falla. No se salta en
    silencio: saltarse una comprobacion cuando falta su insumo es el fallo abierto
    que este guion existe para no tener.

    `-m` esta por el ultimo hallazgo de la revisión cruzada: sin el, `git log --diff-filter=A`
    NO entra en los diffs de los commits de merge, asi que un archivo anadido solo
    dentro de un merge quedaba fuera del ancla. El repo no tiene merges hoy y el
    conjunto sale identico con y sin la bandera, pero costaba una linea y prefiero
    cerrarlo a declararlo.
    """
    try:
        r = subprocess.run(
            ["git", "-c", "core.quotePath=false", "log", "-m", "--diff-filter=A", "--name-only", "--format=", "--", patron],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return {l.strip() for l in r.stdout.split("\n") if l.strip()}


def ruta_plana_valida(archivo):
    """La ruta es una copia plana bajo docs/archivo/ terminada en .md."""
    if not archivo.startswith('docs/archivo/') or '..' in archivo:
        return False
    resto = archivo[len('docs/archivo/'):]
    return '/' not in resto and resto.endswith('.md') and resto != '.md'


def main(registro=REGISTRO, texto=None, copias=COPIAS):
    if texto is None:
        texto = open(registro, encoding='utf-8').read()
    fallos = []
    verificadas = 0

    # PRIMERO lo malformado, antes de verificar archivo alguno. Un bloque que
    # pretende ser entrada y no lo consigue es un fallo por si mismo; saltarlo
    # es el fallo abierto de clase 1.
    fallos.extend(malformadas(texto))

    vistas = {}          # version -> titulo
    rutas_con_entrada = set()

    # DUPLICADOS, SOBRE BLOQUES Y NO SOBRE IDIOMAS. Una entrada rinde un par por
    # lengua, asi que contar sobre `entradas()` veria la vigente dos veces y
    # llamaria duplicado a lo que es una sola entrada bilingue. Contar bloques
    # —una entrada del registro, tenga uno o dos idiomas— mantiene el control
    # estricto: dos BLOQUES que declaren la misma version siguen siendo un
    # duplicado, que es lo que esto existe para impedir.
    por_version: dict = {}
    for titulo, _a, _s in bloques(texto):
        m_v = VERSION.search(titulo)
        if not m_v:
            continue
        por_version.setdefault(m_v.group(1), []).append(titulo)
    for version, titulos in por_version.items():
        if len(titulos) > 1:
            fallos.append('%s · version %s duplicada, ya declarada por «%s»'
                          % (titulos[-1], version, titulos[0]))

    for titulo, archivo, declarado in entradas(texto):
        # -- El titulo se parsea. Antes no, y por eso una version duplicada o
        #    apocrifa pasaba con salida 0 (fallo de clase 3).
        m_v = VERSION.search(titulo)
        if not m_v:
            fallos.append('%s · el titulo no declara una version `vN.N`' % titulo)
            continue
        version = m_v.group(1)
        vistas[version] = titulo

        if not ruta_plana_valida(archivo):
            fallos.append('%s · no apunta a una copia plana bajo docs/archivo/ (%s)'
                          % (titulo, archivo))
            continue
        # -- El nombre del archivo debe llevar la version de la entrada. Sin esto,
        #    una entrada titulada v2.10 podia apuntar al archivo de v2.11.
        if not archivo.endswith('-%s.md' % version):
            fallos.append('%s · el archivo no corresponde a %s: %s'
                          % (titulo, version, archivo))
            continue
        if os.path.islink(archivo):
            fallos.append('%s · el archivo es un enlace simbolico: %s'
                          % (titulo, archivo))
            continue
        if not os.path.exists(archivo):
            fallos.append('%s · archivo inexistente: %s' % (titulo, archivo))
            continue

        rutas_con_entrada.add(archivo)
        real = sha256(archivo)
        verificadas += 1
        if real != declarado:
            fallos.append('%s · %s\n    declarado %s\n    real      %s'
                          % (titulo, archivo, declarado, real))
        else:
            print('OK  %-46s %s' % (titulo[:46], archivo))

    # -- EL ANCLA (fallo de clase 2). Sin esto, verificar lo que el registro dice
    #    contener no dice nada sobre lo que deberia contener: el registro vacio
    #    pasaba anunciando «0 entradas verificadas, todas reproducen».
    excepciones = excepciones_declaradas(texto)
    fallos.extend(excepciones_invalidas(excepciones))
    todas = set(glob.glob(copias))
    # Un enlace simbolico en el directorio de archivo es un señuelo: apunta a un
    # archivo que puede cambiar, con nombre de copia inmutable. Antes se filtraba
    # en silencio, que es la misma falta que se corrige en todo este guion —
    # saltar lo anomalo en vez de reportarlo.
    enlaces = sorted(p for p in todas if os.path.islink(p))
    for ruta in enlaces:
        fallos.append('enlace simbolico en el directorio de archivo: %s -> %s '
                      '(una copia congelada es un archivo, no un puntero)'
                      % (ruta, os.readlink(ruta)))
    en_disco = todas - set(enlaces)
    huerfanas = sorted(en_disco - rutas_con_entrada - excepciones)
    for ruta in huerfanas:
        fallos.append('copia archivada sin entrada en el registro: %s '
                      '(declararla como excepcion si no es una version congelada)'
                      % ruta)
    for ruta in sorted(excepciones - en_disco):
        fallos.append('excepcion declarada para un archivo inexistente: %s' % ruta)
    if not verificadas:
        fallos.append('el registro no declara ninguna entrada verificable')

    # -- ANCLA MONOTONA: toda copia que alguna vez existio debe tener entrada.
    #    Independiente del encabezado del vigente y de lo que hoy haya en disco.
    historicas = copias_segun_git()
    if historicas is None:
        fallos.append('no pude consultar el historial de git para anclar el '
                      'conjunto esperado; la comprobacion NO se salta, falla')
    else:
        for ruta in sorted(historicas - rutas_con_entrada - excepciones):
            fallos.append('copia que existio en el historial y hoy no tiene '
                          'entrada en el registro: %s' % ruta)

    # -- ANCLA DEL VIGENTE: la cadena de versiones debe llegar al documento vigente.
    #    Sin esto, borrar una entrada Y su archivo a la vez pasa sin rastro.
    esperada = version_del_vigente()
    if esperada is None:
        fallos.append('no pude leer la version del documento vigente (%s)' % VIGENTE)
    else:
        v_str = 'v%d.%d' % esperada
        if v_str not in vistas:
            fallos.append('el documento vigente declara %s y el registro no tiene '
                          'esa entrada' % v_str)
        # La cadena de la serie mayor del vigente debe ser contigua hasta el.
        mayor = esperada[0]
        menores = sorted(int(v.split('.')[1]) for v in vistas
                         if v.startswith('v%d.' % mayor))
        faltan = [n for n in range(0, esperada[1] + 1) if n not in menores]
        if faltan:
            fallos.append('faltan entradas en la cadena v%d.x hasta %s: %s'
                          % (mayor, v_str,
                             ', '.join('v%d.%d' % (mayor, n) for n in faltan)))

    # -- Los hashes de esquema del bloque de estado actual se comparaban con
    #    nada, y declaraban un esquema de dos versiones atras. Los de las
    #    entradas historicas NO se tocan: son correctos para su momento.
    # Se comprueban DOS clases de bloque contra los archivos reales:
    #   - el marcado `Vigente | si`, que es el estado actual;
    #   - la ENTRADA de la version vigente, que congela el esquema de ahora.
    # Las entradas historicas NO: declaran hashes de su momento, con razon.
    # La revisión cruzada encontro que la entrada congelada declaraba el hash del esquema y
    # nadie lo comparaba con nada; hoy coincide por accidente, porque el bloque
    # vigente declara el mismo par, pero puede derivar sin alarma.
    v_actual = version_del_vigente()
    # Por la version PARSEADA del titulo, no por su final: el titulo de la entrada
    # congelada es «… · v2.15 — ESQUEMA CONGELADO» y un endswith no casaba. Atar
    # esto a la redaccion del titulo es el error que ya cometi al congelar.
    etiqueta_actual = ('v%d.%d' % v_actual) if v_actual else None
    vigentes = 0
    for bloque in re.split(r'\n## ', texto):
        titulo = bloque.split('\n')[0].strip()
        m_t = VERSION.search(titulo)
        es_entrada_actual = bool(etiqueta_actual and m_t
                                 and m_t.group(1) == etiqueta_actual)
        if MARCA_VIGENTE.search(bloque):
            vigentes += 1
        elif not es_entrada_actual:
            continue
        for ruta, declarado in FILA_RUTA_HASH.findall(bloque):
            if not os.path.exists(ruta):
                fallos.append('estado actual · ruta inexistente: %s' % ruta)
            elif sha256(ruta) != declarado:
                fallos.append('estado actual · %s\n    declarado %s\n    real      %s'
                              % (ruta, declarado, sha256(ruta)))

    # Exactamente un bloque vigente. Cero significa que la marca se perdio al
    # editar y el chequeo dejo de correr —el fallo abierto que ya ocurrio dos
    # veces—; mas de uno significa que hay dos estados actuales.
    if vigentes != 1:
        fallos.append('el registro declara %d bloques con marca `Vigente | si`, '
                      'debe declarar exactamente 1' % vigentes)

    print()
    for ruta in ESQUEMA:
        print('%s  %s' % (sha256(ruta), ruta))

    if fallos:
        print('\nFALLA la verificacion del registro:\n')
        for f in fallos:
            print('  - %s' % f)
        return 1

    print('\n%d entradas verificadas contra %d copias archivadas '
          '(%d excepciones declaradas); todas reproducen su hash.'
          % (verificadas, len(en_disco), len(excepciones)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
