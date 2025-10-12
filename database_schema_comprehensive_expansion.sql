--
-- PostgreSQL database dump
--

\restrict AjkvRh1rbJGgfES3hssBwQeub7EL0cv9b1E9On3eqsdQ6BjTVZBcgajzHkWRUAN

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

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
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: scraper_user
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO scraper_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: video_transcripts; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.video_transcripts (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    video_url text NOT NULL,
    video_id character varying(100),
    platform character varying(50),
    transcript_text text,
    transcript_json jsonb,
    duration integer,
    language character varying(10),
    extracted_at timestamp without time zone NOT NULL
);


ALTER TABLE public.video_transcripts OWNER TO scraper_user;

--
-- Name: video_transcripts_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.video_transcripts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.video_transcripts_id_seq OWNER TO scraper_user;

--
-- Name: video_transcripts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.video_transcripts_id_seq OWNED BY public.video_transcripts.id;


--
-- Name: workflow_business_intelligence; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_business_intelligence (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    revenue_impact numeric(10,2),
    cost_savings numeric(10,2),
    efficiency_gains numeric(5,2),
    time_savings integer,
    resource_savings numeric(10,2),
    error_reduction numeric(5,2),
    productivity_gains numeric(5,2),
    quality_improvements numeric(5,2),
    customer_satisfaction numeric(5,2),
    business_value_score numeric(5,2),
    roi_estimate numeric(5,2),
    payback_period integer,
    implementation_cost numeric(10,2),
    maintenance_cost numeric(10,2),
    support_cost numeric(10,2),
    training_cost numeric(10,2),
    customization_cost numeric(10,2),
    integration_cost numeric(10,2),
    business_function character varying(100),
    business_process character varying(100),
    business_outcome character varying(100),
    business_metric character varying(100),
    business_kpi character varying(100),
    business_goal character varying(100),
    business_requirement text,
    business_constraint text,
    business_risk text,
    business_opportunity text,
    business_challenge text,
    business_solution text,
    business_benefit text,
    business_advantage text,
    business_competitive_advantage text,
    business_innovation text,
    business_transformation text,
    business_digitalization text,
    business_automation text,
    business_optimization text,
    business_standardization text,
    business_compliance text,
    business_governance text,
    business_audit text,
    business_security text,
    business_privacy text,
    business_ethics text,
    extracted_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.workflow_business_intelligence OWNER TO scraper_user;

--
-- Name: workflow_business_intelligence_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_business_intelligence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_business_intelligence_id_seq OWNER TO scraper_user;

--
-- Name: workflow_business_intelligence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_business_intelligence_id_seq OWNED BY public.workflow_business_intelligence.id;


--
-- Name: workflow_community_data; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_community_data (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    comments_count integer DEFAULT 0,
    reviews_count integer DEFAULT 0,
    questions_count integer DEFAULT 0,
    answers_count integer DEFAULT 0,
    discussions_count integer DEFAULT 0,
    mentions_count integer DEFAULT 0,
    bookmarks_count integer DEFAULT 0,
    favorites_count integer DEFAULT 0,
    follows_count integer DEFAULT 0,
    forks_count integer DEFAULT 0,
    clones_count integer DEFAULT 0,
    remixes_count integer DEFAULT 0,
    downloads_count integer DEFAULT 0,
    installs_count integer DEFAULT 0,
    usage_count integer DEFAULT 0,
    community_rating numeric(3,2),
    community_rating_count integer DEFAULT 0,
    community_engagement_score numeric(5,2),
    community_activity_score numeric(5,2),
    community_growth_rate numeric(5,2),
    community_retention_rate numeric(5,2),
    community_sentiment_score numeric(5,2),
    community_satisfaction_score numeric(5,2),
    extracted_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.workflow_community_data OWNER TO scraper_user;

--
-- Name: workflow_community_data_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_community_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_community_data_id_seq OWNER TO scraper_user;

--
-- Name: workflow_community_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_community_data_id_seq OWNED BY public.workflow_community_data.id;


--
-- Name: workflow_content; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_content (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    explainer_text text,
    explainer_html text,
    setup_instructions text,
    use_instructions text,
    has_videos boolean,
    video_count integer,
    has_iframes boolean,
    iframe_count integer,
    raw_content jsonb,
    extracted_at timestamp without time zone NOT NULL
);


ALTER TABLE public.workflow_content OWNER TO scraper_user;

--
-- Name: workflow_content_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_content_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_content_id_seq OWNER TO scraper_user;

--
-- Name: workflow_content_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_content_id_seq OWNED BY public.workflow_content.id;


--
-- Name: workflow_enhanced_content; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_enhanced_content (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    tutorial_content text,
    documentation_content text,
    faq_content text,
    troubleshooting_content text,
    best_practices_content text,
    video_count integer DEFAULT 0,
    video_duration integer DEFAULT 0,
    video_quality character varying(50),
    video_views integer DEFAULT 0,
    image_count integer DEFAULT 0,
    image_types jsonb,
    image_quality character varying(50),
    image_alt_text jsonb,
    diagram_count integer DEFAULT 0,
    flowchart_count integer DEFAULT 0,
    architecture_count integer DEFAULT 0,
    code_example_count integer DEFAULT 0,
    configuration_example_count integer DEFAULT 0,
    use_case_example_count integer DEFAULT 0,
    business_case_example_count integer DEFAULT 0,
    integration_example_count integer DEFAULT 0,
    customization_example_count integer DEFAULT 0,
    performance_example_count integer DEFAULT 0,
    security_example_count integer DEFAULT 0,
    maintenance_example_count integer DEFAULT 0,
    support_example_count integer DEFAULT 0,
    community_example_count integer DEFAULT 0,
    feedback_example_count integer DEFAULT 0,
    update_example_count integer DEFAULT 0,
    version_example_count integer DEFAULT 0,
    migration_example_count integer DEFAULT 0,
    upgrade_example_count integer DEFAULT 0,
    troubleshooting_example_count integer DEFAULT 0,
    debugging_example_count integer DEFAULT 0,
    extracted_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.workflow_enhanced_content OWNER TO scraper_user;

--
-- Name: workflow_enhanced_content_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_enhanced_content_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_enhanced_content_id_seq OWNER TO scraper_user;

--
-- Name: workflow_enhanced_content_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_enhanced_content_id_seq OWNED BY public.workflow_enhanced_content.id;


--
-- Name: workflow_metadata; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_metadata (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    title text,
    description text,
    use_case text,
    author_name character varying(255),
    author_url text,
    views integer,
    shares integer,
    categories jsonb,
    tags jsonb,
    workflow_created_at timestamp without time zone,
    workflow_updated_at timestamp without time zone,
    extracted_at timestamp without time zone NOT NULL,
    raw_metadata jsonb,
    author_id character varying(100),
    author_followers integer DEFAULT 0,
    author_workflows_count integer DEFAULT 0,
    author_verified boolean DEFAULT false,
    author_bio text,
    author_location character varying(100),
    workflow_rating numeric(3,2),
    workflow_rating_count integer DEFAULT 0,
    workflow_reviews_count integer DEFAULT 0,
    workflow_difficulty_score numeric(5,2),
    workflow_complexity_score numeric(5,2),
    workflow_estimated_time integer,
    workflow_skill_level character varying(50),
    workflow_industry character varying(100),
    workflow_company_size character varying(50),
    workflow_use_case_category character varying(100),
    workflow_business_value numeric(5,2),
    workflow_roi_estimate numeric(5,2),
    workflow_maintenance_level character varying(50),
    workflow_support_level character varying(50),
    workflow_security_level character varying(50),
    workflow_compliance_level character varying(50),
    workflow_integration_count integer DEFAULT 0,
    workflow_dependency_count integer DEFAULT 0,
    workflow_customization_level character varying(50),
    workflow_scalability_level character varying(50)
);


ALTER TABLE public.workflow_metadata OWNER TO scraper_user;

--
-- Name: workflow_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_metadata_id_seq OWNER TO scraper_user;

--
-- Name: workflow_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_metadata_id_seq OWNED BY public.workflow_metadata.id;


--
-- Name: workflow_performance_analytics; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_performance_analytics (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    execution_success_rate numeric(5,2),
    execution_failure_rate numeric(5,2),
    execution_error_rate numeric(5,2),
    performance_benchmarks jsonb,
    performance_metrics jsonb,
    performance_trends jsonb,
    usage_statistics jsonb,
    usage_patterns jsonb,
    usage_analytics jsonb,
    error_analytics jsonb,
    error_patterns jsonb,
    error_trends jsonb,
    optimization_opportunities jsonb,
    optimization_recommendations jsonb,
    scaling_requirements jsonb,
    scaling_limitations jsonb,
    scaling_recommendations jsonb,
    monitoring_requirements jsonb,
    monitoring_metrics jsonb,
    monitoring_alerts jsonb,
    maintenance_cost numeric(10,2),
    support_cost numeric(10,2),
    training_cost numeric(10,2),
    documentation_cost numeric(10,2),
    testing_cost numeric(10,2),
    deployment_cost numeric(10,2),
    integration_cost numeric(10,2),
    customization_cost numeric(10,2),
    security_cost numeric(10,2),
    compliance_cost numeric(10,2),
    governance_cost numeric(10,2),
    audit_cost numeric(10,2),
    backup_cost numeric(10,2),
    maintenance_requirements jsonb,
    support_requirements jsonb,
    training_requirements jsonb,
    documentation_requirements jsonb,
    testing_requirements jsonb,
    deployment_requirements jsonb,
    integration_requirements jsonb,
    customization_requirements jsonb,
    security_requirements jsonb,
    compliance_requirements jsonb,
    governance_requirements jsonb,
    audit_requirements jsonb,
    backup_requirements jsonb,
    support_level character varying(50),
    training_level character varying(50),
    documentation_level character varying(50),
    testing_level character varying(50),
    deployment_level character varying(50),
    integration_level character varying(50),
    customization_level character varying(50),
    security_level character varying(50),
    compliance_level character varying(50),
    governance_level character varying(50),
    audit_level character varying(50),
    backup_level character varying(50),
    maintenance_schedule jsonb,
    extracted_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.workflow_performance_analytics OWNER TO scraper_user;

--
-- Name: workflow_performance_analytics_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_performance_analytics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_performance_analytics_id_seq OWNER TO scraper_user;

--
-- Name: workflow_performance_analytics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_performance_analytics_id_seq OWNED BY public.workflow_performance_analytics.id;


--
-- Name: workflow_relationships; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_relationships (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    parent_workflows jsonb,
    child_workflows jsonb,
    sibling_workflows jsonb,
    dependent_workflows jsonb,
    dependency_workflows jsonb,
    prerequisite_workflows jsonb,
    related_workflows jsonb,
    similar_workflows jsonb,
    alternative_workflows jsonb,
    workflow_versions jsonb,
    workflow_branches jsonb,
    workflow_forks jsonb,
    workflow_clones jsonb,
    workflow_remixes jsonb,
    workflow_adaptations jsonb,
    workflow_integrations jsonb,
    workflow_extensions jsonb,
    workflow_plugins jsonb,
    workflow_templates jsonb,
    workflow_examples jsonb,
    workflow_tutorials jsonb,
    workflow_documentation jsonb,
    workflow_guides jsonb,
    workflow_manuals jsonb,
    workflow_support jsonb,
    workflow_community jsonb,
    workflow_forums jsonb,
    workflow_updates jsonb,
    workflow_patches jsonb,
    workflow_fixes jsonb,
    workflow_migrations jsonb,
    workflow_upgrades jsonb,
    workflow_downgrades jsonb,
    workflow_retirements jsonb,
    workflow_deprecations jsonb,
    workflow_archivals jsonb,
    workflow_licenses jsonb,
    workflow_permissions jsonb,
    workflow_restrictions jsonb,
    workflow_ownership jsonb,
    workflow_attribution jsonb,
    workflow_credits jsonb,
    workflow_collaboration jsonb,
    workflow_contributors jsonb,
    workflow_maintainers jsonb,
    extracted_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.workflow_relationships OWNER TO scraper_user;

--
-- Name: workflow_relationships_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_relationships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_relationships_id_seq OWNER TO scraper_user;

--
-- Name: workflow_relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_relationships_id_seq OWNED BY public.workflow_relationships.id;


--
-- Name: workflow_structure; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_structure (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    node_count integer,
    connection_count integer,
    node_types jsonb,
    extraction_type character varying(50),
    fallback_used boolean,
    workflow_json jsonb,
    extracted_at timestamp without time zone NOT NULL
);


ALTER TABLE public.workflow_structure OWNER TO scraper_user;

--
-- Name: workflow_structure_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_structure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_structure_id_seq OWNER TO scraper_user;

--
-- Name: workflow_structure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_structure_id_seq OWNED BY public.workflow_structure.id;


--
-- Name: workflow_technical_details; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflow_technical_details (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    api_endpoints jsonb,
    api_authentication_types jsonb,
    api_rate_limits jsonb,
    credential_requirements jsonb,
    credential_types jsonb,
    security_requirements jsonb,
    performance_metrics jsonb,
    execution_time numeric(10,3),
    memory_usage numeric(10,2),
    cpu_usage numeric(5,2),
    error_handling_patterns jsonb,
    retry_mechanisms jsonb,
    fallback_strategies jsonb,
    data_validation_rules jsonb,
    data_transformation_rules jsonb,
    workflow_triggers jsonb,
    workflow_conditions jsonb,
    workflow_actions jsonb,
    workflow_branches jsonb,
    workflow_loops jsonb,
    workflow_parallelism jsonb,
    workflow_error_handling jsonb,
    workflow_logging jsonb,
    workflow_monitoring jsonb,
    workflow_backup_strategies jsonb,
    workflow_recovery_strategies jsonb,
    workflow_scaling_strategies jsonb,
    workflow_optimization_strategies jsonb,
    workflow_testing_strategies jsonb,
    workflow_deployment_strategies jsonb,
    workflow_maintenance_strategies jsonb,
    workflow_support_strategies jsonb,
    workflow_documentation_level character varying(50),
    workflow_tutorial_level character varying(50),
    workflow_example_count integer DEFAULT 0,
    workflow_template_count integer DEFAULT 0,
    workflow_customization_level character varying(50),
    workflow_configuration_level character varying(50),
    workflow_integration_level character varying(50),
    workflow_extension_level character varying(50),
    workflow_automation_level character varying(50),
    workflow_intelligence_level character varying(50),
    extracted_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.workflow_technical_details OWNER TO scraper_user;

--
-- Name: workflow_technical_details_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflow_technical_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_technical_details_id_seq OWNER TO scraper_user;

--
-- Name: workflow_technical_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflow_technical_details_id_seq OWNED BY public.workflow_technical_details.id;


--
-- Name: workflows; Type: TABLE; Schema: public; Owner: scraper_user
--

CREATE TABLE public.workflows (
    id integer NOT NULL,
    workflow_id character varying(50) NOT NULL,
    url text NOT NULL,
    extracted_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    processing_time double precision,
    quality_score double precision,
    layer1_success boolean,
    layer2_success boolean,
    layer3_success boolean,
    error_message text,
    retry_count integer,
    last_scraped_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    version character varying(50),
    fork_count integer DEFAULT 0,
    clone_count integer DEFAULT 0,
    star_count integer DEFAULT 0,
    download_count integer DEFAULT 0,
    is_public boolean DEFAULT true,
    is_featured boolean DEFAULT false,
    is_verified boolean DEFAULT false,
    is_premium boolean DEFAULT false,
    layer4_success boolean DEFAULT false,
    layer5_success boolean DEFAULT false,
    layer6_success boolean DEFAULT false,
    layer7_success boolean DEFAULT false
);


ALTER TABLE public.workflows OWNER TO scraper_user;

--
-- Name: workflows_id_seq; Type: SEQUENCE; Schema: public; Owner: scraper_user
--

CREATE SEQUENCE public.workflows_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflows_id_seq OWNER TO scraper_user;

--
-- Name: workflows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scraper_user
--

ALTER SEQUENCE public.workflows_id_seq OWNED BY public.workflows.id;


--
-- Name: video_transcripts id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.video_transcripts ALTER COLUMN id SET DEFAULT nextval('public.video_transcripts_id_seq'::regclass);


--
-- Name: workflow_business_intelligence id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_business_intelligence ALTER COLUMN id SET DEFAULT nextval('public.workflow_business_intelligence_id_seq'::regclass);


--
-- Name: workflow_community_data id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_community_data ALTER COLUMN id SET DEFAULT nextval('public.workflow_community_data_id_seq'::regclass);


--
-- Name: workflow_content id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_content ALTER COLUMN id SET DEFAULT nextval('public.workflow_content_id_seq'::regclass);


--
-- Name: workflow_enhanced_content id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_enhanced_content ALTER COLUMN id SET DEFAULT nextval('public.workflow_enhanced_content_id_seq'::regclass);


--
-- Name: workflow_metadata id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_metadata ALTER COLUMN id SET DEFAULT nextval('public.workflow_metadata_id_seq'::regclass);


--
-- Name: workflow_performance_analytics id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_performance_analytics ALTER COLUMN id SET DEFAULT nextval('public.workflow_performance_analytics_id_seq'::regclass);


--
-- Name: workflow_relationships id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_relationships ALTER COLUMN id SET DEFAULT nextval('public.workflow_relationships_id_seq'::regclass);


--
-- Name: workflow_structure id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_structure ALTER COLUMN id SET DEFAULT nextval('public.workflow_structure_id_seq'::regclass);


--
-- Name: workflow_technical_details id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_technical_details ALTER COLUMN id SET DEFAULT nextval('public.workflow_technical_details_id_seq'::regclass);


--
-- Name: workflows id; Type: DEFAULT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflows ALTER COLUMN id SET DEFAULT nextval('public.workflows_id_seq'::regclass);


--
-- Name: video_transcripts video_transcripts_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.video_transcripts
    ADD CONSTRAINT video_transcripts_pkey PRIMARY KEY (id);


--
-- Name: workflow_business_intelligence workflow_business_intelligence_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_business_intelligence
    ADD CONSTRAINT workflow_business_intelligence_pkey PRIMARY KEY (id);


--
-- Name: workflow_community_data workflow_community_data_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_community_data
    ADD CONSTRAINT workflow_community_data_pkey PRIMARY KEY (id);


--
-- Name: workflow_content workflow_content_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_content
    ADD CONSTRAINT workflow_content_pkey PRIMARY KEY (id);


--
-- Name: workflow_content workflow_content_workflow_id_key; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_content
    ADD CONSTRAINT workflow_content_workflow_id_key UNIQUE (workflow_id);


--
-- Name: workflow_enhanced_content workflow_enhanced_content_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_enhanced_content
    ADD CONSTRAINT workflow_enhanced_content_pkey PRIMARY KEY (id);


--
-- Name: workflow_metadata workflow_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_metadata
    ADD CONSTRAINT workflow_metadata_pkey PRIMARY KEY (id);


--
-- Name: workflow_metadata workflow_metadata_workflow_id_key; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_metadata
    ADD CONSTRAINT workflow_metadata_workflow_id_key UNIQUE (workflow_id);


--
-- Name: workflow_performance_analytics workflow_performance_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_performance_analytics
    ADD CONSTRAINT workflow_performance_analytics_pkey PRIMARY KEY (id);


--
-- Name: workflow_relationships workflow_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_relationships
    ADD CONSTRAINT workflow_relationships_pkey PRIMARY KEY (id);


--
-- Name: workflow_structure workflow_structure_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_structure
    ADD CONSTRAINT workflow_structure_pkey PRIMARY KEY (id);


--
-- Name: workflow_structure workflow_structure_workflow_id_key; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_structure
    ADD CONSTRAINT workflow_structure_workflow_id_key UNIQUE (workflow_id);


--
-- Name: workflow_technical_details workflow_technical_details_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_technical_details
    ADD CONSTRAINT workflow_technical_details_pkey PRIMARY KEY (id);


--
-- Name: workflows workflows_pkey; Type: CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_pkey PRIMARY KEY (id);


--
-- Name: idx_categories_gin; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_categories_gin ON public.workflow_metadata USING gin (categories);


--
-- Name: idx_node_types_gin; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_node_types_gin ON public.workflow_structure USING gin (node_types);


--
-- Name: idx_workflow_business_intelligence_roi; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_business_intelligence_roi ON public.workflow_business_intelligence USING btree (roi_estimate);


--
-- Name: idx_workflow_business_intelligence_value; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_business_intelligence_value ON public.workflow_business_intelligence USING btree (business_value_score);


--
-- Name: idx_workflow_business_intelligence_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_business_intelligence_workflow_id ON public.workflow_business_intelligence USING btree (workflow_id);


--
-- Name: idx_workflow_community_data_engagement; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_community_data_engagement ON public.workflow_community_data USING btree (community_engagement_score);


--
-- Name: idx_workflow_community_data_rating; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_community_data_rating ON public.workflow_community_data USING btree (community_rating);


--
-- Name: idx_workflow_community_data_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_community_data_workflow_id ON public.workflow_community_data USING btree (workflow_id);


--
-- Name: idx_workflow_enhanced_content_video_count; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_enhanced_content_video_count ON public.workflow_enhanced_content USING btree (video_count);


--
-- Name: idx_workflow_enhanced_content_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_enhanced_content_workflow_id ON public.workflow_enhanced_content USING btree (workflow_id);


--
-- Name: idx_workflow_metadata_author_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_metadata_author_id ON public.workflow_metadata USING btree (author_id);


--
-- Name: idx_workflow_metadata_difficulty; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_metadata_difficulty ON public.workflow_metadata USING btree (workflow_difficulty_score);


--
-- Name: idx_workflow_metadata_industry; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_metadata_industry ON public.workflow_metadata USING btree (workflow_industry);


--
-- Name: idx_workflow_metadata_rating; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_metadata_rating ON public.workflow_metadata USING btree (workflow_rating);


--
-- Name: idx_workflow_performance_analytics_success; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_performance_analytics_success ON public.workflow_performance_analytics USING btree (execution_success_rate);


--
-- Name: idx_workflow_performance_analytics_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_performance_analytics_workflow_id ON public.workflow_performance_analytics USING btree (workflow_id);


--
-- Name: idx_workflow_relationships_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_relationships_workflow_id ON public.workflow_relationships USING btree (workflow_id);


--
-- Name: idx_workflow_technical_details_performance; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_technical_details_performance ON public.workflow_technical_details USING btree (execution_time);


--
-- Name: idx_workflow_technical_details_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflow_technical_details_workflow_id ON public.workflow_technical_details USING btree (workflow_id);


--
-- Name: idx_workflows_download_count; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflows_download_count ON public.workflows USING btree (download_count);


--
-- Name: idx_workflows_fork_count; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflows_fork_count ON public.workflows USING btree (fork_count);


--
-- Name: idx_workflows_is_featured; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflows_is_featured ON public.workflows USING btree (is_featured);


--
-- Name: idx_workflows_is_verified; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflows_is_verified ON public.workflows USING btree (is_verified);


--
-- Name: idx_workflows_star_count; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX idx_workflows_star_count ON public.workflows USING btree (star_count);


--
-- Name: ix_video_transcripts_platform; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX ix_video_transcripts_platform ON public.video_transcripts USING btree (platform);


--
-- Name: ix_video_transcripts_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX ix_video_transcripts_workflow_id ON public.video_transcripts USING btree (workflow_id);


--
-- Name: ix_workflow_content_has_videos; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX ix_workflow_content_has_videos ON public.workflow_content USING btree (has_videos);


--
-- Name: ix_workflow_metadata_title; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX ix_workflow_metadata_title ON public.workflow_metadata USING btree (title);


--
-- Name: ix_workflow_structure_node_count; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX ix_workflow_structure_node_count ON public.workflow_structure USING btree (node_count);


--
-- Name: ix_workflows_extracted_at; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX ix_workflows_extracted_at ON public.workflows USING btree (extracted_at);


--
-- Name: ix_workflows_quality_score; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE INDEX ix_workflows_quality_score ON public.workflows USING btree (quality_score);


--
-- Name: ix_workflows_workflow_id; Type: INDEX; Schema: public; Owner: scraper_user
--

CREATE UNIQUE INDEX ix_workflows_workflow_id ON public.workflows USING btree (workflow_id);


--
-- Name: workflow_business_intelligence update_workflow_business_intelligence_updated_at; Type: TRIGGER; Schema: public; Owner: scraper_user
--

CREATE TRIGGER update_workflow_business_intelligence_updated_at BEFORE UPDATE ON public.workflow_business_intelligence FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workflow_community_data update_workflow_community_data_updated_at; Type: TRIGGER; Schema: public; Owner: scraper_user
--

CREATE TRIGGER update_workflow_community_data_updated_at BEFORE UPDATE ON public.workflow_community_data FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workflow_enhanced_content update_workflow_enhanced_content_updated_at; Type: TRIGGER; Schema: public; Owner: scraper_user
--

CREATE TRIGGER update_workflow_enhanced_content_updated_at BEFORE UPDATE ON public.workflow_enhanced_content FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workflow_performance_analytics update_workflow_performance_analytics_updated_at; Type: TRIGGER; Schema: public; Owner: scraper_user
--

CREATE TRIGGER update_workflow_performance_analytics_updated_at BEFORE UPDATE ON public.workflow_performance_analytics FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workflow_relationships update_workflow_relationships_updated_at; Type: TRIGGER; Schema: public; Owner: scraper_user
--

CREATE TRIGGER update_workflow_relationships_updated_at BEFORE UPDATE ON public.workflow_relationships FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workflow_technical_details update_workflow_technical_details_updated_at; Type: TRIGGER; Schema: public; Owner: scraper_user
--

CREATE TRIGGER update_workflow_technical_details_updated_at BEFORE UPDATE ON public.workflow_technical_details FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: video_transcripts video_transcripts_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.video_transcripts
    ADD CONSTRAINT video_transcripts_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_business_intelligence workflow_business_intelligence_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_business_intelligence
    ADD CONSTRAINT workflow_business_intelligence_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_community_data workflow_community_data_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_community_data
    ADD CONSTRAINT workflow_community_data_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_content workflow_content_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_content
    ADD CONSTRAINT workflow_content_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_enhanced_content workflow_enhanced_content_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_enhanced_content
    ADD CONSTRAINT workflow_enhanced_content_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_metadata workflow_metadata_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_metadata
    ADD CONSTRAINT workflow_metadata_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_performance_analytics workflow_performance_analytics_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_performance_analytics
    ADD CONSTRAINT workflow_performance_analytics_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_relationships workflow_relationships_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_relationships
    ADD CONSTRAINT workflow_relationships_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_structure workflow_structure_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_structure
    ADD CONSTRAINT workflow_structure_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- Name: workflow_technical_details workflow_technical_details_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scraper_user
--

ALTER TABLE ONLY public.workflow_technical_details
    ADD CONSTRAINT workflow_technical_details_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict AjkvRh1rbJGgfES3hssBwQeub7EL0cv9b1E9On3eqsdQ6BjTVZBcgajzHkWRUAN

