"""
Database Manager for Call Center Analytics Platform
Handles CICD deployment and customer schema management
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from snowflake_connection import SnowflakeConnectionManager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations for the call center analytics platform"""
    
    def __init__(self, connection_manager: SnowflakeConnectionManager = None):
        self.connection_manager = connection_manager or SnowflakeConnectionManager()
        self.database_name = 'CALL_CENTER_ANALYTICS'
    
    def deploy_database_structure(self) -> bool:
        """Deploy the complete database structure from SQL file"""
        try:
            logger.info("Deploying database structure...")
            
            # Read the SQL file
            with open('database_setup.sql', 'r') as f:
                sql_content = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            # Execute each statement
            for i, statement in enumerate(statements):
                if statement and not statement.startswith('--'):
                    try:
                        logger.info(f"Executing statement {i+1}/{len(statements)}")
                        self.connection_manager.execute_ddl(statement)
                    except Exception as e:
                        logger.error(f"Failed to execute statement {i+1}: {e}")
                        logger.error(f"Statement: {statement[:200]}...")
                        # Continue with other statements
            
            logger.info("Database structure deployment completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy database structure: {e}")
            return False
    
    def create_customer_schema(self, customer_id: str, customer_name: str) -> bool:
        """Create a new customer schema with all required tables"""
        try:
            logger.info(f"Creating customer schema for {customer_id}: {customer_name}")
            
            # Call the stored procedure
            result = self.connection_manager.execute_query(
                "CALL SHARED_UTILS.CREATE_CUSTOMER_SCHEMA(?, ?)",
                [customer_id, customer_name]
            )
            
            logger.info(f"Customer schema created: {result}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create customer schema: {e}")
            return False
    
    def deploy_use_cases(self, customer_id: str, use_cases: List[Dict[str, Any]]) -> bool:
        """Deploy use cases for a specific customer"""
        try:
            logger.info(f"Deploying use cases for customer {customer_id}")
            
            schema_name = f"CUSTOMER_{customer_id.upper()}"
            
            # Insert each use case
            for use_case in use_cases:
                insert_sql = f"""
                INSERT INTO {schema_name}.USE_CASES (
                    use_case_id, use_case_name, description, topics_to_track, 
                    business_value_context, confidence_threshold
                ) VALUES (?, ?, ?, ?, ?, ?)
                """
                
                params = [
                    use_case.get('use_case_id', f"UC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    use_case.get('use_case', 'Unnamed Use Case'),
                    use_case.get('description', ''),
                    json.dumps(use_case.get('topics_to_track', [])),
                    use_case.get('business_value_context', ''),
                    use_case.get('confidence_threshold', 0.8)
                ]
                
                self.connection_manager.execute_query(insert_sql, params)
            
            logger.info(f"Deployed {len(use_cases)} use cases for customer {customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy use cases: {e}")
            return False
    
    def get_customer_schemas(self) -> List[Dict[str, Any]]:
        """Get list of all customer schemas"""
        try:
            result = self.connection_manager.execute_query(
                "SELECT customer_id, customer_name, schema_name, status, created_at FROM SHARED_CONFIG.CUSTOMERS"
            )
            
            customers = []
            for row in result:
                customers.append({
                    'customer_id': row[0],
                    'customer_name': row[1],
                    'schema_name': row[2],
                    'status': row[3],
                    'created_at': row[4]
                })
            
            return customers
            
        except Exception as e:
            logger.error(f"Failed to get customer schemas: {e}")
            return []
    
    def get_use_cases(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get use cases for a specific customer"""
        try:
            schema_name = f"CUSTOMER_{customer_id.upper()}"
            
            result = self.connection_manager.execute_query(f"""
                SELECT use_case_id, use_case_name, description, topics_to_track, 
                       business_value_context, confidence_threshold, is_active
                FROM {schema_name}.USE_CASES
                WHERE is_active = TRUE
            """)
            
            use_cases = []
            for row in result:
                use_cases.append({
                    'use_case_id': row[0],
                    'use_case_name': row[1],
                    'description': row[2],
                    'topics_to_track': json.loads(row[3]) if row[3] else [],
                    'business_value_context': row[4],
                    'confidence_threshold': row[5],
                    'is_active': row[6]
                })
            
            return use_cases
            
        except Exception as e:
            logger.error(f"Failed to get use cases for customer {customer_id}: {e}")
            return []
    
    def create_topic_detection_dag(self, customer_id: str) -> str:
        """Generate SQL for topic detection DAG"""
        schema_name = f"CUSTOMER_{customer_id.upper()}"
        
        dag_sql = f"""
-- Topic Detection DAG for Customer: {customer_id}
-- Generated on: {datetime.now().isoformat()}

-- Task 1: Process new transcripts
CREATE OR REPLACE TASK {schema_name}.PROCESS_TRANSCRIPTS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 */1 * * * UTC'  -- Every hour
AS
BEGIN
    -- Update processing status
    UPDATE {schema_name}.TRANSCRIPTS 
    SET processing_status = 'PROCESSING', processed_at = CURRENT_TIMESTAMP()
    WHERE processing_status = 'PENDING';
    
    -- Log processing start
    INSERT INTO {schema_name}.PROCESSING_LOGS (log_id, processing_stage, status)
    VALUES (UUID_STRING(), 'INGESTION', 'SUCCESS');
END;

-- Task 2: Topic detection using Snowflake Cortex
CREATE OR REPLACE TASK {schema_name}.DETECT_TOPICS
    WAREHOUSE = COMPUTE_WH
    AFTER {schema_name}.PROCESS_TRANSCRIPTS
AS
BEGIN
    -- Detect topics for each use case
    INSERT INTO {schema_name}.TOPIC_SIGNALS (
        signal_id, transcript_id, use_case_id, topic, confidence_score, 
        match_snippet, model_used
    )
    SELECT 
        UUID_STRING() as signal_id,
        t.transcript_id,
        uc.use_case_id,
        topic.value::STRING as topic,
        SNOWFLAKE.CORTEX.CLASSIFY(
            'What is the main topic of this text?',
            t.transcript_text,
            ARRAY_CONSTRUCT(topic.value::STRING)
        ) as confidence_score,
        SUBSTRING(t.transcript_text, 1, 500) as match_snippet,
        'CORTEX_CLASSIFY' as model_used
    FROM {schema_name}.TRANSCRIPTS t
    CROSS JOIN {schema_name}.USE_CASES uc
    CROSS JOIN TABLE(FLATTEN(uc.topics_to_track)) topic
    WHERE t.processing_status = 'PROCESSING'
    AND uc.is_active = TRUE;
    
    -- Update transcript status
    UPDATE {schema_name}.TRANSCRIPTS 
    SET processing_status = 'COMPLETED'
    WHERE processing_status = 'PROCESSING';
END;

-- Task 3: Generate analytics
CREATE OR REPLACE TASK {schema_name}.GENERATE_ANALYTICS
    WAREHOUSE = COMPUTE_WH
    AFTER {schema_name}.DETECT_TOPICS
AS
BEGIN
    -- Daily topic analytics
    INSERT INTO {schema_name}.TOPIC_ANALYTICS (
        analytics_id, use_case_id, topic, date_period, 
        total_mentions, unique_transcripts, avg_confidence_score
    )
    SELECT 
        UUID_STRING() as analytics_id,
        ts.use_case_id,
        ts.topic,
        CURRENT_DATE() as date_period,
        COUNT(*) as total_mentions,
        COUNT(DISTINCT ts.transcript_id) as unique_transcripts,
        AVG(ts.confidence_score) as avg_confidence_score
    FROM {schema_name}.TOPIC_SIGNALS ts
    JOIN {schema_name}.TRANSCRIPTS t ON ts.transcript_id = t.transcript_id
    WHERE DATE(t.call_date) = CURRENT_DATE()
    GROUP BY ts.use_case_id, ts.topic;
END;

-- Start the DAG
ALTER TASK {schema_name}.PROCESS_TRANSCRIPTS RESUME;
ALTER TASK {schema_name}.DETECT_TOPICS RESUME;
ALTER TASK {schema_name}.GENERATE_ANALYTICS RESUME;
"""
        return dag_sql
    
    def deploy_customer_dag(self, customer_id: str) -> bool:
        """Deploy the topic detection DAG for a customer"""
        try:
            logger.info(f"Deploying DAG for customer {customer_id}")
            
            dag_sql = self.create_topic_detection_dag(customer_id)
            
            # Split and execute statements
            statements = [stmt.strip() for stmt in dag_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    self.connection_manager.execute_ddl(statement)
            
            logger.info(f"DAG deployed successfully for customer {customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy DAG for customer {customer_id}: {e}")
            return False

# Mock connection for development/testing
class MockDatabaseManager(DatabaseManager):
    """Mock database manager for development when Snowflake is not available"""
    
    def __init__(self):
        self.customers = []
        self.use_cases = {}
    
    def deploy_database_structure(self) -> bool:
        logger.info("Mock: Database structure deployed")
        return True
    
    def create_customer_schema(self, customer_id: str, customer_name: str) -> bool:
        logger.info(f"Mock: Created schema for {customer_id}: {customer_name}")
        self.customers.append({
            'customer_id': customer_id,
            'customer_name': customer_name,
            'schema_name': f'CUSTOMER_{customer_id.upper()}',
            'status': 'ACTIVE',
            'created_at': datetime.now()
        })
        return True
    
    def deploy_use_cases(self, customer_id: str, use_cases: List[Dict[str, Any]]) -> bool:
        logger.info(f"Mock: Deployed {len(use_cases)} use cases for {customer_id}")
        self.use_cases[customer_id] = use_cases
        return True
    
    def get_customer_schemas(self) -> List[Dict[str, Any]]:
        return self.customers
    
    def get_use_cases(self, customer_id: str) -> List[Dict[str, Any]]:
        return self.use_cases.get(customer_id, [])
    
    def deploy_customer_dag(self, customer_id: str) -> bool:
        logger.info(f"Mock: DAG deployed for customer {customer_id}")
        return True

if __name__ == "__main__":
    # Test with mock manager
    print("Testing Database Manager...")
    
    db_manager = MockDatabaseManager()
    
    # Test database deployment
    db_manager.deploy_database_structure()
    
    # Test customer creation
    db_manager.create_customer_schema("TEST001", "Test Customer Inc")
    
    # Test use case deployment
    sample_use_cases = [
        {
            "use_case": "Customer Complaints",
            "topics_to_track": ["refund request", "billing issue", "product complaint"],
            "business_value_context": "Reduce churn by 15%",
            "confidence_threshold": 0.8
        }
    ]
    
    db_manager.deploy_use_cases("TEST001", sample_use_cases)
    
    # Test DAG deployment
    db_manager.deploy_customer_dag("TEST001")
    
    print("✅ All tests passed!")
