# Snowflake Google Sheets Integration

This repository contains a complete integration between Snowflake and Google Sheets, allowing you to write data directly from Snowflake to Google Sheets using Snowpark UDFs.

## 🚀 Features

- **Single Row Writing**: Write individual rows to Google Sheets
- **Batch Writing**: Write multiple rows in a single operation
- **OAuth Authentication**: Secure authentication using Google OAuth 2.0
- **External Access Integration**: Proper Snowflake external access setup
- **Git Integration**: Functions automatically available via Snowflake git integration

## 📋 Setup Instructions

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API
4. Create OAuth 2.0 credentials:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Note down the Client ID and Client Secret

### 2. Get Refresh Token

You'll need to get a refresh token for your Google account:

```python
# Use this Python script to get refresh token
import requests
from urllib.parse import urlencode

# Step 1: Get authorization code
auth_url = "https://accounts.google.com/o/oauth2/auth"
params = {
    'client_id': 'your_client_id',
    'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
    'scope': 'https://www.googleapis.com/auth/spreadsheets',
    'response_type': 'code',
    'access_type': 'offline',
    'prompt': 'consent'
}

print(f"Visit this URL: {auth_url}?{urlencode(params)}")
auth_code = input("Enter the authorization code: ")

# Step 2: Exchange for refresh token
token_url = "https://oauth2.googleapis.com/token"
data = {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'code': auth_code,
    'grant_type': 'authorization_code',
    'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
}

response = requests.post(token_url, data=data)
tokens = response.json()
print(f"Refresh Token: {tokens['refresh_token']}")
```

### 3. Snowflake Setup

1. Update the credentials in `snowflake_google_sheets_setup.sql`:
   ```sql
   CREATE OR REPLACE SECRET GOOGLE_OAUTH_CLIENT_ID
   TYPE = GENERIC_STRING
   SECRET_STRING = 'your_actual_client_id_here';
   
   CREATE OR REPLACE SECRET GOOGLE_OAUTH_CLIENT_SECRET
   TYPE = GENERIC_STRING
   SECRET_STRING = 'your_actual_client_secret_here';
   
   CREATE OR REPLACE SECRET GOOGLE_OAUTH_REFRESH_TOKEN
   TYPE = GENERIC_STRING
   SECRET_STRING = 'your_actual_refresh_token_here';
   ```

2. Run the setup script in Snowflake console:
   ```sql
   -- Copy and paste the entire snowflake_google_sheets_setup.sql file
   ```

## 📖 Usage Examples

### Single Row Write
```sql
SELECT WRITE_TO_GOOGLE_SHEETS(
    '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms', -- Spreadsheet ID
    'Sheet1',                                           -- Sheet name
    ['John Doe', 'john@example.com', '2024-01-01', 100.50]
);
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

### Batch Write
```sql
SELECT BATCH_WRITE_TO_GOOGLE_SHEETS(
    '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    'Sheet1',
    [
        ['Name1', 'Email1', 'Date1', 'Amount1'],
        ['Name2', 'Email2', 'Date2', 'Amount2'],
        ['Name3', 'Email3', 'Date3', 'Amount3']
    ]
);
```

### Write Query Results to Sheets
```sql
-- Example: Write customer data to Google Sheets
WITH customer_data AS (
    SELECT 
        customer_name,
        email,
        registration_date,
        total_orders
    FROM customers 
    WHERE registration_date >= '2024-01-01'
    LIMIT 10
)
SELECT WRITE_TO_GOOGLE_SHEETS(
    '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    'CustomerData',
    ARRAY_CONSTRUCT(customer_name, email, registration_date, total_orders)
) as result
FROM customer_data;
```

## 🔧 Functions Available

### `WRITE_TO_GOOGLE_SHEETS(spreadsheet_id, sheet_name, row_data)`
- **spreadsheet_id**: Google Sheets spreadsheet ID (from URL)
- **sheet_name**: Name of the sheet/tab
- **row_data**: Array of values to write

### `APPEND_ROW_TO_SHEET(spreadsheet_id, sheet_name, col1, col2, col3, col4, col5)`
- Simplified wrapper for up to 5 columns
- Automatically handles null values

### `BATCH_WRITE_TO_GOOGLE_SHEETS(spreadsheet_id, sheet_name, rows_data)`
- Write multiple rows in one operation
- **rows_data**: Array of arrays containing row data

## 🔍 Finding Spreadsheet ID

The spreadsheet ID is in the Google Sheets URL:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                      ^-- This is the spreadsheet ID --^
```

## 🛠️ Troubleshooting

### Common Issues

1. **"External access integration not found"**
   - Make sure you ran the setup as ACCOUNTADMIN
   - Verify the integration exists: `SHOW INTEGRATIONS;`

2. **"Secret not found"**
   - Check secrets exist: `SHOW SECRETS;`
   - Verify permissions are granted to your role

3. **"Authentication failed"**
   - Verify your OAuth credentials are correct
   - Make sure the refresh token is valid
   - Check that Google Sheets API is enabled

4. **"Spreadsheet not found"**
   - Verify the spreadsheet ID is correct
   - Make sure the Google account has access to the spreadsheet

## 📁 Files in this Repository

- `google_sheets_handler.py` - Core Python handler for Google Sheets API
- `snowflake_google_sheets_setup.sql` - Complete Snowflake setup script
- `README.md` - This documentation

## 🔐 Security Notes

- OAuth credentials are stored as Snowflake secrets
- External access is limited to Google APIs only
- Refresh tokens should be rotated periodically
- Never commit actual credentials to git

## 🎯 Next Steps

1. Set up your Google OAuth credentials
2. Run the Snowflake setup script
3. Test with a simple write operation
4. Integrate into your data pipelines

Happy data writing! 🚀
