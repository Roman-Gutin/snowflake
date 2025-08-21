-- ========================================
-- Google Sheets Integration Setup for Snowflake
-- Creates external access integration and UDF for writing to Google Sheets
-- ========================================

USE ROLE ACCOUNTADMIN;

-- Step 1: Create External Access Integration for Google APIs
CREATE OR REPLACE NETWORK RULE GOOGLE_APIS_NETWORK_RULE
MODE = EGRESS
TYPE = HOST_PORT
VALUE_LIST = (
    'oauth2.googleapis.com:443',
    'sheets.googleapis.com:443'
);

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION GOOGLE_SHEETS_ACCESS_INTEGRATION
ALLOWED_NETWORK_RULES = (GOOGLE_APIS_NETWORK_RULE)
ENABLED = TRUE
COMMENT = 'External access integration for Google Sheets API';

-- Step 2: Create secrets for Google OAuth credentials
-- Replace these with your actual Google OAuth credentials
CREATE OR REPLACE SECRET GOOGLE_OAUTH_CLIENT_ID
TYPE = GENERIC_STRING
SECRET_STRING = 'your_google_client_id_here'
COMMENT = 'Google OAuth Client ID for Sheets API';

CREATE OR REPLACE SECRET GOOGLE_OAUTH_CLIENT_SECRET
TYPE = GENERIC_STRING
SECRET_STRING = 'your_google_client_secret_here'
COMMENT = 'Google OAuth Client Secret for Sheets API';

CREATE OR REPLACE SECRET GOOGLE_OAUTH_REFRESH_TOKEN
TYPE = GENERIC_STRING
SECRET_STRING = 'your_google_refresh_token_here'
COMMENT = 'Google OAuth Refresh Token for Sheets API';

-- Step 3: Grant permissions to SYSADMIN
GRANT USAGE ON INTEGRATION GOOGLE_SHEETS_ACCESS_INTEGRATION TO ROLE SYSADMIN;
GRANT READ ON SECRET GOOGLE_OAUTH_CLIENT_ID TO ROLE SYSADMIN;
GRANT READ ON SECRET GOOGLE_OAUTH_CLIENT_SECRET TO ROLE SYSADMIN;
GRANT READ ON SECRET GOOGLE_OAUTH_REFRESH_TOKEN TO ROLE SYSADMIN;

-- Step 4: Switch to SYSADMIN and create the UDF
USE ROLE SYSADMIN;

-- Create the Python UDF for writing to Google Sheets
CREATE OR REPLACE FUNCTION WRITE_TO_GOOGLE_SHEETS(
    SPREADSHEET_ID STRING,
    SHEET_NAME STRING,
    ROW_DATA VARIANT
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('requests', 'snowflake-snowpark-python')
IMPORTS = ('@GIT_STAGE/google_sheets_handler.py')
EXTERNAL_ACCESS_INTEGRATIONS = (GOOGLE_SHEETS_ACCESS_INTEGRATION)
SECRETS = (
    'client_id' = GOOGLE_OAUTH_CLIENT_ID,
    'client_secret' = GOOGLE_OAUTH_CLIENT_SECRET,
    'refresh_token' = GOOGLE_OAUTH_REFRESH_TOKEN
)
HANDLER = 'google_sheets_handler.write_to_google_sheets_udf'
AS
$$
import json
import sys
import importlib.util

# Import the handler from the uploaded file
spec = importlib.util.spec_from_file_location("google_sheets_handler", sys.import_meta.resolve("google_sheets_handler.py"))
google_sheets_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google_sheets_handler)

def write_to_google_sheets_udf(spreadsheet_id, sheet_name, row_data):
    """
    Snowpark UDF wrapper for Google Sheets integration
    """
    try:
        # Get credentials from secrets
        import _snowflake
        
        credentials = {
            'client_id': _snowflake.get_generic_secret_string('client_id'),
            'client_secret': _snowflake.get_generic_secret_string('client_secret'),
            'refresh_token': _snowflake.get_generic_secret_string('refresh_token')
        }
        
        # Convert row_data to list if it's not already
        if isinstance(row_data, str):
            row_list = json.loads(row_data)
        elif isinstance(row_data, list):
            row_list = row_data
        else:
            row_list = [str(row_data)]
        
        # Use the handler to write to Google Sheets
        result = google_sheets_handler.write_to_google_sheets(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            row_data=json.dumps(row_list),
            credentials=json.dumps(credentials)
        )
        
        return json.loads(result)
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': 'udf_error'
        }
$$;

-- Step 5: Create a simplified wrapper function
CREATE OR REPLACE FUNCTION APPEND_ROW_TO_SHEET(
    SPREADSHEET_ID STRING,
    SHEET_NAME STRING,
    COL1 STRING DEFAULT NULL,
    COL2 STRING DEFAULT NULL,
    COL3 STRING DEFAULT NULL,
    COL4 STRING DEFAULT NULL,
    COL5 STRING DEFAULT NULL
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
    SELECT WRITE_TO_GOOGLE_SHEETS(
        SPREADSHEET_ID,
        SHEET_NAME,
        ARRAY_CONSTRUCT_COMPACT(COL1, COL2, COL3, COL4, COL5)
    )
$$;

-- Step 6: Create batch write function
CREATE OR REPLACE FUNCTION BATCH_WRITE_TO_GOOGLE_SHEETS(
    SPREADSHEET_ID STRING,
    SHEET_NAME STRING,
    ROWS_DATA VARIANT
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('requests', 'snowflake-snowpark-python')
IMPORTS = ('@GIT_STAGE/google_sheets_handler.py')
EXTERNAL_ACCESS_INTEGRATIONS = (GOOGLE_SHEETS_ACCESS_INTEGRATION)
SECRETS = (
    'client_id' = GOOGLE_OAUTH_CLIENT_ID,
    'client_secret' = GOOGLE_OAUTH_CLIENT_SECRET,
    'refresh_token' = GOOGLE_OAUTH_REFRESH_TOKEN
)
HANDLER = 'batch_write_handler'
AS
$$
import json
import sys
import importlib.util

# Import the handler from the uploaded file
spec = importlib.util.spec_from_file_location("google_sheets_handler", sys.import_meta.resolve("google_sheets_handler.py"))
google_sheets_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google_sheets_handler)

def batch_write_handler(spreadsheet_id, sheet_name, rows_data):
    """
    Batch write handler for multiple rows
    """
    try:
        # Get credentials from secrets
        import _snowflake
        
        credentials = {
            'client_id': _snowflake.get_generic_secret_string('client_id'),
            'client_secret': _snowflake.get_generic_secret_string('client_secret'),
            'refresh_token': _snowflake.get_generic_secret_string('refresh_token')
        }
        
        # Initialize handler
        handler = google_sheets_handler.GoogleSheetsHandler(credentials)
        
        # Convert rows_data to proper format
        if isinstance(rows_data, str):
            rows_list = json.loads(rows_data)
        else:
            rows_list = rows_data
        
        # Write to sheet
        result = handler.batch_write_rows(spreadsheet_id, sheet_name, rows_list)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': 'batch_udf_error'
        }
$$;

-- ========================================
-- Usage Examples
-- ========================================

-- Example 1: Write a single row
-- SELECT WRITE_TO_GOOGLE_SHEETS(
--     'your_spreadsheet_id',
--     'Sheet1',
--     ['Name', 'Email', 'Date', 'Amount']
-- );

-- Example 2: Use the simplified wrapper
-- SELECT APPEND_ROW_TO_SHEET(
--     'your_spreadsheet_id',
--     'Sheet1',
--     'John Doe',
--     'john@example.com',
--     '2024-01-01',
--     '100.00'
-- );

-- Example 3: Batch write multiple rows
-- SELECT BATCH_WRITE_TO_GOOGLE_SHEETS(
--     'your_spreadsheet_id',
--     'Sheet1',
--     [
--         ['Name1', 'Email1', 'Date1'],
--         ['Name2', 'Email2', 'Date2'],
--         ['Name3', 'Email3', 'Date3']
--     ]
-- );

-- ========================================
-- Verification
-- ========================================

-- Check that everything was created
SHOW INTEGRATIONS LIKE 'GOOGLE_SHEETS_ACCESS_INTEGRATION';
SHOW SECRETS LIKE 'GOOGLE_OAUTH%';
SHOW FUNCTIONS LIKE 'WRITE_TO_GOOGLE_SHEETS';
SHOW FUNCTIONS LIKE 'APPEND_ROW_TO_SHEET';
SHOW FUNCTIONS LIKE 'BATCH_WRITE_TO_GOOGLE_SHEETS';
