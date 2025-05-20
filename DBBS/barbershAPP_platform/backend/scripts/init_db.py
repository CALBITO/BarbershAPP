from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from geoalchemy2 import Geometry
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from src.database.db import db, migrate, get_session, get_connection_info
from scripts.verify_postgres import verify_postgres

logger = logging.getLogger(__name__)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    try:
        if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
            db.init_app(app)
            migrate.init_app(app, db)
            logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise

def init_database():
    """Initialize PostgreSQL database"""
    # Verify PostgreSQL service first
    if not verify_postgres():
        logger.error("❌ PostgreSQL service verification failed")
        return False
        
    # Connection parameters
    params = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': 'localhost',
        'port': '5432'
    }
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create database
        db_name = os.getenv('DB_NAME', 'barbershop_db')
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ Database '{db_name}' created")
        
        # Create user
        db_user = os.getenv('DB_USER', 'CALBITO')
        db_pass = os.getenv('DB_PASSWORD', 'N8t3rdvZn')
        
        cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{db_user}'")
        if not cur.fetchone():
            cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_pass}'")
            logger.info(f"✅ User '{db_user}' created")
        
        # Grant privileges
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        logger.info(f"✅ Privileges granted to '{db_user}'")
        
        # Close initial connection
        cur.close()
        conn.close()
        
        # Connect to new database with updated parameters
        new_params = params.copy()
        new_params['dbname'] = db_name
        conn = psycopg2.connect(**new_params)
        cur = conn.cursor()
        
        # Enable PostGIS
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        conn.commit()
        logger.info("✅ PostGIS extension enabled")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    init_database()