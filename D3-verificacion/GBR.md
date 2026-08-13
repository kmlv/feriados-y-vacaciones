# Reino Unido — apéndice de verificación

Jurisdicción de referencia: **Londres**  ·  código ISO3: `GBR`

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

**Cobertura de citas en esta unidad: 4 de 17 celdas traen el pasaje textual dentro del documento (24 %).** El resto de las celdas remite a
las fuentes listadas abajo, que hay que consultar en su origen. Es la limitación
principal de este apéndice y se declara arriba, no en una nota final.

## Índice de celdas

| celda | qué verifica | valor |
|---|---|---|
| V1 | Feriado · Boxing Day | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V2 | Feriado · Christmas Day | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V3 | Feriado · Early May bank holiday | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V4 | Feriado · Easter Monday | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V5 | Feriado · Good Friday | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V6 | Feriado · New Year's Day | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V7 | Feriado · Spring bank holiday | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V8 | Feriado · Summer bank holiday | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V9 | Conteo de feriados, corte 2016 | 8,0 |
| V10 | Conteo de feriados, corte 2026 | 8,0 |
| V11 | Vacaciones · cantidad y unidad de conteo | 5,6 días de tipo «semanas» |
| V12 | Vacaciones · procedencia del corte 2016 | sin cambio, buscado y confirmado — rama (a) índice oficial de modificaciones, nivel de fuente 1 |
| V13 | Vacaciones · base semanal | 5 días, declarada por la norma (norma) |
| V14 | Vacaciones · conversión a unidad común | 5,60 semanas de derecho, o 28,0 días de trabajo sobre semana de cinco |
| V15 | Vacaciones · imputación de feriados | sin_regla_explicita |
| V16 | Colocación · regla 1 (todo_el_derecho) | iniciativa «trabajador» |
| V17 | Escala de antigüedad | 2 tramos |

## Fuentes citadas en este documento

| nivel | autoridad | localización |
|---|---|---|
| 1 · gaceta oficial | The Working Time Regulations 1998 (SI 1998/1833), regs. 4, 10 y 11 | https://www.legislation.gov.uk/uksi/1998/1833/contents |
| 2 · portal gubernamental | Banking and Financial Dealings Act 1971, c.80 — section 1 y Schedule 1 | https://www.legislation.gov.uk/ukpga/1971/80 |
| 2 · portal gubernamental | The Employment Rights (Amendment, Revocation and Transitional Provision) Regulations 2023, SI 2023/1426 | https://www.legislation.gov.uk/uksi/2023/1426 |
| 2 · portal gubernamental | The Working Time Regulations 1998, SI 1998/1833 — regs 13, 13A, 15, 15A | https://www.legislation.gov.uk/uksi/1998/1833 |
| 2 · portal gubernamental | gov.uk — «Holiday entitlement» (guia oficial del gobierno del Reino Unido) | https://www.gov.uk/holiday-entitlement-rights |
| 4 · una sola secundaria | Proclamaciones reales bajo s.1(3) de la ley de 1971 — Privy Council / The Gazette | https://privycouncil.independent.gov.uk/ |

## Desarrollo, celda por celda

### V1 · Feriado · Boxing Day

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 12-26
```

**Nota:** Schedule 1: «26th December, if it be not a Sunday», con el 27 de diciembre en su lugar cuando el 25 o el 26 caen en domingo. La condicionalidad no cabe en `clase_de_regla: fija` y queda solo en esta nota.


### V2 · Feriado · Christmas Day

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 12-25
```

**Nota:** Feriado de COMMON LAW en Inglaterra y Gales; el Schedule 1 solo lo lista para Escocia. s.1(4) lo usa como VARA DE MEDIR de lo que es un bank holiday, lo que confirma que no lo es por esta ley.


### V3 · Feriado · Early May bank holiday

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: primer lunes del mes 5
```

**Nota:** NO esta en el Schedule 1 para Inglaterra y Gales (si para Escocia). Se proclama cada ano bajo s.1(3).


### V4 · Feriado · Easter Monday

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua+1 días
```

**Nota:** Schedule 1, Inglaterra y Gales.


### V5 · Feriado · Good Friday

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua-2 días
```

**Nota:** Feriado de COMMON LAW en Inglaterra y Gales: no figura en el Schedule 1, que si lo lista para Escocia. Su existencia no depende de la ley de 1971.


### V6 · Feriado · New Year's Day

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 01-01
```

**Nota:** NO esta en el Schedule 1 para Inglaterra y Gales. Se proclama cada ano bajo s.1(3). Si cae en sabado o domingo se proclama el lunes siguiente como sustituto; la regla de traslado no esta capturada como campo.


### V7 · Feriado · Spring bank holiday

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: último lunes del mes 5
```

**Nota:** Schedule 1: «The last Monday in May».


### V8 · Feriado · Summer bank holiday

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: último lunes del mes 8
```

**Nota:** Schedule 1: «The last Monday in August». En Escocia es el PRIMER lunes de agosto: la divergencia interna del Reino Unido es real y por eso la jurisdiccion de referencia esta declarada.


### V9 · Conteo de feriados, corte 2016

**Valor publicado:** 8,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Boxing Day                                               1
Christmas Day                                            1
Early May bank holiday                                   1
Easter Monday                                            1
Good Friday                                              1
New Year's Day                                           1
Spring bank holiday                                      1
Summer bank holiday                                      1
----------------------------------------------------------
TOTAL                                                    8
```


### V10 · Conteo de feriados, corte 2026

**Valor publicado:** 8,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Boxing Day                                               1
Christmas Day                                            1
Early May bank holiday                                   1
Easter Monday                                            1
Good Friday                                              1
New Year's Day                                           1
Spring bank holiday                                      1
Summer bank holiday                                      1
----------------------------------------------------------
TOTAL                                                    8
```


### V11 · Vacaciones · cantidad y unidad de conteo

**Valor publicado:** 5,6 días de tipo «semanas»

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _captura, campo «literal»_
>
> «reg 13(1) four weeks' annual leave in each leave year + reg 13A(2) 1.6 weeks additional leave; reg 13A(3) aggregate capped at 28 days»

**Nota:** La unidad de conteo **no se infiere**: se lee de la norma. Sin ella el número no es comparable con el de otra unidad.


### V12 · Vacaciones · procedencia del corte 2016

**Valor publicado:** sin cambio, buscado y confirmado — rama (a) índice oficial de modificaciones, nivel de fuente 1

**Regla aplicada:** §10 bis — Las pantallas en la variable de vacaciones: cuando un par unidad-corte se codifica «sin cambio confirmado», y las dos ramas que lo autorizan.

**Pasaje o pasajes de los que sale:**

> _captura, «buscado_en»_
>
> «Registro oficial de legislacion del Reino Unido, fichas de los reglamentos 13 y 13A del Working Time Regulations 1998 con su seccion «Textual Amendments» y su lista de versiones fechadas»

> _captura, pasaje citado_
>
> «Las 5,6 semanas salen de dos piezas y las dos son ANTERIORES a la ventana: el reglamento 13(1), que da cuatro semanas, fue SUSTITUIDO el 25-10-2001 por el S.I. 2001/3256; y el 13A, que anade 1,6 semanas, fue INSERTADO el 1-10-2007 por el S.I. 2007/2079. Dentro de la ventana el registro sólo lista dos cambios del reglamento 13 —26-03-2020 y 1-01-2024— y en el 13A uno, el de 2024: son el arrastre por pandemia y las reglas de horario irregular del S.I. 2023/1426, que insertan apartados nuevos y no tocan la cantidad.»

**Nota:** **Confirmado no es lo mismo que supuesto**, y el paquete los distingue: aquí se buscó la modificatoria y se comprobó que no existe o que no toca la cantidad. Un «supuesto» sólo dice que no se halló.


### V13 · Vacaciones · base semanal

**Valor publicado:** 5 días, declarada por la norma (norma)

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.


### V14 · Vacaciones · conversión a unidad común

**Valor publicado:** 5,60 semanas de derecho, o 28,0 días de trabajo sobre semana de cinco

**Regla aplicada:** §3.1 — Conversión a unidad común. La unidad común son semanas de derecho; la cifra en días de trabajo es semanas × 5.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
5,6 semanas, tal como las concede la norma
5,6000 semanas x 5 días = 28,00 días de trabajo (semana de cinco)
```

**Nota:** Las semanas de derecho **no tienen parámetro libre**. Pasar a días de trabajo sobre semana de cinco es multiplicar por cinco: un cambio de rótulo, no un supuesto.


### V15 · Vacaciones · imputación de feriados

**Valor publicado:** sin_regla_explicita

**Regla aplicada:** §4 — Imputación de feriados al período vacacional: si lo extienden o se computan contra él.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Nota:** Decide si un feriado dentro del período vacacional lo extiende o se computa contra él. En un derecho contado en días calendario, la diferencia puede valer varios días.


### V16 · Colocación · regla 1 (todo_el_derecho)

**Valor publicado:** iniciativa «trabajador»

**Regla aplicada:** §5 — Reglas de colocación en capas, y §34.2 para la resolución del desacuerdo cuando la colocación es negociada.

**Pasaje o pasajes de los que sale:**

> _literal registrado en la base_
>
> «reg 15(1) a worker may take leave on such days as he may elect by giving notice to his employer; reg 15(2) the employer may require the worker to take or not take leave on particular days by giving counter-notice; reg 15(4) counter-notice at least as many days in advance as the days of leave; reg 15(5) any right or obligation under (1)-(4) may be varied or excluded by a relevant agreement»


### V17 · Escala de antigüedad

**Valor publicado:** 2 tramos

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _literal del primer tramo_
>
> «reg 13(1) four weeks' annual leave in each leave year + reg 13A(2) 1.6 weeks additional leave; reg 13A(3) aggregate capped at 28 days»

**Aritmética:**

```
desde el mes   0 hasta 12     -> 0.0 días semanas
desde el mes  12 hasta sin fin -> 5.6 días semanas
```

**Nota:** El trabajador de referencia tiene doce meses exactos de servicio continuo; la cifra de portada es la de su tramo.
