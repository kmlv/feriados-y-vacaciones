# Registro de congelamiento de protocolos

Este archivo es append-only. Cada entrada fija una versión de protocolo con su
hash, para que cualquier dato recolectado pueda atribuirse a un conjunto de
reglas exacto y verificable.

**Cada entrada congelada apunta a su copia inmutable en `docs/archivo/`, nunca al
documento vigente.** El vigente es `docs/02-protocolo.md` y cambia; una entrada
que lo cite deja de reproducirse en cuanto alguien lo edita. Así se rompió este
registro: cuatro entradas citaban el mismo archivo mutable, una copia archivada
estaba etiquetada v2.3 y contenía otra cosa, y v2.6 no tenía copia.

## Copias archivadas sin entrada propia

El verificador exige una **biyección**: toda copia de protocolo en
`docs/archivo/` tiene exactamente una entrada, y toda entrada apunta a una copia
existente. Es lo que impide que una entrada desaparezca sin dejar rastro —por
borrado, por registro vacío o por homoglifos en las etiquetas de su tabla—, que
es como el verificador fallaba abierto antes.

Las copias que legítimamente **no** son versiones congeladas se declaran aquí, y
este script las lee del registro. Una excepción declarada es visible; una
excepción escondida en el código del verificador es un agujero con otro nombre.

| Archivo | Por qué no tiene entrada |
|---|---|
| `docs/archivo/02-protocolo-v2.3-correccion-editorial.md` | No es una versión: es v2.3 con el título corregido, archivada al descubrir que su hash se había anotado bajo v2.2. La entrada de v2.3 es la que cuenta. |

---

Verificar **todo** el registro —única forma admitida de afirmar que está sano—:

```bash
python3 scripts/verificar_congelamiento.py
```

---

## feriados · v1.0

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-feriados-v1.0.md` (superseded por v1.1) |
| SHA-256 | `696c961f81cdd3ee9dbd5c7914fd3f0b45dbfb3133e8151ef765801e939f16c7` |
| Fecha UTC | 2026-08-07T17:30:36Z |
| Commit | (el de este archivo; ver `git log`) |
| Principal | Kristian López Vargas |
| Revisión de esquema | la revisión cruzada — `[blocker]` cerrado, hilo T-001 rev 26 |
| Registro público | Ninguno, por decisión del principal |

**Decisiones del principal incorporadas:** estimando triple sobre hechos
atómicos; los tres constructos A/B/C derivados; subnacional nacional + ponderado;
tres pantallas concurrentes para declarar "sin cambio"; ventana 2015–2026 anual;
agentes IA con adjudicación humana ciega; los cuatro atributos opcionales;
traducción automática válida citando el original; producto = dataset público
citable; jurisdicción de referencia = ciudad más poblada; frontera con vacaciones
diferida; congelamiento con hash sin registro público.

**Adoptado por defecto, sin pronunciamiento del principal:** C-03 — panel no
balanceado + vista balanceada, sin relleno retroactivo de fronteras.

**Deuda registrada para implementación (no bloqueante):** `especificacion` como
gramática canónica validable; claves foráneas y cardinalidades de
`determinacion_id`.

**Regla de cambio:** toda modificación del protocolo abre una versión nueva con
su propio hash y **obliga a recalcular el panel completo**. No se aplican
cambios de regla sobre datos ya recolectados sin recálculo.

---

## feriados · v1.1

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-feriados-v1.1.md` (superseded por v2.0) |
| SHA-256 | `d89514d480633312c484e0dfa00bcf45be6ba9ea3616264435664ba5567b0400` |
| Fecha UTC | 2026-08-08T04:55:41Z |
| Supersede a | v1.0 (`696c961f…`), archivada en `docs/archivo/` |
| Principal | Kristian López Vargas |
| Registro público | Ninguno, por decisión del principal |

**Qué cambió.** El panel de niveles pasa de doce cortes anuales a **dos cortes,
1-ene-2016 y 1-ene-2026**. El **ledger de reformas y la semilla siguen cubriendo
el intervalo completo**, que es lo que preserva las fechas de reforma, las
reversiones y los feriados transitorios. Nueva regla de tolerancia del ancla
2016: ±1 año con `fecha_efectiva_de_medicion` obligatoria por celda y publicación
de la distribución de desviaciones.

**Recálculo exigido por §9:** costo cero. El cambio ocurrió antes de recolectar
el primer dato.

**Se pierde y queda declarado:** no hay serie anual de niveles; no se pueden
estimar tendencias sobre el nivel ni usar especificaciones que requieran
variación anual en esa variable.

---

## feriados y vacaciones · v2.0 — nunca recolectada, superseded por v2.1

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.0.md` (archivada; el hash corresponde al estado revisado por la revisión cruzada, renombrado a v2.1 despues) |
| SHA-256 | `99174c0b1f8b43916905745e8f7992e56ee3bb3505aeeedfeed4d10a5003a0a8` |
| Fecha UTC | 2026-08-08T05:55:25Z |
| Supersede a | v1.1 (`d89514d4…`) y a `05-definiciones.md`, ambos archivados |
| Principal | Kristian López Vargas |
| Registro público | Ninguno, por decisión del principal |

**Qué cambió.** Documento operativo único. Entran **ambas variables** al mismo
diseño; los tres constructos de feriados se reconcilian en **dos columnas ×
nominal/efectivo**; la frontera entre variables queda resuelta con regla de
imputación; el modelo pasa a **dos módulos de hechos sobre capa de derecho
común**; los rangos los resuelve el trabajador de referencia; y se incorpora el
**piso supranacional** con mínimo efectivo derivado.

**Refinamientos que salieron de revisar el material archivado:** escala de
antigüedad como campo obligatorio y como tipo de evento del ledger — es el
riesgo que podría convertir la rigidez observada en un artefacto de codificación;
nuevo tipo de evento "reforma de reglas sin cambio de quantum"; advertencia
obligatoria de interpretación sobre el delta cero; semilla priorizada de
candidatos a auditar importada del archivo; y el registro de divergencias de
definición con el material importado.

**Recálculo exigido:** costo cero. Sigue sin recolectarse el primer dato.

---

## feriados y vacaciones · v2.1

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.1.md` (archivada) |
| SHA-256 | `35799de6b74af4e7ec404f929377bc3e68f8f8f3bcc8118a99f06e265b439ca0` |
| Fecha UTC | 2026-08-08T06:01:26Z |
| Supersede a | v2.0 (`99174c0b…`), nunca recolectada |
| Revisión | **CERRADA.** la revisión cruzada: tres `[blocker]` aceptados y verificados, luz verde para recolectar. La revisión de diseño: sin blockers |
| Principal | Kristian López Vargas |

**Qué cambió respecto de v2.0.** (1) El total de la frontera se define como
**esperanza bajo distribución de fechas de inicio declarada**, con fórmula
versionada; `sin_regla_explicita` va a `NA` con intervalo de sensibilidad en vez
de asimilarse a `extienden`. (2) La antigüedad del trabajador de referencia se
fija en **doce meses exactos** —v2.0 se contradecía— y la escala pasa a ser una
**tabla de tramos versionados** en vez de dos campos descriptivos. (3) Se
restituyen dos garantías que v1.1 tenía y la consolidación había perdido:
identificación polimórfica de hechos con cardinalidades en `evidencia`, relación
`reforma_versiones`, y la tabla `mediciones` que hace auditable la tolerancia de
±1 año. (4) El piso supranacional pasa de atributo a tabla con vigencia y
aplicabilidad acreditadas.

**Recálculo exigido:** costo cero. Sigue sin recolectarse el primer dato.

---

## feriados y vacaciones · v2.2

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.2.md` (archivada) |
| SHA-256 | `857f05a4d2cb70a47d8b4f0d35b3ff975551eb66e9a60daf5335733db594b054` |
| Fecha UTC | 2026-08-08T16:31:42Z |
| Supersede a | v2.1, nunca recolectada |
| Principal | Kristian López Vargas |

**Qué cambió.** Se añade la **banda de colocación** (§4.3): el total se calcula
bajo tres supuestos —mínimo, esperado y cota estilizada— y la **amplitud** pasa
a ser variable propia, como medida de flexibilidad normativa. Objetivo fijado en
días de trabajo programados, pagados y no trabajados. Nuevos: tabla
`particiones_admisibles`, campo `control_del_momento` con sus derivados
`cota_accesible_al_trabajador` y `cota_negociable`, y degeneración derivada como
`max == min` con causa. §17bis marca la banda como constructo conductual, fuera
de las columnas de derecho.

**Revisión de la banda (segunda pasada).** la revisión cruzada levantó cuatro `[blocker]`:
particiones admisibles no representables con escalares; dominio de fechas
admisibles ausente; `de_comun_acuerdo` no otorga acceso; y caracterización de
degeneración no exhaustiva. Los cuatro aceptados. La serie se redefine como
**cota estilizada renombrada**, con sus exclusiones publicadas junto a la
columna. La revisión de diseño: sin blockers; su propuesta de dos archivos físicos fue declinada
por el principal y queda como riesgo asumido en §22.

**Recálculo:** costo cero. Sin dato recolectado.

**Corrección editorial 2026-08-08** (no cambia ninguna regla): el título decía
v2.2 y el conteo de unidades decía 48 cuando el grupo congelado tiene 47 —46
comparadores más la base—. Detectado por el review de la revisión adversarial. Hash actualizado
a `7af4470964a523234693d63f52ade3b80b57f50d47afd5af5468492308f1512c`.

**Corregido 2026-08-09, al recalcular:** ese hash **no es de v2.2**. La
corrección se aplicó cuando el archivo ya se llamaba v2.3, así que corresponde al
documento v2.3 con el título arreglado, y está archivado como
`docs/archivo/02-protocolo-v2.3-correccion-editorial.md`. Anotarlo bajo v2.2 hizo
que el archivo etiquetado v2.3 contuviera este estado en vez del que declara la
entrada v2.3. No se ve leyendo: aparece al recalcular los hashes.

---

## feriados y vacaciones · v2.3 — superseded por v2.4

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.3.md` (archivada) |
| SHA-256 | `1328063acdd907db90612a64ea383d8a8be09d6a4346b75a1a55d94bb6474b23` |
| Fecha UTC | 2026-08-08T16:54:01Z |
| Supersede a | v2.2, nunca recolectada |
| Revisión | la revisión cruzada y la revisión de diseño: luz verde con condiciones, todas aplicadas |

**Qué cambió.** Grilla de antigüedad a **1, 5 y 10 años** (§3.2.1), derivada de
la tabla de tramos. Nuevo campo `base_antiguedad` con su regla de
reconocimiento —hecho faltante que detectó la revisión cruzada y que ni la revisión de diseño ni yo habíamos
visto—. Convención de frontera `[desde, hasta)` sin huecos ni solapamientos, con
el operador literal de la fuente conservado en `operador_frontera` y
granularidad de fecha donde haya fronteras submensuales. §3.2.2 advertencia
estructural de corte transversal frente a cohorte, con la advertencia en el
nombre de la variable. §3.2.3 separa `sin_diferencia_en_grilla_1_5_10` de
`escala_sin_escalonamiento`, que no son lo mismo. §3.2.4: la banda de colocación
no se replica en la grilla.

**Recálculo:** costo cero. Sin dato recolectado.

---

## feriados y vacaciones · v2.4 — superseded por v2.5

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.4.md` (archivada) |
| SHA-256 | `759c6ed6c1a0dba7740658c81d6a0daaa7b4762297de47365af8f0dfad760ab9` |
| Fecha UTC | 2026-08-09T00:00:10Z |
| Principal | Kristian López Vargas |

**Qué cambió.** §23 nueva: antecedente externo. El índice del CBR puede aportar
candidatos con fecha y cita, y evidencia de existencia de reforma, pero **no
puede confirmar ausencia de cambio ni probar el quantum** — su nivel de fuente
es 4, no 1. **Captura ciega obligatoria**: quien codifica no ve el valor externo
antes de capturar, la concordancia nunca eleva `estado_verificacion`, y la
muestra de doble codificación se estratifica hacia celdas divergentes.

Tres tablas nuevas —`medicion_externa`, `reforma_externa`, `crosswalk_causa`—
**fuera del registro `hechos`**, y cuatro validaciones que impiden verificar una
celda sólo con el antecedente y exigen declarar la causa de divergencia.

**Recálculo:** costo cero. Paso 1a ya ejecutado pero no escribe hechos.

---

## esquema · borrador — APROBACIÓN RETIRADA 2026-08-09

> **Esta entrada certificaba hashes y estatus que ya no son ciertos.** Se
> aprobó el esquema con 24 tablas y 19 validaciones; después cambió
> sustancialmente y el comando de verificación que instruye **hoy falla**.
> Un registro que certifica un hash obsoleto es peor que no tener registro:
> afirma una garantía que no existe.
>
> **Estado real: NO APROBADO.** El esquema está en revisión adversarial
> activa. Los hashes de abajo son el registro de lo que se aprobó entonces,
> no de lo que hay ahora.

Estado histórico de aquella aprobación: **No es todavía el DDL definitivo**: por diseño se congela
después del piloto (paso 3 del plan), porque el esquema aún no ha tocado un
texto legal.

| | |
|---|---|
| `schema/draft/001_schema.sql` | `530d4adf7d6508c5ffff59633a61c38c902a0496fa69f061788371a8e8f7c989` |
| `schema/draft/900_validaciones.sql` | `68bd2f132343227f8dcfeff54249be6abeaa4e0eefc370fad1197aa2515eb2e7` |

24 tablas · 24 triggers · 19 validaciones.

Verificar:

```bash
shasum -a 256 schema/draft/001_schema.sql schema/draft/900_validaciones.sql
```

**Cómo se llegó aquí.** 41 revisiones en el hilo T-001 y 80 menciones de
`[blocker]`. Cada ronda se cerró **ejecutando**, no leyendo: la revisión cruzada cargaba el
esquema en una base desechable e intentaba insertar estados prohibidos.

Las tres lecciones que quedaron escritas en los archivos, porque son
transferibles:

1. **"Ejecuta limpio" sólo prueba sintaxis.** La primera versión ejecutaba sin
   errores y aceptaba una fecha 2026-99-99.
2. **Un falso positivo es tan grave como un falso negativo.** Una validación que
   marca infactible lo factible empuja a corromper dato bueno para callar la
   alerta.
3. **La lógica de tres valores hace fallar abierto.** En SQL, `x <> NULL` es
   NULL y un `CHECK` que evalúa a NULL **pasa**. Este error apareció dos veces,
   en sitios distintos, con veinte minutos de diferencia.

---

## feriados y vacaciones · v2.5 — superseded por v2.6

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.5.md` (archivada) |
| SHA-256 | `a034910c0df6f0df526bb467ca870603aea2c57b2ed5c7bfd0daad5382d1b1d1` |
| Fecha UTC | 2026-08-09T03:24:47Z |

**Enmienda sustantiva, no implementación.** §24: el campo `control_del_momento`
se elimina y lo reemplaza la tabla `regla_colocacion`, hija de
`vacaciones_version`, con precedencia, alcance y dos atributos condicionales.
Motivo doble: el enumerado presuponía que alguien decide —y `trabajador` no se
instanciaba en ninguna unidad—, y sobre todo aplanaba reglas en capas que existen
en el derecho revisado.

**La derivación de la cota accesible pasa a ser restrictiva por defecto**, y se
declara que será `NA` en casi todo el universo. Eso no es defecto de la
derivación: es el hallazgo. El silencio aprobatorio no garantiza nada, y la
colocación que maximiza el tiempo libre es la que más probablemente choca con la
causal de veto.

---

## feriados y vacaciones · v2.6 — superseded por v2.7

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.6.md` (archivada) |
| SHA-256 | `3c5856acbd0e7a0a1c5bdfc2f0aa0ecc572a42017c22ced02525453900f19b1c` |
| Fecha UTC | 2026-08-09T03:34:06Z |

**§24 reescrita y §25 nueva.** Las reglas de colocación distinguen **partición**
de **cascada**: no son la misma estructura, y tratar la cascada belga como
porciones exigía inventar días que la norma no contiene. Se restaura `sin_regla`
como estado sustantivo —Alemania no tiene regla de silencio, que no es lo mismo
que "el silencio no aprueba"—. Las reglas pasan a ser hechos evidenciables con su
propia procedencia, porque las capas vienen de instrumentos distintos.
`lote_captura` declara versión y hash de protocolo: un comentario de cabecera se
desincroniza, y se había desincronizado.

**Retirada una sobreafirmación:** que la cota accesible sea `NA` en casi todo el
universo es una predicción del diseño, no un hallazgo. Nadie ha medido nada aún.

---

## feriados y vacaciones · v2.7 — superseded por v2.8

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.7.md` (archivada) |
| SHA-256 | `d625aa627ed9e93e4bcd50715ef57e3a06b18a332bd1d69ef545d3b35116bb3b` |
| Fecha UTC | 2026-08-09T03:50:29Z |

**§24.2 especifica la cascada**, que hasta ahora existía en el esquema y no en el
protocolo: modo de aplicación, raíz incondicional, condición de vocabulario
cerrado, y el rechazo de grupos de un solo nivel.

**§24.3 corrige la sobreafirmación en su sitio.** La retractación anterior vivía
en §25.2 y dejaba al documento contradiciéndose consigo mismo. Cuarta lección de
método: una retractación tiene que corregir el original, no anexarse.

---

## feriados y vacaciones · v2.8 — superseded por v2.9

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.8.md` |
| SHA-256 | `84226656f212ac8c74a6eb573935f2400dc963e41fee5d100e69dda7bdc5c45c` |
| Fecha UTC | 2026-08-09T04:15:00Z |

**Corrección de puntero, 2026-08-09.** Esta entrada nació apuntando al documento
vigente, que es exactamente lo que la cabecera de este registro y §26 prohíben.
La copia archivada se creó después y es idéntica byte a byte: el hash no cambió,
así que el hecho que la entrada certifica es el mismo y sólo se movió el puntero
a una ruta estable. Se deja escrito en vez de repuntarlo en silencio.

**§24.2 especifica la composición, que era lo que faltaba.** La cascada ya tenía
forma —raíz, condición, grupos de más de un nivel— pero no tenía aritmética: la
unidad de asignación es la porción reclamada, y una cascada reclama una sola por
grupo. Exclusividad del alcance total, un residual como máximo, residual definido
contra alguna porción, suma acotada por el derecho y unidades no mezclables, todo
contando cascadas y particiones juntas.

**Por qué era necesario.** Mientras las comprobaciones aritméticas filtraban por
modo partición, etiquetar una regla como cascada la eximía de todas. Medido: una
cascada de 0,6 más una partición de 0,5 más residual sumaba 1,1 del derecho con
cero violaciones; una cascada en días y una partición en fracción convivían sin
base de conversión; y dos cascadas residuales reclamaban las dos el remanente.

**§26 nueva: el vigente deja de llevar versión en el nombre.** Se llama
`docs/02-protocolo.md` y cada congelamiento deja copia inmutable en
`docs/archivo/`. El nombre versionado era la causa de que este registro apuntara
cuatro veces a un archivo mutable.

**Recálculo:** costo cero. Sigue sin recolectarse el primer dato.

---

## artefactos archivados y reproducibles

Las once versiones anteriores están en `docs/archivo/`, recuperadas del historial
de git. Cada entrada de este registro apunta a la suya, no al vigente.

Verificar el registro entero, que es lo único que acredita que está sano:

```bash
python3 scripts/verificar_congelamiento.py
```

## esquema — CONGELADO 2026-08-10 (v2.15)

**Este es el bloque de estado vigente.** La marca de abajo es la que hace que el
verificador compruebe estos hashes contra los archivos reales. No se borra ni se
duplica: sin ella el chequeo deja de correr en silencio, y con dos hay dos
estados actuales.

| | |
|---|---|
| `schema/draft/001_schema.sql` | `fb93bcabebaed914a91c10d27192e56c2905760e59e883e4e86c61331c2d026c` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |

26 tablas · 27 triggers · 1 vista · 37 validaciones · **en revisión adversarial.**

La vista `asignacion_colocacion` es la que hace contable la cascada: expone una
unidad de asignación por regla de partición y una por grupo de cascada, y sobre
ella corren V24 a V27 y V37.

Suite adversarial reproducible, con las dos mitades que hacen falta —los estados
prohibidos deben rechazarse y las estructuras fieles deben entrar limpias—:

```bash
python3 scripts/probar_colocacion.py
```

---

## feriados y vacaciones · v2.9

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.9.md` |
| SHA-256 | `cb1532b2d71ec8b389cdbcbc9176cdff7e7ecfb6e5c66659f9e41d34ee8b0e66` |
| Fecha UTC | 2026-08-09T19:55:00Z |
| `schema/draft/001_schema.sql` | `fc77897f2c9261286f1987b4a099b88878ef0c86681205f1ed7f4b88f1690156` |
| Revision de esquema | la revisión cruzada rev124 — residuo SILENCIOSO cerrado parcialmente y declarado |

**Endurecimiento del catalogo, y una limitacion declarada.** El ataque de la revisión cruzada
sobre v2.8 sembraba `v2v.8` con hash ficticio y ruta vacia, ataba un lote y
cerraba el ciclo sin violacion. Ahora la version exige forma exacta `vN.N` y la
ruta debe estar bajo `docs/archivo/` y terminar en `.md` — la regla de §26 era de
prefijo de ruta, y eso si es expresable en SQL.

Lo que SQLite no puede hacer —leer el disco, calcular SHA-256— queda como
**limitacion declarada en §25.1**, por decision del principal: no se convierte el
verificador en puerta obligatoria del ciclo de captura. El parrafo de §25.1 que
prometia de mas se corrigio **en su sitio**.

**Excepcion eliminada.** El verificador eximia de la regla «nunca al vigente» a
las entradas tituladas `VIGENTE`, y v2.8 se congelo amparada en eso. La copia de
v2.8 se creo a posteriori, identica byte a byte, y la correccion del puntero
quedo escrita en su entrada.

Suite reproducible del catalogo, con las dos mitades y la limitacion ejecutada:

```bash
python3 scripts/probar_catalogo.py
```

---

## feriados y vacaciones · v2.10

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.10.md` |
| SHA-256 | `17536127495a3808f298697271ec49896f59eec309a33ffc6b945dc5340b4024` |
| Fecha UTC | 2026-08-09T20:30:00Z |
| `schema/draft/001_schema.sql` | `1f4eb1f6d790155de122e87cf8cb4eb82b51ccbb8ee17142c996b751caae9599` |
| Hallazgo | la revisión cruzada rev131 — travesia de ruta sobre el CHECK introducido en v2.9 |

**Un prefijo de ruta no acota una ruta que puede volver hacia atras.**
`docs/archivo/../02-protocolo.md` casaba con el CHECK de v2.9 y resolvia al
documento vigente, que es justo lo que la regla prohibe; tambien entraban la
barra doble y la travesia desde subdirectorio. El cierre no enumera travesias
—esa carrera se pierde— sino que usa un hecho de la estructura: **el archivo de
protocolos es plano**, asi que lo que sigue al prefijo no lleva ninguna barra.
La misma comprobacion se replico en `verificar_congelamiento.py`, donde el CHECK
de SQLite no alcanza.

**Tres fixtures corregidos de paso.** Al endurecer la ruta, tres casos negativos
de `probar_colocacion.py` pasaron a fallar por la ruta en vez de por su hash, su
version o su marca de tiempo — rechazados por el motivo equivocado, que es el
primer patron de fallo de esta serie. Y el caso llamado «catalogo legitimo»
apuntaba al documento vigente: que pasara era el defecto, no la prueba.

---

## feriados y vacaciones · v2.11

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.11.md` |
| SHA-256 | `7f2df0325ba1fae716f47438a34b037fc17ea602425d6dfb2c17fc24be68bad8` |
| Fecha UTC | 2026-08-09T20:35:00Z |
| `schema/draft/001_schema.sql` | `1f4eb1f6d790155de122e87cf8cb4eb82b51ccbb8ee17142c996b751caae9599` |
| Hallazgo | la revisión cruzada rev137 — el verificador externo fallaba abierto ante SHA malformado |

**Una puerta que falla abierta no es una puerta.** El parseo reconocia una
entrada solo si su hash ya casaba con 64 hexadecimales, asi que un hash corrupto
no daba error: **hacia desaparecer el bloque**. El verificador comprobaba las
doce entradas restantes y anunciaba que todas reproducian, con salida 0. El
defecto era peor que los que el verificador detecta, porque afectaba al
mecanismo del que depende la limitacion declarada en §25.1.

Causa: dos preguntas fundidas en una —si el bloque pretende ser entrada, y si
esta bien formado—. Separadas, la primera decide si se examina y la segunda si
pasa. Regresiones nuevas en `scripts/probar_verificador.py`, que corrompe el
registro en memoria y exige salida 1 en siete formas distintas.

**Nit de la revisión cruzada, cerrado derivando en vez de reescribiendo.** El resumen de
`probar_colocacion.py` decia «las cuatro estructuras fieles» cuando ya corrian
seis. El numero se cuenta ahora; un literal a mano se desincroniza igual que se
desincronizo la cabecera del DDL.

```bash
python3 scripts/probar_verificador.py
```

---

## feriados y vacaciones · v2.12

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.12.md` |
| SHA-256 | `899d8c435eae6cadb24135b249b0e3ee1f4f096bd6fa7010a927206c824ef64d` |
| Fecha UTC | 2026-08-09T20:50:00Z |
| `schema/draft/001_schema.sql` | `1f4eb1f6d790155de122e87cf8cb4eb82b51ccbb8ee17142c996b751caae9599` |
| Hallazgo | la revisión adversarial rev140 — el fallo abierto persistia un nivel mas arriba |

**Verificar lo que un registro dice contener no dice nada sobre lo que deberia
contener.** la revisión adversarial reviso el arreglo de v2.11 —porque quien lo escribio no puede
aprobarlo— y encontro que la clase de defecto seguia abierta: registro vacio,
entrada borrada y homoglifos cirilicos en las etiquetas producian los tres una
salida 0 anunciando exito. Y el titulo no se leia, asi que una version duplicada
o apocrifa pasaba igual.

**Ancla, no parche por sintoma.** Biyeccion entre las copias de
`docs/archivo/02-protocolo*.md` y las entradas; el nombre del archivo debe llevar
la version de su entrada; las copias que no son versiones congeladas se declaran
en una tabla del registro que el verificador lee. Los enlaces simbolicos en el
directorio de archivo pasan de ignorarse a fallar.

**Dos hallazgos VISIBLES de la misma revision, cerrados.** El bloque de estado
actual declaraba un hash de esquema de dos versiones atras y no se comparaba con
nada. Y las regresiones se conformaban con salida 1: ahora **cada caso declara
que mensaje espera**, porque fallar por otra razon es indistinguible de no haber
probado nada.

```bash
python3 scripts/probar_verificador.py   # 15 corrupciones + señuelo simbolico
```

---

## feriados y vacaciones · v2.13

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.13.md` |
| SHA-256 | `5595381ce9aae71bf2b9c7920ec32099fcbea6492aec4f614d77a4720e4eea51` |
| Fecha UTC | 2026-08-09T23:55:00Z |
| `schema/draft/001_schema.sql` | `35856e089c2eefd51fd90440e40ae440c411884ec2c1c4c6b44593adadeb90da` |
| Origen | Piloto de ocho unidades; cuatro decisiones del principal |

**El piloto hizo su trabajo.** Las ocho unidades produjeron normas reales que el
esquema no podia representar, y ninguna se forzo. Cuatro decisiones de
constructo, todas del principal:

1. `clase_de_regla` gana `delegada_a_jurisdiccion_local` — Guatemala y El
   Salvador conceden un feriado cuya fecha fija la costumbre local, sin
   instrumento que la determine.
2. `tipo_de_dia` gana `werktage` y `semanas`, y entra `base_semanal_dias` —
   Alemania concede 24 Werktage sobre semana de seis dias, y codificarlos como
   habiles sobreestima su derecho en un quinto.
3. `periodo_anios` — Mexico concede un feriado cada seis anios, y con dos cortes
   eso produciria un delta que no es una reforma.
4. `iniciativa` gana `asignacion_estatal` — en Indonesia 8 de los 12 dias de
   vacaciones vienen con fecha puesta por decreto y descuentan del saldo.

```bash
python3 scripts/probar_decisiones_piloto.py
```

---

## feriados y vacaciones · v2.14

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.14.md` |
| SHA-256 | `163d1a2863bccb1bfe788f2748ef3149c18851bf6b86dbf3522c5fd19b753861` |
| Fecha UTC | 2026-08-10T00:45:00Z |
| `schema/draft/001_schema.sql` | `d6058841ca2adf2cb89ee65d0950a018ac663d4b82c3eb5d3394437d61274010` |
| Origen | Carga de las ocho unidades; dos clases de fecha que faltaban |

**Dos feriados de noventa y cuatro no entraban, y el cargador se nego a
forzarlos.** `relativa_a_fecha` para el Victoria Day de Ontario —el lunes
anterior al 25 de mayo, con el signo del desplazamiento como direccion— y
`remision_normativa` para la jornada electoral mexicana, que obliga a citar a que
norma remite y prohibe toda fecha propia.

Van separadas a proposito: una sola clase «no determinable» habria escondido que
el Victoria Day SI es calculable y puede generar ocurrencias.

**Estado del piloto: 94 feriados en ocho unidades, cero omitidos, 37 validaciones
en cero.** Una cuarta parte no lleva fecha escrita en su norma.

```bash
python3 scripts/cargar_piloto.py --validar
python3 scripts/probar_decisiones_piloto.py
```

---

## feriados y vacaciones · v2.15 — ESQUEMA CONGELADO

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.15.md` |
| SHA-256 | `f26c28e9ac7c087a7eaa86cddbc1da397f0862021a61c421b20940df5097dc63` |
| Fecha UTC | 2026-08-10T13:00:00Z |
| `schema/draft/001_schema.sql` | `8c9efbed67fe71f59a47f2dd6143c7d49c21f5be1bc951bd8ac59246e407987f` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Base del piloto | 95 feriados y 8 titularidades en 8 unidades; 37 validaciones en cero |

**El piloto cierra y el esquema se congela.** Orden fijado por el principal:
cerrar primero los pendientes de captura, porque son la clase de caso que rompio
el esquema siete veces, y descongelar obliga a recalcular lo recolectado.

Las ocho imputaciones se verificaron **una por una** en vez de derivarse del tipo
de dia. La correspondencia se confirmo en las ocho, y verificar cambio el
resultado en un caso: **El Salvador art. 178 dice explicitamente que los asuetos
comprendidos en el periodo NO prolongan su duracion**, y ademas prohibe que las
vacaciones se inicien en tales dias.

**Queda declarado al congelar:** seis fuentes en nivel 4 por elevar; el corte 2016
sin capturar en Indonesia y El Salvador, no rellenado; delta cero sin verificar la
ausencia en Guatemala y Toronto; y los feriados religiosos turcos sin capturar.

```bash
python3 scripts/cargar_piloto.py --validar
python3 scripts/panel.py
```

---

## feriados y vacaciones · v2.16

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.16.md` |
| SHA-256 | `8d49ae47bcb1a0e48264911ec492cbcd4639a3ff21034bfbfdc94e760eefce94` |
| Fecha UTC | 2026-08-10T20:00:00Z |
| `schema/draft/001_schema.sql` | `397ca90ffcb18d7193e59cdeb1b46b616220f0d245f5b422cab3ada37687f04a` |
| Origen | Escalado a las 47 unidades; cinco capturadores independientes |

**Descongelar estaba previsto y es barato aqui**, porque el panel se deriva de la
base con un comando.

`ancla` gana `pascua_ortodoxa` y `equinoccio_septiembre`. Dos lotes encontraron el
mismo hueco y lo resolvieron AL REVES: uno codifico los feriados ortodoxos rumanos
como `pascua`, que da fecha equivocada en silencio, y el otro omitio los griegos.

Cuatro defectos del cargador destapados por los datos, el peor una afirmacion mia:
el campo de vigencia admitia solo anio «porque dentro del anio da igual», y
Portugal repuso cuatro feriados el 2 de abril de 2016 — 13 feriados donde van 9,
borrando la reversion que el proyecto buscaba.

**Queda declarado y abierto:** una quinta unidad de conteo (Israel), la escala por
EDAD (Hungria, Noruega, Suiza), la imposibilidad de fechar reformas de vacaciones,
la colocacion en cascada en seis unidades, las reglas de fecha disyuntivas, la
cuota tailandesa, y si las bases semanales puestas fueron leidas o elegidas.

---

## feriados y vacaciones · v2.17

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.17.md` |
| SHA-256 | `750e2f33bfaf8c1a67f780fea59ddf2c46b0ff1a73b7e37c52f17e0f5238cbce` |
| Fecha UTC | 2026-08-10T20:35:00Z |
| `schema/draft/001_schema.sql` | `fb93bcabebaed914a91c10d27192e56c2905760e59e883e4e86c61331c2d026c` |
| Origen | Escalado a 47: ocho unidades definen el derecho contra el horario del trabajador |

`base_semanal_origen`. Exigir la base semanal siempre fue correcto para Alemania y
no es general: Nueva Zelanda, Paises Bajos, Japon y Paraguay definen el derecho
contra el horario DEL TRABAJADOR. Exigir la base ahi obligaba a inventarla, que es
el error de factor dos por la otra puerta. Ahora se declara el origen; omitirla en
silencio sigue prohibido.

---

## feriados y vacaciones · v2.18

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.18.md` |
| SHA-256 | `e192130ee4295fce20e9fce12e0d45a465099148afec04088c40f25a89259f81` |
| Fecha UTC | 2026-08-10T22:00:00Z |
| `schema/draft/001_schema.sql` | `fb93bcabebaed914a91c10d27192e56c2905760e59e883e4e86c61331c2d026c` |
| Origen | Cruce completo contra el CBR sobre las 47 |

**El hallazgo principal, medido.** Convertidas 42 unidades a dias de trabajo
sobre semana de cinco, la diferencia media contra el indice del CBR se ordena por
la unidad en que esta escrita la norma: habil -0,4 · semanas -2,0 · werktage -3,6
· calendario -5,8. Cuanto mas se aleja la unidad legal de dias habiles, mas
generoso aparece el pais.

Peru-Alemania lo resume: en el indice, 1,00 contra 0,67, o sea 49% mas. En dias de
trabajo, 21 contra 20, o sea 7%. La brecha publicada es siete veces la real.

Sin cambios de esquema. Solo protocolo.

---

## feriados y vacaciones · v2.19

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.19.md` |
| SHA-256 | `5f584b19f890ed9ffb48218ef6a81d1ee66bb0a8acd247c1be36a6eec34cd39f` |
| Fecha UTC | 2026-08-11T00:20:00Z |
| `schema/draft/001_schema.sql` | `3eaccce1520293f151720f96426506f58691f64f16212e6a69e29c4e315ce18a` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | Doble codificacion ciega sobre ocho unidades |

**Tasa de fiabilidad — no publicada.** El resultado de la doble codificacion ciega se conserva en la documentacion interna del proyecto y no forma parte de este paquete. La omision se declara en `EXCLUSIONES.md` con su motivo. Los hashes y las fechas de esta entrada no estan tocados.

**Cambio de esquema: `resolucion_desacuerdo` en `regla_colocacion`.** Nueve
unidades codificadas `negociada` escondian seis regimenes distintos de que pasa
cuando el acuerdo no llega — decide el empleador, no puede negarse sin motivo, el
empleador queda obligado a conceder, dirime un tercero, la ley remite al convenio,
o la ley calla. Peru y Grecia salian identicos resolviendo el desacuerdo en
direcciones opuestas. Obligatorio cuando la iniciativa es `negociada`, por CHECK
con igualdad.

**Y una regla de lectura, §34.1:** la colocacion se lee del articulo que fija la
OPORTUNIDAD. Si el literal habla de dividir, acumular o aplazar, no es ese
articulo aunque lo parezca. El error estaba en Peru y la trampa en otras cuatro.

---

## feriados y vacaciones · v2.20

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.20.md` |
| SHA-256 | `b55d76c5f4115dd3a337c514b78bc29e3b459bfe3e62824cea464439328371f9` |
| Fecha UTC | 2026-08-11T02:10:00Z |
| `schema/draft/001_schema.sql` | `a30d6edbc36790195e0e38008cbc15006e00826bdcbf1534233f3ac506ce9188` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | Las cuatro decisiones de constructo sobre los feriados sin clase |

**Cero feriados omitidos en las 47 unidades.** Siete feriados de cinco unidades
estaban fuera del conteo por no tener clase de fecha representable. Cuatro
decisiones del principal los cierran sin inventar ninguna fecha.

Los dos solsticios entran al catalogo de anclas. La clase `lunar` admite el dia
contado DESDE EL FIN del mes, que es como Corea define la vispera del Anio Nuevo.
Nace `cuota_designada_por_empleador`, y con ella Tailandia pasa de 1 a 13 — la
mayor discrepancia de una sola unidad contra el antecedente, ahora coincidente.

Y la de fondo: **un feriado puede tener varias reglas de fecha, cada una con su
condicion, y como maximo una sin condicion.** Existencia condicional y regla
disyuntiva resultaron ser el mismo mecanismo visto desde dos lados — un feriado
cuyas reglas TODAS llevan condicion no ocurre cuando ninguna se cumple, y esa
ausencia de regla por defecto no necesita campo propio.

Chile pasa de 15 a 18, Corea de 17 a 18, Irlanda de 9 a 10 y Tailandia de 1 a 13.

---

## feriados y vacaciones · v2.21

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.21.md` |
| SHA-256 | `7de033a2d99388060bc8793a71e876d15f0ecc9e0e6d78f98dcb8f2410f532a2` |
| Fecha UTC | 2026-08-11T04:30:00Z |
| `schema/draft/001_schema.sql` | `b33114d290d8ba540e424489303852a51b4b2581a7a9e038e3db8959c2efe52c` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | Captura de la jornada semanal legal de las 47 unidades |

**La tabla `regimen_jornada` deja de estar vacia.** Existia desde el disenio y
nunca se habia poblado; ahora tiene las 47, capturadas en cinco lotes. Cierra los
dos huecos que la metrica de descanso habia declarado sobre si misma: la semana
del trabajador y que pasa cuando un feriado cae en el descanso semanal.

TRES CONFUSIONES QUE §36.1 DEJA ESCRITAS, y dos las cometi yo. La base de la
norma de vacaciones no es la semana de trabajo. El descanso minimo garantizado
TAMPOCO lo es —restar de siete da el maximo permitido, no lo ordinario—. Y la
cifra semanal puede ser un producto y no un texto: la ley alemana de jornada no
escribe ninguna, sus 48 horas son ocho por seis Werktage.

Solo 21 de 47 unidades tienen los dias ordinarios fijados o derivables de la ley.
La ganancia de la captura no es haber rellenado las otras 26: es saber cuales son.

Y el traslado resulto tener OCHO mecanismos donde yo esperaba dos, con el efecto
separado en campo propio: Polonia no mueve nada y libera un dia, Italia mueve
comodo y libera cero.

---

## feriados y vacaciones · v2.22

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.22.md` |
| SHA-256 | `7b6f50ee52f33d16ce7c4159ba99776a7a559cfb41641de332d3260cd7278da2` |
| Fecha UTC | 2026-08-11T08:10:00Z |
| Vigente | no |
| `schema/draft/001_schema.sql` | `b33114d290d8ba540e424489303852a51b4b2581a7a9e038e3db8959c2efe52c` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | El conteo esperado de feriados |

**Sin cambio de esquema. Solo protocolo.**

La comparacion entre cortes con conteo REALIZADO mide la rotacion del calendario
y no la reforma: 23 de 45 unidades cambian mas de un dia entre 2016 y 2026 y la
mediana del cambio es 1,85 dias, que es del mismo orden que las reformas que
buscamos. Con conteo ESPERADO la mediana es CERO y solo se mueven las que
reformaron.

Y la esperanza es defendible porque no suaviza el conjunto: la mitad del conteo ya
es determinista —32% lo rescata la ley, 14% esta anclado en Pascua, que es
siempre domingo y por tanto fija el dia de la semana para todos los anios— y la
fraccion entra solo en el 49% de fecha fija sin rescate.

Queda descartado por escrito el atajo de suponer que ningun feriado cae en fin de
semana: le daria el mismo numero a la unidad que traslada y a la que no, y esa
diferencia vale de cero a seis dias segun el pais.

---

## feriados y vacaciones · v2.23

| | |
|---|---|
| Archivo | `docs/archivo/02-protocolo-v2.23.md` |
| SHA-256 | `e1995d6141fb7178ce0f06c129211679227b45d18c0443a9b8d32d94a78d1cac` |
| Fecha UTC | 2026-08-11T16:20:00Z |
| Vigente | no |
| `schema/draft/001_schema.sql` | `93ad50c47b17e6ce7aafe26bd83162217ae780e09e193ce2f6d1ac2d54896a64` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | El paquete pasa a bilingüe |

**Qué cambia en el esquema.** `jurisdicciones` gana `nombre_en`. Es el primer
cambio de esquema desde el congelamiento de v2.15, y se hace porque la
alternativa era peor: mapear los nombres en la plantilla inglesa dejaba el CSV
publicable en castellano y creaba dos verdades para el mismo hecho.

**Qué no cambia.** Ninguna validación. La columna es opcional y nada la exige,
así que las 37 siguen dando cero filas sin tocarlas.

**Por qué columna y no tabla de traducciones.** El proyecto publica en dos
idiomas, no en N. Una tabla genérica sería estructura para un caso que todavía
no existe, y este repositorio ya ha pagado dos veces por cosas declaradas y
nunca conectadas —`eventos_reforma` con cero filas durante semanas, y dos
plantillas que ningún guion leía—. Si llega un tercer idioma, ese es el momento.

---

## feriados y vacaciones · v2.24

| | |
|---|---|
| Archivo (es) | `docs/archivo/02-protocolo-v2.24.md` |
| Archivo (en) | `docs/archivo/02-protocol-v2.24.md` |
| SHA-256 (es) | `f55ba9bbbe1f8cdcc651d3d62de2e97963d4e7f8d200477da14c0e7fa84fd61a` |
| SHA-256 (en) | `842e0ea0632b98a5e9bd23617ba2105b8d936703a44967a9e550d767b0435729` |
| Fecha UTC | 2026-08-11T17:40:00Z |
| Vigente | no |
| `schema/draft/001_schema.sql` | `93ad50c47b17e6ce7aafe26bd83162217ae780e09e193ce2f6d1ac2d54896a64` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | Sale la tabla de resultados |

**Qué cambia.** Se retira del protocolo la tabla de diferencia media por unidad
de conteo y el caso Perú–Alemania en cifras. Queda la remisión al apéndice de
hallazgos, por título y sin repetir ninguna cifra, y un ejemplo de conversión
**aritmético** —30/7 = 4,29 semanas— que es una identidad y no envejece.

**Por qué.** Un documento congelado por hash no puede contener un estadístico
vivo. El congelamiento certifica que el texto no cambió; un resultado dentro de
él acaba certificando que un número que sí cambió no cambió. Las dos propiedades
son incompatibles y gana la equivocada: el documento queda intacto y mintiendo.
No es hipotético — esa tabla llegó a publicar `−0,4` donde el cálculo daba `−0,8`
y hoy da `−0,5`, en la fila que sostiene el hallazgo principal, y no se podía
corregir sin romper el congelamiento que la hacía citable.

**Qué NO cambia.** Ni el esquema ni las validaciones. Sale un resultado, no un
método: la regla de unidad común, la definición del trabajador de referencia y
las decisiones de constructo se quedan enteras. La línea es *cómo se mide* se
queda, *qué salió* se va.

**Los dos idiomas van en UNA entrada, no en dos.** Dos entradas separadas
permitirían un registro completo y consistente con una traducción que se quedó
atrás: cada entrada verdadera por separado, nada falla, y sólo se vería
comparando fechas que nadie compara. Con una fila, la desviación es
**estructuralmente indecible** — no hay forma de registrar el castellano de una
versión sin decir a la vez qué inglés le corresponde. Es la misma diferencia que
entre lista de exclusión y lista blanca: permitir que falte no es lo mismo que
exigir que esté.

Y la regla operativa que se sigue: **si la traducción de una versión no está
lista, la entrada no se abre.** El protocolo sube de versión cuando los dos
idiomas están. La alternativa es un hueco en una columna, y un hueco en una
columna se rellena luego, que quiere decir nunca.

**Las versiones archivadas anteriores se quedan como están.** Sus tablas de
resultado eran correctas el día en que se congelaron. Corregirlas seria reescribir
la historia, que es lo contrario de para qué existe un archivo — y romperia sus
hashes, que es lo que las hace citables. **Toda tabla de resultado en una copia
archivada refleja el cálculo de SU fecha, no el vigente.**

---

## feriados y vacaciones · v2.25

| | |
|---|---|
| Archivo (es) | `docs/archivo/02-protocolo-v2.25.md` |
| Archivo (en) | `docs/archivo/02-protocol-v2.25.md` |
| SHA-256 (es) | `5fc6cf78dec77b8b3be807de650aebd5b99e4e6ce59f5f35e619af546c62548d` |
| SHA-256 (en) | `4633f0a04644f9c95ab6bfaff8f52bcf2134c19d882f6716899b7b8b2f663f85` |
| Fecha UTC | 2026-08-11T19:20:00Z |
| Vigente | no |
| `schema/draft/001_schema.sql` | `93ad50c47b17e6ce7aafe26bd83162217ae780e09e193ce2f6d1ac2d54896a64` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | §10 bis · las pantallas en vacaciones |

**Qué cambia.** Entra §10 bis. La pantalla 1 del §10 —diff de fuente terciaria—
se declara **no aplicable** a la variable de vacaciones, y el estado
`sin_cambio_confirmado` pasa a alcanzarse por dos ramas: índice oficial de nivel
1 o 2, o reproducción de nivel 3 más pantalla 3.

**Por qué, y la evidencia es medida y no argumental.** No existe fuente terciaria
que publique el derecho vacacional por año y unidad. La sustituta autorizada se
probó sobre las 45 unidades con dato en los dos años: **un candidato, falso**
—Tailandia, cuyo artículo dice seis días antes y ahora— y **ciega al caso
israelí**, que es reforma verificada y cae dentro de su propia ventana. Un falso
positivo y un falso negativo, los dos sobre casos nuestros.

Sin la enmienda, ninguna unidad podía alcanzar ese estado en vacaciones por bien
que se buscara, porque una de las tres condiciones era imposible. Habría quedado
declarado en el esquema y muerto en la práctica.

**Qué NO cambia.** Ni el esquema ni las validaciones: `sin_cambio_confirmado` ya
estaba en el CHECK. Y la enmienda **no reclasifica ninguna celda**: el reparto
entre (a) y (b) es trabajo de codificación, unidad por unidad.

**Procedencia.** Texto redactado por la campaña del corte 2016 en
`notes/15-enmienda-pantallas-vacaciones.md`, con la demostración de rendimiento;
decisión del principal; adopción y traducción en este carril, que es el que posee
el protocolo.

## feriados y vacaciones · v2.26

| | |
|---|---|
| Archivo (es) | `docs/archivo/02-protocolo-v2.26.md` |
| Archivo (en) | `docs/archivo/02-protocol-v2.26.md` |
| SHA-256 (es) | `822279c65c9cc82d11b9be266bcd273102efcc6a9767411011f01556854cfd74` |
| SHA-256 (en) | `461ee4c1380be9980ebb68f907163c7bb40d2bec6fd9274cce5c93fc5b616875` |
| Fecha UTC | 2026-08-12T18:40:00Z |
| Vigente | no |
| `schema/draft/001_schema.sql` | `93ad50c47b17e6ce7aafe26bd83162217ae780e09e193ce2f6d1ac2d54896a64` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | §34 · las cifras de fiabilidad dejan de publicarse |

**Qué cambia.** El §34 deja de traer las tasas de acuerdo de la doble
codificación ciega. Decisión del principal: la medición y su material —tasas,
segundas lecturas y programa de cruce— se conservan en la documentación interna y
no viajan al paquete publicado. El apartado conserva lo que es doctrina —el
apareamiento es estricto y no difuso— y advierte que mencionar el ejercicio no
afirma concordancia alta.

**Por qué obliga a una versión y no a una corrección de la copia.** El protocolo
viaja byte a byte en el paquete porque su SHA lo certifica el registro que viaja a
su lado; tachar la copia embarcada rompería esa certificación y la compuerta C10
lo detecta. La vía es enmendar, versionar y recongelar, que es el procedimiento
que este registro existe para soportar. La v2.25 archivada conserva las cifras y
queda en el repositorio privado.

## feriados y vacaciones · v2.27

| | |
|---|---|
| Archivo (es) | `docs/archivo/02-protocolo-v2.27.md` |
| Archivo (en) | `docs/archivo/02-protocol-v2.27.md` |
| SHA-256 (es) | `bb9db022dec2e48cdf70a7bc788afe0e35ef2567828eb89605422fa0ae1b8185` |
| SHA-256 (en) | `cd0acd797275ff63afd38eb2ac4790200f6cc3e38c00c2b4f18727bf93101af3` |
| Fecha UTC | 2026-08-12T19:30:00Z |
| Vigente | si |
| `schema/draft/001_schema.sql` | `93ad50c47b17e6ce7aafe26bd83162217ae780e09e193ce2f6d1ac2d54896a64` |
| `schema/draft/900_validaciones.sql` | `669596299ba8a5c02eeefe5c170713d68e232ae88422291a14470fb7c7ac3bc2` |
| Origen | Despersonalizacion: las objeciones se atribuyen al papel |

**Que cambia.** Ninguna regla. Las atribuciones dejan de nombrar identificadores
internos de sesion y nombran el PAPEL: la revision cruzada, la revision
adversarial, la revision de diseno. Treinta y dos referencias en cada idioma y
diecinueve en este registro.

**Por que, y por que se conservan distintas.** El protocolo viaja en el paquete
publicado, y un identificador interno no significa nada para el lector externo:
le pide un organigrama que no tiene y convierte una leccion de metodo en una
anecdota. Pero fundir los tres en una sola etiqueta habria borrado algo que este
documento registra a proposito — que los revisores DISCREPARON entre si, con su
nota de desacuerdo incluida. Se conserva la distincion y se quita el handle.

**Por que aparecio tarde.** La despersonalizacion se aplico a `scripts/` y luego,
al descubrir que faltaba, a las capturas. `metodo/` viaja igual y no estaba en
ninguna de las dos pasadas: **arreglado donde se encontro y no donde vive**, por
tercera vez. Lo caza ahora la compuerta C5, ampliada a todo el arbol publicado.

