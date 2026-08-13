# Feriados y vacaciones legales — exportacion

Generado por `scripts/exportar.py` desde `data/derived/piloto.db`.
**No editar a mano.** Cualquier correccion va en la captura de origen
(`data/raw/<unidad>/captura.json`) y se regenera el paquete.

Protocolo **v2.27** · commit y hashes en `MANIFEST.csv`.

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

### `unidades.csv` — 47 filas

Las 47 unidades de referencia. `jurisdiccion_de_referencia` es la ciudad concreta que se midio, no el pais: en un pais federal sin ley nacional de feriados no existe «el numero del pais». Los nombres van en los dos idiomas: los paises con el nombre corto ingles de la ISO 3166-1 —de ahi «Türkiye» y «Czechia»—, y las ciudades con el exonimo ingles establecido donde existe y el endonimo cuando no, que es convencion editorial y se dice.

### `feriados.csv` — 582 filas

`regla_id` identifica la FILA y `feriado_id` el feriado: para contar feriados se agrupa por `feriado_id`. Una REGLA DE FECHA por fila, no un feriado: desde v2.20 un feriado puede tener varias reglas —una por defecto y las alternativas condicionales—, asi que para contar feriados hay que contar `feriado` distintos por unidad y no filas. El archivo lo dice aqui porque un CSV que cambia de grano en silencio es peor que uno mal disenado. `categoria` y `regimen` son lo que decide si cuenta: no todos los dias festivos obligan a descanso pagado. OJO con `condicion_dia_semana`: un feriado puede tener VARIAS filas, una por regla, y si TODAS llevan condicion, ese feriado no ocurre en los anios en que ninguna se cumple — es el caso de los tres condicionales chilenos, que estan en el registro y no en el conteo de 2016 ni de 2026.

### `vacaciones.csv` — 49 filas

Una VERSION de titularidad por fila, no una unidad: desde que el panel de vacaciones dejo de ser plano, una jurisdiccion con reforma en la ventana aparece dos veces, con sus `vigencia_desde` y `vigencia_hasta` distintos. Para contar unidades, cuente `iso3` distintos. `dias_texto_legal` NO es comparable entre filas si `tipo_de_dia` difiere: 30 dias calendario peruanos y 24 Werktage alemanes no son la misma magnitud. Para comparar, `vacaciones_convertido.csv`. LA PROCEDENCIA DEL CORTE ANTIGUO VA EN COLUMNA y no en prosa, porque una afirmacion que solo se puede comprobar abriendo cuarenta y un archivos no es comprobable. `estado_2016` dice de donde sale el corte de 2016 de cada fila: `sin_cambio_confirmado` es «se busco la modificatoria y se comprobo que no existe o que no toca la cantidad», `verificado_primaria` es «la reforma esta capturada y fechada», y `supuesto` es solo «no se hallo» — que NO es evidencia de que no cambiara. Y `nivel_fuente_2016` con `rama_10bis` dicen CON QUE se confirmo, porque no vale lo mismo un indice oficial de nivel 1 que una reproduccion de nivel 3 con una tercera pantalla coincidente: son las dos ramas del §10 bis del protocolo y se publican separadas en vez de aplastarse en un unico «confirmado». `buscado_en_2016` nombra el documento que se consulto. El apendice de verificacion de cada unidad trae la misma celda con su pasaje citado.

### `escala_antiguedad.csv` — 167 filas

Tramos de antiguedad, donde la titularidad no es un numero unico. `literal_normativo` guarda la frase de la ley que fija el tramo.

### `colocacion.csv` — 53 filas

Quien decide CUANDO se toman las vacaciones. Un derecho de 30 dias que fija el empleador sin veto del trabajador no es el mismo bien que 30 dias de eleccion libre, y el numero solo no lo distingue. `resolucion_desacuerdo` dice que pasa cuando la negociacion no llega a acuerdo: sin esa columna, Peru y Grecia parecen iguales y resuelven en direcciones opuestas.

### `fuentes.csv` — 251 filas

Toda fuente citada, con su nivel. Nivel 1 es gaceta oficial; nivel 4 es fuente secundaria sin confirmar. El nivel se declara, no se maquilla.

### `evidencia.csv` — 1475 filas

El puente entre cada hecho y la fuente que lo respalda. Es lo que hace auditable el dataset: cualquier fila de feriados o vacaciones se puede seguir hasta el documento.

### `panel_feriados.csv` — 47 filas

DERIVADO. Conteo por corte, obtenido preguntando a la base que feriados estaban vigentes en cada fecha. **`estado_2016` es la columna que mas importa** y durante un tiempo este archivo la prometia sin emitirla: `verificado` es que las modificatorias de la ventana estan localizadas y datadas; `verificado_parcial`, que se verifico el conteo y hay cambio de regla sin cambio de cantidad; `supuesto_sin_cambio`, que NO se hallo modificatoria — ausencia no verificada, no ausencia; y `no_capturado`, que ese corte no se leyo y no se rellena con el otro. **`feriados_*` cuenta TODO dia festivo capturado y `exigibles_*` solo el descanso pagado obligatorio**, que es lo que la metrica principal usa: para Estados Unidos son doce y cero, porque sus feriados son cierre del sector publico y ninguno obliga al empleador privado.

### `vacaciones_convertido.csv` — 49 filas

DERIVADO Y CONVENCIONAL. La conversion a dias de trabajo sobre semana de 5 la decidimos nosotros, no la ley. Se publica aparte para que nadie la confunda con el texto legal, y con el supuesto en su propia columna.

## Como citar una fila

Toma su `iso3` y el hecho, busca en `evidencia.csv` la fuente con su nivel y
fecha de verificacion, y cita esa norma. El dataset no pide que se le crea: pide
que se le siga hasta el documento.
