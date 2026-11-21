--
-- PostgreSQL database dump
--

\restrict iFxvwb6OBcenqAX4fpJUJMVO5IKb38DuGUbMbJWGNNURnYMal1R0j4uXwPv6Grh

-- Dumped from database version 18.7
-- Dumped by pg_dump version 18.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.observaciones DROP CONSTRAINT IF EXISTS fk_observaciones_telescopio;
ALTER TABLE IF EXISTS ONLY public.observaciones DROP CONSTRAINT IF EXISTS fk_observaciones_astronomo;
ALTER TABLE IF EXISTS ONLY public.observaciones DROP CONSTRAINT IF EXISTS fk_observaciones_astro;
ALTER TABLE IF EXISTS ONLY public.astros DROP CONSTRAINT IF EXISTS fk_astros_tipo;
ALTER TABLE IF EXISTS ONLY public.tipos_astro DROP CONSTRAINT IF EXISTS uq_tipos_astro_nombre;
ALTER TABLE IF EXISTS ONLY public.telescopios DROP CONSTRAINT IF EXISTS uq_telescopios_codigo;
ALTER TABLE IF EXISTS ONLY public.astros DROP CONSTRAINT IF EXISTS uq_astros_nombre;
ALTER TABLE IF EXISTS ONLY public.astronomos DROP CONSTRAINT IF EXISTS uq_astronomos_documento;
ALTER TABLE IF EXISTS ONLY public.astronomos DROP CONSTRAINT IF EXISTS uq_astronomos_correo;
ALTER TABLE IF EXISTS ONLY public.tipos_astro DROP CONSTRAINT IF EXISTS pk_tipos_astro;
ALTER TABLE IF EXISTS ONLY public.telescopios DROP CONSTRAINT IF EXISTS pk_telescopios;
ALTER TABLE IF EXISTS ONLY public.observaciones DROP CONSTRAINT IF EXISTS pk_observaciones;
ALTER TABLE IF EXISTS ONLY public.astros DROP CONSTRAINT IF EXISTS pk_astros;
ALTER TABLE IF EXISTS ONLY public.astronomos DROP CONSTRAINT IF EXISTS pk_astronomos;
ALTER TABLE IF EXISTS public.tipos_astro ALTER COLUMN id_tipo_astro DROP DEFAULT;
ALTER TABLE IF EXISTS public.telescopios ALTER COLUMN id_telescopio DROP DEFAULT;
ALTER TABLE IF EXISTS public.observaciones ALTER COLUMN id_observacion DROP DEFAULT;
ALTER TABLE IF EXISTS public.astros ALTER COLUMN id_astro DROP DEFAULT;
ALTER TABLE IF EXISTS public.astronomos ALTER COLUMN id_astronomo DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.tipos_astro_id_tipo_astro_seq;
DROP TABLE IF EXISTS public.tipos_astro;
DROP SEQUENCE IF EXISTS public.telescopios_id_telescopio_seq;
DROP TABLE IF EXISTS public.telescopios;
DROP SEQUENCE IF EXISTS public.observaciones_id_observacion_seq;
DROP TABLE IF EXISTS public.observaciones;
DROP SEQUENCE IF EXISTS public.astros_id_astro_seq;
DROP TABLE IF EXISTS public.astros;
DROP SEQUENCE IF EXISTS public.astronomos_id_astronomo_seq;
DROP TABLE IF EXISTS public.astronomos;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: astronomos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.astronomos (
    id_astronomo integer NOT NULL,
    documento character varying(15) NOT NULL,
    nombre character varying(100) NOT NULL,
    correo character varying(120) NOT NULL,
    CONSTRAINT ck_astronomos_correo CHECK (((correo)::text ~~ '%@%'::text))
);


--
-- Name: astronomos_id_astronomo_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.astronomos_id_astronomo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: astronomos_id_astronomo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.astronomos_id_astronomo_seq OWNED BY public.astronomos.id_astronomo;


--
-- Name: astros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.astros (
    id_astro integer NOT NULL,
    nombre character varying(80) NOT NULL,
    id_tipo_astro integer NOT NULL,
    constelacion character varying(60),
    visible_a_simple_vista boolean DEFAULT false NOT NULL
);


--
-- Name: astros_id_astro_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.astros_id_astro_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: astros_id_astro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.astros_id_astro_seq OWNED BY public.astros.id_astro;


--
-- Name: observaciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.observaciones (
    id_observacion integer NOT NULL,
    fecha date NOT NULL,
    id_astronomo integer NOT NULL,
    id_telescopio integer NOT NULL,
    id_astro integer NOT NULL,
    duracion_min integer NOT NULL,
    calidad_cielo integer NOT NULL,
    notas character varying(300),
    CONSTRAINT ck_observaciones_calidad CHECK (((calidad_cielo >= 1) AND (calidad_cielo <= 5))),
    CONSTRAINT ck_observaciones_duracion CHECK ((duracion_min > 0))
);


--
-- Name: observaciones_id_observacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.observaciones_id_observacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: observaciones_id_observacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.observaciones_id_observacion_seq OWNED BY public.observaciones.id_observacion;


--
-- Name: telescopios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.telescopios (
    id_telescopio integer NOT NULL,
    codigo character varying(10) NOT NULL,
    nombre character varying(80) NOT NULL,
    tipo character varying(20) NOT NULL,
    apertura_mm integer NOT NULL,
    CONSTRAINT ck_telescopios_apertura CHECK ((apertura_mm > 0)),
    CONSTRAINT ck_telescopios_tipo CHECK (((tipo)::text = ANY ((ARRAY['Refractor'::character varying, 'Reflector'::character varying, 'Catadióptrico'::character varying])::text[])))
);


--
-- Name: telescopios_id_telescopio_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.telescopios_id_telescopio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: telescopios_id_telescopio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.telescopios_id_telescopio_seq OWNED BY public.telescopios.id_telescopio;


--
-- Name: tipos_astro; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipos_astro (
    id_tipo_astro integer NOT NULL,
    nombre character varying(60) NOT NULL,
    descripcion character varying(200)
);


--
-- Name: tipos_astro_id_tipo_astro_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tipos_astro_id_tipo_astro_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipos_astro_id_tipo_astro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tipos_astro_id_tipo_astro_seq OWNED BY public.tipos_astro.id_tipo_astro;


--
-- Name: astronomos id_astronomo; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astronomos ALTER COLUMN id_astronomo SET DEFAULT nextval('public.astronomos_id_astronomo_seq'::regclass);


--
-- Name: astros id_astro; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astros ALTER COLUMN id_astro SET DEFAULT nextval('public.astros_id_astro_seq'::regclass);


--
-- Name: observaciones id_observacion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observaciones ALTER COLUMN id_observacion SET DEFAULT nextval('public.observaciones_id_observacion_seq'::regclass);


--
-- Name: telescopios id_telescopio; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.telescopios ALTER COLUMN id_telescopio SET DEFAULT nextval('public.telescopios_id_telescopio_seq'::regclass);


--
-- Name: tipos_astro id_tipo_astro; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_astro ALTER COLUMN id_tipo_astro SET DEFAULT nextval('public.tipos_astro_id_tipo_astro_seq'::regclass);


--
-- Data for Name: astronomos; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (1, '1075234567', 'Valentina Rojas Perdomo', 'valentina.rojas@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (2, '1075345678', 'Santiago Cárdenas Losada', 'santiago.cardenas@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (3, '36184592', 'Marta Lucía Trujillo', 'marta.trujillo@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (4, '7712345', 'Hernando Polanco Díaz', 'hernando.polanco@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (5, '1080123456', 'Daniela Cuéllar Ramos', 'daniela.cuellar@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (6, '1077456789', 'Andrés Felipe Medina', 'andres.medina@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (7, '55172634', 'Gloria Inés Tovar', 'gloria.tovar@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (8, '1079567890', 'Juan Sebastián Bermeo', 'juan.bermeo@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (9, '1081678901', 'Camila Andrea Quintero', 'camila.quintero@example.com');
INSERT INTO public.astronomos (id_astronomo, documento, nombre, correo) VALUES (10, '12113456', 'Óscar Iván Cabrera', 'oscar.cabrera@example.com');


--
-- Data for Name: astros; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (1, 'Luna', 2, NULL, true);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (2, 'Júpiter', 1, NULL, true);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (3, 'Saturno', 1, NULL, true);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (4, 'Titán', 2, NULL, false);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (5, 'Sirio', 3, 'Can Mayor', true);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (6, 'Betelgeuse', 3, 'Orión', true);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (7, 'Nebulosa de Orión', 4, 'Orión', true);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (8, 'Nebulosa del Anillo', 4, 'Lira', false);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (9, 'Pléyades', 5, 'Tauro', true);
INSERT INTO public.astros (id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista) VALUES (10, 'Galaxia del Sombrero', 6, 'Virgo', false);


--
-- Data for Name: observaciones; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (1, '2026-07-18', 1, 1, 3, 45, 5, 'Anillos muy nítidos; se distingue la división de Cassini.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (2, '2026-07-18', 2, 2, 8, 60, 5, 'Se aprecia la forma de anillo usando visión lateral.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (3, '2026-08-21', 3, 5, 1, 30, 4, 'Poco después del cuarto creciente; cráteres Tycho y Copérnico.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (4, '2026-10-03', 1, 3, 3, 50, 4, 'Saturno cerca de su oposición; imagen muy estable.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (5, '2026-10-03', 5, 3, 4, 25, 3, 'Titán se ve como un punto anaranjado junto a Saturno.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (6, '2026-10-10', 2, 1, 2, 40, 4, 'Bandas ecuatoriales y las cuatro lunas galileanas.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (7, '2026-10-17', 6, 7, 9, 35, 5, 'Todo el cúmulo cabe en el campo de visión.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (8, '2026-11-06', 4, 2, 7, 55, 5, 'Se distinguen las cuatro estrellas del Trapecio.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (9, '2026-11-07', 6, 4, 1, 20, 2, 'Nubes altas; solo se pudo observar por momentos.');
INSERT INTO public.observaciones (id_observacion, fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas) VALUES (10, '2026-11-14', 5, 1, 2, 45, 4, 'Gran Mancha Roja visible cerca del centro del disco.');


--
-- Data for Name: telescopios; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (1, 'TEL-01', 'Celestron NexStar 8SE', 'Catadióptrico', 203);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (2, 'TEL-02', 'Sky-Watcher Dobson 250', 'Reflector', 254);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (3, 'TEL-03', 'Meade LX200 12 pulgadas', 'Catadióptrico', 305);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (4, 'TEL-04', 'Celestron AstroMaster 130EQ', 'Reflector', 130);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (5, 'TEL-05', 'Sky-Watcher Evostar 80ED', 'Refractor', 80);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (6, 'TEL-06', 'Orion SkyQuest XT8', 'Reflector', 203);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (7, 'TEL-07', 'Takahashi FSQ-106', 'Refractor', 106);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (8, 'TEL-08', 'Celestron EdgeHD 14', 'Catadióptrico', 356);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (9, 'TEL-09', 'Sky-Watcher Skymax 127', 'Catadióptrico', 127);
INSERT INTO public.telescopios (id_telescopio, codigo, nombre, tipo, apertura_mm) VALUES (10, 'TEL-10', 'Explore Scientific ED102', 'Refractor', 102);


--
-- Data for Name: tipos_astro; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (1, 'Planeta', 'Cuerpo que gira alrededor de una estrella y no tiene luz propia');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (2, 'Satélite natural', 'Cuerpo que gira alrededor de un planeta, como la Luna');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (3, 'Estrella', 'Esfera de gas muy caliente que produce su propia luz');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (4, 'Nebulosa', 'Nube de gas y polvo en el espacio');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (5, 'Cúmulo estelar', 'Grupo de estrellas que nacieron de la misma nube');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (6, 'Galaxia', 'Conjunto de miles de millones de estrellas');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (7, 'Cometa', 'Cuerpo de hielo y polvo que forma una cola al acercarse al Sol');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (8, 'Asteroide', 'Cuerpo rocoso pequeño que gira alrededor del Sol');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (9, 'Planeta enano', 'Cuerpo redondo, más pequeño que un planeta, como Plutón');
INSERT INTO public.tipos_astro (id_tipo_astro, nombre, descripcion) VALUES (10, 'Estrella doble', 'Dos estrellas que giran una alrededor de la otra');


--
-- Name: astronomos_id_astronomo_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.astronomos_id_astronomo_seq', 10, true);


--
-- Name: astros_id_astro_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.astros_id_astro_seq', 10, true);


--
-- Name: observaciones_id_observacion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.observaciones_id_observacion_seq', 10, true);


--
-- Name: telescopios_id_telescopio_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.telescopios_id_telescopio_seq', 10, true);


--
-- Name: tipos_astro_id_tipo_astro_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipos_astro_id_tipo_astro_seq', 10, true);


--
-- Name: astronomos pk_astronomos; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astronomos
    ADD CONSTRAINT pk_astronomos PRIMARY KEY (id_astronomo);


--
-- Name: astros pk_astros; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astros
    ADD CONSTRAINT pk_astros PRIMARY KEY (id_astro);


--
-- Name: observaciones pk_observaciones; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observaciones
    ADD CONSTRAINT pk_observaciones PRIMARY KEY (id_observacion);


--
-- Name: telescopios pk_telescopios; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.telescopios
    ADD CONSTRAINT pk_telescopios PRIMARY KEY (id_telescopio);


--
-- Name: tipos_astro pk_tipos_astro; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_astro
    ADD CONSTRAINT pk_tipos_astro PRIMARY KEY (id_tipo_astro);


--
-- Name: astronomos uq_astronomos_correo; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astronomos
    ADD CONSTRAINT uq_astronomos_correo UNIQUE (correo);


--
-- Name: astronomos uq_astronomos_documento; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astronomos
    ADD CONSTRAINT uq_astronomos_documento UNIQUE (documento);


--
-- Name: astros uq_astros_nombre; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astros
    ADD CONSTRAINT uq_astros_nombre UNIQUE (nombre);


--
-- Name: telescopios uq_telescopios_codigo; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.telescopios
    ADD CONSTRAINT uq_telescopios_codigo UNIQUE (codigo);


--
-- Name: tipos_astro uq_tipos_astro_nombre; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_astro
    ADD CONSTRAINT uq_tipos_astro_nombre UNIQUE (nombre);


--
-- Name: astros fk_astros_tipo; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.astros
    ADD CONSTRAINT fk_astros_tipo FOREIGN KEY (id_tipo_astro) REFERENCES public.tipos_astro(id_tipo_astro) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: observaciones fk_observaciones_astro; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observaciones
    ADD CONSTRAINT fk_observaciones_astro FOREIGN KEY (id_astro) REFERENCES public.astros(id_astro) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: observaciones fk_observaciones_astronomo; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observaciones
    ADD CONSTRAINT fk_observaciones_astronomo FOREIGN KEY (id_astronomo) REFERENCES public.astronomos(id_astronomo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: observaciones fk_observaciones_telescopio; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observaciones
    ADD CONSTRAINT fk_observaciones_telescopio FOREIGN KEY (id_telescopio) REFERENCES public.telescopios(id_telescopio) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict iFxvwb6OBcenqAX4fpJUJMVO5IKb38DuGUbMbJWGNNURnYMal1R0j4uXwPv6Grh

