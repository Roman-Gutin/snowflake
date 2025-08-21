-- ========================================
-- Google Sheets Integration Setup
-- Run these commands in Snowflake console
-- ========================================

USE ROLE SYSADMIN;

-- Step 1: Sync the repository to get latest files
ALTER GIT REPOSITORY ASPECT.PUBLIC.SNOWFLAKE_REPO FETCH;

-- Step 2: Verify files are available
LIST @ASPECT.PUBLIC.SNOWFLAKE/gsuite/gsheets_crud/;

-- Step 3: Switch to ACCOUNTADMIN to create secrets and integrations
USE ROLE ACCOUNTADMIN;

-- Create External Access Integration for Google APIs
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

-- Create secrets for Google OAuth credentials
-- ⚠️  REPLACE THESE WITH YOUR ACTUAL GOOGLE OAUTH CREDENTIALS ⚠️
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

-- Grant permissions to SYSADMIN
GRANT USAGE ON INTEGRATION GOOGLE_SHEETS_ACCESS_INTEGRATION TO ROLE SYSADMIN;
GRANT READ ON SECRET GOOGLE_OAUTH_CLIENT_ID TO ROLE SYSADMIN;
GRANT READ ON SECRET GOOGLE_OAUTH_CLIENT_SECRET TO ROLE SYSADMIN;
GRANT READ ON SECRET GOOGLE_OAUTH_REFRESH_TOKEN TO ROLE SYSADMIN;

-- Switch back to SYSADMIN to create functions
USE ROLE SYSADMIN;

-- Create the main Google Sheets UDF
CREATE OR REPLACE FUNCTION WRITE_TO_GOOGLE_SHEETS(
    SPREADSHEET_ID STRING,
    SHEET_NAME STRING,
    ROW_DATA VARIANT
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('requests', 'snowflake-snowpark-python')
IMPORTS = ('@ASPECT.PUBLIC.SNOWFLAKE/gsuite/gsheets_crud/google_sheets_handler.py')
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

-- Create simplified wrapper function
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

-- Test the setup
SHOW FUNCTIONS LIKE 'WRITE_TO_GOOGLE_SHEETS';
SHOW FUNCTIONS LIKE 'APPEND_ROW_TO_SHEET';

SELECT '🎉 Google Sheets UDF setup complete! Update the secrets with your actual credentials.' as status;
