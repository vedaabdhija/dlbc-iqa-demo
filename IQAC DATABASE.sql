--
-- PostgreSQL database dump
--

\restrict Lz8nwiAL31OOoqJxEYbG00ukqHFnxPgk6qjzsPEz8X3rugj605sBloRFrqWcKXn

-- Dumped from database version 17.9
-- Dumped by pg_dump version 17.9

-- Started on 2026-05-15 15:40:58

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 16413)
-- Name: calendar_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.calendar_events (
    id integer NOT NULL,
    event_date date NOT NULL,
    event_title character varying(255) NOT NULL,
    event_type character varying(50) NOT NULL
);


--
-- TOC entry 219 (class 1259 OID 16412)
-- Name: calendar_events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.calendar_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4941 (class 0 OID 0)
-- Dependencies: 219
-- Name: calendar_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.calendar_events_id_seq OWNED BY public.calendar_events.id;


--
-- TOC entry 223 (class 1259 OID 16514)
-- Name: departments_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.departments_data (
    dept character varying(50) NOT NULL,
    faculty integer DEFAULT 0,
    y1 integer DEFAULT 0,
    y2 integer DEFAULT 0,
    y3 integer DEFAULT 0,
    y4 integer DEFAULT 0,
    cse integer DEFAULT 0,
    ece integer DEFAULT 0,
    eee integer DEFAULT 0,
    civil integer DEFAULT 0,
    placed integer DEFAULT 0
);


--
-- TOC entry 222 (class 1259 OID 16420)
-- Name: form_sections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.form_sections (
    id integer NOT NULL,
    sec_num integer NOT NULL,
    title character varying(255) NOT NULL,
    description text
);


--
-- TOC entry 221 (class 1259 OID 16419)
-- Name: form_sections_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.form_sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4942 (class 0 OID 0)
-- Dependencies: 221
-- Name: form_sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.form_sections_id_seq OWNED BY public.form_sections.id;


--
-- TOC entry 218 (class 1259 OID 16396)
-- Name: submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submissions (
    id character varying(50) NOT NULL,
    dept character varying(100),
    month character varying(20),
    year character varying(20),
    status character varying(50),
    sections integer,
    complete_pct integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    report_data jsonb
);


--
-- TOC entry 217 (class 1259 OID 16389)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id character varying(100) NOT NULL,
    pass character varying(255) NOT NULL,
    name character varying(100) NOT NULL,
    role character varying(50) NOT NULL,
    dept character varying(100)
);


--
-- TOC entry 4760 (class 2604 OID 16416)
-- Name: calendar_events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calendar_events ALTER COLUMN id SET DEFAULT nextval('public.calendar_events_id_seq'::regclass);


--
-- TOC entry 4761 (class 2604 OID 16423)
-- Name: form_sections id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form_sections ALTER COLUMN id SET DEFAULT nextval('public.form_sections_id_seq'::regclass);


--
-- TOC entry 4932 (class 0 OID 16413)
-- Dependencies: 220
-- Data for Name: calendar_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.calendar_events (id, event_date, event_title, event_type) FROM stdin;
1	2026-04-08	Auto-generated Monthly Report	iqac
2	2026-03-29	Kalotsav	academic
3	2026-03-29	Kalotsav	academic
4	2099-01-01	__DIAG_TEST_EVENT__	diagnostic
\.


--
-- TOC entry 4935 (class 0 OID 16514)
-- Dependencies: 223
-- Data for Name: departments_data; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.departments_data (dept, faculty, y1, y2, y3, y4, cse, ece, eee, civil, placed) FROM stdin;
CSE	0	0	0	0	0	0	0	0	0	0
Civil	0	0	0	0	0	0	0	0	0	0
ECE	0	0	0	0	0	0	0	0	0	0
EEE	0	0	0	0	0	0	0	0	0	0
BHS	0	0	0	0	0	0	0	0	0	0
\.


--
-- TOC entry 4934 (class 0 OID 16420)
-- Dependencies: 222
-- Data for Name: form_sections; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.form_sections (id, sec_num, title, description) FROM stdin;
\.


--
-- TOC entry 4930 (class 0 OID 16396)
-- Dependencies: 218
-- Data for Name: submissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.submissions (id, dept, month, year, status, sections, complete_pct, created_at, report_data) FROM stdin;
SUB-VFHX6W	CSE	January	2025-26	Draft	4	18	2026-03-30 00:47:09.583496	{"Section 1": "9", "Section 3": "National", "Section 6": "Invited Lecture", "Section 12": "Applied"}
HIST-CIVIL	Civil	June-Dec Summary	2025-26	Approved	8	36	2026-03-31 22:14:26.1728	{"Section 1": "1", "Section 2": "39 (Repeated)", "Section 4": "1", "Section 5": "2", "Section 8": "1 book", "Section 9": "100", "Section 10": "183", "Section 15": "7"}
HIST-EEE	EEE	June-Dec Summary	2025-26	Approved	6	27	2026-03-31 22:14:26.1728	{"Section 2": "3", "Section 4": "1", "Section 7": "1 communicated", "Section 9": "27", "Section 10": "30", "Section 14": "2"}
HIST-BHS	BHS	June-Dec Summary	2025-26	Approved	12	55	2026-03-31 22:14:26.1728	{"Section 1": "1", "Section 2": "20 Repeated", "Section 4": "1", "Section 5": "7", "Section 7": "1", "Section 9": "46", "Section 10": "19", "Section 11": "1", "Section 13": "1", "Section 16": "1", "Section 19": "1", "Section 22": "3"}
HIST-CSE	CSE	June-Dec Summary	2025-26	Approved	13	59	2026-03-31 22:14:26.1728	{"Section 1": "1", "Section 2": "3", "Section 6": "2", "Section 7": "1", "Section 9": "36", "Section 10": "50", "Section 11": "1", "Section 13": "1", "Section 14": "41 (NPTEL)", "Section 16": "21", "Section 17": "6", "Section 18": "0", "Section 19": "0 Internship"}
HIST-ECE	ECE	June-Dec Summary	2025-26	Approved	10	45	2026-03-31 22:14:26.1728	{"Section 2": "7", "Section 7": "1", "Section 9": "356", "Section 10": "216", "Section 12": "1", "Section 13": "4", "Section 14": "5", "Section 17": "2", "Section 19": "1 internship and Gate classes", "Section 22": "1 remedial"}
DIAG-1775996317017	TEST	1	2099	Draft	0	0	2026-04-12 17:48:37.64881	{}
\.


--
-- TOC entry 4929 (class 0 OID 16389)
-- Dependencies: 217
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, pass, name, role, dept) FROM stdin;
principal@dlbce.ac.in	Pass@123	Deepak Chowdary	Principal	
ardc@dlbce.ac.in	Pass@123	Dr. B. Parthasarathi	Committee Head	Anti Ragging and Discipline
scst@dlbce.ac.in	Pass@123	Sangeeth Kumar	Committee Head	SC/ST Committee
obc@dlbce.ac.in	Pass@123	B. Ramarao	Committee Head	OBC Committee
minorities@dlbce.ac.in	Pass@123	Dr. Amareshwari	Committee Head	Minorities Committee
rnd@dlbce.ac.in	Pass@123	Dr. K. V. Rama Rao	Committee Head	R&D
esi@dlbce.ac.in	Pass@123	Dr. Vamsi Krishna	Committee Head	Entrepreneurship, Startup and Innovation
sports@dlbce.ac.in	Pass@123	Dr. Lakshman Reddy	Committee Head	Sports
placement@dlbce.ac.in	Pass@123	Dr. Bhujanga Rao	Committee Head	SDC / Internship / Placement / III Cell
alumni@dlbce.ac.in	Pass@123	Dr. Satish Naidu	Committee Head	Alumni / NSS
maintenance@dlbce.ac.in	Pass@123	Dr. Arunima Mahapatra	Committee Head	Maintenance
canteen@dlbce.ac.in	Pass@123	Mr. B. Santosh Kumar	Committee Head	Canteen and Food
profbodies@dlbce.ac.in	Pass@123	Dr. Giridhar	Committee Head	Professional Bodies
narasimha@dlbce.ac.in	Admin@1234	Prof. C. Narasimham	Super Admin	Equity, IQAC
madhavi@dlbce.ac.in	Pass@123	Prof. Dr. D. Madhavi	HOD & Committee Head	CSE, ICC, Student Grievances and Redressal, IT & Website
sdg@dlbce.ac.in	Pass@123	Prof. Dr. G. Tirupati Naidu	HOD & Committee Head	Civil, SDG
lcc@dlbce.ac.in	Pass@123	Dr. Radha Devi	HOD & Committee Head	BHA, Literary and Cultural
hod_ece@dlbce.ac.in	Pass@123	J. Babu	HOD	ECE
hod_eee@dlbce.ac.in	Pass@123	ANANDH	HOD	EEE
\.


--
-- TOC entry 4943 (class 0 OID 0)
-- Dependencies: 219
-- Name: calendar_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.calendar_events_id_seq', 4, true);


--
-- TOC entry 4944 (class 0 OID 0)
-- Dependencies: 221
-- Name: form_sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.form_sections_id_seq', 1, true);


--
-- TOC entry 4777 (class 2606 OID 16418)
-- Name: calendar_events calendar_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calendar_events
    ADD CONSTRAINT calendar_events_pkey PRIMARY KEY (id);


--
-- TOC entry 4783 (class 2606 OID 16528)
-- Name: departments_data departments_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments_data
    ADD CONSTRAINT departments_data_pkey PRIMARY KEY (dept);


--
-- TOC entry 4779 (class 2606 OID 16427)
-- Name: form_sections form_sections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form_sections
    ADD CONSTRAINT form_sections_pkey PRIMARY KEY (id);


--
-- TOC entry 4781 (class 2606 OID 16429)
-- Name: form_sections form_sections_sec_num_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form_sections
    ADD CONSTRAINT form_sections_sec_num_key UNIQUE (sec_num);


--
-- TOC entry 4775 (class 2606 OID 16401)
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4773 (class 2606 OID 16395)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


-- Completed on 2026-05-15 15:40:58

--
-- PostgreSQL database dump complete
--

\unrestrict Lz8nwiAL31OOoqJxEYbG00ukqHFnxPgk6qjzsPEz8X3rugj605sBloRFrqWcKXn

