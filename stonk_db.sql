--
-- PostgreSQL database dump
--

-- Dumped from database version 13.1
-- Dumped by pg_dump version 13.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: listed_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.listed_items (
    code integer NOT NULL,
    item_code integer NOT NULL,
    quantity bigint NOT NULL,
    price bigint NOT NULL,
    user_id bigint,
    list_type character varying,
    "time" integer
);


ALTER TABLE public.listed_items OWNER TO postgres;

--
-- Name: prefix; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prefix (
    guild bigint NOT NULL,
    prefix character varying[],
    staff bigint[],
    promo bigint,
    trade bigint[]
);


ALTER TABLE public.prefix OWNER TO postgres;

--
-- Name: user_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_data (
    user_id bigint NOT NULL,
    guilds bigint[],
    worth bigint,
    trades bigint,
    trust integer
);


ALTER TABLE public.user_data OWNER TO postgres;

--
-- Data for Name: listed_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.listed_items (code, item_code, quantity, price, user_id, list_type, "time") FROM stdin;
3	31	2	90000	488278979900342282	sell	1609992782
\.


--
-- Data for Name: prefix; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prefix (guild, prefix, staff, promo, trade) FROM stdin;
735451687652818985	{+}	{752412333615087616}	752412547721986070	{735451688135294998,752404728536629329}
\.


--
-- Data for Name: user_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_data (user_id, guilds, worth, trades, trust) FROM stdin;
488278979900342282	{735451687652818985}	0	0	0
\.


--
-- Name: listed_items listed_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.listed_items
    ADD CONSTRAINT listed_items_pkey PRIMARY KEY (code);


--
-- Name: prefix prefix_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prefix
    ADD CONSTRAINT prefix_pkey PRIMARY KEY (guild);


--
-- Name: user_data user_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_data
    ADD CONSTRAINT user_data_pkey PRIMARY KEY (user_id);


--
-- PostgreSQL database dump complete
--

