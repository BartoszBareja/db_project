--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

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

--
-- Name: user_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_status AS ENUM (
    'online',
    'offline',
    'hidden'
);


ALTER TYPE public.user_status OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: achievements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.achievements (
    id integer NOT NULL,
    game_id integer NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(255),
    points integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.achievements OWNER TO postgres;

--
-- Name: achievements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.achievements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.achievements_id_seq OWNER TO postgres;

--
-- Name: achievements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.achievements_id_seq OWNED BY public.achievements.id;


--
-- Name: countries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.countries (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    short_code character varying(5) NOT NULL
);


ALTER TABLE public.countries OWNER TO postgres;

--
-- Name: countries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.countries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.countries_id_seq OWNER TO postgres;

--
-- Name: countries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.countries_id_seq OWNED BY public.countries.id;


--
-- Name: friends; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.friends (
    user1_id integer NOT NULL,
    user2_id integer NOT NULL,
    friends_since timestamp without time zone NOT NULL,
    CONSTRAINT chk_no_self_friendship CHECK ((user1_id <> user2_id))
);


ALTER TABLE public.friends OWNER TO postgres;

--
-- Name: game_genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.game_genres (
    game_id integer NOT NULL,
    genre_id integer NOT NULL
);


ALTER TABLE public.game_genres OWNER TO postgres;

--
-- Name: game_ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.game_ratings (
    user_id integer NOT NULL,
    game_id integer NOT NULL,
    rating smallint,
    description character varying(500),
    rated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.game_ratings OWNER TO postgres;

--
-- Name: games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.games (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    avaliable_languages character varying,
    description character varying,
    price numeric(10,2) DEFAULT 0 NOT NULL,
    version character varying(50) NOT NULL,
    producer_id integer NOT NULL,
    pegi_rating character varying(10),
    release_date timestamp without time zone NOT NULL,
    itch_link character varying(100),
    min_cpu character varying(50),
    min_gpu character varying(50),
    min_ram character varying(50),
    min_disk character varying(50)
);


ALTER TABLE public.games OWNER TO postgres;

--
-- Name: games_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.games_id_seq OWNER TO postgres;

--
-- Name: games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.games_id_seq OWNED BY public.games.id;


--
-- Name: genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genres (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.genres OWNER TO postgres;

--
-- Name: genres_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.genres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genres_id_seq OWNER TO postgres;

--
-- Name: genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.genres_id_seq OWNED BY public.genres.id;


--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    game_id integer NOT NULL,
    filename character varying(255) NOT NULL,
    is_thumbnail boolean DEFAULT false NOT NULL
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.images_id_seq OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: library; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library (
    user_id integer NOT NULL,
    game_id integer NOT NULL,
    purchase_date timestamp without time zone NOT NULL,
    is_owned boolean
);


ALTER TABLE public.library OWNER TO postgres;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    sender_id integer,
    receiver_id integer,
    content text NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: producer_ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producer_ratings (
    producer_id integer NOT NULL,
    user_id integer NOT NULL,
    rating smallint NOT NULL,
    description character varying(500),
    rated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.producer_ratings OWNER TO postgres;

--
-- Name: producers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producers (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    logo character varying(255),
    description character varying(300),
    country_id integer NOT NULL
);


ALTER TABLE public.producers OWNER TO postgres;

--
-- Name: producers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.producers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.producers_id_seq OWNER TO postgres;

--
-- Name: producers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.producers_id_seq OWNED BY public.producers.id;


--
-- Name: user_achievements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_achievements (
    user_id integer NOT NULL,
    achievement_id integer NOT NULL,
    achieved_at timestamp without time zone NOT NULL
);


ALTER TABLE public.user_achievements OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    profile_picture character varying(255),
    profile_description character varying(300),
    wallet_balance numeric(10,2) DEFAULT 0 NOT NULL,
    created_at timestamp without time zone NOT NULL,
    birth_date date NOT NULL,
    country_id integer,
    sum_points integer DEFAULT 0 NOT NULL,
    status public.user_status DEFAULT 'offline'::public.user_status NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: wishlist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wishlist (
    user_id integer NOT NULL,
    game_id integer NOT NULL,
    added_at timestamp without time zone NOT NULL
);


ALTER TABLE public.wishlist OWNER TO postgres;

--
-- Name: achievements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.achievements ALTER COLUMN id SET DEFAULT nextval('public.achievements_id_seq'::regclass);


--
-- Name: countries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries ALTER COLUMN id SET DEFAULT nextval('public.countries_id_seq'::regclass);


--
-- Name: games id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games ALTER COLUMN id SET DEFAULT nextval('public.games_id_seq'::regclass);


--
-- Name: genres id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres ALTER COLUMN id SET DEFAULT nextval('public.genres_id_seq'::regclass);


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: producers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producers ALTER COLUMN id SET DEFAULT nextval('public.producers_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: achievements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.achievements (id, game_id, name, description, points) FROM stdin;
1	1	Achievement_1_1	Description for Achievement_1_1	38
2	1	Achievement_1_2	Description for Achievement_1_2	27
3	1	Achievement_1_3	Description for Achievement_1_3	75
4	2	Achievement_2_1	Description for Achievement_2_1	21
5	2	Achievement_2_2	Description for Achievement_2_2	16
6	2	Achievement_2_3	Description for Achievement_2_3	24
7	3	Achievement_3_1	Description for Achievement_3_1	90
8	3	Achievement_3_2	Description for Achievement_3_2	30
9	4	Achievement_4_1	Description for Achievement_4_1	64
10	4	Achievement_4_2	Description for Achievement_4_2	86
11	4	Achievement_4_3	Description for Achievement_4_3	18
12	4	Achievement_4_4	Description for Achievement_4_4	59
13	5	Achievement_5_1	Description for Achievement_5_1	86
14	5	Achievement_5_2	Description for Achievement_5_2	69
15	5	Achievement_5_3	Description for Achievement_5_3	77
16	6	Achievement_6_1	Description for Achievement_6_1	80
17	6	Achievement_6_2	Description for Achievement_6_2	11
18	6	Achievement_6_3	Description for Achievement_6_3	97
19	7	Achievement_7_1	Description for Achievement_7_1	24
20	7	Achievement_7_2	Description for Achievement_7_2	97
21	7	Achievement_7_3	Description for Achievement_7_3	78
22	7	Achievement_7_4	Description for Achievement_7_4	44
23	8	Achievement_8_1	Description for Achievement_8_1	53
24	8	Achievement_8_2	Description for Achievement_8_2	24
25	8	Achievement_8_3	Description for Achievement_8_3	47
26	8	Achievement_8_4	Description for Achievement_8_4	65
27	9	Achievement_9_1	Description for Achievement_9_1	68
28	9	Achievement_9_2	Description for Achievement_9_2	10
29	10	Achievement_10_1	Description for Achievement_10_1	43
30	10	Achievement_10_2	Description for Achievement_10_2	74
31	10	Achievement_10_3	Description for Achievement_10_3	32
32	10	Achievement_10_4	Description for Achievement_10_4	74
\.


--
-- Data for Name: countries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.countries (id, name, short_code) FROM stdin;
1	Poland	PL
2	Germany	DE
3	United States	US
4	Japan	JP
5	Brazil	BR
\.


--
-- Data for Name: friends; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.friends (user1_id, user2_id, friends_since) FROM stdin;
21	22	2025-03-05 14:00:00
23	24	2025-03-07 17:20:00
25	26	2025-03-10 09:30:00
27	28	2025-03-11 18:45:00
29	30	2025-03-14 13:15:00
31	32	2025-03-16 20:40:00
33	34	2025-03-19 22:10:00
35	36	2025-03-21 11:25:00
37	38	2025-03-24 15:00:00
39	40	2025-03-26 19:30:00
31	25	2025-04-01 08:00:00
22	26	2025-04-02 10:20:00
23	27	2025-04-03 12:15:00
24	28	2025-04-04 14:50:00
29	33	2025-04-06 16:00:00
30	34	2025-04-08 18:30:00
31	35	2025-04-09 20:00:00
32	36	2025-04-11 21:10:00
37	21	2025-04-12 13:00:00
40	23	2025-04-14 09:45:00
41	42	2025-06-15 11:51:43.834032
43	42	2025-06-15 20:56:37.518523
43	41	2025-06-15 20:56:42.679667
41	22	2025-06-15 22:43:56.767734
41	26	2025-06-16 03:11:32.72816
41	33	2025-06-16 03:13:15.470287
41	27	2025-06-16 03:14:56.450502
41	23	2025-06-16 03:16:59.702816
41	31	2025-06-16 03:20:21.074521
\.


--
-- Data for Name: game_genres; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.game_genres (game_id, genre_id) FROM stdin;
1	12
2	8
2	11
3	9
4	12
5	1
5	3
6	7
6	9
7	5
7	6
8	5
8	10
9	2
9	13
10	4
10	5
\.


--
-- Data for Name: game_ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.game_ratings (user_id, game_id, rating, description, rated_at) FROM stdin;
21	3	5	Absolutely amazing experience!	2025-04-12 15:23:45
22	1	4	Great visuals and relaxing gameplay.	2025-04-20 11:00:00
23	5	3	Good, but could use more polish.	2025-03-29 18:45:21
24	7	2	Not really my style, bit boring.	2025-05-03 22:11:03
25	2	5	Loved the storytelling!	2025-04-15 09:40:12
26	6	1	Buggy and unplayable for me.	2025-03-19 13:14:59
27	4	4	Solid arcade action.	2025-04-02 17:25:33
28	9	3	Interesting idea, average execution.	2025-03-10 10:09:55
29	10	5	Free and fantastic, nice job.	2025-05-01 19:50:44
30	8	4	Quirky and fun little game.	2025-03-27 12:00:00
\.


--
-- Data for Name: games; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.games (id, title, avaliable_languages, description, price, version, producer_id, pegi_rating, release_date, itch_link, min_cpu, min_gpu, min_ram, min_disk) FROM stdin;
1	Cheese is the reason	English	A bizarre platformer where cheese solves everything.	0.00	1.0	1	\N	2025-04-08 00:00:00	https://studio-laaya.itch.io/cheese-is-the-reason	Intel i3	Intel HD 4000	4GB	500MB
2	Many Nights a Whisper	English	Unravel secrets whispered in the shadows of forgotten nights.	2.99	1.0	2	\N	2025-05-01 00:00:00	https://deconstructeam.itch.io/many-nights-a-whisper	Intel i5	GTX 750	6GB	2GB
3	Sub-Verge	English	Dive into an underwater rift of puzzles and light.	6.99	1.0	3	\N	2025-05-02 00:00:00	https://pantaloon-io.itch.io/sub-verge	Intel i5	GTX 950	8GB	3GB
4	All Hell Unleashed	English	Blast your way through pixel demons in this chaotic shooter.	0.00	1.0	4	\N	2025-04-13 00:00:00	https://8bitslasher.itch.io/ahu	Intel i3	GT 1030	4GB	1GB
5	Grid Ranger	English	Protect the grid in a fast-paced arcade defense sim.	4.00	1.0	5	\N	2025-03-10 00:00:00	https://pixeljam.itch.io/grid-ranger	Intel i3	Intel HD 4600	4GB	1GB
6	Decrypto Project Demo	English	Sneak and decode in this atmospheric hacking teaser.	0.00	1.0	6	\N	2025-05-10 00:00:00	https://slothjam.itch.io/decrypto-project-demo	Intel i5	GTX 1050	8GB	2GB
7	Red Finger	English	Follow the trace of a mysterious red fingerprint.	0.00	1.0	7	\N	2025-04-19 00:00:00	https://kenforest.itch.io/red-finger	Intel i3	Intel UHD 620	4GB	1GB
8	The Electrifying Incident	English	A cozy mystery in a town where static shocks tell stories.	5.00	1.0	8	\N	2025-02-21 00:00:00	https://draknek.itch.io/the-electrifying-incident	Intel i3	GTX 660	4GB	1.5GB
9	Late Night Mop	English	Clean the house… but something lurks behind the mess.	0.00	1.0	9	\N	2025-03-05 00:00:00	https://lixiangames.itch.io/late-night-mop	Intel i3	Intel HD 5000	4GB	600MB
10	Ignited Entry	English	Rush into the blaze and uncover the truth of the fire.	0.00	1.0	10	\N	2025-01-08 00:00:00	https://jordiboi.itch.io/ignited-entry	Intel i3	GTX 650	4GB	1GB
\.


--
-- Data for Name: genres; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.genres (id, name) FROM stdin;
1	Arcade
2	Horror
3	Tower Defense
4	Action
5	Mystery
6	Thriller
7	Stealth
8	Adventure
9	Puzzle
10	Cozy Adventure
11	Interactive Fiction
12	Platformer
13	Simulation
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.images (id, game_id, filename, is_thumbnail) FROM stdin;
1	1	cheeseisthereason.png	t
2	1	cheeseisthereason2.png	f
3	2	manynightsawhisper1.png	t
4	2	manynightsawhisper2.png	f
5	2	manynightsawhisper3.png	f
6	2	manynightsawhisper4.png	f
7	3	subverge1.png	t
8	3	subverge2.png	f
9	3	subverge3.png	f
10	3	subverge4.png	f
11	4	allhellunleashed1.png	t
12	4	allhellunleashed2.png	f
13	4	allhellunleashed3.png	f
14	4	allhellunleashed4.png	f
15	5	gridranger1.png	t
16	5	gridranger2.png	f
17	5	gridranger3.png	f
18	5	gridranger4.png	f
19	6	decryptoproject.png	t
20	6	decryptoproject2.png	f
21	6	decryptoproject3.png	f
22	7	redfinger1.png	t
23	7	rendfinger2.png	f
24	7	redfinger3.png	f
25	7	redfinger4.png	f
26	8	electryfingincident1.png	t
27	8	electryfingincident2.png	f
28	8	electryfingincident3.png	f
29	9	latenightmop1.png	t
30	9	latenightmop2.png	f
31	9	latenightmop3.png	f
32	10	igniteedentry.png	t
33	10	igniteedentry2.png	f
34	10	igniteedentry3.png	f
\.


--
-- Data for Name: library; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.library (user_id, game_id, purchase_date, is_owned) FROM stdin;
21	7	2025-03-16 12:47:06	t
22	3	2025-05-06 01:38:10	t
23	1	2025-04-10 23:42:14	t
23	7	2025-04-27 21:44:01	t
24	8	2025-03-07 04:01:49	t
24	5	2025-04-07 08:34:22	t
25	9	2025-04-07 01:14:14	t
25	8	2025-04-27 20:31:14	t
26	4	2025-04-15 10:38:07	t
27	4	2025-04-21 08:55:32	t
27	1	2025-03-25 09:50:14	t
28	9	2025-04-23 17:06:35	t
28	1	2025-03-02 02:45:09	t
28	6	2025-05-06 01:10:30	t
29	1	2025-03-12 02:55:29	t
30	8	2025-05-06 04:30:01	t
30	9	2025-04-22 03:13:53	t
30	3	2025-03-26 21:44:51	t
31	9	2025-05-02 05:32:57	t
32	3	2025-04-03 00:39:58	t
33	10	2025-03-11 19:56:07	t
34	4	2025-03-29 11:54:17	t
35	2	2025-04-12 05:04:35	t
35	4	2025-03-16 08:32:03	t
36	10	2025-04-14 01:15:10	t
36	1	2025-03-01 07:33:43	t
36	2	2025-03-26 13:44:27	t
37	10	2025-04-18 14:27:00	t
37	9	2025-03-18 08:17:20	t
38	5	2025-04-19 06:59:02	t
38	4	2025-03-11 07:57:18	t
39	6	2025-04-30 17:03:18	t
39	4	2025-03-29 23:25:36	t
39	5	2025-05-02 00:51:36	t
40	3	2025-04-19 06:56:24	t
40	5	2025-04-29 03:00:12	t
41	3	2025-06-14 23:41:00.570412	t
41	2	2025-06-15 20:26:46.397015	t
41	1	2025-06-15 21:32:57.186925	t
41	6	2025-06-15 22:51:47.278148	t
41	4	2025-06-16 00:45:58.73512	t
42	4	2025-06-16 01:46:38.919172	t
42	2	2025-06-16 01:47:50.645589	t
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (id, sender_id, receiver_id, content, "timestamp") FROM stdin;
1	42	41	test	2025-06-15 10:07:18.969746
2	41	42	hi	2025-06-15 10:09:07.818658
3	41	42	co tam?	2025-06-15 10:13:37.24253
4	41	42	nic spcjalnego	2025-06-15 10:17:26.889901
5	43	42	hello	2025-06-15 18:56:49.608575
6	41	43	hi	2025-06-15 23:00:34.703834
7	42	41	whaddup	2025-06-15 23:11:44.967266
\.


--
-- Data for Name: producer_ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producer_ratings (producer_id, user_id, rating, description, rated_at) FROM stdin;
1	22	5	Studio Laaya never disappoints.	2025-04-10 13:55:00
2	24	4	Unique vision and consistent quality.	2025-03-25 16:30:00
3	26	3	Some hits, some misses.	2025-04-18 10:10:00
4	21	2	Mediocre content overall.	2025-05-04 08:22:00
5	27	5	Pixeljam is a pixel art genius.	2025-03-15 20:00:00
6	23	4	Creative studio, promising work.	2025-04-06 11:11:11
7	25	3	Solid first impression.	2025-04-13 15:45:00
8	29	1	Not a fan of their design.	2025-04-01 09:00:00
9	28	5	Lixian always delivers quality.	2025-03-22 14:15:00
10	30	4	Very creative and consistent work.	2025-04-30 17:00:00
\.


--
-- Data for Name: producers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producers (id, name, logo, description, country_id) FROM stdin;
1	Studio Laaya	\N	A small indie studio focused on quirky, narrative-driven experiences.	2
2	Deconstructeam	\N	Experimental dev team crafting emotional, artistic stories.	3
3	pantaloon	\N	Solo developer making abstract sci-fi puzzle worlds.	5
4	8-Bit Slasher	\N	Retro-inspired studio specializing in pixelated chaos.	1
5	Pixeljam	\N	Arcade-style developers inspired by the 80s digital era.	4
6	slothJam	\N	Relaxed studio delivering slow-paced, clever demos.	1
7	kenforest	\N	Creates minimalistic and experimental thrillers.	2
8	Draknek and Friends	\N	Puzzle game specialists with a unique artistic twist.	3
9	LixianGames	\N	Known for comedic and horror one-night experiences.	5
10	JordiBoi	\N	Solo creator exploring high-energy action design.	4
\.


--
-- Data for Name: user_achievements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_achievements (user_id, achievement_id, achieved_at) FROM stdin;
21	20	2025-04-14 00:31:21
21	13	2025-05-01 17:15:07
22	24	2025-04-05 10:07:14
22	11	2025-03-16 19:00:41
22	1	2025-04-05 22:35:03
23	32	2025-04-04 11:50:26
23	2	2025-03-21 08:11:12
23	8	2025-05-05 01:37:16
23	24	2025-03-26 22:06:12
24	16	2025-05-08 03:21:35
24	4	2025-05-06 08:46:53
24	6	2025-05-02 22:01:54
24	32	2025-03-07 22:22:47
25	9	2025-04-29 03:22:41
25	31	2025-05-01 15:36:23
26	17	2025-03-17 14:46:55
26	28	2025-04-21 20:38:10
26	14	2025-03-24 18:27:02
27	20	2025-03-16 20:45:19
27	26	2025-04-14 21:08:39
27	24	2025-04-06 20:11:42
28	29	2025-03-27 05:01:26
28	8	2025-05-02 03:18:27
28	16	2025-05-06 19:32:00
28	15	2025-04-24 01:47:13
28	5	2025-03-22 07:44:25
29	2	2025-05-06 11:16:00
29	15	2025-04-01 11:38:00
29	1	2025-03-06 10:20:41
29	5	2025-03-23 05:43:14
30	15	2025-03-04 02:47:56
30	5	2025-03-31 15:03:31
31	22	2025-04-08 22:46:54
31	5	2025-03-26 23:52:53
32	18	2025-03-07 10:13:50
32	32	2025-03-21 11:37:32
32	14	2025-04-25 01:37:31
33	31	2025-03-31 13:15:09
33	16	2025-03-21 15:27:20
33	27	2025-05-03 15:16:58
34	7	2025-04-18 11:17:35
34	28	2025-04-08 09:53:20
34	23	2025-05-02 09:57:12
35	27	2025-04-14 13:12:08
35	30	2025-03-14 20:54:53
35	4	2025-03-26 17:12:55
35	7	2025-03-14 13:21:44
35	26	2025-03-24 22:41:01
36	7	2025-04-24 12:04:57
36	16	2025-04-22 07:54:29
36	13	2025-03-26 12:13:56
36	29	2025-04-26 18:11:02
37	28	2025-04-11 14:19:23
37	12	2025-04-26 15:43:48
37	18	2025-04-08 18:40:14
38	16	2025-04-05 03:30:46
38	5	2025-03-22 07:03:15
38	29	2025-03-14 10:20:10
38	7	2025-04-19 11:16:56
38	4	2025-04-17 21:58:30
39	6	2025-03-09 19:50:03
39	16	2025-03-05 13:47:20
40	27	2025-03-11 15:30:03
40	32	2025-03-15 20:08:45
40	31	2025-04-30 22:03:18
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, profile_picture, profile_description, wallet_balance, created_at, birth_date, country_id, sum_points, status) FROM stdin;
21	ShadowSniper99	shadow99@gmail.com	hash1	\N	FPS to moje życie.	34.20	2025-03-04 14:35:00	1999-02-11	1	1250	online
22	PixelHero	pixhero@protonmail.com	hash2	\N	Uwielbiam retro platformówki.	5.00	2025-03-17 08:12:00	1995-09-23	2	880	offline
23	xDarkSoulx	darksoul@outlook.com	hash3	\N	Zawsze gram solo.	12.75	2025-03-22 19:45:00	1993-12-03	3	730	hidden
24	CaptainCrit	capt.crit@gmail.com	hash4	\N	Kocham oceniać gry.	2.00	2025-03-29 13:22:00	2001-01-15	4	460	online
25	NovaStrike42	nova42@yahoo.com	hash5	\N	Fan sci-fi i eksploracji.	18.90	2025-04-01 10:00:00	1997-07-30	1	990	offline
26	SilentByte	silentbyte@interia.pl	hash6	\N	Introvert gracz.	9.99	2025-04-03 16:40:00	1990-06-18	2	310	hidden
27	L33tHunter	leet_hunter@gmail.com	hash7	\N	Gracz od czasów Quake.	13.37	2025-04-05 21:00:00	1988-04-01	3	666	offline
28	SkyMage	skymage2025@o2.pl	hash8	\N	Mag w każdej grze RPG.	8.50	2025-04-06 11:15:00	1992-10-10	4	740	online
29	FuryFox	fury.fox@gmail.com	hash9	\N	Szybko, agresywnie, skutecznie.	25.00	2025-04-08 17:29:00	1996-08-09	1	870	online
30	BinaryBro	binarybro@protonmail.com	hash10	\N	Dev i gracz jednocześnie.	0.00	2025-04-10 22:50:00	1994-11-11	2	550	offline
31	WitcherFan777	wfan777@gmail.com	hash11	\N	Wiedźmin ponad wszystko.	3.33	2025-04-13 10:30:00	1989-05-25	3	1010	online
32	ToxicTurtle	toxic.turtle@o2.pl	hash12	\N	Gram 5h dziennie. Minimum.	6.00	2025-04-14 15:40:00	1998-03-03	4	420	hidden
33	LagMasterX	lagmasterx@wp.pl	hash13	\N	Mam zły net, ale dobry aim.	7.77	2025-04-16 20:10:00	2000-07-04	1	390	offline
34	VR_Overlord	vrolord@protonmail.com	hash14	\N	Tylko VR, reszta się nie liczy.	22.22	2025-04-18 13:55:00	1991-02-28	2	840	online
35	MechaPunk	mechpunk@outlook.com	hash15	\N	Cyberpunk i kawa.	4.00	2025-04-20 18:03:00	1990-09-09	3	710	offline
36	AFKWizard	afkwizard@interia.pl	hash16	\N	Zawsze online, rzadko gram.	11.00	2025-04-22 09:25:00	1997-06-06	4	150	hidden
37	QuickScopeZ	qs.zed@gmail.com	hash17	\N	Snajper bez granic.	30.00	2025-04-25 12:10:00	1995-05-05	1	1300	online
38	Rogue_Unit	rogue_unit@o2.pl	hash18	\N	Uwielbiam skradanki.	16.50	2025-04-27 17:00:00	1993-01-01	2	640	offline
39	GameDad	gamedad@wp.pl	hash19	\N	Dzieci śpią – tata gra.	5.55	2025-04-29 23:33:00	1985-12-12	3	990	online
40	EchoFalcon	echofalcon@gmail.com	hash20	\N	Gram dla fabuły.	14.44	2025-05-02 08:45:00	1999-09-19	4	875	online
42	Tester	tester@test	$2b$12$LBVwW068aQqeIWAT4KKJQO.kFbe/SFEozx/UiZaUZndZHbFLlCNii	\N	\N	0.00	2025-06-14 22:15:34.570907	2025-06-15	\N	0	offline
43	Testownik	test@test	$2b$12$mcvaARilEEfd8/u7RmWhCuzdT7tBActb3TDeWu5O/xBpZlQNSEdgm	\N	\N	0.00	2025-06-15 18:51:59.106417	2025-06-15	\N	0	offline
41	testowy	testowy@test	$2b$12$oajFoUf4dsvUC9hdM4pRtuBJpZl4x79kXEQBT.DZREoXk.pAHMGRi	\N	hello\r\nI like FPS	0.00	2025-06-14 22:01:00.07371	2025-06-15	\N	0	offline
44	testowy2	test2@test	$2b$12$HS0vRwVFmc1vLAk8fTwrDe6jbzp4B/C4GwghqA9GgVVzcLyrlCeem	\N	\N	0.00	2025-06-16 00:42:21.045344	2025-06-07	\N	0	offline
\.


--
-- Data for Name: wishlist; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.wishlist (user_id, game_id, added_at) FROM stdin;
21	2	2025-03-05 10:32:00
21	5	2025-04-01 16:21:00
22	1	2025-03-18 09:44:00
23	4	2025-04-07 14:00:00
23	6	2025-04-08 11:30:00
24	3	2025-03-15 19:55:00
25	7	2025-05-01 08:25:00
25	2	2025-05-03 12:40:00
26	5	2025-03-21 15:10:00
27	8	2025-03-30 13:13:00
27	1	2025-04-04 18:30:00
28	6	2025-03-25 10:45:00
29	9	2025-04-15 09:00:00
30	10	2025-03-27 20:10:00
30	4	2025-04-10 14:22:00
31	2	2025-03-19 12:00:00
32	3	2025-04-05 11:11:00
32	7	2025-04-06 13:25:00
33	8	2025-03-16 15:30:00
34	1	2025-04-01 17:45:00
34	9	2025-04-03 08:10:00
35	6	2025-03-22 13:00:00
36	10	2025-04-12 10:10:00
37	5	2025-04-17 11:50:00
37	3	2025-04-19 16:35:00
38	7	2025-03-28 14:40:00
39	2	2025-04-21 18:00:00
39	4	2025-04-22 09:30:00
40	1	2025-03-13 20:00:00
41	5	2025-06-14 23:39:38.496734
41	1	2025-06-14 23:39:55.278799
41	3	2025-06-14 23:40:22.493068
41	2	2025-06-15 21:21:20.226374
41	9	2025-06-15 22:47:38.049966
41	6	2025-06-16 01:10:05.247401
41	4	2025-06-16 01:45:49.656341
\.


--
-- Name: achievements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.achievements_id_seq', 32, true);


--
-- Name: countries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.countries_id_seq', 5, true);


--
-- Name: games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.games_id_seq', 10, true);


--
-- Name: genres_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.genres_id_seq', 13, true);


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.images_id_seq', 34, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.messages_id_seq', 7, true);


--
-- Name: producers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.producers_id_seq', 10, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 44, true);


--
-- Name: achievements achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT achievements_pkey PRIMARY KEY (id);


--
-- Name: countries countries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (id);


--
-- Name: game_genres game_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_genres
    ADD CONSTRAINT game_genres_pkey PRIMARY KEY (game_id, genre_id);


--
-- Name: game_ratings game_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_ratings
    ADD CONSTRAINT game_ratings_pkey PRIMARY KEY (user_id, game_id);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
-- Name: genres genres_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_name_key UNIQUE (name);


--
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: library library_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT library_pkey PRIMARY KEY (user_id, game_id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: producer_ratings producer_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producer_ratings
    ADD CONSTRAINT producer_ratings_pkey PRIMARY KEY (producer_id, user_id);


--
-- Name: producers producers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producers
    ADD CONSTRAINT producers_pkey PRIMARY KEY (id);


--
-- Name: user_achievements user_achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_achievements
    ADD CONSTRAINT user_achievements_pkey PRIMARY KEY (user_id, achievement_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wishlist wishlist_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wishlist
    ADD CONSTRAINT wishlist_pkey PRIMARY KEY (user_id, game_id);


--
-- Name: achievements fk_achievements_game_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT fk_achievements_game_id FOREIGN KEY (game_id) REFERENCES public.games(id);


--
-- Name: friends fk_friends_user1_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT fk_friends_user1_id FOREIGN KEY (user1_id) REFERENCES public.users(id);


--
-- Name: friends fk_friends_user2_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT fk_friends_user2_id FOREIGN KEY (user2_id) REFERENCES public.users(id);


--
-- Name: game_ratings fk_game_ratings_game_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_ratings
    ADD CONSTRAINT fk_game_ratings_game_id FOREIGN KEY (game_id) REFERENCES public.games(id);


--
-- Name: game_ratings fk_game_ratings_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_ratings
    ADD CONSTRAINT fk_game_ratings_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: games fk_games_producer_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT fk_games_producer_id FOREIGN KEY (producer_id) REFERENCES public.producers(id);


--
-- Name: library fk_library_game_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT fk_library_game_id FOREIGN KEY (game_id) REFERENCES public.games(id);


--
-- Name: library fk_library_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT fk_library_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: producer_ratings fk_producer_ratings_producer_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producer_ratings
    ADD CONSTRAINT fk_producer_ratings_producer_id FOREIGN KEY (producer_id) REFERENCES public.producers(id);


--
-- Name: producer_ratings fk_producer_ratings_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producer_ratings
    ADD CONSTRAINT fk_producer_ratings_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: producers fk_producers_country_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producers
    ADD CONSTRAINT fk_producers_country_id FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: user_achievements fk_user_achievements_achievement_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_achievements
    ADD CONSTRAINT fk_user_achievements_achievement_id FOREIGN KEY (achievement_id) REFERENCES public.achievements(id);


--
-- Name: user_achievements fk_user_achievements_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_achievements
    ADD CONSTRAINT fk_user_achievements_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users fk_users_country_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_country_id FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: wishlist fk_wishlist_game_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wishlist
    ADD CONSTRAINT fk_wishlist_game_id FOREIGN KEY (game_id) REFERENCES public.games(id);


--
-- Name: wishlist fk_wishlist_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wishlist
    ADD CONSTRAINT fk_wishlist_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: game_genres game_genres_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_genres
    ADD CONSTRAINT game_genres_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id) ON DELETE CASCADE;


--
-- Name: game_genres game_genres_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_genres
    ADD CONSTRAINT game_genres_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id) ON DELETE CASCADE;


--
-- Name: images images_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id) ON DELETE CASCADE;


--
-- Name: messages messages_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id);


--
-- Name: messages messages_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

