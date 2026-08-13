# República Dominicana — apéndice de verificación

Jurisdicción de referencia: **Santo Domingo**  ·  código ISO3: `DOM`

> **Procedencia de este documento.** Generado automáticamente. No editar a mano.
>
> | | |
> |---|---|
> | Protocolo | `v2.27` |
> | Hash del protocolo | `bb9db022dec2e48c…` |
> | Hash de la base | `44ddb8105c321371…` |
> | Hash del generador | `3f83fbd42e3e929f…` |
> | Versión publicada | `v1.0.1` |


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

**Cobertura de citas en esta unidad: 4 de 20 celdas traen el pasaje textual dentro del documento (20 %).** El resto de las celdas remite a
las fuentes listadas abajo, que hay que consultar en su origen. Es la limitación
principal de este apéndice y se declara arriba, no en una nota final.

## Índice de celdas

| celda | qué verifica | valor |
|---|---|---|
| V1 | Feriado · Año Nuevo | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V2 | Feriado · Corpus Christi | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V3 | Feriado · Día de Duarte | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V4 | Feriado · Día de la Constitución | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V5 | Feriado · Día de la Independencia Nacional | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V6 | Feriado · Día de la Restauración | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V7 | Feriado · Día de los Santos Reyes | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V8 | Feriado · Día del Trabajo | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V9 | Feriado · Navidad | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V10 | Feriado · Nuestra Señora de la Altagracia | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V11 | Feriado · Nuestra Señora de las Mercedes | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V12 | Feriado · Viernes Santo | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V13 | Conteo de feriados, corte 2016 | 12,0 |
| V14 | Conteo de feriados, corte 2026 | 12,0 |
| V15 | Vacaciones · cantidad y unidad de conteo | 14,0 días de tipo «habil» |
| V16 | Vacaciones · procedencia del corte 2016 | sin cambio, buscado y confirmado — rama (b) reproducción de nivel 3 más pantalla 3 |
| V17 | Vacaciones · base semanal | 6 días, declarada por la norma (norma) |
| V18 | Vacaciones · imputación de feriados | sin_regla_explicita |
| V19 | Colocación · regla 1 (todo_el_derecho) | iniciativa «empleador» |
| V20 | Escala de antigüedad | 2 tramos |

## Fuentes citadas en este documento

| nivel | autoridad | localización |
|---|---|---|
| 2 · portal gubernamental | Código de Trabajo de la República Dominicana (Ley 16-92), arts. 146, 147, 148, 163, 164 y 165 | https://mt.gob.do/wp-content/uploads/2024/07/codigo_de_trabajo.pdf |
| 3 · secundarias concordantes | Código de Trabajo de la República Dominicana, Ley 16-92 — arts. 163, 164, 165, 177 a 189 | https://docs.republica-dominicana.justia.com/nacionales/codigos/codigo-de-trabajo.pdf |
| 3 · secundarias concordantes | Ley No. 139-97, sobre traslado a los lunes de los días feriados que coincidan con martes, miercoles, jueves o viernes | https://docs.republica-dominicana.justia.com/nacionales/leyes/ley-139-97.pdf |
| 4 · una sola secundaria | Ministerio de Trabajo — comunicado oficial de días feriados 2026 | https://mt.gob.do/ministerio-de-trabajo-informa-dias-feriados-correspondientes-al-ano-2026/ |

## Desarrollo, celda por celda

### V1 · Feriado · Año Nuevo

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 01-01
```


### V2 · Feriado · Corpus Christi

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua+60 días
```

**Nota:** Jueves posterior al domingo de la Trinidad = Pascua + 60 dias.


### V3 · Feriado · Día de Duarte

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 01-26
```


### V4 · Feriado · Día de la Constitución

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 11-06
```


### V5 · Feriado · Día de la Independencia Nacional

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 02-27
```


### V6 · Feriado · Día de la Restauración

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 08-16
```

**Nota:** Su traslado es CONDICIONAL a un ciclo politico de cuatro anos. El esquema no tiene donde poner una condicion de traslado dependiente del calendario electoral.


### V7 · Feriado · Día de los Santos Reyes

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 01-06
```


### V8 · Feriado · Día del Trabajo

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 05-01
```


### V9 · Feriado · Navidad

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 12-25
```


### V10 · Feriado · Nuestra Señora de la Altagracia

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 01-21
```


### V11 · Feriado · Nuestra Señora de las Mercedes

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 09-24
```


### V12 · Feriado · Viernes Santo

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua-2 días
```


### V13 · Conteo de feriados, corte 2016

**Valor publicado:** 12,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Año Nuevo                                                1
Corpus Christi                                           1
Día de Duarte                                            1
Día de la Constitución                                   1
Día de la Independencia Nacional                         1
Día de la Restauración                                   1
Día de los Santos Reyes                                  1
Día del Trabajo                                          1
Navidad                                                  1
Nuestra Señora de la Altagracia                          1
Nuestra Señora de las Mercedes                           1
Viernes Santo                                            1
----------------------------------------------------------
TOTAL                                                   12
```


### V14 · Conteo de feriados, corte 2026

**Valor publicado:** 12,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Año Nuevo                                                1
Corpus Christi                                           1
Día de Duarte                                            1
Día de la Constitución                                   1
Día de la Independencia Nacional                         1
Día de la Restauración                                   1
Día de los Santos Reyes                                  1
Día del Trabajo                                          1
Navidad                                                  1
Nuestra Señora de la Altagracia                          1
Nuestra Señora de las Mercedes                           1
Viernes Santo                                            1
----------------------------------------------------------
TOTAL                                                   12
```


### V15 · Vacaciones · cantidad y unidad de conteo

**Valor publicado:** 14,0 días de tipo «habil»

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _captura, campo «literal»_
>
> «un periodo de vacaciones de catorce (14) dias laborables, con disfrute de salario (art. 177)»

**Nota:** La unidad de conteo **no se infiere**: se lee de la norma. Sin ella el número no es comparable con el de otra unidad.


### V16 · Vacaciones · procedencia del corte 2016

**Valor publicado:** sin cambio, buscado y confirmado — rama (b) reproducción de nivel 3 más pantalla 3

**Regla aplicada:** §10 bis — Las pantallas en la variable de vacaciones: cuando un par unidad-corte se codifica «sin cambio confirmado», y las dos ramas que lo autorizan.

**Pasaje o pasajes de los que sale:**

> _captura, «buscado_en»_
>
> «Reproducciones del Código de Trabajo dominicano con la nota de modificación del art. 177»

> _captura, pasaje citado_
>
> ««Los empleadores tienen la obligacion de conceder a todo trabajador un periodo de vacaciones de catorce días laborables con disfrute de salario», con escala a dieciocho días de salario desde los cinco anios. El artículo lleva su nota: MODIFICADO POR LA LEY 97-97, publicada en la Gaceta Oficial 9955 de 31 de mayo de 1997. Es su última modificación y queda muy fuera de la ventana.»

> _captura, pantalla 3_
>
> «Prensa dominicana: la reforma integral del código NO se promulgo. A agosto de 2026 sigue en tramite —aprobada en primera lectura por la Camara de Diputados el 20 de mayo de 2026, pendiente de segunda lectura y del Senado—. Dato util aunque no mueva el corte: el proyecto MANTIENE los catorce días para el tramo de uno a tres anios, de modo que ni promulgandose moveria al trabajador de referencia.»

**Nota:** **Confirmado no es lo mismo que supuesto**, y el paquete los distingue: aquí se buscó la modificatoria y se comprobó que no existe o que no toca la cantidad. Un «supuesto» sólo dice que no se halló.


### V17 · Vacaciones · base semanal

**Valor publicado:** 6 días, declarada por la norma (norma)

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.


### V18 · Vacaciones · imputación de feriados

**Valor publicado:** sin_regla_explicita

**Regla aplicada:** §4 — Imputación de feriados al período vacacional: si lo extienden o se computan contra él.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Nota:** Decide si un feriado dentro del período vacacional lo extiende o se computa contra él. En un derecho contado en días calendario, la diferencia puede valer varios días.


### V19 · Colocación · regla 1 (todo_el_derecho)

**Valor publicado:** iniciativa «empleador»

**Regla aplicada:** §5 — Reglas de colocación en capas, y §34.2 para la resolución del desacuerdo cuando la colocación es negociada.

**Pasaje o pasajes de los que sale:**

> _literal registrado en la base_
>
> «Los empleadores deben fijar y distribuir, durante los primeros quince dias del mes de enero, los periodos de vacaciones de sus trabajadores (art. 186); el empleador puede variar, en caso de necesidad, la distribucion del periodo de vacaciones, pero por ninguna circunstancia los trabajadores dejaran de disfrutar integramente de las vacaciones dentro de los seis meses de la fecha de adquisicion del derecho (art. 188)»


### V20 · Escala de antigüedad

**Valor publicado:** 2 tramos

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _literal del primer tramo_
>
> «un periodo de vacaciones de catorce (14) dias laborables, con disfrute de salario (art. 177)»

**Aritmética:**

```
desde el mes   0 hasta 12     -> 0.0 días habil
desde el mes  12 hasta sin fin -> 14.0 días habil
```

**Nota:** El trabajador de referencia tiene doce meses exactos de servicio continuo; la cifra de portada es la de su tramo.
