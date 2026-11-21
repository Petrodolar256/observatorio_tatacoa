# Diccionario de datos

Base de datos: `observatorio_tatacoa` · Motor: PostgreSQL · Script: [`database/01_crear_tablas.sql`](../database/01_crear_tablas.sql)

**Abreviaturas de las restricciones**

| Abreviatura | Significado |
|---|---|
| **PK** | Llave primaria: identifica cada fila y no se repite. |
| **FK** | Llave foránea: apunta a la llave primaria de otra tabla. |
| **NOT NULL** | Obligatorio: no puede quedar vacío. |
| **UNIQUE** | Único: no puede haber dos filas con el mismo valor. |
| **CHECK** | Regla que el valor debe cumplir. |
| **DEFAULT** | Valor que se pone solo si no se indica otro. |

Todas las llaves primarias son `SERIAL`: PostgreSQL les asigna solo el siguiente número (1, 2, 3...).

Todas las llaves foráneas usan `ON UPDATE CASCADE ON DELETE RESTRICT`: **no se puede borrar** un registro mientras otra tabla lo esté usando.

---

## 1. `tipos_astro`

Categorías de astros: Planeta, Estrella, Galaxia...

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| `id_tipo_astro` | SERIAL | **PK** (`pk_tipos_astro`) | Identificador del tipo de astro. |
| `nombre` | VARCHAR(60) | NOT NULL, **UNIQUE** (`uq_tipos_astro_nombre`) | Nombre del tipo. Ejemplo: `Planeta`. |
| `descripcion` | VARCHAR(200) | Opcional (admite NULL) | Explicación corta del tipo. |

## 2. `astros`

Lo que se observa en el cielo: Júpiter, Sirio, la Luna...

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| `id_astro` | SERIAL | **PK** (`pk_astros`) | Identificador del astro. |
| `nombre` | VARCHAR(80) | NOT NULL, **UNIQUE** (`uq_astros_nombre`) | Nombre del astro. Ejemplo: `Júpiter`. |
| `id_tipo_astro` | INTEGER | NOT NULL, **FK** → `tipos_astro(id_tipo_astro)` (`fk_astros_tipo`) | Tipo al que pertenece el astro. |
| `constelacion` | VARCHAR(60) | Opcional (admite NULL) | Constelación donde se ubica. Los planetas y las lunas no tienen una fija. |
| `visible_a_simple_vista` | BOOLEAN | NOT NULL, DEFAULT `FALSE` | `TRUE` si se puede ver sin telescopio. |

## 3. `telescopios`

Equipos del observatorio.

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| `id_telescopio` | SERIAL | **PK** (`pk_telescopios`) | Identificador del telescopio. |
| `codigo` | VARCHAR(10) | NOT NULL, **UNIQUE** (`uq_telescopios_codigo`) | Placa de inventario. Ejemplo: `TEL-01`. Se guarda en mayúsculas. |
| `nombre` | VARCHAR(80) | NOT NULL | Nombre con que se conoce el equipo (su marca y modelo). |
| `tipo` | VARCHAR(20) | NOT NULL, **CHECK** (`ck_telescopios_tipo`): solo `Refractor`, `Reflector` o `Catadióptrico` | Tipo de óptica del telescopio. |
| `apertura_mm` | INTEGER | NOT NULL, **CHECK** (`ck_telescopios_apertura`): `apertura_mm > 0` | Diámetro del lente o espejo principal, en milímetros. |

## 4. `astronomos`

Personas que realizan las observaciones.

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| `id_astronomo` | SERIAL | **PK** (`pk_astronomos`) | Identificador del astrónomo. |
| `documento` | VARCHAR(15) | NOT NULL, **UNIQUE** (`uq_astronomos_documento`) | Número de documento de identidad, solo dígitos. |
| `nombre` | VARCHAR(100) | NOT NULL | Nombre completo. |
| `correo` | VARCHAR(120) | NOT NULL, **UNIQUE** (`uq_astronomos_correo`), **CHECK** (`ck_astronomos_correo`): debe contener `@` | Correo electrónico. Se guarda en minúsculas. |

## 5. `observaciones`

Tabla de movimientos: «un astrónomo observa un astro con un telescopio». Tiene **3 llaves foráneas**.

| Campo | Tipo de dato | Restricciones | Descripción |
|---|---|---|---|
| `id_observacion` | SERIAL | **PK** (`pk_observaciones`) | Identificador de la observación. |
| `fecha` | DATE | NOT NULL | Día de la observación. La aplicación no acepta fechas futuras. |
| `id_astronomo` | INTEGER | NOT NULL, **FK** → `astronomos(id_astronomo)` (`fk_observaciones_astronomo`) | Quién observó. |
| `id_telescopio` | INTEGER | NOT NULL, **FK** → `telescopios(id_telescopio)` (`fk_observaciones_telescopio`) | Con qué telescopio. |
| `id_astro` | INTEGER | NOT NULL, **FK** → `astros(id_astro)` (`fk_observaciones_astro`) | Qué astro se observó. |
| `duracion_min` | INTEGER | NOT NULL, **CHECK** (`ck_observaciones_duracion`): `duracion_min > 0` | Duración de la observación, en minutos. |
| `calidad_cielo` | INTEGER | NOT NULL, **CHECK** (`ck_observaciones_calidad`): entre 1 y 5 | Calidad del cielo: 1 = muy nublado, 5 = despejado. |
| `notas` | VARCHAR(300) | Opcional (admite NULL) | Qué se alcanzó a ver. |

---

## Relaciones (cardinalidades)

| Relación | Cardinalidad | Se lee así |
|---|---|---|
| `tipos_astro` → `astros` | 1 a N | Un tipo de astro clasifica muchos astros; cada astro tiene un solo tipo. |
| `astros` → `observaciones` | 1 a N | Un astro se observa muchas veces; cada observación es de un solo astro. |
| `astronomos` → `observaciones` | 1 a N | Un astrónomo realiza muchas observaciones; cada observación la hace un solo astrónomo. |
| `telescopios` → `observaciones` | 1 a N | Un telescopio se usa en muchas observaciones; cada observación usa un solo telescopio. |

## Dónde se valida cada regla

Las reglas de la base de datos se revisan **dos veces**: primero en la aplicación (para darle al usuario un mensaje claro) y luego en la base de datos (para que se cumplan siempre, sin importar por dónde lleguen los datos).

| Regla | En la aplicación | En la base de datos |
|---|---|---|
| Campos obligatorios | `validaciones.py` | `NOT NULL` |
| Longitud máxima de los textos | `validaciones.py` (parámetro `maximo`) | `VARCHAR(n)` |
| Valores que no se repiten | Se captura el error y se traduce en `db.py` | `UNIQUE` |
| Llaves foráneas válidas | `validar_seleccion()` en `validaciones.py` | `FOREIGN KEY` |
| Apertura y duración mayores que cero; calidad del cielo de 1 a 5 | `validar_entero()` con `minimo` y `maximo` | `CHECK` |
| Tipo de telescopio permitido | `validar_opcion()` con `TIPOS_DE_TELESCOPIO` | `CHECK` |
| No borrar registros en uso | Se captura el error y se traduce en `db.py` | `ON DELETE RESTRICT` |

Además, la aplicación tiene algunas reglas propias, que la base de datos no tiene:

| Regla | Dónde está |
|---|---|
| La fecha de una observación no puede ser futura | `validar_fecha()` con `permitir_futuro=False` |
| El documento solo tiene dígitos, entre 6 y 15 | `validar_documento()` |
| El correo tiene la forma `nombre@dominio.algo` y se guarda en minúsculas | `validar_correo()` |
| El código del telescopio se guarda en mayúsculas | `validar_codigo()` |
| Topes razonables: apertura hasta 20 000 mm y duración hasta 1 440 minutos (un día) | `validar_entero()` con `maximo` |
