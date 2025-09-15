import os
import sys
import pyodbc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get connection parameters from environment variables
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER", "SQL Server")

# Print connection parameters (without password)
print(f"Server: {server}")
print(f"Database: {database}")
print(f"Username: {username}")
print(f"Driver: {driver}")

try:
    # Create connection string
    conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};Connection Timeout=30;'
    
    # Try to connect
    print("Attempting to connect...")
    conn = pyodbc.connect(conn_str)
    
    # If connection successful, print success message
    print("Connection successful!")
    
    # Test query to verify we can execute commands
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    row = cursor.fetchone()
    print(f"SQL Server version: {row[0]}")
    
    # Close connection
    cursor.close()
    conn.close()
    print("Connection closed.")
    sys.exit(0)

except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)
