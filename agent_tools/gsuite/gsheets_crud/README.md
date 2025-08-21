# Google Sheets CRUD Integration

Snowpark UDF integration for writing data from Snowflake directly to Google Sheets using OAuth 2.0 authentication.

## 🚀 Features

- **Single Row Writing**: Write individual rows to Google Sheets
- **Batch Writing**: Write multiple rows in a single operation  
- **OAuth Authentication**: Secure authentication using Google OAuth 2.0
- **External Access Integration**: Proper Snowflake external access setup
- **Error Handling**: Comprehensive error reporting and logging
- **Git Integration**: Functions automatically available via Snowflake git integration

## 📁 Files

- `google_sheets_handler.py` - Core Python handler for Google Sheets API operations
- `setup_google_sheets.sql` - Complete setup script (update with your credentials)
- `README.md` - This documentation

## 🔧 Setup Instructions

### 1. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API
4. Create OAuth 2.0 credentials (Desktop application)
5. Get refresh token using OAuth flow

### 2. Sync Repository in Snowflake

```sql
USE ROLE SYSADMIN;
ALTER GIT REPOSITORY ASPECT.PUBLIC.SNOWFLAKE_REPO FETCH;

-- Verify files are available
LIST @ASPECT.PUBLIC.SNOWFLAKE_REPO/branches/main/agent_tools/gsuite/gsheets_crud/;
```

### 3. Run the Setup Script

1. Copy `setup_google_sheets.sql`
2. Replace the placeholder credentials with your actual values:
   - `your_google_client_id_here`
   - `your_google_client_secret_here` 
   - `your_google_refresh_token_here`
3. Run the updated script in Snowflake console

## 📖 Usage Examples

### Single Row Write
```sql
SELECT WRITE_TO_GOOGLE_SHEETS(
    '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms', -- Spreadsheet ID
    'Sheet1',                                           -- Sheet name
    ['John Doe', 'john@example.com', '2024-01-01', 100.50]
) as result;
```

### Simplified Wrapper
```sql
SELECT APPEND_ROW_TO_SHEET(
    '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    'Sheet1',
    'John Doe',      -- Column 1
    'john@email.com', -- Column 2
    '2024-01-01',    -- Column 3
    '100.50'         -- Column 4
);
```

### Write Query Results
```sql
WITH sample_data AS (
    SELECT 
        'Customer ' || ROW_NUMBER() OVER (ORDER BY 1) as name,
        'customer' || ROW_NUMBER() OVER (ORDER BY 1) || '@example.com' as email,
        CURRENT_DATE()::STRING as date_created,
        (RANDOM() * 1000)::NUMBER(10,2) as amount
    FROM TABLE(GENERATOR(ROWCOUNT => 5))
)
SELECT 
    name,
    email, 
    date_created,
    amount,
    WRITE_TO_GOOGLE_SHEETS(
        'your_spreadsheet_id',
        'CustomerData',
        ARRAY_CONSTRUCT(name, email, date_created, amount)
    ) as sheets_result
FROM sample_data;
```

## 🔍 Finding Spreadsheet ID

The spreadsheet ID is in the Google Sheets URL:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                      ^-- This is the spreadsheet ID --^
```

## 🎯 Functions Available

### `WRITE_TO_GOOGLE_SHEETS(spreadsheet_id, sheet_name, row_data)`
- **spreadsheet_id**: Google Sheets spreadsheet ID (from URL)
- **sheet_name**: Name of the sheet/tab
- **row_data**: Array of values to write
- **Returns**: JSON object with operation result

### `APPEND_ROW_TO_SHEET(spreadsheet_id, sheet_name, col1, col2, col3, col4, col5)`
- Simplified wrapper for up to 5 columns
- Automatically handles null values
- **Returns**: JSON object with operation result

## 🛠️ Troubleshooting

### Common Issues

1. **"External access integration not found"**
   - Make sure you ran the setup as ACCOUNTADMIN
   - Verify: `SHOW INTEGRATIONS LIKE 'GOOGLE_SHEETS_ACCESS_INTEGRATION';`

2. **"Secret not found"**
   - Check: `SHOW SECRETS LIKE 'GOOGLE_OAUTH%';`
   - Verify permissions are granted to your role

3. **"Authentication failed"**
   - Verify OAuth credentials are correct
   - Check that Google Sheets API is enabled
   - Ensure refresh token is valid

4. **"Import file not found"**
   - Verify git repository is synced
   - Check file path in stage

## 🔐 Security Notes

- OAuth credentials are stored as Snowflake secrets
- External access is limited to Google APIs only
- Never commit actual credentials to git
- Refresh tokens should be rotated periodically

## 📊 Response Format

**Success Response:**
```json
{
  "success": true,
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "sheet_name": "Sheet1", 
  "updated_range": "Sheet1!A1:D1",
  "updated_rows": 1,
  "updated_columns": 4,
  "updated_cells": 4
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "error_type": "http_error|json_error|general_error"
}
```

Happy data writing! 🚀
