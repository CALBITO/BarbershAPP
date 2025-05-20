from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from geoalchemy2 import Geometry
from firebase_admin import firestore # type: ignore
import logging

logger = logging.getLogger(__name__)

# Initialize databases
db = SQLAlchemy()
migrate = Migrate()
firestore_db = None

def init_db(app):
    """Initialize PostgreSQL and Firestore"""
    try:
        # Initialize PostgreSQL with PostGIS
        db.init_app(app)
        migrate.init_app(app, db)
        
        with app.app_context():
            # Enable PostGIS
            db.session.execute('CREATE EXTENSION IF NOT EXISTS postgis')
            db.session.commit()
            
            # Initialize Firestore
            global firestore_db
            firestore_db = firestore.client()
            
            logger.info("Databases initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def get_session():
    """Get PostgreSQL session for geospatial queries"""
    return db.session

def get_firestore():
    """Get Firestore client for user data"""
    return firestore_db

def check_connections():
    """Check both database connections"""
    status = {
        "postgresql": False,
        "firestore": False
    }
    
    try:
        # Check PostgreSQL
        db.session.execute('SELECT 1')
        db.session.commit()
        status["postgresql"] = True
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")

    try:
        # Check Firestore
        if firestore_db:
            firestore_db.collection('health_check').get()
            status["firestore"] = True
    except Exception as e:
        logger.error(f"Firestore connection failed: {e}")

    return status