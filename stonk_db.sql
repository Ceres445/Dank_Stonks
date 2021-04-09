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
    trade bigint[],
    verified boolean DEFAULT false
);


ALTER TABLE public.guild_info OWNER TO postgres;

--
-- Name: traded_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.traded_items (
    code integer NOT NULL,
    list_type character varying,
    user_item integer,
    trade_item json,
    stock integer,
    user_id bigint,
    "time" bigint
);


ALTER TABLE public.listed_trades OWNER TO postgres;

--
-- Name: trades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trades (
    code integer NOT NULL,
    user_1 bigint,
    user_2 bigint,
    type character varying,
    info json,
    verified boolean,
    "time" bigint
);


ALTER TABLE public.completed_trades OWNER TO postgres;

--
-- Name: trades_code_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trades_code_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trades_code_seq OWNER TO postgres;

--
-- Name: trades_code_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trades_code_seq OWNED BY public.completed_trades.code;


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
-- Name: trades code; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.completed_trades ALTER COLUMN code SET DEFAULT nextval('public.trades_code_seq'::regclass);


--
-- Data for Name: listed_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.listed_items (code, item_code, quantity, price, user_id, list_type, "time") FROM stdin;
8	33	90000	15	488278979900342282	buy	1610862247
11	33	90000	1	488278979900342282	buy	1610864413
\.


--
-- Data for Name: prefix; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.guild_info (guild, guild_info, staff, promo, trade, verified) FROM stdin;
735451687652818985	{+}	{752412333615087616}	743684248552079360	{743684248552079360}	t
729930293695217694	{+}	\N	743684248552079360	{743684248552079360}	t
715911019561746592	{+}	\N	\N	\N	t
621276986437795850	{+}	\N	\N	\N	t
\.


--
-- Data for Name: traded_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.listed_trades (code, list_type, user_item, trade_item, stock, user_id, "time") FROM stdin;
9	sell	33	{"2": 1}	15	488278979900342282	1610864161
12	sell	33	{"39": 1}	15	488278979900342282	1610864966
13	sell	33	{"39": 1, "31": 5}	15	488278979900342282	1610865052
\.


--
-- Data for Name: trades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.completed_trades (code, user_1, user_2, type, info, verified, "time") FROM stdin;
\.


--
-- Data for Name: user_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_data (user_id, guilds, worth, trades, trust) FROM stdin;
787564443273396264	{621276986437795850}	0	0	10
488278979900342282	{735451687652818985,729930293695217694,715911019561746592,621276986437795850}	0	10	10
503074925117046807	{729930293695217694,715911019561746592}	0	10	10
\.


--
-- Name: trades_code_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trades_code_seq', 1, false);


--
-- Name: listed_items listed_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.listed_items
    ADD CONSTRAINT listed_items_pkey PRIMARY KEY (code);


--
-- Name: prefix prefix_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_info
    ADD CONSTRAINT prefix_pkey PRIMARY KEY (guild);


--
-- Name: traded_items traded_items_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.listed_trades
    ADD CONSTRAINT traded_items_pk PRIMARY KEY (code);


--
-- Name: trades trades_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.completed_trades
    ADD CONSTRAINT trades_pk PRIMARY KEY (code);


--
-- Name: user_data user_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_data
    ADD CONSTRAINT user_data_pkey PRIMARY KEY (user_id);


--
-- PostgreSQL database dump complete
--
