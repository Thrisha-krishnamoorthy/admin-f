import mysql.connector
import os

# Load environment variables (if using a .env file, uncomment the next two lines)
from dotenv import load_dotenv
load_dotenv()

# TiDB connection configuration
db_config = {
    'host': os.getenv('DB_HOST', '').replace('http://', '').replace('https://', ''),  # Remove protocol
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'ssl_ca': os.getenv('CA'),  # Path to the SSL certificate
    'port': int(os.getenv('DB_PORT', 4000))  # Default TiDB port is 4000
}

# Establish the database connection
try:
    db = mysql.connector.connect(**db_config)
    print("Connected to TiDB")
except mysql.connector.Error as err:
    print(f"Error connecting to TiDB: {err}")

# Export db if needed