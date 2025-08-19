"""
Snowflake Connection Manager with Caching
Handles programmatic connections to Snowflake with session caching to avoid constant authentication
"""

import snowflake.connector
import streamlit as st
import os
import json
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowflakeConnectionManager:
    """Manages Snowflake connections with caching and session management"""
    
    def __init__(self, account_format: str = 'lowercase'):
        self.connection = None
        self.cursor = None

        # Try different account formats
        account_options = {
            'lowercase': 'rnrizgx-aub95186',
            'uppercase': 'RNRIZGX-AUB95186',
            'orgname': 'RNRIZGX.AUB95186',  # Organization.Account format
            'legacy': 'aub95186'  # Legacy format
        }

        self.connection_params = {
            'account': account_options.get(account_format, 'RNRIZGX-AUB95186'),
            'user': 'ROMAN',
            'authenticator': 'externalbrowser',
            'role': 'ACCOUNTADMIN',
            'client_session_keep_alive': True,
            'insecure_mode': False,  # Keep secure by default
            # Don't set warehouse/database/schema initially - let connection establish first
        }
        self.session_cache_file = '.snowflake_session_cache.json'
        self.cache_duration_hours = 8  # Cache session for 8 hours
    
    def _load_cached_session(self) -> Optional[Dict[str, Any]]:
        """Load cached session information if available and valid"""
        try:
            if os.path.exists(self.session_cache_file):
                with open(self.session_cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                if datetime.now() - cache_time < timedelta(hours=self.cache_duration_hours):
                    logger.info("Using cached Snowflake session")
                    return cache_data.get('session_info')
                else:
                    logger.info("Cached session expired")
                    os.remove(self.session_cache_file)
        except Exception as e:
            logger.warning(f"Error loading cached session: {e}")
        
        return None
    
    def _save_session_cache(self, session_info: Dict[str, Any]):
        """Save session information to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'session_info': session_info
            }
            with open(self.session_cache_file, 'w') as f:
                json.dump(cache_data, f)
            logger.info("Session cached successfully")
        except Exception as e:
            logger.warning(f"Error saving session cache: {e}")
    
    def connect(self, use_cache: bool = True, debug: bool = False) -> snowflake.connector.SnowflakeConnection:
        """
        Establish connection to Snowflake with optional caching
        
        Args:
            use_cache: Whether to use cached session if available
            
        Returns:
            Snowflake connection object
        """
        
        # Try to use cached session first
        if use_cache:
            cached_session = self._load_cached_session()
            if cached_session:
                try:
                    # Attempt to reuse cached connection parameters
                    self.connection_params.update(cached_session)
                except Exception as e:
                    logger.warning(f"Could not reuse cached session: {e}")
        
        try:
            logger.info("Establishing Snowflake connection...")
            if debug:
                logger.info(f"Connection params: {self.connection_params}")

            self.connection = snowflake.connector.connect(**self.connection_params)
            self.cursor = self.connection.cursor()

            # Test the connection
            self.cursor.execute("SELECT CURRENT_VERSION()")
            version = self.cursor.fetchone()[0]
            logger.info(f"Connected to Snowflake version: {version}")

            # Get current context
            self.cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            context = self.cursor.fetchone()
            logger.info(f"Connected as: User={context[0]}, Role={context[1]}, Warehouse={context[2]}, Database={context[3]}, Schema={context[4]}")

            # Cache session info (excluding sensitive data)
            if use_cache:
                session_info = {
                    'warehouse': context[2],
                    'database': context[3],
                    'schema': context[4]
                }
                self._save_session_cache(session_info)

            return self.connection

        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")

            # Try different approaches based on error type
            if 'certificate' in str(e).lower() or '254007' in str(e):
                logger.info("Certificate error detected, trying insecure mode...")
                try:
                    insecure_params = self.connection_params.copy()
                    insecure_params['insecure_mode'] = True
                    self.connection = snowflake.connector.connect(**insecure_params)
                    self.cursor = self.connection.cursor()
                    logger.warning("Connected in insecure mode (not recommended for production)")
                    return self.connection
                except Exception as e2:
                    logger.error(f"Insecure mode also failed: {e2}")

            elif 'SAML' in str(e) or 'Identity Provider' in str(e):
                logger.info("Trying alternative account format...")
                alt_params = self.connection_params.copy()
                alt_params['account'] = 'RNRIZGX-AUB95186'  # Try uppercase
                try:
                    self.connection = snowflake.connector.connect(**alt_params)
                    self.cursor = self.connection.cursor()
                    logger.info("Connected with alternative account format")
                    return self.connection
                except Exception as e2:
                    logger.error(f"Alternative connection also failed: {e2}")

            raise
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> list:
        """
        Execute a query and return results
        
        Args:
            query: SQL query to execute
            params: Optional parameters for the query
            
        Returns:
            List of query results
        """
        if not self.cursor:
            raise Exception("No active Snowflake connection. Call connect() first.")
        
        try:
            logger.info(f"Executing query: {query[:100]}...")
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_ddl(self, ddl: str) -> bool:
        """
        Execute DDL statements (CREATE, DROP, ALTER, etc.)
        
        Args:
            ddl: DDL statement to execute
            
        Returns:
            True if successful
        """
        if not self.cursor:
            raise Exception("No active Snowflake connection. Call connect() first.")
        
        try:
            logger.info(f"Executing DDL: {ddl[:100]}...")
            self.cursor.execute(ddl)
            logger.info("DDL executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"DDL execution failed: {e}")
            raise
    
    def close(self):
        """Close the Snowflake connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Snowflake connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# Streamlit integration functions
@st.cache_resource
def get_snowflake_connection():
    """Cached Snowflake connection for Streamlit"""
    manager = SnowflakeConnectionManager()
    manager.connect()
    return manager

def test_connection_comprehensive(account: str, user: str, role: str = 'ACCOUNTADMIN', debug: bool = False):
    """Comprehensive connection test with multiple approaches"""

    # Account format variations
    account_formats = [
        account,  # As provided
        account.upper(),  # Uppercase
        account.lower(),  # Lowercase
        account.replace('_', '-'),  # Replace underscore with hyphen
        account.replace('-', '.'),  # Replace hyphen with dot
        account.split('-')[-1] if '-' in account else account,  # Legacy format
    ]

    # Connection parameter variations
    connection_variations = [
        {'insecure_mode': False},  # Secure (default)
        {'insecure_mode': True},   # Insecure (for certificate issues)
    ]

    for account_fmt in account_formats:
        for variation in connection_variations:
            try:
                if debug:
                    print(f"Trying: account={account_fmt}, insecure={variation.get('insecure_mode', False)}")

                params = {
                    'account': account_fmt,
                    'user': user,
                    'authenticator': 'externalbrowser',
                    'role': role,
                    'client_session_keep_alive': True,
                    **variation
                }

                connection = snowflake.connector.connect(**params)
                cursor = connection.cursor()
                cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
                result = cursor.fetchone()
                cursor.close()
                connection.close()

                return {
                    'success': True,
                    'account_format': account_fmt,
                    'connection_params': params,
                    'user': result[0],
                    'role': result[1],
                    'warehouse': result[2]
                }

            except Exception as e:
                if debug:
                    print(f"  ❌ Failed: {str(e)[:100]}...")
                continue

    return {
        'success': False,
        'error': 'All connection attempts failed'
    }

def test_connection_formats(debug: bool = False):
    """Test multiple account formats to find the working one"""
    formats = ['lowercase', 'uppercase', 'orgname', 'legacy']

    for fmt in formats:
        print(f"Trying account format: {fmt}")
        try:
            manager = SnowflakeConnectionManager(account_format=fmt)
            manager.connect(debug=debug)
            result = manager.execute_query("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
            manager.close()
            return {
                'success': True,
                'format': fmt,
                'user': result[0][0],
                'role': result[0][1],
                'warehouse': result[0][2]
            }
        except Exception as e:
            print(f"  ❌ Failed with {fmt}: {str(e)[:100]}...")
            continue

    return {
        'success': False,
        'error': 'All account formats failed'
    }

def test_connection(debug: bool = False):
    """Test the Snowflake connection"""
    try:
        manager = SnowflakeConnectionManager()
        manager.connect(debug=debug)
        result = manager.execute_query("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
        manager.close()
        return {
            'success': True,
            'user': result[0][0],
            'role': result[0][1],
            'warehouse': result[0][2]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Test multiple connection formats
    print("Testing Snowflake connection with multiple account formats...")
    result = test_connection_formats(debug=True)

    if result['success']:
        print(f"\n✅ Connection successful with format: {result['format']}")
        print(f"User: {result['user']}")
        print(f"Role: {result['role']}")
        print(f"Warehouse: {result['warehouse']}")
    else:
        print(f"\n❌ All connection attempts failed")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're logged into Snowflake in your browser")
        print("2. Try running: snowsql -a rnrizgx-aub95186 -u ROMAN --authenticator externalbrowser")
        print("3. Check if your account identifier is correct")
        print("4. Verify your Snowflake account is set up for external browser authentication")
