-- =====================================================================
-- 02_cargar_datos.sql
-- Base de datos: observatorio_tatacoa          Motor: PostgreSQL
--
-- Carga 10 registros de ejemplo en cada una de las 5 tablas.
-- Se ejecuta DESPUÉS de 01_crear_tablas.sql (con las tablas recién creadas).
--
-- Orden de carga: primero las tablas "padre" y al final las que tienen
-- llaves foráneas, porque una FK solo puede apuntar a algo que ya existe.
--
-- Datos pensados para las pruebas:
--   * Hay registros CON relaciones (no se dejan eliminar) y registros SIN
--     relaciones (sí se dejan eliminar). Ejemplos:
--       - El tipo "Planeta" tiene astros        -> no se puede eliminar.
--       - El tipo "Cometa" no tiene astros      -> sí se puede eliminar.
--       - El telescopio TEL-01 tiene observaciones; el TEL-10 no.
-- =====================================================================

SET client_encoding = 'UTF8';


-- ---------------------------------------------------------------------
-- 1. tipos_astro   (quedan con id del 1 al 10, en este orden)
-- ---------------------------------------------------------------------
INSERT INTO tipos_astro (nombre, descripcion) VALUES
('Planeta',           'Cuerpo que gira alrededor de una estrella y no tiene luz propia'),
('Satélite natural',  'Cuerpo que gira alrededor de un planeta, como la Luna'),
('Estrella',          'Esfera de gas muy caliente que produce su propia luz'),
('Nebulosa',          'Nube de gas y polvo en el espacio'),
('Cúmulo estelar',    'Grupo de estrellas que nacieron de la misma nube'),
('Galaxia',           'Conjunto de miles de millones de estrellas'),
('Cometa',            'Cuerpo de hielo y polvo que forma una cola al acercarse al Sol'),
('Asteroide',         'Cuerpo rocoso pequeño que gira alrededor del Sol'),
('Planeta enano',     'Cuerpo redondo, más pequeño que un planeta, como Plutón'),
('Estrella doble',    'Dos estrellas que giran una alrededor de la otra');


-- ---------------------------------------------------------------------
-- 2. astros   (id_tipo_astro apunta a la tabla anterior)
--    Los planetas y las lunas no tienen constelación fija: queda en NULL.
-- ---------------------------------------------------------------------
INSERT INTO astros (nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES
('Luna',                 2, NULL,        TRUE),
('Júpiter',              1, NULL,        TRUE),
('Saturno',              1, NULL,        TRUE),
('Titán',                2, NULL,        FALSE),
('Sirio',                3, 'Can Mayor', TRUE),
('Betelgeuse',           3, 'Orión',     TRUE),
('Nebulosa de Orión',    4, 'Orión',     TRUE),
('Nebulosa del Anillo',  4, 'Lira',      FALSE),
('Pléyades',             5, 'Tauro',     TRUE),
('Galaxia del Sombrero', 6, 'Virgo',     FALSE);


-- ---------------------------------------------------------------------
-- 3. telescopios
-- ---------------------------------------------------------------------
INSERT INTO telescopios (codigo, nombre, tipo, apertura_mm) VALUES
('TEL-01', 'Celestron NexStar 8SE',        'Catadióptrico', 203),
('TEL-02', 'Sky-Watcher Dobson 250',       'Reflector',     254),
('TEL-03', 'Meade LX200 12 pulgadas',      'Catadióptrico', 305),
('TEL-04', 'Celestron AstroMaster 130EQ',  'Reflector',     130),
('TEL-05', 'Sky-Watcher Evostar 80ED',     'Refractor',      80),
('TEL-06', 'Orion SkyQuest XT8',           'Reflector',     203),
('TEL-07', 'Takahashi FSQ-106',            'Refractor',     106),
('TEL-08', 'Celestron EdgeHD 14',          'Catadióptrico', 356),
('TEL-09', 'Sky-Watcher Skymax 127',       'Catadióptrico', 127),
('TEL-10', 'Explore Scientific ED102',     'Refractor',     102);


-- ---------------------------------------------------------------------
-- 4. astronomos   (personas y datos inventados para el ejemplo)
-- ---------------------------------------------------------------------
INSERT INTO astronomos (documento, nombre, correo) VALUES
('1075234567', 'Valentina Rojas Perdomo',     'valentina.rojas@example.com'),
('1075345678', 'Santiago Cárdenas Losada',    'santiago.cardenas@example.com'),
('36184592',   'Marta Lucía Trujillo',        'marta.trujillo@example.com'),
('7712345',    'Hernando Polanco Díaz',       'hernando.polanco@example.com'),
('1080123456', 'Daniela Cuéllar Ramos',       'daniela.cuellar@example.com'),
('1077456789', 'Andrés Felipe Medina',        'andres.medina@example.com'),
('55172634',   'Gloria Inés Tovar',           'gloria.tovar@example.com'),
('1079567890', 'Juan Sebastián Bermeo',       'juan.bermeo@example.com'),
('1081678901', 'Camila Andrea Quintero',      'camila.quintero@example.com'),
('12113456',   'Óscar Iván Cabrera',          'oscar.cabrera@example.com');


-- ---------------------------------------------------------------------
-- 5. observaciones   (3 llaves foráneas: astrónomo, telescopio y astro)
--
--    Columnas: fecha, id_astronomo, id_telescopio, id_astro,
--              duracion_min, calidad_cielo (1 a 5), notas
-- ---------------------------------------------------------------------
INSERT INTO observaciones
    (fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas)
VALUES
('2026-07-18', 1, 1, 3, 45, 5, 'Anillos muy nítidos; se distingue la división de Cassini.'),
('2026-07-18', 2, 2, 8, 60, 5, 'Se aprecia la forma de anillo usando visión lateral.'),
('2026-08-21', 3, 5, 1, 30, 4, 'Poco después del cuarto creciente; cráteres Tycho y Copérnico.'),
('2026-10-03', 1, 3, 3, 50, 4, 'Saturno cerca de su oposición; imagen muy estable.'),
('2026-10-03', 5, 3, 4, 25, 3, 'Titán se ve como un punto anaranjado junto a Saturno.'),
('2026-10-10', 2, 1, 2, 40, 4, 'Bandas ecuatoriales y las cuatro lunas galileanas.'),
('2026-10-17', 6, 7, 9, 35, 5, 'Todo el cúmulo cabe en el campo de visión.'),
('2026-11-06', 4, 2, 7, 55, 5, 'Se distinguen las cuatro estrellas del Trapecio.'),
('2026-11-07', 6, 4, 1, 20, 2, 'Nubes altas; solo se pudo observar por momentos.'),
('2026-11-14', 5, 1, 2, 45, 4, 'Gran Mancha Roja visible cerca del centro del disco.');
