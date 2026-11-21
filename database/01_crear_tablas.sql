-- =====================================================================
-- 01_crear_tablas.sql
-- Base de datos: observatorio_tatacoa          Motor: PostgreSQL
--
-- Crea las 5 tablas del proyecto con sus llaves primarias (PK), llaves
-- foráneas (FK) y restricciones de integridad (NOT NULL, UNIQUE, CHECK).
--
-- La idea del modelo, en una frase:
--     "Un astrónomo observa un astro con un telescopio."
--
--     tipos_astro --< astros ----+
--     telescopios ---------------+--< observaciones
--     astronomos ----------------+
--
-- Cómo se ejecuta: lo hace solo  "python crear_base_de_datos.py".
-- También se puede pegar en la Query Tool de pgAdmin 4.
-- =====================================================================

SET client_encoding = 'UTF8';

-- Si las tablas ya existen, se borran para empezar de cero.
-- Se borran en orden inverso: primero las "hijas" (las que tienen FK).
DROP TABLE IF EXISTS observaciones;
DROP TABLE IF EXISTS astros;
DROP TABLE IF EXISTS tipos_astro;
DROP TABLE IF EXISTS telescopios;
DROP TABLE IF EXISTS astronomos;


-- ---------------------------------------------------------------------
-- 1. tipos_astro: las categorías de astros (Planeta, Estrella, Galaxia...)
-- ---------------------------------------------------------------------
CREATE TABLE tipos_astro (
    id_tipo_astro SERIAL,                  -- número automático: 1, 2, 3...
    nombre        VARCHAR(60)  NOT NULL,
    descripcion   VARCHAR(200),            -- opcional

    CONSTRAINT pk_tipos_astro        PRIMARY KEY (id_tipo_astro),
    CONSTRAINT uq_tipos_astro_nombre UNIQUE (nombre)
);


-- ---------------------------------------------------------------------
-- 2. astros: lo que se observa en el cielo (Júpiter, Sirio, la Luna...)
--    Cada astro pertenece a un tipo  ->  FK hacia tipos_astro
-- ---------------------------------------------------------------------
CREATE TABLE astros (
    id_astro               SERIAL,
    nombre                 VARCHAR(80) NOT NULL,
    id_tipo_astro          INTEGER     NOT NULL,
    constelacion           VARCHAR(60),                     -- opcional
    visible_a_simple_vista BOOLEAN     NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_astros        PRIMARY KEY (id_astro),
    CONSTRAINT uq_astros_nombre UNIQUE (nombre),
    CONSTRAINT fk_astros_tipo   FOREIGN KEY (id_tipo_astro)
        REFERENCES tipos_astro (id_tipo_astro)
        ON UPDATE CASCADE
        ON DELETE RESTRICT       -- no deja borrar un tipo que tenga astros
);


-- ---------------------------------------------------------------------
-- 3. telescopios: los equipos del observatorio
-- ---------------------------------------------------------------------
CREATE TABLE telescopios (
    id_telescopio SERIAL,
    codigo        VARCHAR(10) NOT NULL,    -- placa de inventario: TEL-01
    nombre        VARCHAR(80) NOT NULL,    -- marca y modelo
    tipo          VARCHAR(20) NOT NULL,
    apertura_mm   INTEGER     NOT NULL,    -- diámetro del lente o espejo

    CONSTRAINT pk_telescopios          PRIMARY KEY (id_telescopio),
    CONSTRAINT uq_telescopios_codigo   UNIQUE (codigo),
    CONSTRAINT ck_telescopios_tipo     CHECK (tipo IN ('Refractor', 'Reflector', 'Catadióptrico')),
    CONSTRAINT ck_telescopios_apertura CHECK (apertura_mm > 0)
);


-- ---------------------------------------------------------------------
-- 4. astronomos: las personas que hacen las observaciones
-- ---------------------------------------------------------------------
CREATE TABLE astronomos (
    id_astronomo SERIAL,
    documento    VARCHAR(15)  NOT NULL,
    nombre       VARCHAR(100) NOT NULL,
    correo       VARCHAR(120) NOT NULL,

    CONSTRAINT pk_astronomos           PRIMARY KEY (id_astronomo),
    CONSTRAINT uq_astronomos_documento UNIQUE (documento),
    CONSTRAINT uq_astronomos_correo    UNIQUE (correo),
    CONSTRAINT ck_astronomos_correo    CHECK (correo LIKE '%@%')
);


-- ---------------------------------------------------------------------
-- 5. observaciones: la tabla de movimientos (tiene 3 llaves foráneas)
--    "Un astrónomo observa un astro con un telescopio."
-- ---------------------------------------------------------------------
CREATE TABLE observaciones (
    id_observacion SERIAL,
    fecha          DATE    NOT NULL,
    id_astronomo   INTEGER NOT NULL,
    id_telescopio  INTEGER NOT NULL,
    id_astro       INTEGER NOT NULL,
    duracion_min   INTEGER NOT NULL,       -- cuántos minutos duró
    calidad_cielo  INTEGER NOT NULL,       -- 1 = muy nublado ... 5 = despejado
    notas          VARCHAR(300),           -- opcional

    CONSTRAINT pk_observaciones PRIMARY KEY (id_observacion),

    CONSTRAINT fk_observaciones_astronomo FOREIGN KEY (id_astronomo)
        REFERENCES astronomos (id_astronomo)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_observaciones_telescopio FOREIGN KEY (id_telescopio)
        REFERENCES telescopios (id_telescopio)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_observaciones_astro FOREIGN KEY (id_astro)
        REFERENCES astros (id_astro)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT ck_observaciones_duracion CHECK (duracion_min > 0),
    CONSTRAINT ck_observaciones_calidad  CHECK (calidad_cielo BETWEEN 1 AND 5)
);
