import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.app import create_app
from src.database.db import db

# Set up path to allow imports from parent directory
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))


def init_database():
    """Initialize PostgreSQL database and user"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment
        DB_NAME = os.getenv('DB_NAME', 'barbershop_db')
        DB_USER = os.getenv('DB_USER', 'barbershop_user')
        DB_PASS = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
        POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

        if not POSTGRES_PASSWORD:
            raise ValueError("POSTGRES_PASSWORD must be set in .env file")
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname='postgres',
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # ...existing code...
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {DB_NAME}")
            logger.info(f"✅ Database '{DB_NAME}' created successfully")
        
        # Close postgres connection
        cur.close()
        conn.close()
        
        # Connect to the new database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user='postgres',
            password=os.getenv('POSTGRES_PASSWORD'),
            host=DB_HOST
        )
        cur = conn.cursor()
        
        # Create user if doesn't exist
        cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}'")
        if not cur.fetchone():
            cur.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASS}'")
            logger.info(f"✅ User '{DB_USER}' created successfully")
        
        # Grant privileges
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}")
        logger.info(f"✅ Privileges granted to '{DB_USER}'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Load environment variables
load_dotenv(backend_dir / '.env')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Verify database connection and PostGIS setup"""
    try:
        engine = create_engine(os.getenv('DATABASE_URL'))
        with engine.connect() as conn:
            # Check PostGIS
            result = conn.execute(text('SELECT PostGIS_Version()'))
            logger.info(f"✅ PostGIS Version: {result.scalar()}")
            
            # Check tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            logger.info("\n✅ Available tables:")
            for row in result:
                logger.info(f"  - {row[0]}")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection check failed: {str(e)}")
        return False

def setup_database():
    """Initialize database with PostGIS and create tables"""
    try:
        # Check connection first
        if not check_database_connection():
            raise Exception("Database connection failed")

        app = create_app()
        with app.app_context():
            # Enable PostGIS
            db.session.execute(text('CREATE EXTENSION IF NOT EXISTS postgis'))
            logger.info("✅ PostGIS extension enabled")
            
            # Create all tables
            db.create_all()
            logger.info("✅ Database tables created successfully")
            db.session.commit()
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        raise

if __name__ == "__main__":
    # Initialize database first
    if init_database():
        # Then run existing setup
        setup_database()
