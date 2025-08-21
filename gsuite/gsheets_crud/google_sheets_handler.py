"""
Google Sheets Handler for Snowpark UDF
Handles writing rows to Google Sheets using Google Sheets API
"""

import json
import requests
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsHandler:
    """Handler for Google Sheets API operations"""
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize with Google OAuth credentials
        
        Args:
            credentials: Dict containing client_id, client_secret, refresh_token
        """
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.refresh_token = credentials.get('refresh_token')
        self.access_token = None
        
    def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token:
            return self.access_token
            
        # Refresh access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        return self.access_token
    
    def write_row_to_sheet(self, 
                          spreadsheet_id: str, 
                          sheet_name: str, 
                          row_data: List[Any],
                          range_start: str = "A1") -> Dict[str, Any]:
        """
        Write a row to Google Sheets
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Name of the sheet/tab
            row_data: List of values to write
            range_start: Starting cell (default A1)
            
        Returns:
            Dict with operation result
        """
        try:
            access_token = self.get_access_token()
            
            # Construct the range
            range_name = f"{sheet_name}!{range_start}"
            
            # Google Sheets API URL
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}:append"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare the data
            body = {
                'values': [row_data],
                'majorDimension': 'ROWS'
            }
            
            params = {
                'valueInputOption': 'USER_ENTERED',
                'insertDataOption': 'INSERT_ROWS'
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=body, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'spreadsheet_id': spreadsheet_id,
                'sheet_name': sheet_name,
                'updated_range': result.get('updates', {}).get('updatedRange'),
                'updated_rows': result.get('updates', {}).get('updatedRows', 0),
                'updated_columns': result.get('updates', {}).get('updatedColumns', 0),
                'updated_cells': result.get('updates', {}).get('updatedCells', 0)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error writing to Google Sheets: {e}")
            return {
                'success': False,
                'error': f'HTTP error: {str(e)}',
                'error_type': 'http_error'
            }
        except Exception as e:
            logger.error(f"Error writing to Google Sheets: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error'
            }
    
    def batch_write_rows(self, 
                        spreadsheet_id: str, 
                        sheet_name: str, 
                        rows_data: List[List[Any]],
                        range_start: str = "A1") -> Dict[str, Any]:
        """
        Write multiple rows to Google Sheets in batch
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Name of the sheet/tab
            rows_data: List of rows, each row is a list of values
            range_start: Starting cell (default A1)
            
        Returns:
            Dict with operation result
        """
        try:
            access_token = self.get_access_token()
            
            # Construct the range
            range_name = f"{sheet_name}!{range_start}"
            
            # Google Sheets API URL
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}:append"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare the data
            body = {
                'values': rows_data,
                'majorDimension': 'ROWS'
            }
            
            params = {
                'valueInputOption': 'USER_ENTERED',
                'insertDataOption': 'INSERT_ROWS'
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=body, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'spreadsheet_id': spreadsheet_id,
                'sheet_name': sheet_name,
                'updated_range': result.get('updates', {}).get('updatedRange'),
                'updated_rows': result.get('updates', {}).get('updatedRows', 0),
                'updated_columns': result.get('updates', {}).get('updatedColumns', 0),
                'updated_cells': result.get('updates', {}).get('updatedCells', 0),
                'rows_written': len(rows_data)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error in batch write to Google Sheets: {e}")
            return {
                'success': False,
                'error': f'HTTP error: {str(e)}',
                'error_type': 'http_error'
            }
        except Exception as e:
            logger.error(f"Error in batch write to Google Sheets: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error'
            }

def write_to_google_sheets(spreadsheet_id: str, 
                          sheet_name: str, 
                          row_data: str,  # JSON string of row data
                          credentials: str) -> str:  # JSON string of credentials
    """
    Main function for Snowpark UDF to write to Google Sheets
    
    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        sheet_name: Name of the sheet/tab
        row_data: JSON string containing row data as list
        credentials: JSON string containing OAuth credentials
        
    Returns:
        JSON string with operation result
    """
    try:
        # Parse inputs
        row_list = json.loads(row_data)
        creds_dict = json.loads(credentials)
        
        # Initialize handler
        handler = GoogleSheetsHandler(creds_dict)
        
        # Write to sheet
        result = handler.write_row_to_sheet(spreadsheet_id, sheet_name, row_list)
        
        return json.dumps(result)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            'success': False,
            'error': f'JSON parsing error: {str(e)}',
            'error_type': 'json_error'
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e),
            'error_type': 'general_error'
        })

def write_to_google_sheets_udf(spreadsheet_id, sheet_name, row_data):
    """
    Snowpark UDF wrapper for write_to_google_sheets
    """
    try:
        # Get credentials from Snowflake secrets
        import _snowflake

        credentials = {
            'client_id': _snowflake.get_generic_secret_string('client_id'),
            'client_secret': _snowflake.get_generic_secret_string('client_secret'),
            'refresh_token': _snowflake.get_generic_secret_string('refresh_token')
        }

        # Call the main function
        result = write_to_google_sheets(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            row_data=row_data,
            credentials=json.dumps(credentials)
        )

        return result

    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e),
            'error_type': 'udf_error'
        })


def export_table_to_google_sheets_udf(table_name, spreadsheet_id, sheet_name, include_headers):
    """
    Snowpark UDF that exports an entire table to Google Sheets
    """
    try:
        # Get credentials from Snowflake secrets
        import _snowflake
        from snowflake.snowpark import Session

        credentials = {
            'client_id': _snowflake.get_generic_secret_string('client_id'),
            'client_secret': _snowflake.get_generic_secret_string('client_secret'),
            'refresh_token': _snowflake.get_generic_secret_string('refresh_token')
        }

        # Get Snowpark session
        session = Session.builder.getOrCreate()

        # Query the table
        df = session.sql(f"SELECT * FROM {table_name}")
        rows_data = df.collect()

        results = []
        row_count = 0

        # Add headers if requested
        if include_headers and rows_data:
            headers = list(rows_data[0].asDict().keys())
            header_result = write_to_google_sheets(
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                row_data=json.dumps(headers),
                credentials=json.dumps(credentials)
            )
            results.append(json.loads(header_result))
            row_count += 1

        # Add data rows
        for row in rows_data:
            row_dict = row.asDict()
            row_values = [str(v) if v is not None else '' for v in row_dict.values()]

            result = write_to_google_sheets(
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                row_data=json.dumps(row_values),
                credentials=json.dumps(credentials)
            )

            results.append(json.loads(result))
            row_count += 1

        return json.dumps({
            'success': True,
            'table_name': table_name,
            'spreadsheet_id': spreadsheet_id,
            'sheet_name': sheet_name,
            'total_rows_exported': row_count,
            'include_headers': include_headers,
            'results': results
        })

    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e),
            'error_type': 'export_error',
            'table_name': table_name,
            'spreadsheet_id': spreadsheet_id,
            'sheet_name': sheet_name
        })


# For testing
if __name__ == "__main__":
    # Example usage
    test_credentials = {
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
        'refresh_token': 'your_refresh_token'
    }
    
    test_row = ['Test', 'Data', '2024-01-01', 123.45]
    
    result = write_to_google_sheets(
        spreadsheet_id='your_spreadsheet_id',
        sheet_name='Sheet1',
        row_data=json.dumps(test_row),
        credentials=json.dumps(test_credentials)
    )
    
    print(result)
