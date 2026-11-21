# Justificación de la normalización (1FN, 2FN y 3FN)

Base de datos: `observatorio_tatacoa` · 5 tablas · Diagrama: [01_mer.png](01_mer.png)

## Las tres formas normales, en palabras sencillas

| Forma normal | Qué exige | Cómo se revisa |
|---|---|---|
| **1FN** | Cada casilla guarda **un solo valor** (nada de listas ni de columnas repetidas como `telefono1`, `telefono2`) y cada fila se distingue por una **llave primaria**. | Mirar que ningún campo guarde varios datos a la vez. |
| **2FN** | Cumplir 1FN y que cada campo dependa de **toda** la llave primaria, no de una parte. | Solo puede fallar cuando la llave primaria tiene varias columnas. |
| **3FN** | Cumplir 2FN y que ningún campo dependa de **otro campo que no sea la llave** (dependencia transitiva). | Preguntar por cada campo: «¿esto describe a *este* registro o a otra cosa?». |

**Sobre la 2FN en este proyecto:** las 5 tablas tienen una llave primaria de **una sola columna** (`id_...`, de tipo `SERIAL`). Con una llave de una sola columna es imposible depender de «una parte» de ella, así que todas las tablas que cumplen 1FN cumplen también 2FN.

## Tabla por tabla

### 1. `tipos_astro`

- **1FN:** `nombre` y `descripcion` guardan un solo valor cada uno. La llave primaria es `id_tipo_astro`.
- **2FN:** la llave primaria es de una sola columna.
- **3FN:** `nombre` y `descripcion` describen únicamente al tipo de astro. Ningún campo depende de otro campo que no sea llave.

### 2. `astros`

- **1FN:** un astro tiene un solo nombre, un solo tipo, una sola constelación y un solo valor de «visible a simple vista». La llave primaria es `id_astro`.
- **2FN:** la llave primaria es de una sola columna.
- **3FN:** del tipo de astro se guarda **solo su id** (`id_tipo_astro`), no su nombre ni su descripción. Si se guardara aquí el nombre del tipo, ese dato dependería de `id_tipo_astro` y no del astro: sería una dependencia transitiva. Para ver el nombre del tipo se hace un `JOIN` con `tipos_astro`.

### 3. `telescopios`

- **1FN:** `codigo`, `nombre`, `tipo` y `apertura_mm` guardan un solo valor cada uno. La llave primaria es `id_telescopio`.
- **2FN:** la llave primaria es de una sola columna.
- **3FN:** `codigo`, `nombre`, `tipo` y `apertura_mm` describen a ese telescopio en particular, el que identifica su llave. `nombre` es el nombre con que se conoce el equipo; no es una llave ni un catálogo de modelos. El campo `tipo` solo admite tres valores fijos (se controla con un `CHECK`) y ningún otro campo depende de él, por eso no hace falta una tabla aparte.

### 4. `astronomos`

- **1FN:** un documento, un nombre y un correo por persona. La llave primaria es `id_astronomo`.
- **2FN:** la llave primaria es de una sola columna.
- **3FN:** `documento`, `nombre` y `correo` describen únicamente al astrónomo. `documento` y `correo` son `UNIQUE` (llaves candidatas), no generan dependencias transitivas.

### 5. `observaciones`

- **1FN:** cada observación tiene una sola fecha, un solo astrónomo, un solo telescopio, un solo astro, una duración, una calidad del cielo y un texto de notas. La llave primaria es `id_observacion`.
- **2FN:** la llave primaria es de una sola columna.
- **3FN:** del astrónomo, del telescopio y del astro se guardan **solo sus id** (las 3 llaves foráneas). No se repite aquí el nombre del astrónomo ni el código del telescopio. `fecha`, `duracion_min`, `calidad_cielo` y `notas` describen a la observación y a nada más.

## ¿Qué se gana con esto?

- **Cada dato vive en un solo lugar.** Si un astrónomo cambia de correo, se corrige en una fila de `astronomos` y todas sus observaciones quedan bien.
- **No hay datos contradictorios.** Es imposible que «Júpiter» aparezca como *Planeta* en una observación y como *Estrella* en otra, porque el tipo se guarda una sola vez, en `astros`.
- **La base de datos cuida la integridad.** Las llaves foráneas impiden registrar una observación de un astro que no existe, o borrar un telescopio que ya tiene observaciones.
