# Suiza — apéndice de verificación

Jurisdicción de referencia: **Zúrich**  ·  código ISO3: `CHE`

> **Procedencia de este documento.** Generado automáticamente. No editar a mano.
>
> | | |
> |---|---|
> | Protocolo | `v2.27` |
> | Hash del protocolo | `bb9db022dec2e48c…` |
> | Hash de la base | `44ddb8105c321371…` |
> | Hash del generador | `71eb599cb03da0a1…` |
> | Versión publicada | `v1.0` |


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

**Cobertura de citas en esta unidad: 4 de 18 celdas traen el pasaje textual dentro del documento (22 %).** El resto de las celdas remite a
las fuentes listadas abajo, que hay que consultar en su origen. Es la limitación
principal de este apéndice y se declara arriba, no en una nota final.

## Índice de celdas

| celda | qué verifica | valor |
|---|---|---|
| V1 | Feriado · Auffahrtstag | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V2 | Feriado · Bundesfeiertag (1. August) | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V3 | Feriado · Karfreitag | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V4 | Feriado · Neujahrstag | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V5 | Feriado · Ostermontag | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V6 | Feriado · Pfingstmontag | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V7 | Feriado · Stephanstag | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V8 | Feriado · Tag der Arbeit (1. Mai) | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V9 | Feriado · Weihnachtstag | descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio» |
| V10 | Conteo de feriados, corte 2016 | 9,0 |
| V11 | Conteo de feriados, corte 2026 | 9,0 |
| V12 | Vacaciones · cantidad y unidad de conteo | 4,0 días de tipo «semanas» |
| V13 | Vacaciones · procedencia del corte 2016 | sin cambio, buscado y confirmado — rama (b) reproducción de nivel 3 más pantalla 3 |
| V14 | Vacaciones · base semanal | 5 días, declarada por la norma (norma) |
| V15 | Vacaciones · conversión a unidad común | 4,00 semanas de derecho, o 20,0 días de trabajo sobre semana de cinco |
| V16 | Vacaciones · imputación de feriados | sin_regla_explicita |
| V17 | Colocación · regla 1 (todo_el_derecho) | iniciativa «empleador» |
| V18 | Escala de antigüedad | 2 tramos |

## Fuentes citadas en este documento

| nivel | autoridad | localización |
|---|---|---|
| 1 · gaceta oficial | Loi federale du 13 mars 1964 sur le travail dans l'industrie, l'artisanat et le commerce (LTr), RS 822.11: art. 9 (duree | https://www.fedlex.admin.ch/eli/cc/1966/57_57_57/fr |
| 2 · portal gubernamental | Bundesgesetz ueber die Arbeit in Industrie, Gewerbe und Handel (Arbeitsgesetz, ArG), SR 822.11 — Art. 20a Abs. 1 | https://www.seco.admin.ch/seco/de/home/Arbeit/Personenfreizugigkeit_Arbeitsbeziehungen/Arbeitsrecht/FAQ_zum_privaten_Arbeitsrecht/freizeit-und-feiertage.html |
| 2 · portal gubernamental | Kanton Zuerich — pagina oficial de Feiertage de la administracion cantonal | https://www.zh.ch/de/wirtschaft-arbeit/arbeitsbedingungen/arbeitsssicherheit-gesundheitsschutz/arbeits-ruhezeiten/feiertage.html |
| 2 · portal gubernamental | Ruhetags- und Ladenoeffnungsgesetz del canton de Zurich (RLG), LS 822.4, de 26 de junio de 2000 — § 1 | https://www.zh.ch/de/politik-staat/gesetze-beschluesse/gesetzessammlung/zhlex-os/erlass-822_4-56-351.html |
| 2 · portal gubernamental | SECO — FAQ zum privaten Arbeitsrecht, Ferien | https://www.seco.admin.ch/seco/de/home/Arbeit/Personenfreizugigkeit_Arbeitsbeziehungen/Arbeitsrecht/FAQ_zum_privaten_Arbeitsrecht/ferien.html |
| 4 · una sola secundaria | Obligationenrecht (OR), SR 220 — Art. 329a y Art. 329c | https://www.swissrights.ch/gesetze/Artikel-329a-OR-0000-DE.php |

## Desarrollo, celda por celda

### V1 · Feriado · Auffahrtstag

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua+39 días
```


### V2 · Feriado · Bundesfeiertag (1. August)

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 08-01
```

**Nota:** UNICO feriado garantizado en toda Suiza. Art. 20a Abs. 1 ArG lo equipara a los domingos; la Constitucion federal lo declara dia nacional pagado. Todos los demas son cantonales.


### V3 · Feriado · Karfreitag

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua-2 días
```


### V4 · Feriado · Neujahrstag

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 01-01
```


### V5 · Feriado · Ostermontag

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua+1 días
```


### V6 · Feriado · Pfingstmontag

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: pascua+50 días
```


### V7 · Feriado · Stephanstag

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 12-26
```


### V8 · Feriado · Tag der Arbeit (1. Mai)

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 05-01
```

**Nota:** NO es feriado en todos los cantones suizos. Es un ejemplo directo de por que no existe calendario nacional.


### V9 · Feriado · Weihnachtstag

**Valor publicado:** descanso_pagado_obligatorio, 1,0 día(s), régimen «descanso_obligatorio»

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
clase de fecha: fecha fija, 12-25
```


### V10 · Conteo de feriados, corte 2016

**Valor publicado:** 9,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Auffahrtstag                                             1
Bundesfeiertag (1. August)                               1
Karfreitag                                               1
Neujahrstag                                              1
Ostermontag                                              1
Pfingstmontag                                            1
Stephanstag                                              1
Tag der Arbeit (1. Mai)                                  1
Weihnachtstag                                            1
----------------------------------------------------------
TOTAL                                                    9
```


### V11 · Conteo de feriados, corte 2026

**Valor publicado:** 9,0

**Regla aplicada:** §2 — Definición de feriado público y su régimen: qué cuenta como descanso pagado obligatorio y qué no.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
Auffahrtstag                                             1
Bundesfeiertag (1. August)                               1
Karfreitag                                               1
Neujahrstag                                              1
Ostermontag                                              1
Pfingstmontag                                            1
Stephanstag                                              1
Tag der Arbeit (1. Mai)                                  1
Weihnachtstag                                            1
----------------------------------------------------------
TOTAL                                                    9
```


### V12 · Vacaciones · cantidad y unidad de conteo

**Valor publicado:** 4,0 días de tipo «semanas»

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _captura, campo «literal»_
>
> «Der Arbeitgeber hat dem Arbeitnehmer jedes Dienstjahr wenigstens vier Wochen... Ferien zu gewaehren (Art. 329a Abs. 1 OR)»

**Nota:** La unidad de conteo **no se infiere**: se lee de la norma. Sin ella el número no es comparable con el de otra unidad.


### V13 · Vacaciones · procedencia del corte 2016

**Valor publicado:** sin cambio, buscado y confirmado — rama (b) reproducción de nivel 3 más pantalla 3

**Regla aplicada:** §10 bis — Las pantallas en la variable de vacaciones: cuando un par unidad-corte se codifica «sin cambio confirmado», y las dos ramas que lo autorizan.

**Pasaje o pasajes de los que sale:**

> _captura, «buscado_en»_
>
> «Reproduccion del texto del art. 329a del Código de las Obligaciones con su nota de versión oficial»

> _captura, pasaje citado_
>
> «Cuatro semanas por anio de servicio, cinco hasta los veinte anios de edad. El artículo lleva su propia nota de versión: redaccion segun la ley de 16 de diciembre de 1983, EN VIGOR DESDE EL 1 DE JULIO DE 1984. Cuarenta anos antes de la ventana.»

> _captura, pantalla 3_
>
> «Prensa suiza: el minimo sigue en cuatro semanas y los intentos de subirlo FRACASARON dentro de la ventana. La iniciativa parlamentaria 22.447, que pedia cinco semanas para todos, fue rechazada por el Consejo Nacional por 121 votos contra 68 en marzo de 2023. Es evidencia mas fuerte que el silencio: hubo intento publico, documentado, y no prospero.»

**Nota:** **Confirmado no es lo mismo que supuesto**, y el paquete los distingue: aquí se buscó la modificatoria y se comprobó que no existe o que no toca la cantidad. Un «supuesto» sólo dice que no se halló.


### V14 · Vacaciones · base semanal

**Valor publicado:** 5 días, declarada por la norma (norma)

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.


### V15 · Vacaciones · conversión a unidad común

**Valor publicado:** 4,00 semanas de derecho, o 20,0 días de trabajo sobre semana de cinco

**Regla aplicada:** §3.1 — Conversión a unidad común. La unidad común son semanas de derecho; la cifra en días de trabajo es semanas × 5.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Aritmética:**

```
4,0 semanas, tal como las concede la norma
4,0000 semanas x 5 días = 20,00 días de trabajo (semana de cinco)
```

**Nota:** Las semanas de derecho **no tienen parámetro libre**. Pasar a días de trabajo sobre semana de cinco es multiplicar por cinco: un cambio de rótulo, no un supuesto.


### V16 · Vacaciones · imputación de feriados

**Valor publicado:** sin_regla_explicita

**Regla aplicada:** §4 — Imputación de feriados al período vacacional: si lo extienden o se computan contra él.

**Pasaje textual:** _la captura no registró un pasaje literal para esta celda._ El valor descansa en las fuentes de la sección 2 del apéndice de país; un verificador tiene que ir a la norma. Es un hueco declarado, no un descuido oculto.

**Nota:** Decide si un feriado dentro del período vacacional lo extiende o se computa contra él. En un derecho contado en días calendario, la diferencia puede valer varios días.


### V17 · Colocación · regla 1 (todo_el_derecho)

**Valor publicado:** iniciativa «empleador»

**Regla aplicada:** §5 — Reglas de colocación en capas, y §34.2 para la resolución del desacuerdo cuando la colocación es negociada.

**Pasaje o pasajes de los que sale:**

> _literal registrado en la base_
>
> «Der Arbeitgeber bestimmt den Zeitpunkt der Ferien und nimmt dabei auf die Wuensche des Arbeitnehmers soweit Ruecksicht, als dies mit den Interessen des Betriebes oder Haushaltes vereinbar ist (Art. 329c Abs. 2 OR); die Ferien sind in der Regel im Verlauf des betreffenden Dienstjahres zu gewaehren, wenigstens zwei Ferienwochen muessen zusammenhaengen (Art. 329c Abs. 1)»


### V18 · Escala de antigüedad

**Valor publicado:** 2 tramos

**Regla aplicada:** §3 — Titularidad de vacaciones anuales: cantidad, unidad de conteo leída de la norma y base semanal.

**Pasaje o pasajes de los que sale:**

> _literal del primer tramo_
>
> «Der Arbeitgeber hat dem Arbeitnehmer jedes Dienstjahr wenigstens vier Wochen... Ferien zu gewaehren (Art. 329a Abs. 1 OR)»

**Aritmética:**

```
desde el mes   0 hasta 12     -> 0.0 días semanas
desde el mes  12 hasta sin fin -> 4.0 días semanas
```

**Nota:** El trabajador de referencia tiene doce meses exactos de servicio continuo; la cifra de portada es la de su tramo.
