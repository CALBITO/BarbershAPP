import sys
import logging
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
import os


db = SQLAlchemy()

def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    """Check database connection and configuration"""
    try:
        # Create test app
        app = Flask(__name__)
        
        # Load environment variables
        load_dotenv()
        
        # Configure database
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:postgres@localhost:5432/barbershop_dev'
        )
        
        # Initialize database
        from src.database.db import db
        db.init_app(app)
        
        with app.app_context():
            # Test connection
            db.engine.connect()
            logger.info("✅ Database connection successful!")
            
            # Check PostGIS
            result = db.session.execute('SELECT PostGIS_Version()').scalar()
            logger.info(f"✅ PostGIS version: {result}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database check failed: {e}")
        return False

if __name__ == '__main__':
    sys.exit(0 if check_database() else 1)