-- =====================================================
-- Call Center Analytics Database Setup
-- CICD-Ready Schema-per-Customer Architecture
-- =====================================================

-- Create main database
CREATE DATABASE IF NOT EXISTS CALL_CENTER_ANALYTICS
    COMMENT = 'Main database for call center analytics platform';

USE DATABASE CALL_CENTER_ANALYTICS;

-- =====================================================
-- SHARED SCHEMAS (Platform-wide)
-- =====================================================

-- Shared configuration and metadata
CREATE SCHEMA IF NOT EXISTS SHARED_CONFIG
    COMMENT = 'Shared configuration, templates, and metadata';

-- Shared utilities and functions
CREATE SCHEMA IF NOT EXISTS SHARED_UTILS
    COMMENT = 'Shared utilities, UDFs, and common functions';

-- Platform monitoring and logging
CREATE SCHEMA IF NOT EXISTS PLATFORM_MONITORING
    COMMENT = 'Platform-wide monitoring, logging, and audit trails';

-- =====================================================
-- CUSTOMER SCHEMAS (Template)
-- =====================================================

-- Template schema for customer-specific deployments
-- This will be replicated for each customer as CUSTOMER_{CUSTOMER_ID}
CREATE SCHEMA IF NOT EXISTS CUSTOMER_TEMPLATE
    COMMENT = 'Template schema for customer-specific deployments';

-- =====================================================
-- SHARED CONFIGURATION TABLES
-- =====================================================

USE SCHEMA SHARED_CONFIG;

-- Customer registry
CREATE TABLE IF NOT EXISTS CUSTOMERS (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    config JSON,
    CONSTRAINT unique_schema_name UNIQUE (schema_name)
);

-- Use case templates
CREATE TABLE IF NOT EXISTS USE_CASE_TEMPLATES (
    template_id VARCHAR(50) PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,
    topics_to_track ARRAY,
    business_value_context TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Topic detection models configuration
CREATE TABLE IF NOT EXISTS TOPIC_DETECTION_MODELS (
    model_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50), -- 'CORTEX_CLASSIFY', 'CORTEX_EXTRACT', 'CUSTOM'
    model_config JSON,
    performance_metrics JSON,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- CUSTOMER TEMPLATE TABLES
-- =====================================================

USE SCHEMA CUSTOMER_TEMPLATE;

-- Raw transcripts table
CREATE TABLE IF NOT EXISTS TRANSCRIPTS (
    transcript_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(50),
    call_id VARCHAR(100),
    call_date TIMESTAMP_NTZ,
    call_duration_seconds INTEGER,
    transcript_text TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    processed_at TIMESTAMP_NTZ,
    processing_status VARCHAR(20) DEFAULT 'PENDING'
);

-- Customer-specific use cases
CREATE TABLE IF NOT EXISTS USE_CASES (
    use_case_id VARCHAR(50) PRIMARY KEY,
    use_case_name VARCHAR(255) NOT NULL,
    description TEXT,
    topics_to_track ARRAY NOT NULL,
    business_value_context TEXT,
    confidence_threshold FLOAT DEFAULT 0.8,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Topic detection results
CREATE TABLE IF NOT EXISTS TOPIC_SIGNALS (
    signal_id VARCHAR(100) PRIMARY KEY,
    transcript_id VARCHAR(100) NOT NULL,
    use_case_id VARCHAR(50) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    confidence_score FLOAT NOT NULL,
    match_snippet TEXT,
    match_position INTEGER,
    detected_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    model_used VARCHAR(50),
    FOREIGN KEY (transcript_id) REFERENCES TRANSCRIPTS(transcript_id),
    FOREIGN KEY (use_case_id) REFERENCES USE_CASES(use_case_id)
);

-- Aggregated analytics
CREATE TABLE IF NOT EXISTS TOPIC_ANALYTICS (
    analytics_id VARCHAR(100) PRIMARY KEY,
    use_case_id VARCHAR(50) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    date_period DATE NOT NULL,
    total_mentions INTEGER DEFAULT 0,
    unique_transcripts INTEGER DEFAULT 0,
    avg_confidence_score FLOAT,
    trend_direction VARCHAR(10), -- 'UP', 'DOWN', 'STABLE'
    business_impact_score FLOAT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (use_case_id) REFERENCES USE_CASES(use_case_id)
);

-- Processing logs
CREATE TABLE IF NOT EXISTS PROCESSING_LOGS (
    log_id VARCHAR(100) PRIMARY KEY,
    transcript_id VARCHAR(100),
    processing_stage VARCHAR(50), -- 'INGESTION', 'TOPIC_DETECTION', 'AGGREGATION'
    status VARCHAR(20), -- 'SUCCESS', 'FAILED', 'RETRY'
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- SHARED UTILITIES
-- =====================================================

USE SCHEMA SHARED_UTILS;

-- Function to create customer schema
CREATE OR REPLACE PROCEDURE CREATE_CUSTOMER_SCHEMA(CUSTOMER_ID VARCHAR, CUSTOMER_NAME VARCHAR)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    schema_name VARCHAR := 'CUSTOMER_' || UPPER(CUSTOMER_ID);
    result STRING;
BEGIN
    -- Create customer schema
    EXECUTE IMMEDIATE 'CREATE SCHEMA IF NOT EXISTS ' || schema_name || 
                     ' COMMENT = ''Customer schema for ' || CUSTOMER_NAME || '''';
    
    -- Clone template tables to customer schema
    EXECUTE IMMEDIATE 'CREATE TABLE ' || schema_name || '.TRANSCRIPTS LIKE CUSTOMER_TEMPLATE.TRANSCRIPTS';
    EXECUTE IMMEDIATE 'CREATE TABLE ' || schema_name || '.USE_CASES LIKE CUSTOMER_TEMPLATE.USE_CASES';
    EXECUTE IMMEDIATE 'CREATE TABLE ' || schema_name || '.TOPIC_SIGNALS LIKE CUSTOMER_TEMPLATE.TOPIC_SIGNALS';
    EXECUTE IMMEDIATE 'CREATE TABLE ' || schema_name || '.TOPIC_ANALYTICS LIKE CUSTOMER_TEMPLATE.TOPIC_ANALYTICS';
    EXECUTE IMMEDIATE 'CREATE TABLE ' || schema_name || '.PROCESSING_LOGS LIKE CUSTOMER_TEMPLATE.PROCESSING_LOGS';
    
    -- Register customer
    INSERT INTO SHARED_CONFIG.CUSTOMERS (customer_id, customer_name, schema_name)
    VALUES (CUSTOMER_ID, CUSTOMER_NAME, schema_name);
    
    result := 'Customer schema ' || schema_name || ' created successfully';
    RETURN result;
END;
$$;

-- Function to deploy use cases for a customer
CREATE OR REPLACE PROCEDURE DEPLOY_USE_CASES(CUSTOMER_ID VARCHAR, USE_CASES_JSON VARCHAR)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    schema_name VARCHAR;
    result STRING;
BEGIN
    -- Get customer schema name
    SELECT c.schema_name INTO schema_name 
    FROM SHARED_CONFIG.CUSTOMERS c 
    WHERE c.customer_id = CUSTOMER_ID;
    
    IF (schema_name IS NULL) THEN
        RETURN 'Customer not found: ' || CUSTOMER_ID;
    END IF;
    
    -- Parse and insert use cases (simplified - would need proper JSON parsing)
    result := 'Use cases deployed to schema: ' || schema_name;
    RETURN result;
END;
$$;

-- =====================================================
-- PLATFORM MONITORING
-- =====================================================

USE SCHEMA PLATFORM_MONITORING;

-- System health metrics
CREATE TABLE IF NOT EXISTS SYSTEM_METRICS (
    metric_id VARCHAR(100) PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(20),
    customer_id VARCHAR(50),
    recorded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Processing performance tracking
CREATE TABLE IF NOT EXISTS PERFORMANCE_METRICS (
    performance_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    processing_date DATE NOT NULL,
    transcripts_processed INTEGER DEFAULT 0,
    avg_processing_time_ms FLOAT,
    success_rate FLOAT,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample customer
CALL SHARED_UTILS.CREATE_CUSTOMER_SCHEMA('DEMO001', 'Demo Customer Inc');

-- Insert sample use case template
INSERT INTO SHARED_CONFIG.USE_CASE_TEMPLATES (
    template_id, template_name, description, topics_to_track, business_value_context
) VALUES (
    'TEMPLATE_001',
    'Customer Service Pain Points',
    'Detect common customer service issues and complaints',
    ['refund request', 'billing issue', 'product complaint', 'service delay'],
    'Identifying service pain points can reduce churn by 15% and improve NPS scores'
);

-- Insert sample topic detection model
INSERT INTO SHARED_CONFIG.TOPIC_DETECTION_MODELS (
    model_id, model_name, model_type, model_config
) VALUES (
    'MODEL_001',
    'Snowflake Cortex Classifier',
    'CORTEX_CLASSIFY',
    '{"function": "SNOWFLAKE.CORTEX.CLASSIFY", "confidence_threshold": 0.8}'
);

COMMIT;
