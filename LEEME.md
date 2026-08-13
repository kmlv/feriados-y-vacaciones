# Feriados y vacaciones de ley — paquete publicable

[Read this in English](README.md)

> **Procedencia de este documento.** Generado automáticamente. No editar a mano.
>
> | | |
> |---|---|
> | Protocolo | `v2.27` |
> | Hash del protocolo | `bb9db022dec2e48c…` |
> | Hash de la base | `44ddb8105c321371…` |
> | Hash del generador | `3f83fbd42e3e929f…` |
> | Versión publicada | `v1.0.1` |


## Qué hay aquí

| ruta | qué es |
|---|---|
| `D1-reporte-principal.md` | El reporte en castellano: el problema, el método en síntesis y los resultados |
| `D1-main-report.md` | El mismo reporte en inglés. **No es una traducción**: las dos versiones se escriben en paralelo contra las mismas marcas, así que sus cifras salen de la misma consulta y su convención numérica es la de cada idioma |
| `D2-paises/<ISO3>.md` | Apéndice por país: fuentes, metodología dadas esas fuentes, decisiones |
| `D3-verificacion/<ISO3>.md` | Apéndice de verificación: cada número con su regla, su fuente y su aritmética, y **con el pasaje citado dentro del documento cuando la captura lo trae** — no en todas las celdas |
| `datos/` | Los archivos tabulares, con manifiesto de hashes |
| `capturas/<unidad>/` | El **dato crudo con procedencia**: lo que se leyó de cada norma, con su literal y su nivel de fuente. Todo lo demás sale de aquí |
| `metodo/` | El protocolo de medición, su registro de congelamiento, el esquema y las validaciones |
| `codigo/` | Los guiones que regeneran el paquete entero desde `capturas/` |
| `figuras/` | Las imágenes que el reporte referencia |
| `EXCLUSIONES.md` | Qué **no** incluye este paquete y por qué |
| `LICENCIA.md` | Condiciones de uso, incluidas las que no controlamos |
| `CITATION.cff` | Cómo citar |

## Por dónde empezar

Si quiere **el argumento**, lea `D1`. Si quiere **usar los datos**, empiece por
`datos/LEEME.md`. Si quiere **comprobar un número concreto**, vaya al `D3` de esa
unidad: está escrito para alguien sin acceso al repositorio del proyecto.

## Las tres cosas que hay que saber antes de usar las cifras

**1. Ningún número de vacaciones es comparable sin su unidad.** 47 unidades,
cuatro unidades de conteo distintas en las leyes. La cantidad legal va pegada al
tipo de día y a la base semanal; la cifra convertida está en otro archivo y
etiquetada como convención.

**2. No todo día festivo cuenta.** Filtre por régimen según lo que quiera medir, y
diga cuál usó.

**3. Ausencia no verificada no es ausencia.** Un delta de cero entre cortes puede
significar que no hubo reforma o que no se buscó, y los datos distinguen los dos
casos.

## Reproducibilidad

Todo lo de este paquete es derivado de las capturas crudas. **Y de los archivos
tabulares usted puede comprobarlo aquí mismo**, sin descargar nada y sin salir de
esta carpeta:

```
./reproducir.sh
```

Reconstruye la base desde `capturas/`, vuelve a exportar los archivos tabulares
a `regenerado/` y los compara **hash por hash** contra los de `datos/`. La
respuesta no es «ha funcionado»: es *coinciden* o *estas filas no coinciden*.
Sale a una carpeta aparte a propósito — reexportar encima de `datos/` borraría
la única copia contra la que comparar.

Sólo necesita Python 3, y **el alcance del comando es ése y conviene decirlo**:
rehace la base y los nueve archivos tabulares. **No** rehace este documento, los
apéndices, las figuras ni el PDF — eso necesita además XeLaTeX y las plantillas,
que no viajan. Un comando que dijera reproducir «todo el paquete» prometería más
de lo que hace.

Si modifica una captura y vuelve a correrlo, dejará de coincidir: eso es
correcto, ha medido otra cosa.

Los hashes de la portada identifican la compilación: dos documentos con hashes
distintos no pertenecen al mismo paquete.
