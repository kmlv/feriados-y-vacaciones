# Tailandia — apéndice de verificación

Jurisdicción de referencia: **Bangkok**  ·  código ISO3: `THA`

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

**Cobertura de citas en esta unidad: 4 de 10 celdas traen el pasaje textual dentro del documento (40 %).** El resto de las celdas remite a
las fuentes listadas abajo, que hay que consultar en su origen. Es la limitación
principal de este apéndice y se declara arriba, no en una nota final.

## Índice de celdas

| celda | qué verifica | valor |
|---|---|---|
| V1 | Feriado · Doce (12) días tradicionales restantes de la cuota de trece — fechas designadas por el empleador | descanso_pagado_obligatorio, 12,0 día(s), régimen «descanso_obligatorio» |
| V2 | Feriado · National Labour Day (Wan Raeng Ngan Haeng Chat) | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V3 | Conteo de feriados, corte 2016 | 13,0 |
| V4 | Conteo de feriados, corte 2026 | 13,0 |
| V5 | Vacaciones · cantidad y unidad de conteo | 6,0 días de tipo «habil» |
| V6 | Vacaciones · procedencia del corte 2016 | sin cambio, buscado y confirmado — rama (b) reproducción de nivel 3 más pantalla 3 |
| V7 | Vacaciones · base semanal | 6 días, declarada por la norma (norma) |
| V8 | Vacaciones · imputación de feriados | sin_regla_explicita |
| V9 | Colocación · regla 1 (todo_el_derecho) | iniciativa «empleador» |
| V10 | Escala de antigüedad | 2 tramos |

## Fuentes citadas en este documento

| nivel | autoridad | localización |
|---|---|---|
| 2 · portal gubernamental | Labour Protection Act, B.E. 2541 (1998), secciones 23, 28 y 29 - traduccion oficial de la Office of the Council of State | https://www.vertic.org/media/National%20Legislation/Thailand/TH_Labor_Protection_Act.pdf |
| 3 · secundarias concordantes | Labour Protection Act, B.E. 2541 (1998) — sections 28, 29, 30, 56, 64 | https://www.vertic.org/media/National%20Legislation/Thailand/TH_Labor_Protection_Act.pdf |
| 4 · una sola secundaria | Novelas de la Labour Protection Act: No. 6 B.E. 2560 (2017), No. 7 B.E. 2562 (2019), No. 8 B.E. 2566 (2023) | https://ilawasia.com/blogs/labour-protection-act-thailand |
| 5 · terciaria | Resoluciones del Consejo de Ministros sobre vanyut ratchakan (feriados oficiales) y lista de feriados de instituciones f | https://www.bangkokpost.com/thailand/general/3132730/thailand-declares-5day-new-year-holiday-to-boost-tourism-economy |

## Desarrollo, celda por celda

### V1 · Feriado · Doce (12) días tradicionales restantes de la cuota de trece — fechas designadas por el empleador

**Valor publicado:** descanso_pagado_obligatorio, 12,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2.4 — Clase de regla de fecha, y §35 para las reglas condicionales y la cuota designada.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: cuota de 12.0 días designados por el empleador de: Dias tradicionales, religiosos y locales de observancia reconocida; el empleador designa doce de ese conjunto tras consultar la practica del establecimiento (Labour Protection Act B.E. 2541, s. 29)
```

**Nota:** RESUELTO. La ley nombra UN feriado y deja doce dias a designacion del empleador dentro de un conjunto tradicional. No es `delegada_a_jurisdiccion_local` —no la fija la jurisdiccion sino el empleador— ni `remision_normativa`, porque no hay una norma unica a la que remitir. La clase nueva registra la CANTIDAD y el CONJUNTO, sin fechas. Omitirlo dejaba el conteo tailandes en 1 contra los 13 del antecedente, que era la mayor discrepancia de una sola unidad del dataset.


### V2 · Feriado · National Labour Day (Wan Raeng Ngan Haeng Chat)

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2.4 — Clase de regla de fecha, y §35 para las reglas condicionales y la cuota designada.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: remite a: Determinacion del Ministro de Trabajo bajo la s.29 parrafo 1 de la Labour Protection Act B.E. 2541; en la practica el 1 de mayo
```

**Nota:** Unico dia que la ley nombra. Su FECHA no esta en la ley: vive en la determinacion ministerial. Es el mismo mecanismo que el feriado electoral mexicano, cuya fecha vive en la ley electoral.


### V3 · Conteo de feriados, corte 2016

**Valor publicado:** 13,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Doce (12) días tradicionales restantes de la cuota d    12
National Labour Day (Wan Raeng Ngan Haeng Chat)          1
----------------------------------------------------------
TOTAL                                                   13
```


### V4 · Conteo de feriados, corte 2026

**Valor publicado:** 13,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Doce (12) días tradicionales restantes de la cuota d    12
National Labour Day (Wan Raeng Ngan Haeng Chat)          1
----------------------------------------------------------
TOTAL                                                   13
```


### V5 · Vacaciones · cantidad y unidad de conteo

**Valor publicado:** 6,0 días de tipo «habil»

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _captura, campo «literal»_
>
> «The employee who has worked consecutively for one year shall have the right to the annual holiday for not less than six working days a year (s.30)»

**Nota:** La unidad de conteo **no se infiere**: se lee de la norma. Sin ella el número no es comparable con el de otra unidad.


### V6 · Vacaciones · procedencia del corte 2016

**Valor publicado:** sin cambio, buscado y confirmado — rama (b) reproducción de nivel 3 más pantalla 3

**Regla aplicada:** §10 bis — Las pantallas en la variable de vacaciones: cuando un par unidad-corte se codifica «sin cambio confirmado», y las dos ramas que lo autorizan.

**Pasaje o pasajes de los que sale:**

> _captura, «buscado_en»_
>
> «Texto de la Labour Protection Act (no. 9) B.E. 2568 reproducido del Boletin Oficial —vol. 142, seccion 74 Kor, 7 de noviembre de 2025— leido artículo por artículo, mas la referencia a la (no. 7) B.E. 2562»

> _captura, pasaje citado_
>
> «TRES reformas de la ley en la ventana, no dos como escribi primero: la n.o 7 B.E. 2562 (2019), la n.o 8 B.E. 2566 (2023) sobre trabajo a distancia, y la n.o 9 B.E. 2568, publicada en el Boletin Oficial el 7 de noviembre de 2025. NINGUNA toca el artículo 30. De la de 2025 se leyo el articulado entero: modifica los articulos 4/1 (nuevo), 41, 41/1 (nuevo), 57/1, 57/2, 59 y 115/1 —maternidad, permiso para asistir al conyuge e inspeccion— y el artículo 30 no aparece. Lo que si hace, y va al ledger, es extender el derecho a contratistas personas fisicas de la administracion y empresas publicas por el nuevo artículo 4/1. La n.o 8 la encontro la pantalla 3, no la 2.»

> _captura, pantalla 3_
>
> «Prensa juridica tailandesa: el artículo 30 sigue en seis días, Y HAY UN PROCESO LEGISLATIVO VIVO que podria moverlo. El 24 de septiembre de 2025 la Camara de Representantes aprobo EN PRINCIPIO dos proyectos de reforma de la ley laboral y nombro comision especial; uno de ellos elevaria el derecho a diez días tras ciento veinte días de servicio. Aprobado en principio no es aprobado: al corte de 2026 rigen los seis. QUEDA EN VIGILANCIA.»

**Nota:** **Confirmado no es lo mismo que supuesto**, y el paquete los distingue: aquí se buscó la modificatoria y se comprobó que no existe o que no toca la cantidad. Un «supuesto» sólo dice que no se halló.


### V7 · Vacaciones · base semanal

**Valor publicado:** 6 días, declarada por la norma (norma)

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.


### V8 · Vacaciones · imputación de feriados

**Valor publicado:** sin_regla_explicita

**Regla aplicada:** §4 — Imputación de feriados al período vacacional: si lo extienden o se computan contra él.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Nota:** Decide si un feriado dentro del período vacacional lo extiende o se computa contra él. En un derecho contado en días calendario, la diferencia puede valer varios días.


### V9 · Colocación · regla 1 (todo_el_derecho)

**Valor publicado:** iniciativa «empleador»

**Regla aplicada:** §5 — Reglas de colocación en capas, y §34.2 para la resolución del desacuerdo cuando la colocación es negociada.

**Pasaje o pasajes de los que sale:**

> _literal registrado en la base_
>
> «The annual holiday shall be provided in advance by the employer or upon the agreement between the employer and the employee (s.30 par. 1); the employer and employee may conclude in advance that the annual holiday may be cumulated and the unused annual holiday of each year may be cumulated for the following year (s.30 par. 3)»


### V10 · Escala de antigüedad

**Valor publicado:** 2 tramos

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _literal del primer tramo_
>
> «The employee who has worked consecutively for one year shall have the right to the annual holiday for not less than six working days a year (s.30)»

**Aritmética:**

```
desde el mes   0 hasta 12     -> 0.0 días habil
desde el mes  12 hasta sin fin -> 6.0 días habil
```

**Nota:** El trabajador de referencia tiene doce meses exactos de servicio continuo; la cifra de portada es la de su tramo.
