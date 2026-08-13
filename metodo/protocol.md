# Measurement protocol — public holidays and annual leave · v2.27

**This file is the document in force and its name carries no version.** The frozen
versions live in `docs/archivo/02-protocolo-vX.Y.md`, they are immutable, and they
are the ones `PROTOCOL_FREEZE.md` cites. The version in force used to be renamed at
each version and the register pointed at a file that kept changing: four historical
entries cited the same mutable file and their verification failed. See §26.

Date: 2026-08-08. **Single operative document.** It supersedes v1.1,
`05-definiciones.md` and the uncollected v2.0, all archived. It incorporates the
three `[blocker]` items from the the cross-review review of v2.0 (§19), the placement band
(§4.3) and the seniority grid (§3.2.1).

Scope: the 47 units of the fixed group, two cuts — **2016** and **2026** — and both
variables. The universe of units is a closed input and is not discussed here.

> **This is the English twin of `docs/02-protocolo.md`, and the Spanish is the
> frozen source.** Where the two diverge, the Spanish governs: it is the text whose
> hash the freeze register certifies. This translation carries the same sections in
> the same order and the same numbering, so that a citation of «§34.1» resolves to
> the same rule in either language. Statute names, verbatim quotations and field
> identifiers are not translated: they are what a reader has to search for in the
> source.

---

# Part 0 · What changes relative to v1.1

| | v1.1 | v2.0 |
|---|---|---|
| Variables | Public holidays; annual leave deferred | **Both, same design** |
| Holiday constructs | Three (A, B, C) | **Two columns × nominal/effective** — subsumes all three |
| Boundary between variables | Deferred | **Resolved**: imputation rule, computed total |
| Data model | One | **Two fact modules over a common entitlement layer** |
| Treatment of ranges | Lower bound | **Resolved by the reference worker** |
| Supranational floor | Not contemplated | **Own field + derived effective minimum** |

The reconciliation of constructs, which had been left pending: what v1.1 called
**A** is `feriados_pagados_obligatorios` nominal; **B** is
`feriados_nacionales_reconocidos` nominal; **C** is the effective version of either
of the two. Nothing is lost, and what is gained is that the principal column is
unambiguous.

---

# Part I · Definitions

## 1. Common core

### 1.1 Reference worker

> A **formal**, **full-time**, **private-sector** employee, with **exactly twelve
> months of continuous service completed** as at 1 January of the cut, on a
> **five-day week**, in the **most populous city** of the unit, **not covered** by
> a collective agreement or a special sectoral regime, in a firm that **does not
> provide essential services**.

Seniority is fixed at **exactly twelve months**, not at "more than a year". The
difference matters: statutory thresholds set at one, two, five or ten years produce
different values, and "more than a year" does not determine which applies. With
twelve months completed, the one-year thresholds are satisfied and the higher ones
are not.

**Besides fixing the scope, it resolves ranges.** The earlier material coded the
lower bound when the source reported an interval, and it warns itself that this
biases federal regimes and those with seniority ladders systematically downwards.
With a defined reference worker the interval **disappears**: there is a single
applicable value. The full range and its cause are recorded all the same —
`federal` · `antiguedad` · `sector` — but the coded value is no longer a
convention, it is the one that corresponds to the case.

### 1.2 De jure, not de facto

What the law requires is measured, not compliance. In economies with high
informality, effective coverage is a minority. This is a **declared limitation of
the construct**, not a defect correctable with more verification.

### 1.3 Unit of measurement

**Working days**, normalised to a five-day week, for **both variables**. That they
share a unit is what makes them comparable and addable.

### 1.4 Geographic scope

**National.** The subnational is excluded from the principal series and recorded
separately, with a population-weighted average as a secondary variable where
applicable.

### 1.5 Temporal anchor

**The statute in force on 1 January** of 2016 and of 2026. Tolerance **±1 year** on
the 2016 anchor if there is no admissible source; outside that band, `NA` with a
cause. The `fecha_efectiva_de_medicion` is recorded **always**, even when it
coincides with the anchor, and the dataset publishes the distribution of
deviations.

## 2. Public holidays

### 2.1 Two columns

| Column | Counts |
|---|---|
| `feriados_pagados_obligatorios` | Days the law requires to be granted **with pay** |
| `feriados_nacionales_reconocidos` | Days recognised as a national holiday, irrespective of any payment mandate |

The **first is the principal one**, and it is the one comparable with annual leave:
both then measure a paid entitlement. Comparing paid days against calendar days
would be comparing different objects.

### 2.2 Compliance regime

Categorical by unit and cut: mandatory rest · rest unless required with a premium ·
recognised without a payment mandate · no national mandate. The **premium rate** is
stored where one exists: it is the only variation in intensity of the variable.

### 2.3 Nominal and effective

**Nominal** is the number the statute recognises, irrespective of the day of the
week. **Effective** is the working days not worked, computed deterministically from
the calendar. They are reported **together, never one in place of the other**:
between 2016 and 2026 the effective figure may differ by several days without a
line of the law changing.

### 2.4 Counting rules

| Situation | Rule |
|---|---|
| Multi-day holiday | Each day counts, if the statute suspends work on those dates |
| Two festivities on the same date | One **date**; two **legal events** |
| Half day | A fraction, **not rounded** |
| Non-Gregorian calendar | The **entitlement** is counted, not the date |

### 2.5 Exclusions

Substitute days for transfer (already in the nominal figure) · bridges and
**recoverable** non-working days (they have to be made up; separate series) ·
one-off extraordinary holidays (`recurrencia = one_off`, separate series) ·
regional holidays · optional observances and commemorations without rest · public
sector closures and bank holidays (separate column).

### 2.6 Compensatory working weekends

They are subtracted **only from the effective figure**, never from the nominal one.

## 3. Annual leave

### 3.1 Calendar days against working days · **the point of greatest error**

Many codes say "thirty days" without specifying the type. **Thirty calendar days
are 21.4 working days** on a five-day week: treating one as the other produces an
error of the order of 40%.

**This is not hypothetical, and the source admits it.** The imported CSV contains
at once 6 units with a value of 30 declared as 6.0 weeks and 10 units with a value
of 22 declared as 4.4 weeks. Twenty-five of 130 cells (19%) fall in the 24–30
range, where the number alone does not reveal the type. The accompanying report
itself acknowledges: *"The other countries were not audited in the same way, so
errors of the same kind almost certainly remain in the dataset."*

**Three fields:**

| Field | Content | Origin |
|---|---|---|
| `texto_legal_dias` | The statute's literal number | Captured |
| `tipo_de_dia` | `calendario` \| `habil`, **read from the statute** | Captured |
| `dias_habiles` | Normalised value, **not rounded** | **Derived** |

`dias_habiles` is published; all three travel in the dataset. Publishing only the
converted value buries the error and makes it undetectable without returning to the
statute; publishing only the literal shifts the error to every user, and
international comparison is where it is committed.

**The type is read, not inferred.** The reliable clue is whether the code itself
excludes weekly rest days from the count.

**The conversion is a declared convention, not a fact.** Thirty calendar days are
21.43 working days *on average*; the realised value is 21 or 22 depending on the day
the period starts. That is why the literal is kept. The conversion takes as an input
the unit's weekly rest convention, which is neither universal nor constant across
the window; being derived, it is recomputed in full if that table is corrected.

### 3.2 The full seniority schedule · **critical**

The reported value is the one corresponding to the reference worker — twelve months
completed. But **the full schedule is captured, with structure**.

The archived report warns that *"many regimes adjust the entitlement by tenure
instead of moving the statutory minimum, so the real change occurs at a margin that
entry-level coding does not capture."* If that is true, the observed rigidity **does
not measure rigidity: it measures that the wrong place was looked at**.

**Two descriptive fields are not enough.** A free-text `regla_de_progresion` plus a
`dias_maximo` do not reconstruct a multi-band schedule: two regimes with identical
entry levels and identical maxima can have different trajectories, and a reform
moving an intermediate band would be invisible in both fields.

That is why the schedule is a **table of versioned bands**, not an attribute:

**`escala_antiguedad`** — `vacaciones_version_id`, `antiguedad_desde_meses`,
`antiguedad_hasta_meses`, `quantum`, `tipo_de_dia`, `vigencia_desde`/`hasta`, plus
its evidence link. The reference worker's level is the band containing twelve
months; it is not captured separately, **it is derived**.

Any change in any band is a ledger event of type
`cambio_de_escala_de_antiguedad`, whether or not it moves the entry band.

#### 3.2.1 Seniority grid: 1, 5 and 10 years · **decided by the principal**

Besides the reference worker, the principal output reports the quantum and its
`tipo_de_dia` at **three seniority points: 1, 5 and 10 years**. All three are
**derived** from `escala_antiguedad`; they are not captured.

**Why, and this is not "more columns".** The central risk of §3.2 is that reforms
occurred in the schedule and not at the entry level, which would make rigidity an
artefact. The grid **is the test of that hypothesis**: if the entry level is flat
and the values at 5 and 10 have moved, the reform margin is located and the
suspected artefact becomes a measured finding.

**Seniority basis** *(a missing fact detected by the cross-review; we had not seen it)*. "Ten
years of seniority" is ambiguous between continuous service with the current
employer, recognised service from previous employers, and total labour experience.
The reference worker fixes continuous service but says nothing about creditable
prior history. It is resolved by both routes at once: a `base_antiguedad` field with
its recognition rule, and an explicit declaration that the three points assume **N
years with the same employer and zero creditable prior service**.

**Boundary convention.** Bands use `[from, to)` intervals, with no overlaps and no
gaps, the last one open. The grid point is defined as **immediately after
completing** 1, 5 or 10 years.

**The source's operator is preserved, not rounded.** A literal rule of "more than
five years" is not simply equivalent to `desde_meses = 60`: an `operador_frontera`
field carries the statutory literal. If a legal system defines sub-monthly
boundaries, whole months are not enough and the band is stored with date
granularity.

**Column names.** They carry the warning built in, following what we already learned
with the cap: `vacaciones_vigentes_a_N_anos_antiguedad_ley_<corte>`.

#### 3.2.2 Cross-section, not cohort · **structural warning**

In the 2016 cut, the value at ten years **is not** the trajectory of someone who
entered in 2006. It is the **statute in force in 2016 evaluated on a hypothetical
worker** with ten years of seniority. They are different objects and they read
identically in a table.

The design review rated this risk as very high: a cross-section evaluated at different seniorities
*"is almost always read as a worker's trajectory"*. The warning travels in the
variable name and in its metadata, not in a note: notes do not travel with the data.

#### 3.2.3 What it means for the three values to coincide · **the cross-review's fifth objection**

I was going to call it "degeneracy", by analogy with the band. The cross-review is right that
this is incorrect: that 1, 5 and 10 coincide **does not imply** an absence of
laddering. There may be steps at 2, 3, 15 or 20 years that the grid does not see.

They are two distinct facts and they are published separately:

| Field | What it says | Where it comes from |
|---|---|---|
| `sin_diferencia_en_grilla_1_5_10` | The three points coincide | From the grid |
| `escala_sin_escalonamiento` | The legal system does not ladder at all | From the **full table** |

And as a safeguard against the arbitrariness of the grid, the **number of bands** and
**the exact thresholds** are also published, derived from the table. That way the
result does not depend on the points we chose.

#### 3.2.4 The placement band is not replicated in the grid

The principal output derives at 1, 5 and 10 years **only** `quantum` and
`tipo_de_dia`. The band of §4.3 is **not** computed at the three points by default.

Reason, from the cross-review: it would mix the test of seniority reforms with a different
estimate and would triple the columns without answering either question better. It
remains available as a secondary analysis if the principal asks for it.

*Note of disagreement:* the design review considered it sufficient to make the two descriptive
fields mandatory; the cross-review held that without structure the field is useless. The cross-review's
position is adopted.

### 3.3 Qualifying period

Minimum service to accrue. If it exceeds one year, the reference worker's value is
**`NA` for not applicable**, not zero. Confusing the two biases the mean downwards.

### 3.4 Supranational floor

A good part of the universe is tied to a supranational minimum that does not move —
ILO Convention 132 sets three weeks; the European working time Directive, four. That
explains the clustering at twenty days visible in the imported data, and it means
that for those units "no change" is the structurally expected result.

**It is not an attribute, it is a table**, because `max(national, supranational)` is
only computable after normalising both to the same unit and after establishing that
the instrument was in force and applicable to that jurisdiction at that cut. Those
two things are facts with evidence, not assumptions inside a function.

**`instrumento_supranacional`** — `instrumento`, `jurisdiccion_id`,
`vigencia_desde`/`hasta`, `piso_dias`, `tipo_de_dia`, `ratificado_o_vinculante`,
evidence link.

Derived: `minimo_efectivo = max(nacional_normalizado, supranacional_normalizado)`,
computed only over instruments with established applicability and validity. Both are
published; the analysis chooses.

### 3.5 Exclusions

Sick, maternity, paternity leave and special permits · improvements by collective
agreement or individual contract · additional days for particular conditions (night
work, unhealthy work, disability, age) unless they apply to the reference worker.

### 3.6 Interpretation warning · **mandatory in every publication**

A zero delta in annual leave **does not mean** that nothing happened to paid rest.
The archived sweep documents that the margin of expansion of the period shifted to
**sick leave and paid family leave**, which fall outside this variable by definition.
Reading the zero as immobility of paid rest is an error of interpretation of the
period, and it has to be forestalled in the dataset itself.

## 4. The boundary between the two variables

There are legal systems where holidays falling inside the leave period **are
counted against it**, and others where they **extend it**.

Mandatory field: `imputacion_feriados_a_vacaciones` ∈ { `se_computan_contra` ·
`extienden` · `sin_regla_explicita` }.

### 4.1 The total, defined as an estimand

The previous version said the overlap was computed "deterministically from the
length of the period and the number of holidays". **That is false** and the cross-review
flagged it: two workers with the same leave length and the same annual number of
holidays can have different overlap depending on when they take the period. The
start date is missing.

Since we do not observe real start dates, the total **is not an observed quantity:
it is an expectation under a declared distribution**. And it has to be declared in
full, or it is not reproducible.

**Versioned definition:**

> `superposicion_esperada` = the expected number of **observed occurrences** of a
> holiday falling inside the leave period, when the start date is distributed
> **uniformly over the working days of the cut year**, and the period is consumed
> in consecutive working days according to the unit's working-time regime.

Four things are fixed by that sentence, and all four are choices: **observed**
occurrences are used, not nominal ones, because the question is whether the day is
actually consumed; the start distribution is **uniform over working days**; the
horizon is the cut year; and consumption is in consecutive working days.

The formula is published with the data and carries its own version number.

### 4.2 How the total is composed

| `imputacion_feriados_a_vacaciones` | Total |
|---|---|
| `extienden` | paid holidays + leave |
| `se_computan_contra` | paid holidays + leave − `superposicion_esperada` |
| `sin_regla_explicita` | **`NA`**, plus a sensitivity interval computed under both assumptions |

**`sin_regla_explicita` is not treated as `extienden`.** Legally they are not the
same thing, and assimilating them is an unidentified imputation that would read as
data. It goes as `NA` and the interval between the two possible readings is
reported, which is honest information about how much we do not know.

**Never a simple sum.** A methodological warning is not enough: it does not travel
with the figure when someone cites it.

### 4.3 Placement band · **decided by the principal**

§4.1 assumes a uniform start date: a worker who does not plan. That is an arbitrary
assumption and it is worth bounding on both sides. The same estimand is computed
under **three placement assumptions**:

| Series | Placement assumption |
|---|---|
| `total_minimo` | The placement that **minimises** paid days not worked |
| `total_esperado` | Uniform start date over the working days of the year (§4.1) |
| `cota_estilizada_colocacion_no_es_derecho` | The placement that **maximises**, subject to working time, holidays and admissible partitions (§4.3.4) |

**Objective of the maximisation, fixed precisely:** **scheduled work days, paid and
not worked**. The short formulation —"paid days not worked"— is ambiguous, because
it would include the weekly rest days that §4.3 treats as consumed inside the
period. The objective counts only days that, without leave or a holiday, would have
been scheduled work.

**Not** consecutive free days. They are different objectives: a bridging strategy
concentrates rest but does not add a single day. If concentration is of interest, it
will be a separate metric.

**The maximum is normative, not behavioural.** It is what the rules admit, not what
people do.

**Subject to what, exactly — pending a decision by the principal.** The cross-review flagged
that "subject to the legal restrictions" is undefined so long as the **domain of
admissible dates** is not represented: windows and deadlines for taking leave,
excluded dates, mandatory shutdowns, notice and approval rules. Two legal systems
with identical splitting fields may permit different calendars and produce different
maxima. There are two ways out and they are mutually exclusive; see §4.3.4.

#### 4.3.0 Admissible partitions · **the cross-review's correction, accepted**

Splitting scalars do not represent the feasible set. `bloque_minimo_dias` does not
say whether the minimum applies to **each** fraction, only to a principal block, or
to a given number of blocks. "At least one block of fourteen days and the rest in
units of one day" and "every fraction of at least fourteen days" have **the same
scalars and different feasible sets** — and therefore different maxima.

That is why splitting is a **versioned table of admissible partitions**, not four
scalars:

**`particiones_admisibles`** — `vacaciones_version_id`, `vigencia_desde`/`hasta`,
`numero_de_bloques` (or its range), and by block position or class: `cardinalidad`,
`tamano_min`, `tamano_max`, `tipo_de_dia`, `obligatorio`,
`requiere_consentimiento`. Plus its evidence link.

The publication scalars —minimum block, maximum number of fractions— are **derived**
from this table; they are not captured.

#### 4.3.1 The width is the result, not the extremes

> `amplitud_de_colocacion = cota_estilizada_colocacion − total_minimo`

It measures **how much of the result depends on discretion over scheduling**. It is
not a characteristic of the worker: it is a characteristic of the legal system —
regulatory flexibility. No prior source measures it, and it is probably the most
original contribution to come out of this metric.

#### 4.3.2 Degeneracy of the band · **corrected characterisation**

The band collapses when the objective function is **constant over the feasible
set**. That happens in more cases than I had declared, and the cross-review was right that my
characterisation was sufficient but not necessary.

`banda_degenerada` **is not declared by rule: it is derived as `max == min` after
optimising**, and it is accompanied by a `causa_de_degeneracion`:

| Cause | When |
|---|---|
| `estructural_por_regla` | Counting in working days **and** holidays that extend: twenty working days are twenty working days whenever you start |
| `estructural_por_ciclo` | An entitlement in calendar days covering a whole number of **working-time cycles** — seven days under a stable week consume the same working days from any start |
| `calendario_realizado` | `se_computan_contra` with zero observed occurrences, or with constant overlap across all feasible placements |
| `factible_singleton` | A single admissible calendar, through mandatory shutdown or a fixed calendar |

**A correction I have to acknowledge.** I claimed that the band "only bites" in
calendar-day regimes or in holiday-netting ones. That is false: the
`estructural_por_ciclo` case is a calendar-day one and **it does not bite**. An
entitlement of seven calendar days under a five-day week consumes five working days
wherever it starts.

`habil + extienden` is kept as a **sufficient condition and principal prediction**,
not as the condition. The distribution of degeneracy causes is published as a
result: it says where regulatory flexibility matters and why it does not matter
where it does not.

#### 4.3.4 Scope of the cap · **decided: stylised**

The cross-review flagged that "subject to the legal restrictions" is undefined so long as the
domain of admissible dates is not represented. The alternative was to capture a
canonical placement rule —leave windows, deadlines, excluded dates, mandatory
shutdowns, notice rules—, which is a **second collection layer** whose facts are
largely not in secondary sources.

**The principal's decision: a stylised cap, and renamed.** The series stops being
called "normative maximum" because it is not one.

**What the cap respects:** the unit's working-time regime; observed holiday
occurrences; the admissible partitions of §4.3.0; and the imputation rule of §4.

**What it ignores, and therefore what it may overstate:** leave windows and
deadlines, excluded dates, mandatory company shutdowns, and notice or approval
rules. Where those restrictions exist, the real cap is lower.

That list of exclusions is published **next to the column**, not in an annex. It is
what stops the cap being read as an entitlement.

#### 4.3.3 Who controls the timing · **the restriction that binds most**

In a good part of civil-law systems the employer sets or approves the leave
calendar. Assuming free choice would be assuming that the most binding restriction
does not exist, and the maximum would not merely be unattainable: it would be
**legally unavailable**.

> **SUPERSEDED BY §24.** This section defined a `control_del_momento` field as an
> enumeration of five values. A targeted search and two re-attacks invalidated it:
> it presupposed that someone decides, and it flattened the layered rules that exist
> in the law reviewed. **The specification in force, and the only one, is §24.** This
> paragraph is kept with its marker, and not its content, because deleting it would
> hide why it changed.

---

# Part II · Data schema

Two fact modules over a **common entitlement layer**. Public holidays are a set of
dated events; annual leave is a scalar entitlement. They do not share realisation,
and forcing them into a single model would require inventing dates for a variable
that has none.

## 5. Common layer

**`jurisdicciones`** — `jurisdiccion_id`, unit, level, parent, validity. Everything
else references `jurisdiccion_id`, never the unit directly.

### 5.1 Polymorphic identification of facts

Every versioned fact row — `feriado_version`, `regla_fecha_version`, `ocurrencias`,
`vacaciones_version`, `escala_antiguedad`, `regimen_jornada`,
`instrumento_supranacional` — carries its own stable version identifier. The tables
of the common layer reference them by the pair (`hecho_tipo`, `hecho_id`).

Without this, the relations below claim to link something that is not identified.

**`evidencia`** — the **fact ↔ source** relation, versioned. Key:
(`hecho_tipo`, `hecho_id`, `fuente_id`). Cardinality: **every fact has at least one
link**; a link proves **exactly one** fact version. A statute proves the entitlement
and a separate proclamation proves the realised date: these are separate links, not
columns of the same row.

Nine fields per link: source, URL, archived version, authority, jurisdiction,
statute date, verification date, source level, reviewer.

**`eventos_reforma`** — `reforma_id`, `tipo` ∈ { creation · abolition · suspension ·
restitution · substitution · coverage extension · **seniority schedule change** ·
**rule reform without a change of quantum** }, `fecha_anuncio`,
`fecha_promulgacion`, `vigencia_desde`, `causa`, `permanente_o_temporal`, citation.

**`reforma_versiones`** — the reform ↔ affected versions relation. `reforma_id`,
`hecho_tipo`, `hecho_id`, `rol` ∈ { `anterior` · `nuevo` }.

This table restores a guarantee v1.1 had and consolidation had lost:
`estado_anterior` and `estado_nuevo` as loose columns **do not say of which
variable, of which entitlement or of which version they are the state**. With the
relation made explicit, a reform can affect holiday versions, leave versions or
both, and which ones is stated. Deltas are not stored: they are derived.

**`mediciones`** — `hecho_tipo`, `hecho_id`, `corte` ∈ { 2016 · 2026 },
`fecha_efectiva_de_medicion`, `estado_verificacion`.

This restores the second lost guarantee. §1.5 requires the effective date to be
recorded **always**, but in consolidation it disappeared from the tables. Without
it, the ±1 year tolerance is an unauditable promise and the distribution of
deviations cannot be published. Living in its own table, it covers both modules
uniformly.

## 6. Public holidays module

**`feriado_version`** — `feriado_id`, `jurisdiccion_id`, `sector`,
`vigencia_desde`/`hasta`, `nombre_oficial`, `categoria`, `recurrencia`, `regimen`,
`tasa_recargo`, `duracion_dias`, `cobertura`, `elegibilidad`.

**`regla_fecha_version`** — `feriado_version_id`, `vigencia_desde`,
`sistema_calendarico`, `clase_de_regla`, **`especificacion`** as an executable
expression with parameters, `regla_de_traslado_aplicable`. The substitution rule may
vary by holiday; the one in `regimen_jornada` is only the default.

**`ocurrencias`** — **one row per date**, without exception. `feriado_version_id`,
`corte`, `indice_en_periodo`, `fecha_nominal`, `fecha_observada`,
`base_de_sustitucion`, `duracion_horas` (`derivada` | a value | `NA` — three
different things), `cayo_en_descanso_semanal`, `overlap_group`, `origen`,
`determinacion_id`.

**`determinaciones_fecha`** — per occurrence: `fecha_legal_original`, calendar and
era, `fecha_gregoriana_local`, `zona_horaria`, `metodo_de_conversion`, `certeza`,
authority, `proclamacion_id` (nullable), source.

**`regimen_jornada`** — by jurisdiction and sector, with **dated intervals**: weekly
rest days, default substitution rule, scheduled hours per day. It cannot be by year:
a mid-year reform would be unrepresentable.

**`eventos_compensatorios`** — bridges and rest days declared working, linked to the
event they compensate. It allows gross, compensation and net to be reported
separately.

## 7. Annual leave module

**`vacaciones_version`** — `vacaciones_version_id`, `jurisdiccion_id`, `sector`,
`vigencia_desde`/`hasta`, `texto_legal_dias`, `tipo_de_dia`,
`periodo_de_calificacion`, `rango_min`, `rango_max`, `causa_del_rango`,
`imputacion_feriados_a_vacaciones`, and the four placement band fields (§4.3):
`fraccionamiento_permitido`, `bloque_minimo_dias` with its
`bloque_minimo_tipo_de_dia`, `numero_maximo_de_fracciones`, `control_del_momento` —
**a field removed in §24**.

**`escala_antiguedad`** — versioned bands (§3.2). The reference worker's value is
the band containing twelve months; it is **derived**, not captured.

**`instrumento_supranacional`** — floors with established applicability and validity
(§3.4).

No occurrences table: the variable has no dates.

## 8. Derived tables

`panel_unidad_corte` — by unit and cut: the two holiday columns in nominal and
effective form, with and without *one-offs*; annual leave in `dias_habiles` and
`minimo_efectivo`; the total with the imputation rule applied; flags for
non-Gregorian calendar, federalism, suspension and range; and `estado_verificacion`
per cell.

Produced by **explicit, versioned functions**, never captured. The functions are
published with the data: publishing only the panel would repeat the defect of the
tertiary sources this project corrects.

---

# Part III · Evidence and verification

## 9. Source hierarchy

1. Statute, decree, official gazette, applicable case law
2. **Contemporaneous** official calendar or guidance from the competent ministry
3. Intergovernmental legal repositories reproducing text and validity
4. Documented secondary databases and literature
5. Reputable press, only to locate extraordinary holidays
6. Collaborative encyclopedias and calendar libraries: **discovery only**

**Commercial sources are actively wrong, not merely out of date.** The archive
documents that global payroll guides published *during* the window were still
reporting a pre-reform value **three years after** the change. This is neither an
old error nor a marginal one.

Using a calendar library to build the panel confuses **software reproducibility with
legal validity**.

## 10. The three screens

A unit-cut pair is coded `sin_cambio_confirmado` **only if all three agree**. Any
discrepancy goes to human adjudication.

1. **Tertiary-source diff** between years, pinned version. It detects candidates;
   **it is not evidence**.
2. **Legislation**: intergovernmental labour legislation database and official
   gazette, filtered to verbs of creating · abolishing · suspending · transferring ·
   restoring · **laddering**.
3. **Local-language press**, with machine translation, citing and archiving the
   original.

**Why screen 1 cannot stand alone — concrete evidence from the archive.** In the
imported reconstruction, the library coded one unit's Sundays as statutory holidays:
**fifty spurious entries** that had to be removed by hand. A panel built on that
source without the other two screens would have reported a unit with more than sixty
holidays.

## 10 bis. Screens for the annual-leave variable

Screen 1 is **not applicable** to the annual-leave variable: no tertiary source
publishes leave entitlement by year and unit, and the substitute —a scored
secondary database— was tested and rejected **on measured performance**: one
candidate out of 45, false, and blind to a verified reform falling inside its own
window.

For this variable, a unit-cut pair is coded `sin_cambio_confirmado` when:

**a)** screen 2 is satisfied by an **official index of amendments to the article,
a version note, or a comparison of dated consolidated texts**, at source level 1
or 2; **or**

**b)** screen 2 is satisfied by a level-3 reproduction, or rests on a negative
without an index, **and** screen 3 agrees.

**An absence is evidence only if the source records presences.** Before admitting
a missing amendment note as proof, check that the consulted document records
amendments **somewhere**. The Spanish gazette's consolidated PDF is the
precedent: it records none, and its silence about the leave article meant
nothing.

**Why the step and not a flat rule.** The three-screen rule exists for redundancy
against the blindness of a single source. When screen 2 is satisfied by an
official index, that is **not a proxy**: it is the authority stating what touched
the article and when, and asking for local press on top adds no information. When
it rests on a level-3 reproduction or on a «found no reform», redundancy is
needed.

**What this amendment prevents.** Without it, no unit can reach
`sin_cambio_confirmado` for leave **however well it is searched**, because one of
the three conditions is impossible to satisfy. The state would hold zero rows for
ever — declared in the schema and dead in practice, a figure this project has met
three times in a single day.

**And it reclassifies nothing on its own.** Adopting the rule turns no already
captured cell into (a) or (b): the split is coding work, done unit by unit.


## 11. Ledger seed — imported from the archive

The archived report left an explicit list of **candidates pending audit**, with a
high *a priori* probability of containing an unverified reform: restructurings of
entire labour codes, rewrites of the private employment regime, reforms associated
with migrant hiring systems, new labour codes, working-time reforms that may have
touched the leave minimum indirectly, and adjustments following adjustment
programmes.

That list enters as a **prioritised seed for screens 2 and 3**, not as a finding. It
is work already done that does not have to be repeated.

## 12. Zero, absence and uncertainty

`0` only when a competent source confirms it under the definition. `NA` with a cause
for unknown, not covered, not applicable, or in conflict. With zero as the default,
**more research effort on a unit looks like a reform**: coding effort enters the
dependent variable.

## 13. Exclusions at three levels

Master frame — it never deletes anything. Measured dataset — it records the status
and cause of what is missing. Sample of each estimate — pre-registered rule,
attrition diagram, and sensitivity where the exclusion may correlate with the
outcome. What is forbidden is not excluding: it is **excluding without a record**.

## 14. Reliability

Blind double coding of 15–20% and reporting of the agreement rate. Available and
publishable baseline: two systems coding the same concept for the same year agreed
exactly in **24%** of cases, correlation 0.57.

---

# Part IV · Divergences from the imported material

Recorded so that nobody reuses those data assuming our definitions apply. **They are
not equivalent and cannot be mixed without conversion.**

| Point | Imported material | v2.0 |
|---|---|---|
| Half days | Excluded | Count as a fraction |
| Government closures | Added to the principal count where the source supports it | Separate column |
| Ranges | Lower bound | Reference worker's value |
| Extraordinary holidays | Included in the principal figure | Separate series |
| Historical column | Imputed by persistence | Measured, or `NA` |
| Compensatory days | Subtracted from the single count | Subtracted only from the effective figure |

---

# Part V · Status and procedure

## 15. Freezing

Hash and date in [`PROTOCOL_FREEZE.md`](PROTOCOL_FREEZE.md), with no external public
register. Every change opens a new version with its own hash and **requires
recomputing the whole panel**: heterogeneous vintage is exactly what makes the prior
sources unusable.

## 16. Implementation debt, non-blocking

Flagged by the cross-review and accepted. It is all resolved in the DDL and the codebook, not in
the protocol:

1. `especificacion` must be a **validatable canonical grammar**, not free text.
2. Declare foreign keys and cardinalities for `determinacion_id`.
3. **Half-open seniority intervals** — or an equivalent declared inclusivity — in
   `escala_antiguedad`, so that the band containing twelve months is unambiguous.
4. **Leave periods crossing 31 December**: the overlap expectation of §4.1 needs an
   explicit convention for consumption extending into the following year.

## 17bis. The band is a behavioural construct, not an entitlement

The stylised cap and `amplitud_de_colocacion` measure what a strategic agent can
extract from the statute, not what the statute grants. **They never enter the
entitlement columns.** They go in a labelled block of the panel, and every published
table including them must say that they are caps under optimal placement subject to
rules, not entitlements.

Specific risk: the band makes the comparison between units partly about **regulatory
flexibility** and not about generosity. A legal system with fewer days and free
splitting can outrank another with more days and rigid blocks. That is a legitimate
and interesting finding, but it is a different question and has to be reported as
such.

## 17. Live risks

- **Leave rigidity may be a coding artefact** if the reforms occurred in the
  seniority schedule. It is the most serious risk left by the review of the archive,
  and §3.2 is the answer.
- With two holiday columns, **which one is the headline** must be declared in every
  published table. The design review's original objection, still live.
- A zero delta in annual leave does not mean immobility of paid rest (§3.6).
- Excluding for unavailability correlated with crisis is selection on the dependent
  variable (§13).

## 18. Principal's decisions incorporated

The three estimands over atomic facts · two holiday columns · three fields for
annual leave · sum with an imputation rule · national + weighted · three screens ·
two cuts, 2016 and 2026 · ±1 year tolerance with a per-cell date · AI agents with
blind human adjudication · the four optional attributes · machine translation valid
when citing the original · public citable dataset · reference jurisdiction = most
populous city.

Adopted by default, without a pronouncement: continuity of units — an unbalanced
panel, with no retroactive filling of borders.


---

## 19. The cross-review review of v2.0 — three blockers, all three accepted

The cross-review reviewed the frozen `99174c0b` and **disagreed** that it was ready for
collection. It accepted the conceptual separation — two modules yes, annual leave
without occurrences yes — but found that the declared facts were not enough to
execute the design without ad hoc decisions. Two of the three were **regressions
introduced when consolidating v1.1 and the definitions document into a single
file**.

| # | Objection | Disposition |
|---|---|---|
| 1 | The total of §4 is not deterministic: length plus number of holidays does not determine the overlap, the start date is missing. And `sin_regla_explicita` is not legally equivalent to `extienden` | **Accepted.** §4.1 defines the total as an **expectation under a declared distribution**, with the four assumptions explicit and a versioned formula. §4.2 sends `sin_regla_explicita` to `NA` with a sensitivity interval |
| 2 | The answer to the seniority risk does not capture the schedule: §1.1 and §3.2 contradicted each other on exact seniority, and two descriptive fields do not reconstruct bands | **Accepted.** Seniority fixed at **exactly twelve months** in a single place. New `escala_antiguedad` table of versioned bands; the reference value is derived from the band |
| 3 | The common layer lost identity: `evidencia` did not identify the fact proved, `eventos_reforma` lost the link to affected versions that v1.1 required, and `fecha_efectiva_de_medicion` disappeared from the tables | **Accepted.** §5.1 adds polymorphic identification, cardinalities for `evidencia`, the `reforma_versiones` relation and the `mediciones` table |
| — | `[suggestion]` `minimo_efectivo` requires unit normalisation and established validity as facts, not assumptions | **Accepted.** §3.4: `instrumento_supranacional` moves from attribute to table with evidence |

**Disagreement between reviewers, resolved.** On the seniority schedule risk, the design review
considered it sufficient to make the two descriptive fields mandatory; the cross-review held
that a field without structure is useless, because two regimes with the same entry
and the same maximum can hide different trajectories and intermediate reforms.
**The cross-review's position is adopted.**

**What this says about the process.** Blockers 2 and 3 did not exist in v1.1: I
introduced them myself when merging two documents into one. Consolidation is not a
neutral operation, and without this review we would have begun collecting with two
fewer guarantees than we already had.


---

## 20. Close of the review — green light

The cross-review verified the frozen `f0c760c3` and closed the three `[blocker]` items:

- **Total:** §4.1 identifies the estimand and fixes observed occurrences, the
  population of start dates, the consumption regime and the horizon; §4.2 treats
  `sin_regla_explicita` as `NA` with sensitivity.
- **Seniority:** exactly twelve months, the full schedule in versioned bands, and the
  reference value derived from the band.
- **Common layer:** stable identifiers for every versioned fact, and the three
  relations —fact↔evidence, reform↔versions, fact↔measurement/cut— with explicit
  cardinalities.

Verbatim verdict: *"No missing fact remains that would force recapture or
reinterpretation later. As far as my review goes, collection can begin."*

The design review had closed earlier, with no blockers.

**Status: v2.1 is the methodology in force and collection can begin.**


---

## 21. v2.2 — placement band

**The principal's decision**, with three choices taken after the push back:

1. **A band of three** —minimum, expected, maximum— plus the width as a variable in
   its own right, instead of a single upper-cap column.
2. **Objective: paid days not worked**, not consecutive free days. A bridging
   strategy concentrates rest but adds no paid days.
3. **`control_del_momento` is coded** as a field with evidence, instead of assuming
   free choice. *(A v2.2 decision. **Superseded by §24**: the field was removed and
   the `regla_colocacion` table replaces it.)*

**Objections raised and how they were resolved:**

| Objection | Resolution |
|---|---|
| It stops measuring entitlement and measures behaviour | §17bis: labelled block, outside the entitlement columns |
| In much of the universe the worker does not choose the date | §4.3.3, today **superseded by §24**: table of layered rules |
| "Optimising" is ambiguous between two different objectives | §4.3: objective fixed as paid days; concentration would be another metric |
| The metric is degenerate over a subset of the universe | §4.3.2: explicit condition, `banda_degenerada` field, and the fraction published as a result |

**What the objection produced, which is the best part of this change.** Requiring
the maximum forced us to code who controls the timing of leave — a first-order
institutional variable that no prior source measures. The defect in the proposal
forced the collection of something valuable.

**Cost:** four new fields in `vacaciones_version`, each with evidence. It is not a
derived metric: it is an additional collection layer.

**Recomputation:** zero cost. The first datum has still not been collected.


---

## 22. Publishing the band — the principal's decision and accepted risk

**The design review recommended two physically separate files**, entitlements on one side and the
placement band on the other, with this argument: *"if the placement variables go in
the same tabular panel as the entitlement ones, the casual user will grab the column
with the largest number and ignore the warnings."*

**The principal decided on a single file.** It is recorded as an **accepted risk**,
not a solved problem: logical separation and a warning in the documentation are
exactly what the design review points out that nobody reads.

**Mitigation adopted, which is the only thing that works inside a single file:** the
column name carries the warning, because the name does travel with the data when
someone copies it. Hence `cota_estilizada_colocacion_no_es_derecho`. It is a
deliberately uncomfortable name.

In addition, the first codebook row for that column and the list of ignored
restrictions from §4.3.4 are published adjacent to it.


---

## 23. External prior source — blind capture and non-contamination · v2.4

There is a serious prior source covering 45 of the 47 units: the CBR (Cambridge)
labour regulation index, 1970–2022, with a public codebook and a statutory citation
per country. Its discovery changes the workflow, and it brings a **process** risk
that is in none of its eight known gaps.

### 23.1 What the prior source can and cannot do

| It can | It cannot |
|---|---|
| Supply reform candidates with a date and a citation | **Confirm the absence of a reform** |
| Serve as evidence of the **existence and date** of an event | Prove the **quantum** of a version, not even as `verificado_secundaria` |
| Locate the applicable statute | Excuse reading it and deriving the value under our construct |

**Its source level is 4**, not 1. The prior-art note called it "T1" and that word is
dangerous because `nivel_de_fuente` is a constrained field: nobody should load a 1
citing that phrase.

**That the prior source records no change means absence in *its* construct and in
*its* window, not in ours.** It is blind to the seniority schedule, to the day type,
to cells censored at its cap, to the subnational, and to 2023–2026. Taking its
silence for confirmation would reintroduce the bias towards zero this project exists
to correct — this time with a prestigious source as an alibi, that is, harder to
detect, not easier.

### 23.2 Blind capture — mandatory

1. **Whoever codes does not see the prior source's value before capturing.** The
   cross-check is computed **afterwards**.
2. **Agreement with the prior source never raises `estado_verificacion`.**
   Coinciding is not verifying.
3. **The double-coding sample is stratified** to include censored and divergent
   cells, not only concordant ones.

**Why, and this is the risk none of the prior source's gaps captures.** If the coder
sees the external value before capturing, their judgement drifts towards it, and
blind double coding **stops being blind**: both coders end up anchored to the same
third party. "Zero by default" would be replaced by "prior source by default".

And there is a second half, worse: if the prior source decides **where the search
happens**, verification effort is allocated away from its blind spots — which are
exactly the six things this project declares as its own contribution. Residual errors
would concentrate where we claim novelty, and agreement would be reported as high
precisely because the sample was conditioned on the prior source. That is selection
on the dependent variable (§13), through another door.

### 23.3 Where the external data live

Tables `medicion_externa`, `reforma_externa` and `crosswalk_causa`, **outside the
`hechos` register**: they are not facts of the project, they are observations from
another instrument. They cannot be referenced by `evidencia`, `reforma_versiones` or
`mediciones`.

The four different rules the prior source applies to federal countries —which today
live as narrative prose in its codebook, country by country— become a **field**:
`regla_subnacional_efectiva`. Whoever uses the number will know which jurisdiction
they bought.

Four new validations enforce it: one prevents a cell being verified on the prior
source alone, and three require the cause of divergence to be declared where there
is censoring, a non-statutory basis, or a subnational rule other than the uniform
one.

### 23.4 What this opens up

- **Auditing the prior source, not merely using it.** The cross-check with coded
  causes measures, unit by unit, the wedge between "normal duration by statute or
  agreement at an indeterminate federal scale" and "the reference worker's statutory
  entitlement in working days". Nobody has measured that wedge.
- **Test of the persistence bias.** Cross-checking the prior source's years of change
  against the imputed historical column of the imported material says how many real
  reforms the persistence assumption swallowed. It is the quantified indictment of
  the defect that organises the design.


---

## 24. Layered placement rules, and what can be derived from them · v2.5

**A substantive amendment, not an implementation detail.** v2.4 defined a
`control_del_momento` field as an enumeration of five values in the leave row. A
targeted search and the cross-review's re-attack invalidated it for two distinct reasons, and
both change the estimand, so this is a protocol amendment and not a schema detail.

### 24.1 Why the enumeration did not work

**First, it presupposed that someone decides.** In the legal systems reviewed no
such thing exists: there is a worker who proposes and an employer who may refuse on
enumerated grounds. The value `trabajador` was instantiated in no unit at all, so
the derived accessible cap would have been `NA` across the whole universe.

**Second, and more seriously, it flattened structure.** One and the same entitlement
may be governed by **concurrent, residual or hierarchical** rules. Dutch article
7:638(2) establishes that the worker's request rule operates only over what is **not
already fixed** by written agreement, collective agreement, competent body or
statute. The Belgian official source describes a four-level cascade. A mandatory
scalar per version can represent neither.

### 24.2 What replaces it

The **`regla_colocacion`** table, a child of `vacaciones_version`.

**Two modes, and they are not the same structure.** `modo_aplicacion` distinguishes
**partition** from **cascade**:

- **Partition**: each rule governs a different portion of the entitlement. This is
  the Dutch case — the agreement fixes one part and the rest is residual.
- **Cascade**: several levels attempt to fix **the same** entitlement in order, and
  the next one operates if the previous one does not fix it. This is the Belgian
  case. Treating it as portions would require inventing days the statute does not
  contain.

A cascade requires `grupo_fallback`, exactly one **unconditional root**
(`es_raiz_fallback`) which must also be the one of lowest precedence, and successors
with a `condicion_fallback` from a closed vocabulary. A single-level group is not a
cascade: it is a simple rule mislabelled, and it is rejected.

Common fields: precedence order, scope —the whole entitlement, a defined portion or
the residual—, the instrument establishing it, initiative, and two **conditional**
attributes: ground for veto and silence rule, which exist **if and only if** the
initiative belongs to the worker. Where the portion is expressed in days, the day
type is mandatory and must match the version's.

The rule is an **evidenceable fact**: it carries its own provenance, because the
layers come from different instruments and a global source on the parent version
would not resolve it.

**The unit of allocation is the claimed portion, not the row.** A partition claims
one portion per rule; a cascade claims **a single** portion per group, because its
levels compete to fix the same thing. All the arithmetic of the entitlement is
evaluated over those units:

- A unit of **total scope coexists with no other**, whether partition or cascade.
  Two claims over the whole entitlement are a conflict, not layers.
- There is **at most one residual unit** per version: the remainder is one.
- A **residual is defined against something**. If there is no defined portion in the
  version, it is not a remainder: it is the whole entitlement declared through the
  back door, and it is rejected. An entitlement governed by a single rule is declared
  of total scope, which is exclusive.
- The portions **sum to at most the entitlement**: the fraction does not exceed one
  and the days do not exceed the version's quantum, counting cascades and partitions
  together.
- Over one and the same version **days and fractions are not mixed** without a
  conversion basis, nor across modes.
- Coverage is established in **three** ways, not two: total scope, a residual picking
  up what is unassigned, **or portions that already sum to exactly the entitlement**.
  Always requiring a residual made a legitimate exhaustive partition such as
  `0.5 + 0.5` unrepresentable.
- And conversely: **if the portions already sum to the entitlement, a residual picks
  up nothing** and is rejected. An empty residual feigns coverage.
- The **cascade condition does not exist in a partition**. There is no previous level
  to be conditioned on.

This is specified here because validating it by mode is not enough. While the
arithmetic checks looked only at the partition, **labelling a rule as a cascade was
enough to exempt it from all of them**: a cascade of 0.6 coexisting with a partition
of 0.5 plus a residual summed to 1.1 of the entitlement without a single violation.
The net existed and was evadable by label.

That conditionality matters: forcing them always to be present manufactured values
where the concept does not apply. A calendar fixed by statute has no "employer veto",
and filling it in with `ninguno` would be inventing a fact.

### 24.3 Derivation of the accessible cap · **restrictive by default**

The rule, taken from the cross-review's re-attack and adopted without softening:

| Situation | `cota_accesible_al_trabajador` |
|---|---|
| A single rule, total scope, worker's initiative, **veto `ninguno`** | = the cap |
| Any veto, for cause or discretionary | **`NA`**, cause `veto_no_evaluado` |
| Negotiated initiative | **`NA`**; it feeds `cota_negociable`, not the accessible one |
| Collective shutdown or fixed calendar | **`NA`**, cause `fechas_no_capturadas` (§4.3.4 decided not to capture the date domain) |
| Layered rules | **`NA`**, cause `regla_no_uniforme` |

**Approval by silence does not change the result.** It describes the effect of a
contingent event —the employer staying silent— not a guarantee. And the placement
that maximises free time is precisely the one most likely to collide with a
compelling operational reason: the regime that makes the cap attractive is the same
one that makes the veto likely.

**An expected consequence, not a measured one.** Under this criterion
`cota_accesible_al_trabajador` is **expected** to come out `NA` across most of the
universe. If measurement bears that out, it will be a reportable finding; until then
it is a **prediction of the design**, and calling it a finding would be overclaiming.
Not a single placement rule has been coded yet.

What can be asserted now is the normative point: establishing that the cap is
attainable would require modelling and evaluating the ground for veto against every
possible calendar, which is a different project from this one.

What does remain measurable and worth reporting is the **procedure**: who takes the
initiative, on what ground the employer may refuse, and what happens in the face of
silence. That is a legitimate institutional characterisation; it is not a cap.

### 24.4 Status of the fields

Placement rules are **facts of law**: they describe the statute. They go in the
entitlement layer, not in the behavioural block of §17bis. The **caps derived** from
them do stay outside the entitlement columns, as §17bis requires.


---

## 25. Batch → protocol link, and an overclaim withdrawn · v2.6

### 25.1 Each batch declares which protocol it was captured against

`lote_captura` now carries `version_protocolo` and `hash_protocolo`, both mandatory.
It closes a blocker the cross-review had been flagging since rev103 and that I had tried to
resolve with a comment in the schema header.

**Why a comment did not do.** It desynchronises the moment the protocol changes, and
in fact it did: the header was still declaring v2.3 when the protocol was at v2.5. A
comment is not a reconstructible link; a mandatory column per batch is.

**Two text columns are not enough either.** Measured: a batch accepted
`version = 'banana'` with sixty-four letter `z`s, and the whole pair could be
rewritten after the batch was closed. That is not a link, it is two editable strings.
The specification in force is:

- **Catalogue of frozen protocols.** Each frozen version is a row with its version,
  its SHA-256 hash, the archived file that reproduces it, and the freeze stamp. The
  version is unique and the version–hash pair is the key.
- **Composite foreign key from the batch.** A batch cannot declare a pair that is not
  frozen. Inventing one on the fly stops being possible.
- **Accredited format.** The hash is sixty-four hexadecimal characters —length alone
  is not enough—, the version has the exact form `vN.N`, the path is a flat copy under
  `docs/archivo/` ending in `.md`, and the freeze stamp passes the same date and time
  checks as the batch. The first three were hardened in v2.9 after a reproducible
  attack: `v2v.8`, `v2.8v`, `v2.8.1` and the empty path all got through, and with them
  a whole batch could be closed.
- **Immobility at both ends.** The batch's pair is part of its audited identity and is
  never touched, not even while the batch is still blind. And the catalogue entry is
  neither edited nor deleted: if its file could be repointed, the register would stop
  reconstructing anything.

**What this buys, and what it does not — corrected in v2.9.** This paragraph used to
claim that given any batch «the exact document it was coded against is recovered and
its hash verified». **That is false, and the correction goes here and not in a
separate section.** What the schema guarantees is narrower: a batch cannot declare a
version–hash pair that is not in the catalogue, that pair is immobile at both ends,
and the path has the shape of an archived copy. None of that establishes that the file
exists or that its content reproduces the hash.

The reason belongs to the tool, not the design: **SQLite does not read the disk or
compute SHA-256.** No declarative constraint can tie a row to a file. Measured on this
same schema: an invented version can be seeded with a well-formed hash corresponding
to no file, a batch tied to it, frozen and cross-checked, and the cycle closes without
a single violation.

**Declared limitation of the dataset.** Reproducing the document from a historical
batch depends on an external check —`scripts/verificar_congelamiento.py`, which
recomputes each hash against the real file— and that check **is not a mandatory gate
of the closing cycle**. It is a decision of the principal's, taken knowing what it
costs: it was preferred not to add a step to the capture flow and to declare the gap
rather than promise a guarantee the database does not sustain. Whoever uses the
dataset should run that verification if they need the full guarantee.

What is closed, and it is not little: without the catalogue, a historical batch
pointed at a file that had already changed, and the pair could be rewritten after the
batch was closed.

### 25.2 Withdrawal of an overclaim

§24.3 said the accessible cap would be `NA` across almost the whole universe and
called that **"the finding"**. It is an expectation derived from the criterion, not a
measured result. **The correction was applied in §24.3 itself**, not here: leaving the
claim in place and retracting it in another section produced a document that
contradicted itself, which is exactly what the cross-review flagged afterwards.

It is the third time in this series that I have confused a consequence of the
criterion with a result. It is recorded as a pattern, not an incident — and as the
fourth methodological lesson: **a retraction has to correct the original, not be
appended to it**.


---

## 26. How the protocol is named and verified · v2.8

**The document in force is called `docs/02-protocolo.md` and carries no version in
its name.** Each freeze leaves an immutable copy in
`docs/archivo/02-protocolo-vX.Y.md`, and it is that copy —never the one in force—
that the register cites.

**Why.** With a versioned name, each version renamed the file and left every written
reference behind. The measured result: four historical register entries pointed at the
same file in force, so the verification the register itself mandates failed in four of
nine cases; one archived copy was labelled v2.3 and contained v2.2; and v2.6 had no
copy. None of the three is visible by reading: they appear on recomputation.

**Reproducible verification.** `scripts/verificar_congelamiento.py` walks the
register, recomputes the SHA-256 of each declared file and reports discrepancies. It
is the only admissible way to assert that the register is sound; the assertion in
prose does not count. The fifth methodological lesson, and it is of the same kind as
the previous ones: **an integrity register that is not executed is prose**.

**Operating rule.** Freezing a version means: copy the one in force to
`docs/archivo/`, add the entry with its hash and its file, and run the verifier. If
the verifier does not pass, the version is not frozen.

**No exceptions — corrected in v2.9.** The verifier exempted from this rule any entry
whose title contained `VIGENTE`, and v2.8 was frozen pointing at the live document
under cover of that exception. A rule whose observance depends on how a heading is
worded is not a rule. The exception was removed, the v2.8 copy was created after the
fact —identical byte for byte, same hash— and the correction of the pointer was
written into the register instead of being made in silence. The check is now
structural: the path begins with `docs/archivo/` or the entry fails, both in the
verifier and in the catalogue's `CHECK`.

---

## 27. Hardening the catalogue, and what stays outside the database · v2.9–v2.12

A reproducible attack on the v2.8 schema seeded the version `v2v.8` with a fictitious
hash and `archivo = ''`, tied a batch to that pair, froze it and cross-checked it.
**The whole cycle closed without a single violation.** Three things failed at once.

**What was closed in the schema.** The version `CHECK` admitted the `v` in any
position and any number of dots; it now requires the exact form `vN.N`. The path had
no restriction at all; it must now be a **flat copy under `docs/archivo/` ending in
`.md`**. That last point matters for what it teaches: **the §26 rule was a path-prefix
rule, and a path prefix is expressible in SQL.** We had left it in prose out of habit,
not out of impossibility. It is worth asking that of every rule before declaring it
inexpressible.

**And the prefix alone was not enough — corrected in v2.10.** The first version of
that constraint required only the prefix, and the cross-review broke it immediately:
`docs/archivo/../02-protocolo.md` matches the prefix and **resolves to the document in
force**, which is precisely what the rule forbids. A double slash and traversal from a
subdirectory also got through. The lesson is of the same kind as the previous ones:
**a path prefix does not bound a path that can double back.** The closure does not
consist in enumerating traversals —that race is lost— but in using a fact about the
structure: the protocol archive is **flat**, so what follows the prefix cannot contain
any slash. That kills `..`, `//` and subdirectories at once. The same check lives in
the verifier, because SQLite's `CHECK` does not reach the Markdown register.

**What cannot be closed there.** SQLite does not read the disk or compute SHA-256, so
no declarative constraint ties a catalogue row to a real file. A well-formed
sixty-four-character hexadecimal hash corresponding to nothing still gets in. That
stays as a **declared limitation**, specified in §25.1, by decision of the principal:
it was preferred not to turn the verifier into a mandatory gate of the capture cycle
and to declare the gap precisely, rather than promise a guarantee the database does
not sustain.

**The gate backing the limitation failed open — corrected in v2.11.** §25.1 declares
that the full guarantee depends on an external check. The cross-review attacked that check and
found that the verifier recognised a register entry only if its hash was already
well-formed: **a corrupt hash did not produce an error, it made the entry disappear**,
and the verifier checked the remainder and announced that all reproduced. A gate that
fails open is not a gate, and the defect was worse than the ones it detects, because
it affected exactly the mechanism the declared limitation depends on.

The cause was fusing two questions into one: *whether the block purports to be an
entry* and *whether it is well-formed*. Now the first decides whether it is examined
—it is enough that it declares a file or hash row— and the second decides whether it
passes. A hash that is absent, short, uppercase, unquoted or duplicated is a failure,
not an invisibility. Regressions in `scripts/probar_verificador.py`, which corrupts the
register in memory and requires the verifier to fail in all seven ways.

**And the whole entry was still disappearing — corrected in v2.12.** the adversarial review, who
reviewed the previous fix because whoever wrote it cannot approve it, found that the
open failure persisted **one level up**. Correcting the malformed hash does not fix the
fact that the register need contain nothing: with an empty register the verifier
announced «0 entries verified, all reproduce» and exited successfully; with an entry
deleted, it verified the remaining thirteen and exited successfully; and with Cyrillic
homoglyphs in a table's labels —`Аrchivo`, visually identical— the block became
invisible and it exited successfully. Moreover the title was never read, so a
duplicated or apocryphal version passed just the same.

**The closure is an anchor, not a symptom patch.** Every protocol copy in
`docs/archivo/` must have exactly one entry, and every entry must point at an existing
copy whose name carries its version. It is a bijection, and that is why the three ways
of making an entry disappear all fail at once: the file is left orphaned. Copies that
legitimately are not frozen versions are declared in a table of the register itself
that the verifier reads — **a declared exception is visible; an exception hidden in the
code is a hole by another name**.

The general lesson, and it is the one that repeats most in this series: **verifying
what a register says it contains says nothing about what it ought to contain.** It has
to be anchored to something outside itself.

**Two more things that came out of that review.** The register's current-status block
declared a schema hash from two versions earlier and **was compared with nothing**; it
is now checked. And the regressions are no longer satisfied with the verifier exiting
with an error: **each case declares which message it expects**, because exiting with an
error for another reason is indistinguishable from not having tested anything.

**Criterion applied.** The agreed stopping rule is not «no defects» but *no residual
defect may corrupt data silently*. This one was silent and now is not: it is stated in
the protocol, it has a verifier that detects it, and the adversarial case demonstrating
it is reproducible with `python3 scripts/probar_catalogo.py`. A declared and executable
defect stops being silent — which is precisely what the criterion asks.

---

## 28. Four construct decisions that came out of the pilot · v2.13

The eight pilot units were captured on 2026-08-09 and produced what a pilot exists to
produce: **real statutes the schema could not represent**. None was forced. The four
decisions are the principal's.

### 28.1 Date delegated to the local jurisdiction

Guatemala grants «the day of the locality's festivity» and El Salvador «the most
important festivity of the place, **according to custom**». The holiday exists with
certainty at national level and its date **is not determinable at that level**.

`clase_de_regla` gains `delegada_a_jurisdiccion_local`, which **forbids** every date
field. What was rejected: putting it in `dependiente_de_proclamacion`, which would have
forced the coder to **invent a non-existent proclamation** for the schema to accept it.

### 28.2 Unit of the legal text, with a declared weekly base

Germany grants «24 **Werktage**» —they include Saturday, exclude Sundays and holidays,
on a six-day week—. Coding them as working days **overstates the German entitlement by
20%**. Ontario grants «**2 weeks**», and storing «10 days» would be presenting a
conversion of ours as if it were the legal text.

`tipo_de_dia` now admits `werktage` and `semanas`, and `base_semanal_dias` enters,
**mandatory when the unit is defined against the week** and forbidden when the days are
calendar days, because there the conversion is a property of the worker
—`regimen_jornada`— and not of the statute.

It is more general than enumerating units: any statute written on a six-day week
becomes representable without touching the schema again.

### 28.3 Non-annual periodic recurrence

Mexico grants 1 October **every six years**, for the transfer of the Executive.
`recurrencia` only distinguished the annual from the extraordinary.

`periodo_anios` enters, mandatory for the recurrent and forbidden for the
extraordinary. **What it buys is concrete**: with two cuts, that holiday may fall in one
and not the other, and the coder would record a delta that **is not a reform**. With the
period explicit the calculation excludes it or notes it, instead of depending on someone
remembering.

### 28.4 Placement by state assignment

Indonesia fixes each year, by decree of three ministers, 8 days of *cuti bersama* that
**are deducted from the 12-day balance** of annual leave. It is not a holiday that adds
nor a recoverable bridge: it is free time charged against the entitlement.

`regla_colocacion.iniciativa` gains `asignacion_estatal`, distinct from
`cierre_colectivo` because the State decides it and not the employer. **No new field was
needed**: the portion arithmetic already in place makes the worker's accessible cap fall
on its own from 12 to 4 days.

### 28.5 Verification

```bash
python3 scripts/probar_decisiones_piloto.py
```

It tests all four **with the statutes that provoked them**, and with both halves: the
forbidden states are rejected and the faithful structures enter clean.

A note of method worth writing down: **writing those cases took four attempts and all
four failures were in the fixture, not in the schema** —a non-existent column, a value
out of domain, a mandatory column omitted, a wrong name—. Each one read as «the schema
rejects the valid». It is the first failure pattern of this series, and that is why the
legitimate cases are explicit: without them, a broken fixture reads as a strict schema.

---

## 29. Two more date classes, and why they go separately · v2.14

Loading the eight units left **two holidays out of ninety-four** that no class admitted.
The loader refused to force them and counted them, which is the correct behaviour: the
convenient label would have been invisible precisely because it was plausible.

| Unit | Literal | Why it did not fit |
|---|---|---|
| Ontario | «the Monday preceding May 25» | It is not `ordinal` —not the nth Monday of the month— nor `relativa`, whose anchor is a **movable** feast. Here the anchor is a **date** |
| Mexico | «the one determined by federal and local electoral statutes» | The date exists but lives in **another body of law** |

**They go separately by decision of the principal, and the reason matters.** Putting them
in a single «not determinable» class would have hidden that **the first one is
computable**: Victoria Day is deterministic and can generate occurrences. Losing that to
gain one fewer class is losing real data in exchange for schema convenience.

**`relativa_a_fecha`.** `mes` and `dia` are the anchor, `dia_semana` the target and the
**sign** of `offset_dias` the direction — negative for the preceding, positive for the
following. Zero displacement is forbidden: without a direction the rule says nothing.

**`remision_normativa`.** It requires `instrumento_remitido` and forbids every date
field. A cross-reference without a destination is not a cross-reference, it is a hole
with a name; and that is why the destination is forbidden in the other classes, so that
the field means something where it appears.

### 29.1 State of the pilot after these two

**94 holidays across the eight units, zero omitted, the 37 validations at zero.**

| Class | Holidays |
|---|---:|
| `fija` | 68 |
| `relativa` | 16 |
| `ordinal` | 6 |
| `delegada_a_jurisdiccion_local` | 2 |
| `relativa_a_fecha` | 1 |
| `remision_normativa` | 1 |

**A quarter of the pilot's holidays carry no date written in their statute.** With a
schema that accepted only fixed dates, that 25% would have been lost or —worse— invented.

---

## 30. Close of the pilot and freezing of the schema · v2.15

The eight units were captured in **both variables**, with the 37 validations at zero.
The pilot ends here and the schema is frozen, in the order the principal set:
**close the capture backlog first**, because those are the class of case that broke
the schema seven times.

### 30.1 The imputation was in the counting unit

The `imputacion_feriados_a_vacaciones` field was verified **one by one**, by decision
of the principal, instead of being derived from the day type. The correspondence was
confirmed in all eight:

| Counting unit | Imputation | Units |
|---|---|---|
| calendar days | `se_computan_contra` | Peru, El Salvador |
| working days · werktage · weeks | `extienden` | Guatemala, Mexico, Indonesia, Canada, Germany, Turkey |

Verifying instead of deriving changed the result in one case, and that case justifies
the whole decision. **El Salvador says the opposite of what the rule would have
predicted for its neighbour**: its article 178 explicitly establishes that holidays
and rest days falling within the period **shall not extend** its duration — and it
adds a restriction no other unit has: leave **may not begin** on such days.

Canada did not fit the reasoning either. Its rule is not that the holiday does not
consume leave, but that it generates a **substitute day** with holiday pay. It arrives
at the same place by another route, and it is visible only by reading.

And Indonesia forced the separation of two things a single field would have merged:
national holidays do **not** reduce the balance, and *cuti bersama* does. That is why
the second is modelled as a portion of state placement and not as imputation.

### 30.2 A convergence that validates a design decision

`werktage` was added to the schema because of Germany. On resolving the Turkish day
type it turned out that Turkey has **the same semantics**: its article 56/5 excludes
Sundays and holidays from the count, and Saturday counts unless otherwise agreed.

The value served without being touched. It is evidence that a **general unit** with a
declared weekly base was the right choice, and not a value named after a country.

### 30.3 What is declared at freezing

- **Sources to be raised.** Eight of eighteen are at level 1; six remain at level 4.
  Each capture carries the note.
- **The 2016 cut of two units was not captured** and was not filled in from the other:
  Indonesia, whose calendar is decreed each year, and El Salvador.
- **Two units with a zero delta and no verified absence**: Guatemala and Toronto.
  Their zero **is not a finding**, and the panel says so where it shows the zero.
- **The Turkish religious holidays** —lunar, multi-day and with a half-day eve— are
  not captured.

---

## 31. Scaling to 47 broke the frozen schema, and it was foreseen · v2.16

The schema was frozen with eight units. On capturing the 47, five independent
capturers found more gaps in one day than fifteen adversarial rounds. Unfreezing has a
cost —§9 requires recomputing the panel— and here it is cheap because the panel is
derived from the database with one command.

### 31.1 An Easter is not the Easter

`ancla` admitted a bare `pascua`. **Two different batches found the gap and resolved
it in opposite ways**: one coded the five Romanian Orthodox holidays as `pascua`
—which produces a wrong date **silently**, because the two Easters differ by up to
five weeks— and the other omitted the Greek ones for the same reason. The dataset was
left internally inconsistent and nobody would have seen it by reading.

`pascua_ortodoxa` and `equinoccio_septiembre` enter, the latter missing and needed by
Japan. **An anchor that does not distinguish the computation is not an anchor.**

### 31.2 Four loader defects the data uncovered

**The serious one, and it was a claim of mine.** The validity field admitted only a
year, with a comment saying that «for cuts at 1 January any date within the year gives
the same result». **That is false.** Portugal restored four holidays on 2 April 2016
—the reversal of 2013, the rare case the project was looking for— and the loader gave
13 holidays at the 2016 cut where 9 belong. The correction goes where the error was,
and `desde` now admits a full date.

**The loader asserted what the capture denied.** It stamped
`descanso_pagado_obligatorio` on every holiday and ignored the capture's `categoria`
and `regimen`. For the Netherlands and Japan that is false: an official list exists and
there is **no** obligation to grant it free or paid. For the Netherlands the difference
is **9 against 0**.

**A qualifying period of zero months** —Norway, where the entitlement does not depend
on accrual— generated a degenerate band that rejected the whole unit.

**And an imprecise statute date** in a source's metadata brought down the entire unit
over an incidental field.

### 31.3 What remains open, declared

The capturers reported more than thirty schema findings. Those that change numbers and
have **not** been closed:

- **A fifth counting unit.** Israel grants 16 days that include at most one weekly rest
  day per seven and exclude public holidays. It is neither calendar, nor working days,
  nor werktage, nor weeks.
- **The AGE schedule.** Hungary, Norway and Switzerland scale by the worker's age, not
  by seniority; Switzerland moreover **decreasingly**. `escala_antiguedad` is indexed on
  months of service.
- **Annual leave cannot be dated.** The holidays module knows how to date its reforms
  and the leave module does not, so the Japanese reform of 2019 and the Israeli one of
  2016 are invisible.
- **Cascading placement**, in at least six units: «by agreement; failing agreement, the
  employer». The database supports it; the capture contract does not expose it.
- **Disjunctive date rules**: the Irish St Brigid's Day is ordinal except when 1
  February falls on a Friday.
- **Thailand has no calendar, it has a quota**: thirteen days the employer designates
  from an open set.
- **`base_semanal_dias` is required where the statute does not fix it.** Eight units
  define the unit against *the worker's* schedule, not against a statutory week. It
  forces a review of whether the bases already entered were **read or chosen**.

---

## 32. Who fixes the weekly base · v2.17

`base_semanal_dias` was required whenever the unit was not calendar days. That was
correct for Germany, whose statute is written explicitly on a six-day week. **Eight
units from the scale-up showed it is not general**: they define the entitlement
against *the worker's* schedule, not against a statutory week.

> New Zealand: «what genuinely constitutes a working week for the employee».
> Netherlands: «vier maal de overeengekomen arbeidsduur per week».

There is no base to read there, and requiring it forced its invention — the same
factor-of-two error, coming in through the other door. Four units failed to load for
that reason, and a capturer flagged what matters: **it is worth reviewing whether the
bases already entered were read or chosen.**

`base_semanal_origen` enters. If the statute fixes it, the base is mandatory; if the
worker's schedule fixes it, it goes null and the conversion uses `regimen_jornada`.
What remains forbidden is **omitting it silently**, which was the only thing the
previous CHECK did catch.

---

## 33. The cross-check against the prior source, measured · v2.18

The cross-check was computed over the 47 units, after capture, as §23.2 requires. It
produces two results of different natures and they should not be confused.

### 33.1 Annual leave: the divergence **is** the finding

The CBR normalises its variable 9 «with an entitlement of 30 days equivalent to 1».
**Thirty days of what, it does not say.** And its own coding notes show that it is not
a single unit:

| Unit | Its note | They code | Do they convert? |
|---|---|---:|---|
| Germany | «24 working days if 6 days week; if 5 days week: 20 days» | 20 | **yes** |
| Turkey | «14 days» | 14 | **no** |
| Peru | «30 days» | 30 | **no**, and they are calendar days |

Turkey and Germany have the **same legal structure** —days excluding Sunday and
public holidays and including Saturday— and receive different treatment.

Converted to work days on a five-day week, the mean difference against their figure
**orders by the unit the statute is written in**: the further the statutory unit is
from «work days on a five-day week», the more generous the country appears in the
index.

**The figures of that ordering live in the «Findings» appendix, not here**, and the
reason is one of design and not of space. This document is frozen by hash, and a
frozen document **cannot contain a live statistic**: freezing certifies that the text
did not change, whereas a result inside it ends up certifying that a number which did
change did not. The two properties are incompatible and the wrong one wins — the
document stays intact and lying. It already happened: this table came to publish half
the value of the row that sustains the finding, and it could not be corrected without
breaking the freeze that made it citable.

What stays here is the METHOD, which is what does not age. If the conversion needs
illustrating, the example is **arithmetic and not measured**: thirty calendar days are
30/7 = 4.29 weeks *whatever is worked*, and twenty-four Werktage on a six-day week are
exactly 4. That is an identity, not a result, and it remains true when the data change.

**A caveat that travels with the finding.** Our conversion is also a convention: taking
30 calendar days to 21.4 assumes a five-day week. The difference is not that we hold
the truth — it is that we publish **the statutory number, its unit and its base
separately**, so that anyone can recompute with another convention. From an index
between 0 and 1 neither how many days there were nor of what type can be recovered.

There is nothing to reconcile here. It is published.

### 33.2 Public holidays: the divergence is a **question**, and it is classified

13 of 41 units agree within one day. The remaining 28 **are not 28 errors of theirs**,
and classifying them is half the work:

- **An artefact of ours.** France and Thailand come out at 1 because of our regime
  filter: in France only 1 May is statutory mandatory rest, and Thai law names one
  holiday and leaves the rest as an employer quota.
- **A different construct.** The United Kingdom and Turkey come out at +8 and +7.5
  because the CBR codes them at zero, and it documents this: there, rest on a holiday
  depends on the contract.
- **Rounding noise.** Their index carries two decimals; any difference below 0.2 is
  arithmetic.
- **Real disagreement.** Some twenty with differences of 1 to 3 days.

**For that last group, reconciling would be the error.** A cross-check that ends with
the two series identical has learned nothing: it copied the other. What is done is to
**classify** each divergence as our error, their being out of date, or a construct
difference — and to publish the breakdown, which is what nobody has published about the
reliability of the field's most used source.

**A declared asymmetry.** Our side is audited date by date, because each holiday carries
its statute. Theirs is not: their index does not say which days it counted. In several
cases it will be possible to assert «ours is right» without being able to assert
«theirs is wrong», and that asymmetry is in itself an argument of the project.

---

## §34 · Blind double coding, and the field it uncovered

The requirement of §23.2 point 3 finally executed, over a stratified sample of units.
Its record is in [`notes/07-doble-codificacion.md`](../notes/07-doble-codificacion.md),
frozen before applying any correction — because the most valuable divergence disappears
the moment it is fixed.

**The figures are not published, and this is a v2.26 amendment.** The agreement rates,
the second readings and the program that cross-checks them are kept in the project's
internal documentation and stay out of the published package; the archived v2.25 of
this protocol contains them. The reason is in `EXCLUSIONES.md`: withdrawing the
conclusion while leaving the input would allow them to be recomputed without the
caveats that accompany them, and a figure without its caveat is worse than none.
**That this section mentions the exercise must not be read as a claim of high
agreement.**

What is doctrine and stays: pairing uses a **strict** criterion, not a fuzzy one. When
two mentions are different transliterations of the same holiday they are not paired —
doing so would require comparison by resemblance, and judging a resemblance is not
recognising an identity.

**What it found, and it is more than a rate.** A missing Colombian holiday —Law 2578 of
June 2026—, corrected. An error in the second coding itself —it anchored Greek Easter to
the Western one—, not corrected because ours was already right. And a systemic defect in
the placement variable, which is what motivates the rest of this section.

### 34.1 · The layer error: splitting is not placement

In five of the eight units, the article governing **dividing the rest period into
blocks** had been used —or invited use— as if it governed **when the whole rest period
is taken**. They are different articles and confusing them inverts who controls the
entitlement.

Peru had it wrong: the capture used art. 17 of D. Leg. 1405 (splitting at the worker's
written request) to code placement as the worker's initiative, when art. 14 of D. Leg.
713 says it is fixed by mutual agreement and that **failing agreement the employer
decides**. Israel, Greece, France and Turkey present the same trap; the first three have
been read, Turkey is declared pending.

**Rule, from now on:** the placement rule is read from the article that fixes the
**timing**. If the captured literal speaks of dividing, accumulating or deferring, it is
not the placement article even if it looks like it.

### 34.2 · `resolucion_desacuerdo`, a new field

Nine units were coded `negociada` and concealed **six different regimes** of what
happens when agreement is not reached. The schema could not express it: `veto_empleador`
belongs by table constraint to the worker's request rules, and rightly so — a veto only
exists against a request.

| value | what it means | precedent |
|---|---|---|
| `empleador` | the employer decides | Peru art. 14, Portugal 241.º n.º 2, France L3141-16 |
| `limite_razonabilidad` | may refuse, but not without cause | Australia s.88(2), New Zealand s.18(4) |
| `trabajador_prevalece` | the employer is obliged to grant | Greece art. 224 |
| `tercero_dirime` | the tie-break comes from the parties | Spain art. 38.2 ET |
| `remitido_a_convenio` | the law delegates, it does not stay silent | Indonesia pasal 79(4) |
| `sin_regla` | the law is silent, and that is a state | Israel |

It is mandatory when the initiative is `negociada`, by table constraint and with `=`,
not with a one-way implication: if it were optional, a coder in a hurry would leave it
`null` and we would return to the collapse the field exists to undo.

**Why it matters beyond the datum.** Collapsing different legal structures under one
label is exactly what this project charges to the prior source. We were doing it in the
placement variable, and it was seen only because two independent readers read the same
statutes.


---

## §35 · The seven holidays without a class, closed

Seven holidays from five units were recorded with no representable date class and were
therefore **outside the count**. Four decisions of the principal close them, and all
four have something in common: none invents a date, all of them extend what the schema
*knows how to say*.

With the last one closed, the loader reports **0 holidays omitted across the 47 units**.

### 35.1 · Two solstices in the anchor catalogue

Chile grants «the day of the winter solstice of each year in the southern hemisphere»:
deterministic and computable with ephemerides, between 20 and 22 June. The catalogue had
the two equinoxes and no solstice. `solsticio_junio` and `solsticio_diciembre` are added
— both, because a catalogue with three of the four cardinal points of the year invites
the next omission.

Fixing it to 21 June would have been writing down the typical year and being wrong in
the others, which is precisely the convenient approximation this protocol exists not to
make.

### 35.2 · Several date rules per holiday, with a condition

**This is the underlying decision, and it resolves four cases that looked like three
problems.**

A holiday may have several rules, each with the condition under which it governs, and
**at most one without a condition** — the one that governs by default, guaranteed by a
partial unique index.

Two things that were thought distinct follow from this:

**Conditional existence.** Chile declares 2 January a holiday only when it falls on a
Monday, and 17 September only when the 18th and 19th fall on a weekend. No existence
field is needed: **a holiday all of whose rules carry a condition does not occur in the
years when none is met.** The absence of a default rule *is* conditional existence.

**Disjunctive rule.** St Brigid's Day in Ireland is the first Monday of February except
when 1 February falls on a Friday. Yom HaAtzmaut in Israel shifts 5 Iyar in three ways
depending on the day of the week. They are two and four catalogue rules alternating, not
new classes.

`condicion_referencia` says which date is examined, and all three forms are needed:

| value | what it examines | case |
|---|---|---|
| `propia` | the date the rule itself computes | Chile: 2 January is a holiday when 2 January falls on a Monday |
| `regla_por_defecto` | the date of the same holiday's unconditional rule | Israel: the alternatives produce 3, 4 and 6 Iyar, but the condition is examined on the 5th |
| `MM-DD` | a different fixed date | Ireland: 1 February is examined while the default produces the first Monday |

The distinction between the first two is not a subtlety: with `propia`, Israel would ask
about the day of the week of the **result** instead of the **base**, and would give the
wrong answer.

A note on Ireland: the single-sentence formulation in circulation —«the first Monday in
February, or 1 February if that date falls on a Friday»— comes from the *Explanatory
Note*, which the instrument itself declares **non-binding**. The operative text is rules
4 and 5, separate, and separately they are coded.

### 35.3 · Lunar day counted from the end of the month

Korea grants the eve of the lunar New Year, which its decree defines as «음력 12월 말일»:
the last day of month 12, which is the 29th or the 30th depending on the year. The
`lunar` class required a fixed day between 1 and 30.

`dia_lunar_desde_fin` is added, where 1 is the last day, mutually exclusive with
`dia_lunar` by table constraint. The `-1` sentinel was discarded: a number that means
something other than a number is a trick nobody remembers two months later.

### 35.4 · Quota designated by the employer

Thailand names **one** holiday by statute and leaves twelve days to the employer's
designation within a traditional set. It is not `delegada_a_jurisdiccion_local` —it is
fixed not by the jurisdiction but by the employer— nor `remision_normativa`, because
there is no single statute to refer to.

The `cuota_designada_por_empleador` class records the **quantity** and the **set**,
without dates. The set is mandatory: a quota without a set cannot be audited, only
believed.

With this Thailand goes from 1 to **13**, which was the largest single-unit discrepancy
against the prior source — and it matches their figure exactly.

The structure will reappear: in France, ten of the eleven public holidays are defined by
collective agreement and not by statute.

### 35.5 · What the net caught, again

On loading the alternative rules they lacked evidence: only the principal one received
its source link. **V1 —«fact without evidence»— caught it with twelve rows.** A fact
without a source is not auditable even if it is the rare variant of a holiday.


---

## §36 · The statutory working week, and why it had to be captured

A rest metric only means something **against the days that would have been worked**.
That counterfactual is not in a leave statute: it is a fact of working-time law. It was
captured for the 47 units, in five batches, and it filled the `regimen_jornada` table,
which had existed empty since the design.

It closed two gaps the rest metric had declared about itself: the worker's week, and
what happens when a holiday falls on weekly rest.

### 36.1 · Three confusions not to make, because I made two

**The basis of the leave statute is not the working week.** The Austrian 30 Werktage
are written on a six-day week; the Austrian worker does five. Using the first as the
second put Austria first in the metric with 42 released days. It was an artefact.

**Nor is the guaranteed minimum rest the working week.** That British law guarantees one
rest day does not mean six are worked: subtracting from seven gives the **maximum
permitted**, not the ordinary. I was about to publish the table with that deduction.

**And the weekly figure may be a product and not a text.** German working-time law
**writes no weekly figure at all**: its 48 hours are eight times six Werktage, and the
six exist because §9 removes Sunday and public holidays from the calendar. The datum
that confirms it is that the federal reform under discussion consists literally of
*writing* that ceiling.

Hence `dias_ordinarios` carries its origin alongside, with four values:

| value | what it means |
|---|---|
| `declarado` | the statute writes the number — Hungary: «five days, Monday to Friday» |
| `derivado` | it comes from dividing the weekly ceiling by the daily one — Germany, Korea |
| `alternativa_legal` | the law **does not choose** and declares between which values — Chile 5–6, Colombia and Indonesia |
| `no_declarado` | silence: the distribution goes to the contract or the collective agreement |

**Naming without choosing is a legal act distinct from staying silent**, and that is why
`alternativa_legal` is not merged with `no_declarado`. Only **21 of 47** units have
ordinary days fixed or derivable from the law; in the remaining 26 the five-day
convention is applied and flagged. The gain from the capture is not having filled those
26 in: it is knowing which they are.

### 36.2 · Mechanism and effect are two fields

What the statute does when a holiday falls on weekly rest, and what the worker ends up
receiving, are different questions. Mixing them was the first design and it did not
survive contact with the data: **eight mechanisms** appeared where I expected two.

| mechanism | case |
|---|---|
| `traslada` | Belgium: substitutes a working day |
| `anade_dia` | Australia: at Christmas and New Year it **adds** a day, it does not substitute |
| `reduce_cuota_de_horas` | Poland: it moves nothing, it deducts eight hours from the period's quota |
| `compensa_en_dinero` | Italy: additional pay, no day |
| `compensa_a_eleccion` | Ireland: the employer chooses between a day and money |
| `regla_sin_efecto` | Honduras: there is a rule and it delivers nothing |
| `se_pierde` | Peru, Germany, Switzerland: the exclusion is **written** |
| `sin_regla` | Sweden: silence |
| `no_aplicable` | Netherlands, Denmark: no statutory paid holiday exists |

And separately, the **effect**, which is the only thing the metric needs:
`dia_libre` · `dinero` · `dia_o_dinero_a_eleccion` · `ninguno` · `indeterminado`.

Poland justifies the split on its own: an unusual mechanism, an effect identical to a
substitution. Italy is the reverse: an easy mechanism to understand, zero effect in
days. `indeterminado` exists because of Nicaragua, whose article says the day «shall be
compensated» without saying with what — choosing on its behalf would be imputing.

**`se_pierde` is not merged with `sin_regla`.** Germany and Switzerland have negative
textual anchoring: their statute says expressly that there is nothing there. A zero with
a statute behind it is not a zero by omission, just as staying silent was not delegating.

### 36.3 · The loading date

The value in force **on 1 January of the cut year** is loaded. It is not a new choice:
it is the date the project already uses in `mediciones`, and using another would make
working time and holidays measured at different moments of the same cut.

It matters because three units change within the window and two within 2026 itself:
Chile moves to 42 hours on 26 April and Colombia on 15 July, so at the cut both are at
44. Mexico steps 48 → 40 between 2026 and 2030 and at the cut is at 48. The full ladders
are kept in the capture so that any date can be recomputed.

### 36.4 · Normalisation lives in the loader, not in the captures

The five batches used different vocabularies because the template I gave them carried
examples and not closed domains. The fault is mine and the correction goes in
`scripts/cargar_jornada.py`, in one place and in plain sight.

**Other people's captures are not rewritten to make them uniform.** Making someone
else's file uniform erases the reason they wrote it that way, and that reason is exactly
what distinguishes Chile's `null` —a statutory range— from Turkey's —silence.


---

## §37 · Expected counting, and why comparison between cuts requires it

The project measures the **evolution of a statutory entitlement between two cuts**. That
estimand forces a decision about public holidays that looks technical and is not.

A fixed-date holiday falls on a weekend some two years in every seven. If the count uses
the calendar of the cut year, a unit's figure **moves without any law changing**, and
that variation enters the 2016–2026 comparison as if it were a reform.

### 37.1 · How much it weighs, measured

| count | units changing by more than one day between cuts | median absolute change |
|---|---:|---:|
| realised in the cut year | **23 of 45** | **1.85 days** |
| expected | 10 of 45 | **0.00 days** |

With realised values, half the sample moves and the median country shifts 1.85 days —
**of the same order as the reforms the project is looking for**. With the expectation,
the median country moves exactly zero, and those that move are the ones that reformed:
Korea +16, Spain +12.8, Indonesia +12, El Salvador +10.3, Greece +4.3, Romania +3.9,
Peru +3.1, Slovakia −2.9.

**Separating calendar rotation from real reform is exactly the distinction this project
exists to make**, and realised counting does not make it.

### 37.2 · What is averaged, and what is not

The expectation is defensible because **it does not smooth the whole set: it touches
half**. Measured on the 2026 cut:

| class | weight | probability of releasing |
|---|---:|---|
| the law rescues it, wherever it falls | 32 % | 1 |
| anchored to Easter | 14 % | 1 or 0, **deterministic** |
| ordinal or moved to a target day | 3 % | 1 or 0, deterministic |
| **fixed date without rescue** | **49 %** | (7 − rest days) ÷ 7 |

The Easter case deserves the explanation because it is not obvious: Easter is **always a
Sunday**, so the holiday's displacement fixes its day of the week for every year. Good
Friday is always a Friday. There is nothing to average.

### 37.3 · Why assuming none falls on a weekend does not do

It is the obvious alternative and it has to be discarded in writing, because it looks
simpler: counting every holiday as if every one released a day.

**It gives the unit that substitutes and the one that does not exactly the same number.**
And that difference is worth from zero to six days depending on the country —Colombia
loses none because its Emiliani law moves them to Monday; Romania loses five and a
half—. The simplification would erase one of the two findings the working-time capture
came to produce.

### 37.4 · What the expectation does not fix

The published figure stops being «what happened in 2026» and becomes «what happens in a
typical year». For a statutory entitlement it is the correct estimand, but **it describes
no particular year** and must not be presented as if it did.

And effective holidays become **fractional**: Austria has 10.4 and not 10. It is an
expectation, not a count, and the label has to say so or it reads as a rounding error.
`--conteo realizado` remains available for anyone who wants a specific year's calendar.

## 38. The jurisdiction name is data, and it carries language

The package moves to being published in two languages, with English as the default
version. This section fixes what that forces to change in the **measurement**, not in
the writing.

### 38.1 What carries language and what does not

Language is carried by the text the project **writes**: country and reference
jurisdiction names, exhibit labels, appendix prose and glosses.

**It is not carried by the text the project CITES.** These stay in their original
language and are never translated:

| What | Why |
|---|---|
| The holiday's official name | It is the name the statute gives it. `Dia do Trabalho` is not a phrase to render: it is the identifier against which a verifier checks the source. Translating it breaks traceability, which is the only thing the verification appendix has. |
| The statutory literal | It is the verbatim quotation. Any retouching of ours falsifies it. |
| The statute's title and identifier | It is cited in order to locate it; translated, it locates nothing. |

The general rule: **if the reader would have to be able to search for it in the source,
it is not translated.**

### 38.2 The English name is a column, not a substitution

`jurisdicciones` gains `nombre_en`. The alternative was to map the names in the English
template, and it is discarded under §6: the publishable tabular file would still come
out in Spanish and there would be **two truths for the same fact**, resolved in the
format layer. A fact appearing in two documents with two values is a defect even if both
are legible.

Declared provenance: countries carry the **English short name from ISO 3166-1** —hence
`Türkiye` and `Czechia`, which are the ones in force—. Cities have no equivalent
standard: the established English exonym is used where one exists —Vienna, Copenhagen,
Warsaw— and the endonym where none does —Guayaquil, Managua. That is **editorial
convention** and it is said, not disguised as a standard.

### 38.3 Number format belongs to the language, and that is why parity does not compare text

The decimal comma was a decision taken **inside** the format function. It comes out to
the call: `32,4` in Spanish, `32.4` in English, the same figure well formatted twice.

From this follows how it is checked that the two versions say the same thing.
**Comparing the resolved text would give a false positive on every decimal figure**, and
a gate that always fails ends up loosened until it checks nothing. What is compared is:

1. the **set of marks** —identical in both versions—;
2. the **underlying value** of each mark, before formatting;
3. the **structure**: number and level of headings in order, number and form of the
   exhibits, referenced figures.

Titles differ between languages by definition; structures and values cannot. It is the
same preference of §35 for the structural test over the arithmetic one: the structural
one has no model of its own to get wrong.
