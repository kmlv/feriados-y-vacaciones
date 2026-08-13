# Statutory holidays and annual leave — publishable package

[Leer en castellano](LEEME.md)

> **Procedencia de este documento.** Generado automáticamente. No editar a mano.
>
> | | |
> |---|---|
> | Protocolo | `v2.27` |
> | Hash del protocolo | `bb9db022dec2e48c…` |
> | Hash de la base | `44ddb8105c321371…` |
> | Hash del generador | `3f83fbd42e3e929f…` |
> | Versión publicada | `v1.0.1` |


## What is here

| path | what it is |
|---|---|
| `D1-main-report.md` · `.pdf` | The report in English: the problem, the method in brief, and the results |
| `D1-reporte-principal.md` · `.pdf` | The same report in Spanish. **Not a translation**: both versions are written in parallel against the same query marks, so their figures come from one query and each uses its own numeric convention |
| `D2-paises/<ISO3>.md` | Country appendix: sources, method given those sources, decisions |
| `D3-verificacion/<ISO3>.md` | Verification appendix, **Spanish only**: every number with its rule, its source and its arithmetic, and **with the passage quoted in the document where the capture carries one** — not in every cell. Whoever checks a figure reads the statute in its original language |
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

Everything in this package derives from the raw captures. **And for the tabular
files you can check that right here**, without downloading anything and without
leaving this folder:

```
./reproducir.sh
```

It rebuilds the database from `capturas/`, re-exports the tabular files into
`regenerado/`, and compares them **hash by hash** against those in `datos/`. The
answer is not «it ran»: it is *they match* or *these files do not match*. It
writes to a separate folder on purpose — re-exporting over `datos/` would erase
the only copy there is to compare against.

You need only Python 3, and **the command's scope is that, and worth stating**:
it rebuilds the database and the nine tabular files. It does **not** rebuild this
document, the appendices, the figures or the PDF — those additionally need
XeLaTeX and the templates, which do not travel. A command claiming to reproduce
«the whole package» would promise more than it does.

If you edit a capture and run it again it will stop matching: that is correct,
you have measured something else.

The hashes on the cover identify the compilation: two documents with different
hashes do not belong to the same package.
