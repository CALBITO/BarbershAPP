import psycopg2
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgres_connection():
    """Test PostgreSQL connection with error handling"""
    # Load environment variables
    load_dotenv()
    
    # Connection parameters
    params = {
        'dbname': os.getenv('DB_NAME', 'barbershop_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        logger.info("🔄 Testing database connection...")
        conn = psycopg2.connect(**params)
        
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info(f"✅ Successfully connected to PostgreSQL\nVersion: {version[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_postgres_connection()