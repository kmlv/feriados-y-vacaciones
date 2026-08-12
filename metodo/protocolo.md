# Protocolo de medición — feriados y vacaciones anuales · v2.27

**Este archivo es el documento vigente y su nombre no lleva versión.** Las
versiones congeladas viven en `docs/archivo/02-protocolo-vX.Y.md`, son inmutables
y son las que cita `PROTOCOL_FREEZE.md`. Antes el vigente se renombraba en cada
versión y el registro apuntaba a un archivo que seguía cambiando: cuatro entradas
históricas citaban el mismo archivo mutable y su verificación fallaba. Ver §26.

Fecha: 2026-08-08. **Documento operativo único.** Supersede a v1.1, a
`05-definiciones.md` y a la v2.0 no recolectada, todos archivados.
Incorpora los tres `[blocker]` del review de la revisión cruzada sobre v2.0 (§19), la banda
de colocación (§4.3) y la grilla de antigüedad (§3.2.1).

Alcance: las 47 unidades del grupo fijo, dos cortes — **2016** y **2026** — y
ambas variables. El universo de unidades es input cerrado y no se discute aquí.

---

# Parte 0 · Qué cambia respecto de v1.1

| | v1.1 | v2.0 |
|---|---|---|
| Variables | Feriados; vacaciones diferida | **Ambas, mismo diseño** |
| Constructos de feriados | Tres (A, B, C) | **Dos columnas × nominal/efectivo** — subsume a las tres |
| Frontera entre variables | Diferida | **Resuelta**: regla de imputación, total calculado |
| Modelo de datos | Uno | **Dos módulos de hechos sobre capa de derecho común** |
| Tratamiento de rangos | Límite inferior | **Resuelto por el trabajador de referencia** |
| Piso supranacional | No contemplado | **Campo propio + mínimo efectivo derivado** |

La reconciliación de constructos, que quedaba pendiente: lo que v1.1 llamaba
**A** es `feriados_pagados_obligatorios` nominal; **B** es
`feriados_nacionales_reconocidos` nominal; **C** es la versión efectiva de
cualquiera de las dos. No se pierde nada y se gana que la columna principal es
inequívoca.

---

# Parte I · Definiciones

## 1. Núcleo común

### 1.1 Trabajador de referencia

> Asalariado **formal**, **tiempo completo**, **sector privado**, con
> **exactamente doce meses de servicio continuo cumplidos** al 1 de enero del
> corte, **semana de cinco días**, en la **ciudad más poblada** de la unidad,
> **no cubierto** por convenio colectivo ni régimen sectorial especial, en
> empresa que **no presta servicios esenciales**.

La antigüedad se fija en **doce meses exactos**, no en "más de un año". La
diferencia importa: umbrales legales situados en uno, dos, cinco o diez años
producen valores distintos, y "más de un año" no determina cuál aplica. Con doce
meses cumplidos se satisfacen los umbrales de un año y no los superiores.

**Además de fijar el alcance, resuelve los rangos.** El material previo codificaba
el límite inferior cuando la fuente reportaba un intervalo, y él mismo advierte
que eso sesga sistemáticamente hacia abajo a los regímenes federales y a los que
escalonan por antigüedad. Con un trabajador de referencia definido, el intervalo
**desaparece**: hay un único valor aplicable. Se registra igualmente el rango
completo y su causa — `federal` · `antiguedad` · `sector` — pero el valor
codificado ya no es una convención, es el que corresponde al caso.

### 1.2 De jure, no de facto

Se mide lo que la ley obliga, no el cumplimiento. En economías con informalidad
alta la cobertura efectiva es minoritaria. Es una **limitación declarada del
constructo**, no un defecto corregible con más verificación.

### 1.3 Unidad de medida

**Días laborables**, normalizados a semana de cinco días, para **ambas
variables**. Que compartan unidad es lo que permite compararlas y sumarlas.

### 1.4 Alcance geográfico

**Nacional.** Lo subnacional se excluye del principal y se registra aparte, con
promedio ponderado por población como variable secundaria donde aplique.

### 1.5 Ancla temporal

**Norma vigente al 1 de enero** de 2016 y de 2026. Tolerancia **±1 año** sobre
el ancla 2016 si no hay fuente admisible; fuera de banda, `NA` con causa. La
`fecha_efectiva_de_medicion` se registra **siempre**, aunque coincida con el
ancla, y el dataset publica la distribución de desviaciones.

## 2. Feriados

### 2.1 Dos columnas

| Columna | Cuenta |
|---|---|
| `feriados_pagados_obligatorios` | Días que la ley obliga a conceder **con goce de haber** |
| `feriados_nacionales_reconocidos` | Días reconocidos como feriado nacional, con independencia del mandato de pago |

La **primera es la principal**, y es la comparable con vacaciones: ambas miden
entonces un derecho remunerado. Comparar días pagados contra días de calendario
sería comparar objetos distintos.

### 2.2 Régimen de cumplimiento

Categórica por unidad y corte: descanso obligatorio · descanso salvo
requerimiento con recargo · reconocido sin mandato de pago · sin mandato
nacional. Se guarda la **tasa de recargo** cuando exista: es la única variación
de intensidad de la variable.

### 2.3 Nominal y efectivo

**Nominal** es el número que la norma reconoce, con independencia del día de la
semana. **Efectivo** son los días laborables no trabajados, calculado de forma
determinista desde el calendario. Se reportan **juntos, nunca uno en lugar del
otro**: entre 2016 y 2026 el efectivo puede diferir varios días sin que cambie
una línea de la ley.

### 2.4 Reglas de conteo

| Situación | Regla |
|---|---|
| Feriado de varios días | Cada día cuenta, si la norma suspende el trabajo esas fechas |
| Dos festividades en la misma fecha | Una **fecha**; dos **eventos jurídicos** |
| Medio día | Fracción, **sin redondear** |
| Calendario no gregoriano | Se cuenta la **titularidad**, no la fecha |

### 2.5 Exclusiones

Días sustitutorios por traslado (ya en el nominal) · puentes y días no
laborables **compensables** (hay que recuperarlos; serie aparte) · feriados
extraordinarios de una sola vez (`recurrencia = one_off`, serie aparte) ·
feriados regionales · observancias optativas y conmemoraciones sin descanso ·
cierres de sector público y feriados bancarios (columna aparte).

### 2.6 Fines de semana laborables compensatorios

Se restan **sólo del efectivo**, nunca del nominal.

## 3. Vacaciones anuales

### 3.1 Días calendario frente a días hábiles · **el punto de mayor error**

Muchos códigos dicen "treinta días" sin especificar el tipo. **Treinta días
calendario son 21,4 días hábiles** en semana de cinco días: tratar uno como el
otro produce un error del orden del 40%.

**No es hipotético, y está admitido por la fuente.** El CSV importado contiene a
la vez 6 unidades con valor 30 declaradas como 6,0 semanas y 10 unidades con
valor 22 declaradas como 4,4 semanas. Veinticinco de 130 celdas (19%) caen en el
rango 24–30, donde el número por sí solo no revela el tipo. El propio reporte
que lo acompaña reconoce: *"No se auditaron los demás países de la misma forma,
de modo que errores del mismo tipo casi con certeza permanecen en el dataset."*

**Tres campos:**

| Campo | Contenido | Origen |
|---|---|---|
| `texto_legal_dias` | Número literal de la norma | Capturado |
| `tipo_de_dia` | `calendario` \| `habil`, **leído de la norma** | Capturado |
| `dias_habiles` | Valor normalizado, **sin redondear** | **Derivado** |

Se publica `dias_habiles`; los tres van en el dataset. Publicar sólo el
convertido entierra el error y lo vuelve indetectable sin volver a la norma;
publicar sólo el literal traslada el error a cada usuario, y la comparación
internacional es donde se comete.

**El tipo se lee, no se infiere.** La pista fiable es si el propio código excluye
o no los días de descanso semanal del cómputo.

**La conversión es una convención declarada, no un hecho.** Treinta días
calendario son 21,43 hábiles *en promedio*; el valor realizado es 21 o 22 según
el día en que arranque el período. Por eso el literal queda guardado. La
conversión toma como insumo la convención de descanso semanal de la unidad, que
no es universal ni constante en la ventana; al ser derivada, se recalcula entera
si esa tabla se corrige.

### 3.2 La escala de antigüedad completa · **crítico**

El valor reportado es el que corresponde al trabajador de referencia — doce
meses cumplidos. Pero **la escala completa se captura, con estructura**.

El reporte archivado advierte que *"muchos regímenes ajustan el derecho por
tenure en lugar de mover el mínimo legal, de modo que el cambio real ocurre en
un margen que la codificación de nivel de entrada no captura."* Si eso es cierto,
la rigidez observada **no mide rigidez: mide que se miró el lugar equivocado**.

**Dos campos descriptivos no bastan.** Un `regla_de_progresion` en texto libre
más un `dias_maximo` no reconstruyen una escala de varios tramos: dos regímenes
con idéntico nivel de entrada e idéntico máximo pueden tener trayectorias
distintas, y una reforma que mueva un tramo intermedio sería invisible en ambos
campos.

Por eso la escala es una **tabla de tramos versionados**, no un atributo:

**`escala_antiguedad`** — `vacaciones_version_id`, `antiguedad_desde_meses`,
`antiguedad_hasta_meses`, `quantum`, `tipo_de_dia`, `vigencia_desde`/`hasta`,
más su vínculo de evidencia. El nivel del trabajador de referencia es el tramo
que contiene los doce meses; no se captura aparte, **se deriva**.

Cualquier cambio en cualquier tramo es un evento del ledger de tipo
`cambio_de_escala_de_antiguedad`, mueva o no el tramo de entrada.

#### 3.2.1 Grilla de antigüedad: 1, 5 y 10 años · **decidido por el principal**

Además del trabajador de referencia, la salida principal reporta el quantum y su
`tipo_de_dia` en **tres puntos de antigüedad: 1, 5 y 10 años**. Los tres se
**derivan** de `escala_antiguedad`; no se capturan.

**Por qué, y no es "más columnas".** El riesgo central de §3.2 es que las
reformas hayan ocurrido en la escala y no en el nivel de entrada, lo que haría
de la rigidez un artefacto. La grilla **es el test de esa hipótesis**: si el
nivel de entrada está plano y los valores a 5 y 10 se movieron, el margen de
reforma queda localizado y el artefacto sospechado pasa a ser hallazgo medido.

**Base de antigüedad** *(hecho faltante detectado por la revisión cruzada; no lo habíamos
visto)*. "Diez años de antigüedad" es ambiguo entre servicio continuo con el
empleador actual, servicio reconocido de empleadores previos, y experiencia
laboral total. El trabajador de referencia fija servicio continuo pero no dice
nada del historial previo acreditable. Se resuelve por las dos vías a la vez:
campo `base_antiguedad` con su regla de reconocimiento, y declaración explícita
de que los tres puntos suponen **N años con el mismo empleador y cero servicio
previo acreditable**.

**Convención de frontera.** Los tramos usan intervalos `[desde, hasta)`, sin
solapamientos ni huecos, con el último abierto. El punto de la grilla se define
como **inmediatamente después de cumplir** 1, 5 o 10 años.

**El operador de la fuente se conserva, no se redondea.** Una regla literal de
"más de cinco años" no equivale sin más a `desde_meses = 60`: campo
`operador_frontera` con el literal normativo. Si un ordenamiento define
fronteras submensuales, los meses enteros no alcanzan y el tramo se almacena con
granularidad de fecha.

**Nombre de las columnas.** Llevan la advertencia incorporada, siguiendo lo que
ya aprendimos con la cota:
`vacaciones_vigentes_a_N_anos_antiguedad_ley_<corte>`.

#### 3.2.2 Corte transversal, no cohorte · **advertencia estructural**

En el corte 2016, el valor a diez años **no es** la trayectoria de quien entró
en 2006. Es la **norma vigente en 2016 evaluada en un trabajador hipotético**
con diez años de antigüedad. Son objetos distintos y se leen igual en una tabla.

La revisión de diseño calificó este riesgo de muy alto: un corte transversal evaluado a distintas
antigüedades *"casi siempre se lee como la trayectoria de un trabajador"*. La
advertencia viaja en el nombre de la variable y en su metadata, no en una nota:
las notas no viajan con el dato.

#### 3.2.3 Qué significa que los tres valores coincidan · **quinto reparo de la revisión cruzada**

Yo iba a llamarlo "degeneración", por analogía con la banda. La revisión cruzada tiene razón
en que es incorrecto: que 1, 5 y 10 coincidan **no implica** ausencia de
escalonamiento. Puede haber saltos a los 2, 3, 15 o 20 años que la grilla no ve.

Son dos hechos distintos y se publican por separado:

| Campo | Qué dice | De dónde sale |
|---|---|---|
| `sin_diferencia_en_grilla_1_5_10` | Los tres puntos coinciden | De la grilla |
| `escala_sin_escalonamiento` | El ordenamiento no escalona en absoluto | De la **tabla completa** |

Y como salvaguarda contra la arbitrariedad de la grilla, se publican también el
**número de tramos** y **los umbrales exactos**, derivados de la tabla. Así el
resultado no depende de los puntos que elegimos nosotros.

#### 3.2.4 La banda de colocación no se replica en la grilla

La salida principal deriva en 1, 5 y 10 años **sólo** `quantum` y `tipo_de_dia`.
La banda de §4.3 **no** se computa en los tres puntos por defecto.

Razón, de la revisión cruzada: mezclaría el test de reformas por antigüedad con una estimación
distinta y triplicaría columnas sin responder mejor ninguna de las dos
preguntas. Queda disponible como análisis secundario si el principal lo pide.

*Nota de desacuerdo:* la revisión de diseño consideró suficiente hacer obligatorios los dos campos
descriptivos; la revisión cruzada sostuvo que sin estructura el campo no sirve. Se adopta la
posición de la revisión cruzada.

### 3.3 Período de calificación

Servicio mínimo para devengar. Si excede un año, el valor del trabajador de
referencia es **`NA` por no aplicable**, no cero. Confundirlos sesga la media
hacia abajo.

### 3.4 Piso supranacional

Buena parte del universo está amarrada a un mínimo supranacional que no se
mueve — el Convenio 132 de la OIT fija tres semanas; la Directiva europea de
tiempo de trabajo, cuatro. Eso explica el agrupamiento en veinte días visible en
los datos importados, y significa que para esas unidades "sin cambio" es el
resultado estructuralmente esperado.

**No es un atributo, es una tabla**, porque `max(nacional, supranacional)` sólo
es computable después de normalizar ambos a la misma unidad y de acreditar que
el instrumento estaba vigente y era aplicable a esa jurisdicción en ese corte.
Esas dos cosas son hechos con evidencia, no supuestos dentro de una función.

**`instrumento_supranacional`** — `instrumento`, `jurisdiccion_id`,
`vigencia_desde`/`hasta`, `piso_dias`, `tipo_de_dia`, `ratificado_o_vinculante`,
vínculo de evidencia.

Derivado: `minimo_efectivo = max(nacional_normalizado,
supranacional_normalizado)`, calculado sólo sobre instrumentos con
aplicabilidad y vigencia acreditadas. Se publican ambos; el análisis elige.

### 3.5 Exclusiones

Licencias por enfermedad, maternidad, paternidad y permisos especiales ·
mejoras por convenio colectivo o contrato individual · días adicionales por
condiciones particulares (nocturno, insalubre, discapacidad, edad) salvo que
apliquen al trabajador de referencia.

### 3.6 Advertencia de interpretación · **obligatoria en toda publicación**

Un delta cero en vacaciones **no significa** que no pasó nada con el descanso
remunerado. El barrido archivado documenta que el margen de expansión del
período se desplazó a **licencia por enfermedad y licencias familiares pagadas**,
que quedan fuera de esta variable por definición. Leer el cero como inmovilidad
del descanso remunerado es un error de interpretación del período, y hay que
prevenirlo en el propio dataset.

## 4. La frontera entre ambas variables

Hay ordenamientos donde los feriados que caen dentro del período vacacional **se
computan contra él**, y otros donde lo **extienden**.

Campo obligatorio: `imputacion_feriados_a_vacaciones` ∈ { `se_computan_contra` ·
`extienden` · `sin_regla_explicita` }.

### 4.1 El total, definido como estimando

La versión anterior decía que la superposición se calculaba "de forma
determinista desde la duración del período y el número de feriados". **Eso es
falso** y la revisión cruzada lo marcó: dos trabajadores con igual duración de vacaciones e
igual número anual de feriados pueden tener superposición distinta según cuándo
tomen el período. Falta la fecha de inicio.

Como no observamos fechas de inicio reales, el total **no es una cantidad
observada: es una esperanza bajo una distribución declarada**. Y hay que
declararla entera, o no es reproducible.

**Definición versionada:**

> `superposicion_esperada` = número esperado de **ocurrencias observadas** de
> feriado que caen dentro del período vacacional, cuando la fecha de inicio se
> distribuye **uniformemente sobre los días hábiles del año del corte**, y el
> período se consume en días hábiles consecutivos según el régimen de jornada de
> la unidad.

Cuatro cosas quedan fijadas por esa frase, y las cuatro son elecciones: se usan
ocurrencias **observadas**, no nominales, porque la pregunta es si el día se
consume realmente; la distribución de inicio es **uniforme sobre días hábiles**;
el horizonte es el año del corte; y el consumo es en días hábiles consecutivos.

La fórmula se publica con el dato y lleva número de versión propio.

### 4.2 Cómo se compone el total

| `imputacion_feriados_a_vacaciones` | Total |
|---|---|
| `extienden` | feriados pagados + vacaciones |
| `se_computan_contra` | feriados pagados + vacaciones − `superposicion_esperada` |
| `sin_regla_explicita` | **`NA`**, más un intervalo de sensibilidad calculado bajo los dos supuestos |

**`sin_regla_explicita` no se trata como `extienden`.** Jurídicamente no son lo
mismo, y asimilarlos es una imputación no identificada que se leería como dato.
Va como `NA` y se reporta el intervalo entre las dos lecturas posibles, que es
información honesta sobre cuánto no sabemos.

**Nunca suma simple.** Una advertencia metodológica no basta: no viaja con la
cifra cuando alguien la cita.

### 4.3 Banda de colocación · **decidido por el principal**

§4.1 supone una fecha de inicio uniforme: un trabajador que no planifica. Es una
suposición arbitraria y conviene acotarla por los dos lados. El mismo estimando
se calcula bajo **tres supuestos de colocación**:

| Serie | Supuesto de colocación |
|---|---|
| `total_minimo` | Colocación que **minimiza** los días pagados no trabajados |
| `total_esperado` | Fecha de inicio uniforme sobre los días hábiles del año (§4.1) |
| `cota_estilizada_colocacion_no_es_derecho` | Colocación que **maximiza**, sujeta a jornada, feriados y particiones admisibles (§4.3.4) |

**Objetivo de la maximización, fijado con precisión:** **días de trabajo
programados, pagados y no trabajados**. La formulación corta —"días pagados no
trabajados"— es ambigua, porque incluiría los días de descanso semanal que §4.3
trata como consumidos dentro del período. El objetivo cuenta sólo días que, sin
vacaciones ni feriado, habrían sido de trabajo programado.

**No** días consecutivos libres. Son objetivos distintos: la estrategia de
puentes concentra el descanso pero no añade un solo día. Si interesa medir
concentración, será una métrica aparte.

**El máximo es normativo, no conductual.** Es lo que las reglas admiten, no lo
que la gente hace.

**Sujeto a qué, exactamente — pendiente de decisión del principal.** La revisión cruzada marcó
que "sujeto a las restricciones legales" no está definido mientras no se
represente el **dominio de fechas admisibles**: ventanas y plazos de disfrute,
fechas excluidas, cierres obligatorios, reglas de aviso y aprobación. Dos
ordenamientos con idénticos campos de fraccionamiento pueden permitir
calendarios distintos y producir máximos distintos. Hay dos salidas y son
excluyentes; ver §4.3.4.

#### 4.3.0 Particiones admisibles · **corrección de la revisión cruzada, aceptada**

Los escalares de fraccionamiento no representan el conjunto factible.
`bloque_minimo_dias` no dice si el mínimo aplica a **cada** fracción, sólo a un
bloque principal, o a un número determinado de bloques. "Al menos un bloque de
catorce días y el resto en unidades de un día" y "toda fracción de al menos
catorce días" tienen **los mismos escalares y conjuntos factibles distintos** —
y por tanto máximos distintos.

Por eso el fraccionamiento es una **tabla de particiones admisibles
versionada**, no cuatro escalares:

**`particiones_admisibles`** — `vacaciones_version_id`, `vigencia_desde`/`hasta`,
`numero_de_bloques` (o su rango), y por posición o clase de bloque:
`cardinalidad`, `tamano_min`, `tamano_max`, `tipo_de_dia`, `obligatorio`,
`requiere_consentimiento`. Más su vínculo de evidencia.

Los escalares de publicación —bloque mínimo, número máximo de fracciones— se
**derivan** de esta tabla; no se capturan.

#### 4.3.1 La amplitud es el resultado, no los extremos

> `amplitud_de_colocacion = cota_estilizada_colocacion − total_minimo`

Mide **cuánto del resultado depende de la discrecionalidad para programar**. No
es una característica del trabajador: es una característica del ordenamiento —
flexibilidad normativa. Ninguna fuente previa la mide, y es probablemente la
contribución más original que sale de esta métrica.

#### 4.3.2 Degeneración de la banda · **caracterización corregida**

La banda colapsa cuando la función objetivo es **constante sobre el conjunto
factible**. Eso ocurre en más casos de los que yo había declarado, y la revisión cruzada tenía
razón en que mi caracterización era suficiente pero no necesaria.

`banda_degenerada` **no se declara por regla: se deriva como `max == min`
después de optimizar**, y se acompaña de una `causa_de_degeneracion`:

| Causa | Cuándo |
|---|---|
| `estructural_por_regla` | Conteo en días hábiles **y** feriados que extienden: veinte hábiles son veinte hábiles se empiece cuando se empiece |
| `estructural_por_ciclo` | Derecho en días calendario que cubre un número **entero de ciclos de jornada** — siete días bajo semana estable consumen los mismos hábiles desde cualquier inicio |
| `calendario_realizado` | `se_computan_contra` con cero ocurrencias observadas, o con superposición constante en todas las colocaciones factibles |
| `factible_singleton` | Un único calendario admisible, por cierre obligatorio o calendario fijo |

**Corrección que me toca reconocer.** Yo afirmé que la banda "sólo muerde" en
regímenes de días calendario o de descuento de feriados. Es falso: el caso
`estructural_por_ciclo` es de días calendario y **no muerde**. Un derecho de
siete días calendario bajo semana de cinco días consume cinco hábiles empiece
donde empiece.

`habil + extienden` se conserva como **condición suficiente y predicción
principal**, no como la condición. La distribución de causas de degeneración se
publica como resultado: dice dónde la flexibilidad normativa importa y por qué
no importa donde no importa.

#### 4.3.4 Alcance de la cota · **decidido: estilizada**

La revisión cruzada marcó que "sujeto a las restricciones legales" no está definido mientras
no se represente el dominio de fechas admisibles. La alternativa era capturar
una regla de colocación canónica —ventanas de disfrute, plazos, fechas
excluidas, cierres obligatorios, reglas de aviso—, que es una **segunda capa de
recolección** cuyos hechos en buena parte no están en fuentes secundarias.

**Decisión del principal: cota estilizada, y renombrada.** La serie deja de
llamarse "máximo normativo" porque no lo es.

**Qué respeta la cota:** régimen de jornada de la unidad; ocurrencias observadas
de feriado; particiones admisibles de §4.3.0; y la regla de imputación de §4.

**Qué ignora, y por tanto qué puede sobreestimar:** ventanas y plazos de
disfrute, fechas excluidas, cierres obligatorios de empresa, y reglas de aviso o
aprobación. Donde esas restricciones existan, la cota real es menor.

Esa lista de exclusiones se publica **junto a la columna**, no en un anexo. Es
lo que impide que la cota se lea como un derecho.

#### 4.3.3 Quién controla el momento · **la restricción que más ata**

En buena parte de los ordenamientos de tradición civil el empleador fija o
aprueba el calendario vacacional. Suponer elección libre sería suponer que no
existe la restricción más atante, y el máximo no sería sólo inalcanzable: sería
**legalmente indisponible**.

> **SUPERSEDIDA POR §24.** Esta sección definía un campo `control_del_momento`
> como enumerado de cinco valores. La búsqueda dirigida y dos reataques lo
> invalidaron: presuponía que alguien decide, y aplanaba reglas en capas que
> existen en el derecho revisado. **La especificación vigente y única es §24.**
> Se conserva este párrafo con la marca, y no su contenido, porque borrarlo
> ocultaría por qué cambió.

---

# Parte II · Esquema de datos

Dos módulos de hechos sobre una **capa de derecho común**. Los feriados son un
conjunto de eventos fechados; las vacaciones son un escalar de titularidad. No
comparten realización y forzarlos a un modelo único obligaría a inventarle
fechas a una variable que no las tiene.

## 5. Capa común

**`jurisdicciones`** — `jurisdiccion_id`, unidad, nivel, padre, vigencia. Todo
lo demás referencia `jurisdiccion_id`, nunca la unidad directamente.

### 5.1 Identificación polimórfica de hechos

Toda fila de hecho versionado — `feriado_version`, `regla_fecha_version`,
`ocurrencias`, `vacaciones_version`, `escala_antiguedad`, `regimen_jornada`,
`instrumento_supranacional` — lleva un identificador de versión propio y estable.
Las tablas de la capa común los referencian por el par
(`hecho_tipo`, `hecho_id`).

Sin esto, las relaciones de abajo dicen enlazar algo que no está identificado.

**`evidencia`** — relación **hecho ↔ fuente**, versionada.
Clave: (`hecho_tipo`, `hecho_id`, `fuente_id`). Cardinalidad: **todo hecho tiene
al menos un vínculo**; un vínculo prueba **exactamente una** versión de hecho.
Una norma prueba el derecho y una proclamación distinta prueba la fecha
realizada: son vínculos separados, no columnas de la misma fila.

Nueve campos por vínculo: fuente, URL, versión archivada, autoridad,
jurisdicción, fecha de norma, fecha de verificación, nivel de fuente, revisor.

**`eventos_reforma`** — `reforma_id`, `tipo` ∈ { creación · abolición ·
suspensión · restitución · sustitución · extensión de cobertura · **cambio de
escala de antigüedad** · **reforma de reglas sin cambio de quantum** },
`fecha_anuncio`, `fecha_promulgacion`, `vigencia_desde`, `causa`,
`permanente_o_temporal`, cita.

**`reforma_versiones`** — relación reforma ↔ versiones afectadas.
`reforma_id`, `hecho_tipo`, `hecho_id`, `rol` ∈ { `anterior` · `nuevo` }.

Esta tabla restituye una garantía que v1.1 tenía y que la consolidación había
perdido: `estado_anterior` y `estado_nuevo` como columnas sueltas **no dicen de
qué variable, de qué derecho ni de qué versión son estado**. Con la relación
explícita, una reforma puede afectar versiones de feriados, de vacaciones o de
ambas, y queda dicho cuáles. Los deltas no se guardan: se derivan.

**`mediciones`** — `hecho_tipo`, `hecho_id`, `corte` ∈ { 2016 · 2026 },
`fecha_efectiva_de_medicion`, `estado_verificacion`.

Restituye la segunda garantía perdida. §1.5 exige registrar la fecha efectiva
**siempre**, pero en la consolidación desapareció de las tablas. Sin ella la
tolerancia de ±1 año es una promesa no auditable y la distribución de
desviaciones no se puede publicar. Al vivir en una tabla propia, cubre los dos
módulos de forma uniforme.

## 6. Módulo feriados

**`feriado_version`** — `feriado_id`, `jurisdiccion_id`, `sector`,
`vigencia_desde`/`hasta`, `nombre_oficial`, `categoria`, `recurrencia`,
`regimen`, `tasa_recargo`, `duracion_dias`, `cobertura`, `elegibilidad`.

**`regla_fecha_version`** — `feriado_version_id`, `vigencia_desde`,
`sistema_calendarico`, `clase_de_regla`, **`especificacion`** como expresión
ejecutable con parámetros, `regla_de_traslado_aplicable`. La regla de traslado
puede variar por feriado; la de `regimen_jornada` es sólo el defecto.

**`ocurrencias`** — **una fila por fecha**, sin excepciones.
`feriado_version_id`, `corte`, `indice_en_periodo`, `fecha_nominal`,
`fecha_observada`, `base_de_sustitucion`, `duracion_horas`
(`derivada` | valor | `NA` — son tres cosas distintas),
`cayo_en_descanso_semanal`, `overlap_group`, `origen`, `determinacion_id`.

**`determinaciones_fecha`** — por ocurrencia: `fecha_legal_original`, calendario
y era, `fecha_gregoriana_local`, `zona_horaria`, `metodo_de_conversion`,
`certeza`, autoridad, `proclamacion_id` (nullable), fuente.

**`regimen_jornada`** — por jurisdicción y sector, con **intervalos fechados**:
días de descanso semanal, regla de traslado por defecto, horas programadas por
día. No puede ser por año: una reforma de mitad de año quedaría irrepresentable.

**`eventos_compensatorios`** — puentes y descansos declarados laborables,
vinculados al evento que compensan. Permite reportar bruto, compensación y neto
por separado.

## 7. Módulo vacaciones

**`vacaciones_version`** — `vacaciones_version_id`, `jurisdiccion_id`, `sector`,
`vigencia_desde`/`hasta`, `texto_legal_dias`, `tipo_de_dia`,
`periodo_de_calificacion`, `rango_min`, `rango_max`, `causa_del_rango`,
`imputacion_feriados_a_vacaciones`, y los cuatro campos de la banda de
colocación (§4.3): `fraccionamiento_permitido`, `bloque_minimo_dias` con su
`bloque_minimo_tipo_de_dia`, `numero_maximo_de_fracciones`,
`control_del_momento` — **campo eliminado en §24**.

**`escala_antiguedad`** — tramos versionados (§3.2). El valor del trabajador de
referencia es el tramo que contiene los doce meses; se **deriva**, no se captura.

**`instrumento_supranacional`** — pisos con aplicabilidad y vigencia acreditadas
(§3.4).

Sin tabla de ocurrencias: la variable no tiene fechas.

## 8. Derivadas

`panel_unidad_corte` — por unidad y corte: las dos columnas de feriados en
nominal y efectivo, con y sin *one-offs*; vacaciones en `dias_habiles` y
`minimo_efectivo`; el total con regla de imputación aplicada; banderas de
calendario no gregoriano, federalismo, suspensión y rango; y
`estado_verificacion` por celda.

Producido por **funciones explícitas y versionadas**, nunca capturado. Las
funciones se publican con el dato: publicar sólo el panel repetiría el defecto
de las fuentes terciarias que este proyecto corrige.

---

# Parte III · Evidencia y verificación

## 9. Jerarquía de fuentes

1. Ley, decreto, gaceta oficial, jurisprudencia aplicable
2. Calendario o guía oficial **contemporánea** del ministerio competente
3. Repositorios jurídicos intergubernamentales que reproduzcan texto y vigencia
4. Bases secundarias documentadas y literatura
5. Prensa reputada, sólo para localizar extraordinarios
6. Enciclopedias colaborativas y librerías de calendario: **sólo descubrimiento**

**Las fuentes comerciales están activamente equivocadas, no sólo
desactualizadas.** El archivo documenta que guías de nómina global publicadas
*durante* la ventana seguían reportando un valor pre-reforma **tres años
después** del cambio. No es un error viejo ni marginal.

Usar una librería de calendario como constructora del panel confunde
**reproducibilidad del software con validez jurídica**.

## 10. Las tres pantallas

Un par unidad-corte se codifica `sin_cambio_confirmado` **sólo si las tres
coinciden**. Cualquier discrepancia va a adjudicación humana.

1. **Diff de fuente terciaria** entre años, versión pinneada. Detecta
   candidatos; **no es evidencia**.
2. **Legislación**: base intergubernamental de legislación laboral y gaceta
   oficial, filtrada a verbos de crear · abolir · suspender · trasladar ·
   restituir · **escalonar**.
3. **Prensa en idioma local**, con traducción automática, citando y archivando
   el original.

**Por qué la pantalla 1 no puede ir sola — evidencia concreta del archivo.** En
la reconstrucción importada, la librería codificaba los domingos de una unidad
como feriados legales: **cincuenta entradas espurias** que hubo que retirar a
mano. Un panel construido sobre esa fuente sin las otras dos pantallas habría
reportado una unidad con más de sesenta feriados.

## 10 bis. Las pantallas en la variable de vacaciones

La pantalla 1 **no es aplicable** a la variable de vacaciones: no existe fuente
terciaria que publique el derecho vacacional por año y unidad, y la sustitución
por una base secundaria puntuada se probó y se descartó **por rendimiento
medido** —un candidato en 45, falso, y ceguera ante una reforma verificada dentro
de su propia ventana—.

Para esta variable, un par unidad-corte se codifica `sin_cambio_confirmado`
cuando:

**a)** la pantalla 2 se satisface con **índice oficial de modificaciones del
artículo, nota de versión, o comparación de textos consolidados fechados**, de
nivel de fuente 1 o 2; **o bien**

**b)** la pantalla 2 se satisface con reproducción de nivel 3, o descansa en un
negativo sin índice, **y además** coincide la pantalla 3.

**Una ausencia sólo es evidencia si la fuente registra las presencias.** Antes de
admitir la falta de nota de modificación como prueba, se comprueba que el
documento consultado anote modificaciones **en algún sitio**. El consolidado en
PDF del boletín español es el precedente: no anota ninguna, y su silencio sobre
el artículo de vacaciones no significaba nada.

**Por qué el escalón y no una regla plana.** La regla de tres existe por
redundancia contra la ceguera de una sola fuente. Cuando la pantalla 2 se
satisface con un índice oficial, eso **no es un proxy**: es la autoridad
declarando qué tocó el artículo y cuándo, y pedirle además prensa local no añade
información. Cuando descansa en una reproducción de nivel 3 o en un «no hallé
reforma», la redundancia sí hace falta.

**Lo que esta enmienda evita.** Sin ella, ninguna unidad puede alcanzar
`sin_cambio_confirmado` en vacaciones **por bien que se busque**, porque una de
las tres condiciones es imposible de satisfacer. El estado quedaría con cero
filas para siempre — declarado en el esquema y muerto en la práctica, que es la
figura que este proyecto ha encontrado tres veces en un solo día.

**Y no reclasifica nada por sí sola.** Adoptar la regla no convierte en (a) ni en
(b) ninguna celda ya capturada: el reparto es trabajo de codificación y se hace
unidad por unidad.


## 11. Semilla del ledger — importada del archivo

El reporte archivado dejó una lista explícita de **candidatos pendientes de
auditar**, con probabilidad *a priori* alta de contener reforma no verificada:
reestructuraciones de códigos laborales completos, reescrituras de régimen
laboral privado, reformas asociadas a sistemas de contratación de migrantes,
códigos de trabajo nuevos, reformas de jornada que pudieron tocar el mínimo
vacacional de forma indirecta, y ajustes posteriores a programas de ajuste.

Esa lista entra como **semilla priorizada de las pantallas 2 y 3**, no como
hallazgo. Es trabajo ya hecho que no hay que repetir.

## 12. Cero, ausencia e incertidumbre

`0` sólo cuando una fuente competente lo confirma bajo la definición. `NA` con
causa para desconocido, no cubierto, no aplicable o en conflicto. Con cero por
defecto, **más esfuerzo de investigación sobre una unidad se parece a una
reforma**: el esfuerzo de codificación entra en la variable dependiente.

## 13. Exclusiones en tres niveles

Marco maestro — nunca borra nada. Dataset medido — registra estado y causa del
faltante. Muestra de cada estimación — regla pre-registrada, diagrama de
*attrition*, y sensibilidad cuando la exclusión pueda correlacionar con el
resultado. Lo prohibido no es excluir: es **excluir sin registro**.

## 14. Fiabilidad

Doble codificación ciega del 15–20% y reporte de la tasa de acuerdo. Línea base
disponible y publicable: dos sistemas codificando el mismo concepto para el
mismo año coincidieron exactamente en **24%**, correlación 0,57.

---

# Parte IV · Divergencias con el material importado

Registradas para que nadie reutilice esos datos suponiendo que aplican nuestras
definiciones. **No son equivalentes y no se pueden mezclar sin conversión.**

| Punto | Material importado | v2.0 |
|---|---|---|
| Medios días | Excluidos | Cuentan como fracción |
| Cierres de gobierno | Sumados al conteo principal cuando la fuente los soporta | Columna aparte |
| Rangos | Límite inferior | Valor del trabajador de referencia |
| Feriados extraordinarios | Incluidos en la cifra principal | Serie aparte |
| Columna histórica | Imputada por persistencia | Medida, o `NA` |
| Compensatorios | Restados del conteo único | Restados sólo del efectivo |

---

# Parte V · Estado y procedimiento

## 15. Congelamiento

Hash y fecha en [`PROTOCOL_FREEZE.md`](PROTOCOL_FREEZE.md), sin registro público
externo. Todo cambio abre versión nueva con hash propio y **obliga a recalcular
el panel completo**: el vintage heterogéneo es exactamente lo que hace
inservibles a las fuentes previas.

## 16. Deuda de implementación, no bloqueante

Señalada por la revisión cruzada y aceptada. Se resuelve toda en el DDL y el codebook, no en
el protocolo:

1. `especificacion` debe ser una **gramática canónica validable**, no texto
   libre.
2. Declarar claves foráneas y cardinalidades de `determinacion_id`.
3. **Intervalos de antigüedad semiabiertos** — o inclusividad equivalente
   declarada — en `escala_antiguedad`, para que el tramo que contiene los doce
   meses sea inequívoco.
4. **Períodos vacacionales que cruzan el 31 de diciembre**: la esperanza de
   superposición de §4.1 necesita una convención explícita para el consumo que
   se extiende al año siguiente.

## 17bis. La banda es un constructo conductual, no un derecho

La cota estilizada y `amplitud_de_colocacion` miden lo que un agente
estratégico puede extraer de la norma, no lo que la norma concede. **Nunca entran
a las columnas de derecho.** Van en un bloque etiquetado del panel, y toda tabla
publicada que los incluya debe decir que son cotas bajo colocación óptima
sujeta a reglas, no titularidades.

Riesgo específico: la banda hace que la comparación entre unidades sea en parte
sobre **flexibilidad normativa** y no sobre generosidad. Un ordenamiento con
menos días y fraccionamiento libre puede superar a otro con más días y bloques
rígidos. Eso es un hallazgo legítimo e interesante, pero es una pregunta
distinta y hay que reportarla como tal.

## 17. Riesgos vivos

- **La rigidez de vacaciones puede ser un artefacto de codificación** si las
  reformas ocurrieron en la escala de antigüedad. Es el riesgo más serio que
  dejó la revisión del archivo, y §3.2 es la respuesta.
- Con dos columnas de feriados hay que **declarar cuál es la titular** en cada
  tabla publicada. Objeción original de la revisión de diseño, sigue viva.
- El delta cero en vacaciones no significa inmovilidad del descanso remunerado
  (§3.6).
- Excluir por indisponibilidad correlacionada con crisis es selección sobre la
  dependiente (§13).

## 18. Decisiones del principal incorporadas

Los tres estimandos sobre hechos atómicos · dos columnas de feriados · tres
campos para vacaciones · suma con regla de imputación · nacional + ponderado ·
tres pantallas · dos cortes 2016 y 2026 · tolerancia ±1 año con fecha por celda ·
agentes IA con adjudicación humana ciega · los cuatro atributos opcionales ·
traducción automática válida citando el original · dataset público citable ·
jurisdicción de referencia = ciudad más poblada.

Adoptado por defecto, sin pronunciamiento: continuidad de unidades — panel no
balanceado, sin relleno retroactivo de fronteras.


---

## 19. Review de la revisión cruzada sobre v2.0 — tres blockers, los tres aceptados

La revisión cruzada revisó el congelado `99174c0b` y **discrepó** de que estuviera listo para
recolectar. Aceptó la separación conceptual — dos módulos sí, vacaciones sin
ocurrencias sí — pero encontró que los hechos declarados no alcanzaban para
ejecutar el diseño sin decisiones ad hoc. Dos de los tres eran **regresiones
introducidas al consolidar v1.1 y el documento de definiciones en un solo
archivo**.

| # | Objeción | Disposición |
|---|---|---|
| 1 | El total de §4 no es determinista: duración más número de feriados no determina la superposición, falta la fecha de inicio. Y `sin_regla_explicita` no equivale jurídicamente a `extienden` | **Aceptado.** §4.1 define el total como **esperanza bajo distribución declarada**, con los cuatro supuestos explícitos y fórmula versionada. §4.2 manda `sin_regla_explicita` a `NA` con intervalo de sensibilidad |
| 2 | La respuesta al riesgo de antigüedad no captura la escala: §1.1 y §3.2 se contradecían sobre la antigüedad exacta, y dos campos descriptivos no reconstruyen tramos | **Aceptado.** Antigüedad fijada en **doce meses exactos** en un solo lugar. Nueva tabla `escala_antiguedad` de tramos versionados; el valor de referencia se deriva del tramo |
| 3 | La capa común perdió identidad: `evidencia` no identificaba el hecho probado, `eventos_reforma` perdió el vínculo a versiones afectadas que v1.1 exigía, y `fecha_efectiva_de_medicion` desapareció de las tablas | **Aceptado.** §5.1 añade identificación polimórfica, cardinalidades de `evidencia`, la relación `reforma_versiones` y la tabla `mediciones` |
| — | `[suggestion]` `minimo_efectivo` requiere normalización de unidad y acreditación de vigencia como hechos, no supuestos | **Aceptado.** §3.4: `instrumento_supranacional` pasa de atributo a tabla con evidencia |

**Desacuerdo entre revisores, resuelto.** Sobre el riesgo de la escala de
antigüedad, la revisión de diseño consideró suficiente hacer obligatorios los dos campos
descriptivos; la revisión cruzada sostuvo que un campo sin estructura no sirve, porque dos
regímenes con igual entrada e igual máximo pueden esconder trayectorias
distintas y reformas intermedias. **Se adopta la posición de la revisión cruzada.**

**Lo que esto dice del proceso.** Los blockers 2 y 3 no existían en v1.1: los
introduje yo al fusionar dos documentos en uno. Consolidar no es una operación
neutra, y sin este review habríamos empezado a recolectar con dos garantías
menos de las que ya teníamos.


---

## 20. Cierre del review — luz verde

La revisión cruzada verificó el congelado `f0c760c3` y cerró los tres `[blocker]`:

- **Total:** §4.1 identifica el estimando y fija ocurrencias observadas,
  población de fechas de inicio, régimen de consumo y horizonte; §4.2 trata
  `sin_regla_explicita` como `NA` con sensibilidad.
- **Antigüedad:** doce meses exactos, escala completa por tramos versionados, y
  el valor de referencia derivado del tramo.
- **Capa común:** identificadores estables para todo hecho versionado, y las
  tres relaciones —hecho↔evidencia, reforma↔versiones, hecho↔medición/corte—
  con cardinalidades explícitas.

Dictamen textual: *"No queda un hecho faltante que obligue a recapturar o
reinterpretar después. Por mi revisión, puede comenzar la recolección."*

La revisión de diseño había cerrado antes, sin blockers.

**Estado: v2.1 es la metodología vigente y la recolección puede comenzar.**


---

## 21. v2.2 — banda de colocación

**Decisión del principal**, con tres elecciones tomadas tras el push back:

1. **Banda de tres** —mínimo, esperado, máximo— más la amplitud como variable
   propia, en vez de una sola columna de cota superior.
2. **Objetivo: días pagados no trabajados**, no días consecutivos libres. La
   estrategia de puentes concentra el descanso pero no añade días pagados.
3. **`control_del_momento` se codifica** como campo con evidencia, en vez de
   suponer elección libre. *(Decisión de v2.2. **Supersedida por §24**: el campo
   se eliminó y lo reemplaza la tabla `regla_colocacion`.)*

**Objeciones que se plantearon y cómo quedaron resueltas:**

| Objeción | Resolución |
|---|---|
| Deja de medir derecho y mide comportamiento | §17bis: bloque etiquetado, fuera de las columnas de derecho |
| En buena parte del universo el trabajador no elige la fecha | §4.3.3, hoy **supersedida por §24**: tabla de reglas en capas |
| "Optimizar" es ambiguo entre dos objetivos distintos | §4.3: objetivo fijado en días pagados; la concentración sería otra métrica |
| La métrica es degenerada en un subconjunto del universo | §4.3.2: condición explícita, campo `banda_degenerada`, y la fracción se publica como resultado |

**Lo que la objeción produjo, que es lo mejor de este cambio.** Exigir el máximo
obligó a codificar quién controla el momento de las vacaciones — una variable
institucional de primer orden que ninguna fuente previa mide. El defecto de la
propuesta forzó a recolectar algo valioso.

**Costo:** cuatro campos nuevos en `vacaciones_version`, cada uno con evidencia.
No es una métrica derivada: es una capa de recolección adicional.

**Recálculo:** costo cero. Sigue sin recolectarse el primer dato.


---

## 22. Publicación de la banda — decisión del principal y riesgo asumido

**La revisión de diseño recomendó dos archivos físicos separados**, derechos por un lado y banda
de colocación por otro, con este argumento: *"si las variables de colocación van
en el mismo panel tabular que las de derecho, el usuario casual va a agarrar la
columna con el número más grande e ignorará las advertencias."*

**El principal decidió un solo archivo.** Queda registrado como **riesgo
asumido**, no como problema resuelto: la separación lógica y la advertencia en
la documentación son exactamente lo que la revisión de diseño señala que nadie lee.

**Mitigación adoptada, que es lo único que funciona dentro de un archivo
único:** el nombre de la columna carga la advertencia, porque el nombre sí viaja
con el dato cuando alguien lo copia. De ahí
`cota_estilizada_colocacion_no_es_derecho`. Es un nombre incómodo a propósito.

Además, la primera fila del codebook para esa columna y la lista de
restricciones ignoradas de §4.3.4 se publican adyacentes a ella.


---

## 23. Antecedente externo — captura ciega y no-contaminación · v2.4

Existe un antecedente serio que cubre 45 de las 47 unidades: el índice de
regulación laboral del CBR (Cambridge), 1970-2022, con codebook público y cita
normativa por país. Su descubrimiento cambia el flujo, y trae un riesgo de
**proceso** que no está en ninguna de sus ocho brechas conocidas.

### 23.1 Lo que el antecedente puede y no puede hacer

| Puede | No puede |
|---|---|
| Aportar candidatos a reforma con fecha y cita | **Confirmar la ausencia de una reforma** |
| Servir de evidencia de **existencia y fecha** de un evento | Probar el **quantum** de una versión, ni siquiera como `verificado_secundaria` |
| Localizar la norma aplicable | Eximir de leerla y derivar el valor bajo nuestro constructo |

**Su nivel de fuente es 4**, no 1. La nota de prior art lo llamó "T1" y esa
palabra es peligrosa porque `nivel_de_fuente` es un campo con restricción: nadie
debe cargar 1 citando esa frase.

**Que el antecedente no registre cambio significa ausencia en *su* constructo y
en *su* ventana, no en la nuestra.** Es ciego a la escala de antigüedad, al tipo
de día, a las celdas censuradas en su tope, a lo subnacional y a 2023-2026.
Tomar su silencio por confirmación reintroduciría el sesgo hacia cero que este
proyecto existe para corregir — esta vez con una fuente prestigiosa como
coartada, o sea más difícil de detectar, no menos.

### 23.2 Captura ciega — obligatoria

1. **Quien codifica no ve el valor del antecedente antes de capturar.** El cruce
   se computa **después**.
2. **La concordancia con el antecedente nunca eleva `estado_verificacion`.**
   Coincidir no es verificar.
3. **La muestra de doble codificación se estratifica** para incluir celdas
   censuradas y divergentes, no sólo concordantes.

**Por qué, y es el riesgo que ninguna brecha del antecedente captura.** Si el
codificador ve el valor externo antes de capturar, su juicio deriva hacia él, y
la doble codificación ciega **deja de ser ciega**: ambos codificadores quedan
anclados al mismo tercero. El "cero por defecto" se sustituiría por "antecedente
por defecto".

Y hay una segunda mitad, peor: si el antecedente decide **dónde se busca**, el
esfuerzo de verificación se asigna lejos de sus puntos ciegos — que son
exactamente las seis cosas que este proyecto declara como contribución propia.
Los errores residuales se concentrarían donde afirmamos novedad, y la
concordancia se reportaría alta precisamente porque se muestreó condicionando en
el antecedente. Es selección sobre la dependiente (§13), por otra puerta.

### 23.3 Dónde vive el dato externo

Tablas `medicion_externa`, `reforma_externa` y `crosswalk_causa`, **fuera del
registro `hechos`**: no son hechos del proyecto, son observaciones de otro
instrumento. No pueden ser referenciadas por `evidencia`, `reforma_versiones` ni
`mediciones`.

Las cuatro reglas distintas que el antecedente aplica a países federales —y que
hoy viven como prosa narrativa en su codebook, país por país— pasan a ser
**campo**: `regla_subnacional_efectiva`. Quien use el número sabrá qué
jurisdicción compró.

Cuatro validaciones nuevas lo hacen cumplir: una impide que una celda quede
verificada sólo con el antecedente, y tres exigen declarar la causa de
divergencia cuando hay censura, base no legal o regla subnacional distinta de la
uniforme.

### 23.4 Lo que esto abre

- **Auditar el antecedente, no sólo usarlo.** El cruce con causas codificadas
  mide, unidad por unidad, la cuña entre "duración normal por ley o convenio a
  escala federal indeterminada" y "derecho legal del trabajador de referencia en
  días hábiles". Nadie ha medido esa cuña.
- **Test del sesgo de persistencia.** Cruzar los años de cambio del antecedente
  contra la columna histórica imputada del material importado dice cuántas
  reformas reales se tragó el supuesto de persistencia. Es la acusación
  cuantificada del defecto que ordena el diseño.


---

## 24. Reglas de colocación en capas, y qué se puede derivar de ellas · v2.5

**Enmienda sustantiva, no implementación.** v2.4 definía un campo
`control_del_momento` como enumerado de cinco valores en la fila de vacaciones.
La búsqueda dirigida y el reataque de la revisión cruzada lo invalidaron por dos razones
distintas, y ambas cambian el estimando, así que esto es enmienda de protocolo y
no detalle de esquema.

### 24.1 Por qué el enumerado no servía

**Primero, presuponía que alguien decide.** En los ordenamientos revisados no
existe eso: hay un trabajador que propone y un empleador que puede negarse sobre
causales tasadas. El valor `trabajador` no se instanciaba en ninguna unidad, con
lo que la derivada de cota accesible habría quedado en `NA` en todo el universo.

**Segundo, y más grave, aplanaba estructura.** Un mismo derecho puede estar
gobernado por reglas **concurrentes, residuales o jerárquicas**. El art. 7:638(2)
neerlandés establece que la regla de solicitud del trabajador opera sólo sobre lo
**no fijado ya** por acuerdo escrito, convenio colectivo, órgano competente o
ley. La fuente oficial belga describe una cascada de cuatro niveles. Un escalar
obligatorio por versión no puede representar ninguna de las dos cosas.

### 24.2 Qué lo reemplaza

Tabla **`regla_colocacion`**, hija de `vacaciones_version`.

**Dos modos, y no son la misma estructura.** `modo_aplicacion` distingue
**partición** de **cascada**:

- **Partición**: cada regla gobierna una porción distinta del derecho. Es el caso
  neerlandés — el convenio fija una parte y el resto queda residual.
- **Cascada**: varios niveles intentan fijar **el mismo** derecho en orden, y el
  siguiente opera si el anterior no lo fija. Es el caso belga. Tratarla como
  porciones obligaría a inventar días que la norma no contiene.

Una cascada exige `grupo_fallback`, exactamente una **raíz incondicional**
(`es_raiz_fallback`) que además debe ser la de menor precedencia, y sucesores con
`condicion_fallback` de vocabulario cerrado. Un grupo de un solo nivel no es
cascada: es una regla simple mal etiquetada, y se rechaza.

Campos comunes: orden de precedencia, alcance —todo el derecho, porción definida
o residual—, instrumento que la establece, iniciativa, y dos atributos
**condicionales**: causal de veto y regla de silencio, que existen **si y sólo
si** la iniciativa es del trabajador. Cuando la porción se expresa en días, el
tipo de día es obligatorio y debe coincidir con el de la versión.

La regla es un **hecho evidenciable**: lleva su propia procedencia, porque las
capas provienen de instrumentos distintos y una fuente global de la versión
padre no la resolvería.

**La unidad de asignación es la porción reclamada, no la fila.** Una partición
reclama una porción por regla; una cascada reclama **una sola** porción por
grupo, porque sus niveles compiten por fijar lo mismo. Toda la aritmética del
derecho se evalúa sobre esas unidades:

- Una unidad de **alcance total no convive con ninguna otra**, sea de partición o
  de cascada. Dos reclamos sobre el derecho entero son un conflicto, no capas.
- Hay **como máximo una unidad residual** por versión: el remanente es uno solo.
- Un **residual se define contra algo**. Si no hay ninguna porción definida en la
  versión, no es un remanente: es el derecho entero declarado por la puerta de
  atrás, y se rechaza. Un derecho gobernado por una sola regla se declara de
  alcance total, que sí es excluyente.
- Las porciones **suman como mucho el derecho**: la fracción no pasa de uno y los
  días no pasan del quantum de la versión, contando cascadas y particiones juntas.
- Sobre una misma versión **no se mezclan días y fracción** sin base de
  conversión, tampoco entre modos.
- La cobertura se acredita de **tres** maneras, no de dos: alcance total,
  residual que recoge lo no asignado, **o porciones que ya suman exactamente el
  derecho**. Exigir siempre un residual hacía irrepresentable una partición
  exhaustiva legítima como `0,5 + 0,5`.
- Y al revés: **si las porciones ya suman el derecho, un residual no recoge
  nada** y se rechaza. Un residual vacío finge cobertura.
- La **condición de cascada no existe en una partición**. No hay nivel anterior
  al cual condicionarse.

Esto se especifica aquí porque no basta con validarlo por modo. Mientras las
comprobaciones aritméticas miraban sólo la partición, **bastaba etiquetar una
regla como cascada para eximirla de todas**: una cascada de 0,6 conviviendo con
una partición de 0,5 más residual sumaba 1,1 del derecho sin una sola violación.
La red existía y era evadible por etiqueta.

Esa condicionalidad importa: obligarlos a estar siempre presentes fabricaba
valores donde el concepto no aplica. Un calendario fijo por ley no tiene "veto
del empleador", y rellenarlo con `ninguno` sería inventar un hecho.

### 24.3 Derivación de la cota accesible · **restrictiva por defecto**

La regla, tomada del reataque de la revisión cruzada y adoptada sin atenuar:

| Situación | `cota_accesible_al_trabajador` |
|---|---|
| Una sola regla, alcance total, iniciativa del trabajador, **veto `ninguno`** | = la cota |
| Cualquier veto causal o discrecional | **`NA`**, causa `veto_no_evaluado` |
| Iniciativa negociada | **`NA`**; alimenta `cota_negociable`, no la accesible |
| Cierre colectivo o calendario fijo | **`NA`**, causa `fechas_no_capturadas` (§4.3.4 decidió no capturar el dominio de fechas) |
| Reglas en capas | **`NA`**, causa `regla_no_uniforme` |

**El silencio aprobatorio no cambia el resultado.** Describe el efecto de un
evento contingente —que el empleador calle— no una garantía. Y la colocación que
maximiza el tiempo libre es precisamente la que más probablemente choca con una
razón imperiosa de servicio: el régimen que hace la cota atractiva es el mismo
que hace probable el veto.

**Consecuencia esperada, no medida.** Con este criterio se **espera** que
`cota_accesible_al_trabajador` resulte `NA` en la mayor parte del universo. Si al
medir resulta así, será un hallazgo reportable; hasta entonces es una **predicción
del diseño**, y llamarla hallazgo sería sobreafirmar. Nadie ha codificado todavía
una sola regla de colocación.

Lo que sí se puede afirmar ahora es lo normativo: establecer que la cota es
alcanzable exigiría modelar y evaluar la causal de veto contra cada calendario
posible, que es un proyecto distinto de éste.

Lo que sí queda medible y vale reportarse es el **procedimiento**: quién toma la
iniciativa, sobre qué causal puede negarse el empleador, y qué pasa ante el
silencio. Es una caracterización institucional legítima; no es una cota.

### 24.4 Estatus de los campos

Las reglas de colocación son **hechos de derecho**: describen la norma. Van en
la capa de derecho, no en el bloque conductual de §17bis. Las **cotas derivadas**
de ellas sí quedan fuera de las columnas de derecho, como manda §17bis.


---

## 25. Vínculo lote → protocolo, y una sobreafirmación retirada · v2.6

### 25.1 Cada lote declara contra qué protocolo se capturó

`lote_captura` lleva ahora `version_protocolo` y `hash_protocolo`, ambos
obligatorios. Cierra un blocker que la revisión cruzada venía señalando desde rev103 y que yo
había intentado resolver con un comentario en la cabecera del esquema.

**Por qué un comentario no servía.** Se desincroniza en cuanto el protocolo
cambia, y de hecho se desincronizó: la cabecera seguía declarando v2.3 cuando el
protocolo iba en v2.5. Un comentario no es un vínculo reconstruible; una columna
obligatoria por lote sí.

**Dos columnas de texto tampoco bastan.** Medido: un lote aceptaba
`version = 'banana'` con sesenta y cuatro letras `z`, y el par entero se podía
reescribir después de cerrar el lote. Eso no es un vínculo, son dos textos
editables. La especificación vigente es:

- **Catálogo de protocolos congelados.** Cada versión congelada es una fila con
  su versión, su hash SHA-256, el archivo archivado que lo reproduce y la marca
  de congelamiento. La versión es única y el par versión–hash es la clave.
- **Clave foránea compuesta desde el lote.** Un lote no puede declarar un par que
  no esté congelado. Deja de ser posible inventarlo al vuelo.
- **Formato acreditado.** El hash es hexadecimal de sesenta y cuatro caracteres
  —no basta la longitud—, la versión tiene forma exacta `vN.N`, la ruta es una copia plana
  bajo `docs/archivo/` terminada en `.md`, y la marca de congelamiento pasa las
  mismas comprobaciones de fecha y hora que el lote. Los tres primeros se
  endurecieron en v2.9 tras un ataque reproducible: `v2v.8`, `v2.8v`, `v2.8.1` y
  la ruta vacía entraban todos, y con ellos se podía cerrar un lote entero.
- **Inmovilidad en las dos puntas.** El par del lote es parte de su identidad
  auditada y no se toca nunca, ni siquiera mientras el lote sigue ciego. Y la
  entrada del catálogo no se edita ni se borra: si se pudiera repuntar su
  archivo, el registro dejaría de reconstruir nada.

**Qué compra esto, y qué no — corregido en v2.9.** Este párrafo afirmaba que
dado un lote cualquiera «se recupera el documento exacto contra el que se
codificó y se verifica su hash». **Es falso, y la corrección va aquí y no en una
sección aparte.** Lo que el esquema garantiza es más estrecho: un lote no puede
declarar un par versión–hash que no esté en el catálogo, ese par es inmóvil en
las dos puntas, y la ruta tiene forma de copia archivada. Nada de eso acredita
que el archivo exista ni que su contenido reproduzca el hash.

La razón es de la herramienta, no del diseño: **SQLite no lee el disco ni calcula
SHA-256.** Ninguna restricción declarativa puede atar una fila a un archivo.
Medido sobre este mismo esquema: se puede sembrar una versión inventada con un
hash bien formado que no corresponde a ningún archivo, atar un lote a ella,
congelarlo y cruzarlo, y el ciclo cierra sin una sola violación.

**Limitación declarada del dataset.** La reproducción del documento desde un lote
histórico depende de una comprobación externa —`scripts/verificar_congelamiento.py`,
que recalcula cada hash contra el archivo real— y esa comprobación **no es una
puerta obligatoria del ciclo de cierre**. Es una decisión del principal, tomada
sabiendo lo que cuesta: se prefirió no agregar un paso al flujo de captura y
declarar el hueco antes que prometer una garantía que la base no sostiene. Quien
use el dataset debe correr esa verificación si necesita la garantía plena.

Lo que sí queda cerrado, y no es poco: sin catálogo, un lote histórico apuntaba a
un archivo que ya había cambiado, y el par se podía reescribir después de cerrar
el lote.

### 25.2 Retiro de una sobreafirmación

§24.3 decía que la cota accesible sería `NA` en casi todo el universo y llamaba a
eso **"el hallazgo"**. Es una expectativa derivada del criterio, no un resultado
medido. **La corrección se aplicó en §24.3 misma**, no aquí: dejar la afirmación
en su sitio y retractarla en otra sección producía un documento que se
contradecía consigo mismo, que es exactamente lo que la revisión cruzada marcó después.

Es la tercera vez en esta serie que confundo una consecuencia del criterio con un
resultado. Queda anotado como patrón, no como incidente — y la cuarta lección de
método: **una retractación tiene que corregir el original, no anexarse**.


---

## 26. Cómo se nombra y se verifica el protocolo · v2.8

**El documento vigente se llama `docs/02-protocolo.md` y no lleva versión en el
nombre.** Cada congelamiento deja una copia inmutable en
`docs/archivo/02-protocolo-vX.Y.md`, y es esa copia —nunca el vigente— la que
cita el registro.

**Por qué.** Con el nombre versionado, cada versión renombraba el archivo y
dejaba atrás toda referencia escrita. El resultado medido: cuatro entradas
históricas del registro apuntaban al mismo archivo vigente, así que la
verificación que el propio registro manda ejecutar fallaba en cuatro de nueve
casos; una copia archivada estaba etiquetada v2.3 y contenía v2.2; y v2.6 no
tenía copia. Ninguna de las tres cosas se ve leyendo: aparecen al recalcular.

**Verificación reproducible.** `scripts/verificar_congelamiento.py` recorre el
registro, recalcula el SHA-256 de cada archivo declarado y reporta discrepancias.
Es la única forma admitida de afirmar que el registro está sano; la afirmación en
prosa no cuenta. La quinta lección de método, y es del mismo tipo que las
anteriores: **un registro de integridad que no se ejecuta es prosa**.

**Regla operativa.** Congelar una versión es: copiar el vigente a
`docs/archivo/`, añadir la entrada con su hash y su archivo, y correr el
verificador. Si el verificador no pasa, la versión no está congelada.

**Sin excepciones — corregido en v2.9.** El verificador eximía de esta regla a
toda entrada cuyo título contuviera `VIGENTE`, y v2.8 se congeló apuntando al
documento vivo amparada en esa excepción. Una regla cuyo cumplimiento depende de
cómo esté redactado un encabezado no es una regla. La excepción se eliminó, la
copia de v2.8 se creó a posteriori —idéntica byte a byte, mismo hash— y la
corrección del puntero quedó escrita en el registro en vez de hacerse en
silencio. La comprobación es ahora estructural: la ruta empieza por
`docs/archivo/` o la entrada falla, tanto en el verificador como en el `CHECK`
del catálogo.

---

## 27. Endurecimiento del catálogo, y qué queda fuera de la base · v2.9–v2.12

Un ataque reproducible sobre el esquema de v2.8 sembró la versión `v2v.8` con un
hash ficticio y `archivo = ''`, ató un lote a ese par, lo congeló y lo cruzó. **El
ciclo completo cerró sin una sola violación.** Tres cosas fallaron a la vez.

**Lo que se cerró en el esquema.** El `CHECK` de versión admitía la `v` en
cualquier posición y cualquier número de puntos; ahora exige la forma exacta
`vN.N`. La ruta no tenía restricción alguna; ahora debe ser una **copia plana
bajo `docs/archivo/` terminada en `.md`**. Esto último importa por lo que enseña:
**la regla de §26 era de prefijo de ruta, y un prefijo de ruta sí es expresable
en SQL.** La habíamos dejado en prosa por costumbre, no por imposibilidad. Vale
la pena preguntarse eso de cada regla antes de darla por inexpresable.

**Y el prefijo por sí solo no bastaba — corregido en v2.10.** La primera versión
de esa restricción exigía sólo el prefijo, y la revisión cruzada la rompió de inmediato:
`docs/archivo/../02-protocolo.md` casa con el prefijo y **resuelve al documento
vigente**, que es precisamente lo que la regla prohíbe. También entraban la barra
doble y la travesía desde un subdirectorio. La lección es del mismo tipo que las
anteriores: **un prefijo de ruta no acota una ruta que puede volver hacia atrás.**
El cierre no consiste en enumerar travesías —esa carrera se pierde— sino en usar
un hecho de la estructura: el archivo de protocolos es **plano**, así que lo que
sigue al prefijo no puede contener ninguna barra. Eso mata `..`, `//` y los
subdirectorios de una vez. La misma comprobación vive en el verificador, porque
el `CHECK` de SQLite no alcanza al registro en Markdown.

**Lo que no se puede cerrar ahí.** SQLite no lee el disco ni calcula SHA-256, así
que ninguna restricción declarativa ata una fila del catálogo a un archivo real.
Un hash de sesenta y cuatro hexadecimales bien formados que no corresponde a nada
sigue entrando. Eso queda como **limitación declarada**, especificada en §25.1,
por decisión del principal: se prefirió no convertir el verificador en puerta
obligatoria del ciclo de captura y declarar el hueco con precisión, antes que
prometer una garantía que la base no sostiene.

**La puerta que respalda la limitación fallaba abierta — corregido en v2.11.**
§25.1 declara que la garantía plena depende de una comprobación externa. La revisión cruzada
atacó esa comprobación y encontró que el verificador reconocía una entrada del
registro sólo si su hash ya estaba bien formado: **un hash corrupto no producía
un error, hacía desaparecer la entrada**, y el verificador comprobaba las
restantes y anunciaba que todas reproducían. Una puerta que falla abierta no es
una puerta, y el defecto era peor que los que detecta, porque afectaba justo al
mecanismo del que depende la limitación declarada.

La causa era fundir dos preguntas en una: *si el bloque pretende ser una entrada*
y *si está bien formado*. Ahora la primera decide si se examina —basta que
declare fila de archivo o de hash— y la segunda decide si pasa. Hash ausente,
corto, en mayúsculas, sin comillas o duplicado son fallos, no invisibilidades.
Regresiones en `scripts/probar_verificador.py`, que corrompe el registro en
memoria y exige que el verificador falle en las siete formas.

**Y la entrada entera seguía desapareciendo — corregido en v2.12.** la revisión adversarial, que
revisó el arreglo anterior porque quien lo escribió no puede aprobarlo, encontró
que el fallo abierto persistía **un nivel más arriba**. Corregir el hash
malformado no arregla que el registro no tenga que contener nada: con el registro
vacío el verificador anunciaba «0 entradas verificadas, todas reproducen» y salía
con éxito; con una entrada borrada, verificaba las trece restantes y salía con
éxito; y con homoglifos cirílicos en las etiquetas de una tabla —`Аrchivo`,
visualmente idéntico— el bloque se volvía invisible y salía con éxito. Además el
título nunca se leía, así que una versión duplicada o apócrifa pasaba igual.

**El cierre es un ancla, no un parche por síntoma.** Toda copia de protocolo en
`docs/archivo/` debe tener exactamente una entrada, y toda entrada debe apuntar a
una copia existente cuyo nombre lleve su versión. Es una biyección, y por eso las
tres formas de hacer desaparecer una entrada fallan a la vez: el archivo queda
huérfano. Las copias que legítimamente no son versiones congeladas se declaran en
una tabla del propio registro que el verificador lee — **una excepción declarada
es visible; una excepción escondida en el código es un agujero con otro nombre**.

La lección general, y es la que más se repite en esta serie: **verificar lo que
un registro dice contener no dice nada sobre lo que debería contener.** Hace
falta anclarlo a algo externo a él.

**Dos cosas más que salieron de esa revisión.** El bloque de estado actual del
registro declaraba un hash de esquema de dos versiones atrás y **no se comparaba
con nada**; ahora se comprueba. Y las regresiones ya no se conforman con que el
verificador salga con error: **cada caso declara qué mensaje espera**, porque
salir con error por otra razón es indistinguible de no haber probado nada.

**Criterio aplicado.** La regla de parada acordada no es «sin defectos» sino
*ningún defecto residual puede corromper dato en silencio*. Éste era silencioso y
ahora no lo es: está dicho en el protocolo, tiene un verificador que lo detecta,
y el caso adversarial que lo demuestra es reproducible con
`python3 scripts/probar_catalogo.py`. Un defecto declarado y ejecutable deja de
ser silencioso — que es precisamente lo que el criterio pide.

---

## 28. Cuatro decisiones de constructo que salieron del piloto · v2.13

Las ocho unidades del piloto se capturaron el 2026-08-09 y produjeron lo que el
piloto existe para producir: **normas reales que el esquema no podía
representar**. Ninguna se forzó. Las cuatro decisiones son del principal.

### 28.1 Fecha delegada a la jurisdicción local

Guatemala concede «el día de la festividad de la localidad» y El Salvador «la
festividad más importante del lugar, **según la costumbre**». El feriado existe
con certeza a nivel nacional y su fecha **no es determinable a ese nivel**.

`clase_de_regla` gana `delegada_a_jurisdiccion_local`, que **prohíbe** todo campo
de fecha. Lo que se rechazó: meterlo en `dependiente_de_proclamacion`, que habría
obligado al codificador a **inventar una proclamación inexistente** para que el
esquema lo aceptara.

### 28.2 Unidad del texto legal, con base semanal declarada

Alemania concede «24 **Werktage**» —incluyen el sábado, excluyen domingos y
feriados, sobre semana de seis días—. Codificarlos como hábiles **sobreestima el
derecho alemán en un 20%**. Ontario concede «**2 semanas**», y guardar «10 días»
sería presentar una conversión nuestra como si fuera el texto legal.

`tipo_de_dia` admite ahora `werktage` y `semanas`, y entra `base_semanal_dias`,
**obligatorio cuando la unidad se define contra la semana** y prohibido cuando
son días calendario, porque ahí la conversión es propiedad del trabajador
—`regimen_jornada`— y no de la norma.

Es más general que enumerar unidades: cualquier norma escrita sobre semana de
seis días queda representable sin tocar el esquema otra vez.

### 28.3 Recurrencia periódica no anual

México concede el 1 de octubre **cada seis años**, por transmisión del Poder
Ejecutivo. `recurrencia` sólo distinguía lo anual de lo extraordinario.

Entra `periodo_anios`, obligatorio para lo recurrente y prohibido para lo
extraordinario. **Lo que compra es concreto**: con dos cortes, ese feriado puede
caer en uno y no en el otro, y el codificador registraría un delta que **no es
una reforma**. Con el período explícito el cálculo lo excluye o lo anota, en vez
de depender de que alguien se acuerde.

### 28.4 Colocación por asignación estatal

Indonesia fija cada año, por decreto de tres ministros, 8 días de *cuti bersama*
que **descuentan del saldo de 12 días** de vacaciones. No es un feriado que se
suma ni un puente compensable: es tiempo libre que se cobra del derecho.

`regla_colocacion.iniciativa` gana `asignacion_estatal`, distinto de
`cierre_colectivo` porque lo decide el Estado y no el empleador. **No hizo falta
campo nuevo**: la aritmética de porciones ya existente hace que la cota accesible
al trabajador caiga sola de 12 a 4 días.

### 28.5 Verificación

```bash
python3 scripts/probar_decisiones_piloto.py
```

Prueba las cuatro **con las normas que las provocaron**, y con las dos mitades:
los estados prohibidos se rechazan y las estructuras fieles entran limpias.

Nota de método que vale la pena dejar escrita: **escribir esos casos costó cuatro
intentos y los cuatro fallos fueron del fixture, no del esquema** —columna
inexistente, valor fuera de dominio, columna obligatoria omitida, nombre
equivocado—. Cada uno se leía como «el esquema rechaza lo válido». Es el primer
patrón de fallo de esta serie, y por eso los casos legítimos van explícitos: sin
ellos, un fixture roto se lee como esquema estricto.

---

## 29. Dos clases mas de fecha, y por que van separadas · v2.14

Al cargar las ocho unidades quedaron **dos feriados de noventa y cuatro** que
ninguna clase admitía. El cargador se negó a forzarlos y los contó, que es la
conducta correcta: la etiqueta cómoda habría sido invisible justo por plausible.

| Unidad | Literal | Por qué no encajaba |
|---|---|---|
| Ontario | «the Monday preceding May 25» | No es `ordinal` —no es el enésimo lunes del mes— ni `relativa`, cuyo ancla es una fiesta **móvil**. Aquí el ancla es una **fecha** |
| México | «el que determinen las leyes federales y locales electorales» | La fecha existe pero vive en **otro cuerpo normativo** |

**Van separadas por decisión del principal, y la razón importa.** Meterlos en una
sola clase «no determinable» habría escondido que **el primero sí es calculable**:
Victoria Day es determinista y puede generar ocurrencias. Perder eso para ganar
una clase menos es perder dato real a cambio de comodidad de esquema.

**`relativa_a_fecha`.** `mes` y `dia` son el ancla, `dia_semana` el objetivo y el
**signo** de `offset_dias` la dirección — negativo el anterior, positivo el
siguiente. Se prohíbe el desplazamiento cero: sin dirección la regla no dice nada.

**`remision_normativa`.** Obliga a `instrumento_remitido` y prohíbe todo campo de
fecha. Una remisión sin destino no es una remisión, es un hueco con nombre; y por
eso el destino está prohibido en las demás clases, para que el campo signifique
algo donde aparece.

### 29.1 Estado del piloto tras estas dos

**94 feriados en las ocho unidades, cero omitidos, las 37 validaciones en cero.**

| Clase | Feriados |
|---|---:|
| `fija` | 68 |
| `relativa` | 16 |
| `ordinal` | 6 |
| `delegada_a_jurisdiccion_local` | 2 |
| `relativa_a_fecha` | 1 |
| `remision_normativa` | 1 |

**Una cuarta parte de los feriados del piloto no lleva fecha escrita en su
norma.** Con un esquema que sólo aceptara fechas fijas, ese 25% se habría perdido
o —peor— se habría inventado.

---

## 30. Cierre del piloto y congelamiento del esquema · v2.15

Las ocho unidades quedaron capturadas en **ambas variables**, con las 37
validaciones en cero. El piloto termina aquí y el esquema se congela, en el orden
que fijó el principal: **cerrar los pendientes de captura primero**, porque son
la clase de caso que rompió el esquema siete veces.

### 30.1 La imputación estaba en la unidad de conteo

El campo `imputacion_feriados_a_vacaciones` se verificó **una por una**, por
decisión del principal, en vez de derivarse del tipo de día. La correspondencia
se confirmó en las ocho:

| Unidad de conteo | Imputación | Unidades |
|---|---|---|
| días calendario | `se_computan_contra` | Perú, El Salvador |
| días de trabajo · werktage · semanas | `extienden` | Guatemala, México, Indonesia, Canadá, Alemania, Turquía |

Verificar en vez de derivar cambió el resultado en un caso, y ese caso justifica
la decisión entera. **El Salvador dice lo contrario de lo que la regla habría
predicho para su vecino**: su artículo 178 establece explícitamente que los
asuetos y descansos comprendidos en el período **no prolongarán** su duración —
y añade una restricción que ninguna otra unidad tiene: las vacaciones **no pueden
iniciarse** en tales días.

Canadá tampoco cabía en el razonamiento. Su regla no es que el feriado no consuma
vacaciones, sino que genera un **día sustituto** con paga de feriado. Llega al
mismo sitio por otro camino, y sólo se ve leyendo.

E Indonesia obligó a separar dos cosas que un solo campo habría fundido: los
feriados nacionales **no** reducen el saldo, y el *cuti bersama* **sí**. Por eso
el segundo se modela como porción de colocación estatal y no como imputación.

### 30.2 Una convergencia que valida una decisión de diseño

`werktage` se añadió al esquema por Alemania. Al resolver el tipo de día turco
resultó que Turquía tiene **la misma semántica**: su artículo 56/5 excluye
domingos y feriados del cómputo, y el sábado cuenta salvo pacto en contrario.

El valor sirvió sin tocarlo. Es la evidencia de que convenía una **unidad
general** con base semanal declarada y no un valor con nombre de país.

### 30.3 Qué queda declarado al congelar

- **Fuentes por elevar.** Ocho de dieciocho están en nivel 1; seis siguen en
  nivel 4. Cada captura lo lleva anotado.
- **El corte 2016 de dos unidades no se capturó** y no se rellenó con el otro:
  Indonesia, cuyo calendario se decreta cada año, y El Salvador.
- **Dos unidades con delta cero sin verificar la ausencia**: Guatemala y Toronto.
  Su cero **no es un hallazgo**, y el panel lo dice donde muestra el cero.
- **Los feriados religiosos turcos** —lunares, multi-día y con medio día de
  víspera— no están capturados.

---

## 31. El escalado a 47 rompió el esquema congelado, y estaba previsto · v2.16

El esquema se congeló con ocho unidades. Al capturar las 47, cinco capturadores
independientes encontraron en un día más huecos que quince rondas adversariales.
Descongelar tiene costo —§9 obliga a recalcular el panel— y aquí es barato porque
el panel se deriva de la base con un comando.

### 31.1 Una Pascua no es la Pascua

`ancla` admitía `pascua` a secas. **Dos lotes distintos encontraron el hueco y lo
resolvieron al revés**: uno codificó los cinco feriados ortodoxos rumanos como
`pascua` —que produce una fecha equivocada **en silencio**, porque las dos pascuas
difieren hasta cinco semanas— y el otro omitió los griegos por el mismo motivo.
El dataset quedaba internamente inconsistente y nadie lo habría visto leyendo.

Entran `pascua_ortodoxa` y `equinoccio_septiembre`, que faltaba y Japón necesita.
**Un ancla que no distingue el cómputo no es un ancla.**

### 31.2 Cuatro defectos del cargador que los datos destaparon

**El grave, y era una afirmación mía.** El campo de vigencia admitía sólo año, con
un comentario que decía que «para cortes al 1 de enero cualquier fecha dentro del
año da el mismo resultado». **Es falso.** Portugal repuso cuatro feriados el 2 de
abril de 2016 —la reversión de 2013, el caso raro que el proyecto buscaba— y el
cargador daba 13 feriados en el corte de 2016 donde van 9. La corrección va donde
estaba el error, y `desde` admite ahora fecha completa.

**El cargador afirmaba lo que la captura negaba.** Estampaba
`descanso_pagado_obligatorio` a todo feriado e ignoraba `categoria` y `regimen` de
la captura. Para Países Bajos y Japón eso es falso: existe lista oficial y **no**
existe obligación de darla libre ni pagada. Para Países Bajos la diferencia es
**9 contra 0**.

**Un período de calificación de cero meses** —Noruega, donde el derecho no depende
del devengo— generaba un tramo degenerado que rechazaba la unidad entera.

**Y una fecha de norma imprecisa** en el metadato de una fuente tumbaba la unidad
completa por un dato accesorio.

### 31.3 Lo que sigue abierto, declarado

Los capturadores reportaron más de treinta hallazgos de esquema. Los que cambian
números y **no** se han cerrado:

- **Una quinta unidad de conteo.** Israel concede 16 días que incluyen como máximo
  un descanso semanal por cada siete y excluyen los festivos. No es calendario, ni
  hábil, ni werktage, ni semanas.
- **La escala por EDAD.** Hungría, Noruega y Suiza escalan por edad del trabajador,
  no por antigüedad; Suiza además de forma **decreciente**. `escala_antiguedad` se
  indexa en meses de servicio.
- **Las vacaciones no se pueden fechar.** El módulo de feriados sabe fechar sus
  reformas y el de vacaciones no, así que la reforma japonesa de 2019 y la
  israelí de 2016 son invisibles.
- **Colocación en cascada**, en al menos seis unidades: «por acuerdo; a falta de
  acuerdo, el empleador». La base lo soporta; el contrato de captura no lo expone.
- **Reglas de fecha disyuntivas**: el día de Santa Brígida irlandés es ordinal
  salvo cuando el 1 de febrero cae en viernes.
- **Tailandia no tiene calendario, tiene una cuota**: trece días que designa el
  empleador de un conjunto abierto.
- **`base_semanal_dias` se exige donde la norma no la fija.** Ocho unidades
  definen la unidad contra el horario *del trabajador*, no contra una semana
  legal. Obliga a revisar si las bases que ya están puestas fueron **leídas o
  elegidas**.

---

## 32. Quién fija la base semanal · v2.17

`base_semanal_dias` se exigía siempre que la unidad no fuera calendario. Fue
correcto para Alemania, cuya ley se escribe explícitamente sobre semana de seis
días. **Ocho unidades del escalado mostraron que no es general**: definen el
derecho contra el horario **del trabajador**, no contra una semana legal.

> Nueva Zelanda: «what genuinely constitutes a working week for the employee».
> Países Bajos: «vier maal de overeengekomen arbeidsduur per week».

Ahí no hay base que leer, y exigirla obligaba a inventarla — el mismo error de
factor dos, entrando por la otra puerta. Cuatro unidades no cargaban por eso, y
un capturador avisó de lo que importa: **conviene revisar si las bases ya puestas
fueron leídas o elegidas.**

Entra `base_semanal_origen`. Si la fija la norma, la base es obligatoria; si la
fija el horario del trabajador, va nula y la conversión usa `regimen_jornada`. Lo
que queda prohibido es **omitirla en silencio**, que era lo único que el CHECK
anterior sí atrapaba.

---

## 33. El cruce contra el antecedente, medido · v2.18

El cruce se computó sobre las 47 unidades, después de la captura, como manda
§23.2. Produce dos resultados de naturaleza distinta y conviene no confundirlos.

### 33.1 Vacaciones: la divergencia **es** el hallazgo

El CBR normaliza su variable 9 «con un derecho de 30 días equivalente a 1».
**Treinta días de qué, no lo dice.** Y sus propias notas de codificación muestran
que no es una unidad sola:

| Unidad | Su nota | Codifican | ¿Convierten? |
|---|---|---:|---|
| Alemania | «24 working days if 6 days week; if 5 days week: 20 days» | 20 | **sí** |
| Turquía | «14 days» | 14 | **no** |
| Perú | «30 days» | 30 | **no**, y son calendario |

Turquía y Alemania tienen la **misma estructura legal** —días que excluyen
domingo y feriados e incluyen sábado— y reciben tratamiento distinto.

Convertidas a días de trabajo sobre semana de cinco, la diferencia media contra
su cifra **se ordena por la unidad en que está escrita la norma**: cuanto más se
aleja la unidad legal de «días de trabajo sobre semana de cinco», más generoso
aparece el país en el índice.

**Las cifras de ese ordenamiento viven en el apéndice «Hallazgos», no aquí**, y
la razón es de diseño y no de espacio. Este documento se congela por hash, y un
documento congelado **no puede contener un estadístico vivo**: el congelamiento
certifica que el texto no cambió, mientras que un resultado dentro de él acaba
certificando que un número que sí cambió no cambió. Las dos propiedades son
incompatibles y gana la equivocada — el documento queda intacto y mintiendo. Ya
pasó: esta tabla llegó a publicar la mitad de su valor en la fila que sostiene el
hallazgo, y no se podía corregir sin romper el congelamiento que la hacía
citable.

Aquí se queda el MÉTODO, que es lo que no envejece. Si hace falta ilustrar la
conversión, el ejemplo es **aritmético y no medido**: treinta días calendario son
30/7 = 4,29 semanas *se trabaje lo que se trabaje*, y veinticuatro Werktage sobre
semana de seis son exactamente 4. Eso es una identidad, no un resultado, y sigue
siendo verdad cuando el dato cambie.

**Caveat que viaja con el hallazgo.** Nuestra conversión también es una
convención: pasar 30 calendario a 21,4 supone semana de cinco días. La diferencia
no es que tengamos la verdad — es que publicamos **el número legal, su unidad y
su base por separado**, así que cualquiera recalcula con otra convención. De un
índice entre 0 y 1 no se recupera ni cuántos días eran ni de qué tipo.

Aquí no hay nada que reconciliar. Se publica.

### 33.2 Feriados: la divergencia es una **pregunta**, y se clasifica

13 de 41 unidades coinciden dentro de un día. Las 28 restantes **no son 28
errores suyos**, y clasificarlas es la mitad del trabajo:

- **Artefacto nuestro.** Francia y Tailandia salen en 1 por nuestro filtro de
  régimen: en Francia sólo el 1 de mayo es descanso obligatorio por ley, y la ley
  tailandesa nombra un feriado y deja el resto como cuota del empleador.
- **Constructo distinto.** Reino Unido y Turquía salen +8 y +7,5 porque el CBR los
  codifica en cero, y lo documenta: allí el descanso en feriado depende del
  contrato.
- **Ruido de redondeo.** Su índice trae dos decimales; toda diferencia bajo 0,2
  es aritmética.
- **Desacuerdo real.** Una veintena con diferencias de 1 a 3 días.

**Para ese último grupo, reconciliar sería el error.** Un cruce que termina con
las dos series iguales no aprendió nada: copió al otro. Lo que se hace es
**clasificar** cada divergencia en error nuestro, desactualización suya, o
diferencia de constructo — y publicar el reparto, que es lo que nadie ha
publicado sobre la fiabilidad de la fuente más usada del campo.

**Asimetría declarada.** Nuestro lado se audita fecha por fecha, porque cada
feriado lleva su norma. El suyo no: su índice no dice qué días contó. En varios
casos se podrá afirmar «lo nuestro está bien» sin poder afirmar «lo suyo está
mal», y esa asimetría es en sí misma un argumento del proyecto.


---

## §34 · La doble codificación ciega, y el campo que destapó

Ejecutada por fin la exigencia de §23.2 punto 3, sobre una muestra estratificada de
unidades. Su registro está en [`notes/07-doble-codificacion.md`](../notes/07-doble-codificacion.md),
congelado antes de aplicar ninguna corrección — porque la divergencia más valiosa
desaparece en cuanto se arregla.

**Las cifras no se publican, y esto es una enmienda de v2.26.** Las tasas de
acuerdo, las segundas lecturas y el programa que las cruza se conservan en la
documentación interna del proyecto y quedan fuera del paquete publicado; la
versión archivada v2.25 de este protocolo las contiene. El motivo está en
`EXCLUSIONES.md`: retirar la conclusión y dejar el insumo permitiría recomputarlas
sin las salvedades que las acompañan, y una cifra sin su salvedad es peor que
ninguna. **Que este apartado mencione el ejercicio no debe leerse como afirmación
de concordancia alta.**

Lo que sí es doctrina y se queda: el apareamiento se hace con criterio **estricto**
y no difuso. Cuando dos menciones son transliteraciones distintas del mismo
feriado, no se aparean — hacerlo exigiría comparación por parecido, y juzgar un
parecido no es reconocer una identidad.

**Lo que encontró, y es más que una tasa.** Un feriado colombiano que faltaba —Ley
2578 de junio de 2026—, corregido. Un error de la propia segunda codificación
—ancló la Pascua griega en la occidental—, no corregido porque el nuestro ya
estaba bien. Y un defecto sistémico de la variable de colocación, que es lo que
motiva el resto de esta sección.

### 34.1 · El error de capa: fraccionamiento no es colocación

En cinco de las ocho unidades, el artículo que rige **partir el descanso en
bloques** se había usado —o empujaba a usarse— como si rigiera **cuándo se toma el
descanso entero**. Son artículos distintos y confundirlos invierte quién controla
el derecho.

Perú lo tenía mal: la captura usaba el art. 17 del D. Leg. 1405 (fraccionamiento a
solicitud escrita del trabajador) para codificar la colocación como iniciativa del
trabajador, cuando el art. 14 del D. Leg. 713 dice que se fija de común acuerdo y
que **a falta de acuerdo decide el empleador**. Israel, Grecia, Francia y Turquía
presentan la misma trampa; las tres primeras están leídas, Turquía queda declarada
como pendiente.

**Regla, desde ahora:** la regla de colocación se lee del artículo que fija la
**oportunidad**. Si el literal capturado habla de dividir, acumular o aplazar, no
es el artículo de la colocación aunque lo parezca.

### 34.2 · `resolucion_desacuerdo`, campo nuevo

Nueve unidades estaban codificadas `negociada` y escondían **seis regímenes
distintos** de qué ocurre cuando el acuerdo no llega. El esquema no podía
expresarlo: `veto_empleador` pertenece por restricción de tabla a las reglas de
solicitud del trabajador, y con razón — un veto sólo existe contra una solicitud.

| valor | qué significa | precedente |
|---|---|---|
| `empleador` | decide el empleador | Perú art. 14, Portugal 241.º n.º 2, Francia L3141-16 |
| `limite_razonabilidad` | puede negarse, pero no sin motivo | Australia s.88(2), Nueva Zelanda s.18(4) |
| `trabajador_prevalece` | el empleador queda obligado a conceder | Grecia art. 224 |
| `tercero_dirime` | el desempate sale de las partes | España art. 38.2 ET |
| `remitido_a_convenio` | la ley delega, no calla | Indonesia pasal 79(4) |
| `sin_regla` | la ley calla, y eso es un estado | Israel |

Es obligatorio cuando la iniciativa es `negociada`, por restricción de tabla y con
`=`, no con una implicación en un solo sentido: si fuera opcional, el codificador
con prisa lo dejaría en `null` y volveríamos al colapso que el campo viene a
deshacer.

**Por qué importa más allá del dato.** Colapsar estructuras legales distintas bajo
una etiqueta es exactamente lo que este proyecto le reprocha al antecedente. Lo
estábamos haciendo en la variable de colocación, y sólo se vio porque dos lectores
independientes leyeron las mismas normas.


---

## §35 · Los siete feriados sin clase, cerrados

Siete feriados de cinco unidades estaban registrados sin clase de fecha
representable y por tanto **fuera del conteo**. Cuatro decisiones del principal
los cierran, y las cuatro tienen algo en común: ninguna inventa una fecha, todas
amplían lo que el esquema *sabe decir*.

Cerrado el último, el cargador reporta **0 feriados omitidos en las 47 unidades**.

### 35.1 · Dos solsticios en el catálogo de anclas

Chile concede «el día del solsticio de invierno de cada año en el hemisferio
sur»: determinista y computable con efemérides, entre el 20 y el 22 de junio. El
catálogo tenía los dos equinoccios y ningún solsticio. Se añaden
`solsticio_junio` y `solsticio_diciembre` — los dos, porque un catálogo con tres
de los cuatro puntos cardinales del año invita a la siguiente omisión.

Fijarlo al 21 de junio habría sido escribir el año típico y equivocarse los
otros, que es justo la aproximación cómoda que este protocolo existe para no
hacer.

### 35.2 · Varias reglas de fecha por feriado, con condición

**Es la decisión de fondo, y resuelve cuatro casos que parecían tres problemas.**

Un feriado puede tener varias reglas, cada una con la condición bajo la que rige,
y **como máximo una sin condición** — la que rige por defecto, garantizada por un
índice único parcial.

De ahí salen dos cosas que se creían distintas:

**Existencia condicional.** Chile declara feriado el 2 de enero sólo cuando cae
lunes, y el 17 de septiembre sólo cuando el 18 y el 19 caen fin de semana. No
hace falta un campo de existencia: **un feriado cuyas reglas todas llevan
condición no ocurre en los años en que ninguna se cumple.** La ausencia de regla
por defecto *es* la existencia condicional.

**Regla disyuntiva.** Santa Brígida en Irlanda es el primer lunes de febrero
salvo cuando el 1 de febrero cae viernes. Yom HaAtzmaut en Israel desplaza el 5
de Iyar de tres maneras según el día de la semana. Son dos y cuatro reglas del
catálogo alternándose, no clases nuevas.

`condicion_referencia` dice qué fecha se examina, y hacen falta las tres formas:

| valor | qué examina | caso |
|---|---|---|
| `propia` | la fecha que la propia regla computa | Chile: el 2 de enero es feriado cuando el 2 de enero cae lunes |
| `regla_por_defecto` | la fecha de la regla sin condición del mismo feriado | Israel: las alternativas producen el 3, 4 y 6 de Iyar, pero la condición se examina sobre el 5 |
| `MM-DD` | una fecha fija distinta | Irlanda: se examina el 1 de febrero mientras el defecto produce el primer lunes |

La distinción entre las dos primeras no es sutileza: con `propia`, Israel
preguntaría por el día de la semana del **resultado** en vez del de la **base**, y
daría mal.

Nota sobre Irlanda: la formulación en una sola frase que circula —«the first
Monday in February, or 1 February if that date falls on a Friday»— es de la
*Explanatory Note*, que el propio instrumento declara **no vinculante**. El
literal operativo son las reglas 4 y 5, separadas, y separadas se codifican.

### 35.3 · Día lunar contado desde el fin del mes

Corea concede la víspera del Año Nuevo lunar, que su decreto define como
«음력 12월 말일»: el último día del mes 12, que es el 29 o el 30 según el año. La
clase `lunar` exigía un día fijo entre 1 y 30.

Se añade `dia_lunar_desde_fin`, donde 1 es el último día, excluyente con
`dia_lunar` por restricción de tabla. Se descartó el centinela `-1`: un número
que significa otra cosa que un número es un truco que nadie recuerda dos meses
después.

### 35.4 · Cuota designada por el empleador

Tailandia nombra **un** feriado por ley y deja doce días a designación del
empleador dentro de un conjunto tradicional. No es `delegada_a_jurisdiccion_local`
—no la fija la jurisdicción sino el empleador— ni `remision_normativa`, porque no
hay una norma única a la que remitir.

La clase `cuota_designada_por_empleador` registra la **cantidad** y el
**conjunto**, sin fechas. El conjunto es obligatorio: una cuota sin conjunto no se
puede auditar, sólo creer.

Con esto Tailandia pasa de 1 a **13**, que era la mayor discrepancia de una sola
unidad contra el antecedente — y coincide con su cifra exactamente.

La estructura reaparecerá: en Francia, diez de los once días festivos los define
el convenio y no la ley.

### 35.5 · Lo que la red atrapó, otra vez

Al cargar las reglas alternativas les faltaba la evidencia: sólo la principal
recibía su vínculo con la fuente. **V1 —«hecho sin evidencia»— lo atrapó con doce
filas.** Un hecho sin fuente no es auditable aunque sea la variante rara de un
feriado.


---

## §36 · La jornada semanal legal, y por qué hizo falta capturarla

Una métrica de descanso sólo significa algo **contra los días que se habrían
trabajado**. Ese contrafáctico no está en un estatuto de vacaciones: es un hecho
de la ley de jornada. Se capturó para las 47 unidades, en cinco lotes, y llenó la
tabla `regimen_jornada`, que existía vacía desde el diseño.

Cerró dos huecos que la métrica de descanso había declarado sobre sí misma: la
semana del trabajador, y qué pasa cuando un feriado cae en el descanso semanal.

### 36.1 · Tres confusiones que hay que no cometer, porque yo cometí dos

**La base de la norma de vacaciones no es la semana de trabajo.** Los 30 Werktage
austriacos están escritos sobre semana de seis; el trabajador austriaco hace
cinco. Usar la primera como la segunda ponía a Austria primera en la métrica con
42 días liberados. Era un artefacto.

**El descanso mínimo garantizado tampoco es la semana de trabajo.** Que la ley
británica garantice un día de descanso no significa que se trabajen seis:
restar de siete da el **máximo permitido**, no lo ordinario. Estuve a punto de
publicar la tabla con esa deducción.

**Y la cifra semanal puede ser un producto y no un texto.** La ley alemana de
jornada **no escribe ninguna cifra semanal**: sus 48 horas son ocho por seis
Werktage, y los seis existen porque el §9 retira del calendario el domingo y los
feriados. El dato que lo confirma es que la reforma federal en discusión consiste
literalmente en *escribir* ese techo.

De ahí que `dias_ordinarios` lleve su origen al lado, con cuatro valores:

| valor | qué significa |
|---|---|
| `declarado` | la norma escribe el número — Hungría: «cinco días, de lunes a viernes» |
| `derivado` | sale de dividir el techo semanal entre el diario — Alemania, Corea |
| `alternativa_legal` | la ley **no elige** y declara entre qué valores — Chile 5–6, Colombia e Indonesia |
| `no_declarado` | silencio: la distribución va al contrato o al convenio |

**Nombrar y no elegir es un acto legal distinto de callar**, y por eso
`alternativa_legal` no se funde con `no_declarado`. Sólo **21 de 47** unidades
tienen los días ordinarios fijados o derivables de la ley; en las 26 restantes se
aplica la convención de cinco y se marca. La ganancia de la captura no es haber
rellenado esas 26: es saber cuáles son.

### 36.2 · Mecanismo y efecto son dos campos

Qué hace la norma cuando un feriado cae en el descanso semanal, y qué acaba
recibiendo el trabajador, son preguntas distintas. Mezclarlas fue el primer
diseño y no sobrevivió al contacto con los datos: aparecieron **ocho mecanismos**
donde yo esperaba dos.

| mecanismo | caso |
|---|---|
| `traslada` | Bélgica: sustituye por un día hábil |
| `anade_dia` | Australia: en Navidad y Año Nuevo **suma** un día, no sustituye |
| `reduce_cuota_de_horas` | Polonia: no mueve nada, resta ocho horas a la cuota del período |
| `compensa_en_dinero` | Italia: retribución adicional, ningún día |
| `compensa_a_eleccion` | Irlanda: el empleador elige entre día y dinero |
| `regla_sin_efecto` | Honduras: hay norma y no entrega nada |
| `se_pierde` | Perú, Alemania, Suiza: la exclusión está **escrita** |
| `sin_regla` | Suecia: silencio |
| `no_aplicable` | Países Bajos, Dinamarca: no existe feriado legal pagado |

Y separado, el **efecto**, que es lo único que la métrica necesita:
`dia_libre` · `dinero` · `dia_o_dinero_a_eleccion` · `ninguno` · `indeterminado`.

Polonia lo justifica solo: mecanismo raro, efecto idéntico al de un traslado.
Italia es el reverso: mecanismo fácil de entender, efecto cero en días.
`indeterminado` existe por Nicaragua, cuyo artículo dice que el día «será
compensado» sin decir con qué — elegir por ella sería imputar.

**`se_pierde` no se funde con `sin_regla`.** Alemania y Suiza tienen anclaje
textual negativo: su norma dice expresamente que ahí no hay nada. Un cero con
norma detrás no es un cero por omisión, igual que callar no era delegar.

### 36.3 · La fecha de carga

Se carga el valor vigente **al 1 de enero del año del corte**. No es elección
nueva: es la fecha que el proyecto ya usa en `mediciones`, y usar otra haría que
la jornada y los feriados se midieran en momentos distintos del mismo corte.

Importa porque tres unidades cambian dentro de la ventana y dos dentro del propio
2026: Chile pasa a 42 horas el 26 de abril y Colombia el 15 de julio, así que al
corte los dos están en 44. México escalona 48 → 40 entre 2026 y 2030 y al corte
está en 48. Las escaleras completas se conservan en la captura para poder
recalcular a cualquier fecha.

### 36.4 · La normalización vive en el cargador, no en las capturas

Los cinco lotes usaron vocabularios distintos porque la plantilla que les di
llevaba ejemplos y no dominios cerrados. La culpa es mía y la corrección va en
`scripts/cargar_jornada.py`, en un solo sitio y a la vista.

**No se reescriben las capturas ajenas para uniformarlas.** Uniformar el archivo
de otro borra la razón por la que lo escribió así, y esa razón es justo lo que
distingue el `null` de Chile —rango legal— del de Turquía —silencio—.


---

## §37 · El conteo esperado, y por qué la comparación entre cortes lo exige

El proyecto mide la **evolución de un derecho legal entre dos cortes**. Ese
estimando obliga a una decisión sobre los feriados que parece técnica y no lo es.

Un feriado en fecha fija cae en fin de semana unos dos años de cada siete. Si el
conteo usa el calendario del año del corte, la cifra de una unidad **se mueve sin
que cambie ninguna ley**, y esa variación entra en la comparación 2016–2026 como
si fuera reforma.

### 37.1 · Cuánto pesa, medido

| conteo | unidades que cambian más de un día entre cortes | mediana del cambio absoluto |
|---|---:|---:|
| realizado en el año del corte | **23 de 45** | **1,85 días** |
| esperado | 10 de 45 | **0,00 días** |

Con valores realizados, la mitad de la muestra se mueve y el país mediano se
desplaza 1,85 días — **del mismo orden que las reformas que el proyecto busca**.
Con la esperanza, el país mediano se mueve exactamente cero, y las que se mueven
son las que reformaron: Corea +16, España +12,8, Indonesia +12, El Salvador
+10,3, Grecia +4,3, Rumanía +3,9, Perú +3,1, Eslovaquia −2,9.

**Separar la rotación del calendario de la reforma real es exactamente la
distinción que este proyecto existe para hacer**, y el conteo realizado no la
hace.

### 37.2 · Qué se promedia, y qué no

La esperanza es defendible porque **no suaviza el conjunto: toca la mitad**.
Medido sobre el corte de 2026:

| clase | peso | probabilidad de liberar |
|---|---:|---|
| lo rescata la ley, caiga donde caiga | 32 % | 1 |
| anclado en Pascua | 14 % | 1 ó 0, **determinista** |
| ordinal o trasladado a día objetivo | 3 % | 1 ó 0, determinista |
| **fecha fija sin rescate** | **49 %** | (7 − días de descanso) ÷ 7 |

El caso de Pascua merece la explicación porque no es obvio: la Pascua es
**siempre domingo**, así que el desplazamiento del feriado fija su día de la
semana para todos los años. El Viernes Santo es viernes siempre. No hay nada que
promediar.

### 37.3 · Por qué no vale suponer que ninguno cae en fin de semana

Es la alternativa evidente y hay que descartarla por escrito, porque parece más
simple: contar todos los feriados como si todos liberaran.

**Le da a la unidad que traslada y a la que no exactamente el mismo número.** Y
esa diferencia vale de cero a seis días según el país —Colombia no pierde ninguno
porque su ley Emiliani los traslada al lunes; Rumanía pierde cinco y medio—. La
simplificación borraría uno de los dos hallazgos que la captura de jornada vino a
producir.

### 37.4 · Lo que la esperanza no arregla

La cifra publicada deja de ser «lo que ocurrió en 2026» y pasa a ser «lo que
ocurre en un año típico». Para un derecho legal es el estimando correcto, pero
**no describe ningún año concreto** y no debe presentarse como si lo hiciera.

Y los feriados efectivos pasan a ser **fraccionarios**: Austria tiene 10,4 y no
10. Es una esperanza, no un recuento, y el rótulo tiene que decirlo o se lee como
un error de redondeo. `--conteo realizado` sigue disponible para quien quiera el
calendario de un año concreto.

## 38. El nombre de la jurisdicción es dato, y lleva idioma

El paquete pasa a publicarse en dos idiomas, con el inglés como versión por
defecto. Esta sección fija lo que eso obliga a cambiar en la **medición**, no en
la redacción.

### 38.1 Qué lleva idioma y qué no

Lleva idioma el texto que el proyecto **escribe**: los nombres de país y de
jurisdicción de referencia, los rótulos de cuadro, la prosa de los apéndices y
las glosas.

**No lo lleva el texto que el proyecto CITA.** Quedan en su lengua original y no
se traducen nunca:

| Qué | Por qué |
|---|---|
| El nombre oficial del feriado | Es el nombre que la norma le da. `Dia do Trabalho` no es una frase que verter: es el identificador contra el que un verificador coteja la fuente. Traducirlo rompe la trazabilidad, que es lo único que el apéndice de verificación tiene. |
| El literal normativo | Es la cita textual. Cualquier retoque nuestro la falsea. |
| El título de la norma y su identificador | Se cita para localizarla; traducido no localiza nada. |

La regla general: **si el lector tendría que poder buscarlo en la fuente, no se
traduce.**

### 38.2 El nombre en inglés es una columna, no una sustitución

`jurisdicciones` gana `nombre_en`. La alternativa era mapear los nombres en la
plantilla inglesa, y se descarta por §6: el archivo tabular publicable seguiría
saliendo en castellano y habría **dos verdades para el mismo hecho**, resueltas
en la capa de formato. Un hecho que aparece en dos documentos con dos valores es
un defecto aunque los dos sean legibles.

Procedencia declarada: los países llevan el **nombre corto inglés de la ISO
3166-1** —de ahí `Türkiye` y `Czechia`, que son los vigentes—. Las ciudades no
tienen norma equivalente: se usa el exónimo inglés establecido donde existe
—Vienna, Copenhagen, Warsaw— y el endónimo cuando no —Guayaquil, Managua—. Eso
es **convención editorial** y va dicho, no disfrazado de estándar.

### 38.3 El formato numérico es del idioma, y por eso la paridad no compara texto

La coma decimal era una decisión tomada **dentro** de la función de formato. Sale
a la llamada: en castellano `32,4`, en inglés `32.4`, la misma cifra bien
formateada dos veces.

De ahí se sigue cómo se comprueba que las dos versiones digan lo mismo.
**Comparar el texto resuelto daría falso positivo en toda cifra decimal**, y una
compuerta que falla siempre acaba aflojada hasta no comprobar nada. Lo que se
compara es:

1. el **conjunto de marcas** —idéntico en las dos versiones—;
2. el **valor subyacente** de cada marca, antes de formatear;
3. la **estructura**: número y nivel de encabezados en orden, número y forma de
   los cuadros, figuras referenciadas.

Los títulos difieren entre idiomas por definición; las estructuras y los valores
no pueden. Es la misma preferencia de §35 por la prueba estructural sobre la
aritmética: la estructural no tiene modelo propio que equivocarse.
