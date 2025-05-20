from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from src.database.db import db, migrate, init_db, get_session, get_connection_info
db = SQLAlchemy()
logger = logging.getLogger(__name__)
migrate = Migrate()

def init_db(app):
    """Initialize the database with the Flask app"""
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        
        # Import models here to avoid circular imports
        from src.models import Barbershop, Barber, Queue, Appointment
        
        with app.app_context():
            # Enable PostGIS
            db.session.execute('CREATE EXTENSION IF NOT EXISTS postgis')
            db.session.commit()
            
            # Create indexes from setup.sql
            db.session.execute('''
                CREATE INDEX IF NOT EXISTS idx_barbershop_location ON barbershops USING GIST (location);
                CREATE INDEX IF NOT EXISTS idx_barber_shop ON barbers(barbershop_id);
                CREATE INDEX IF NOT EXISTS idx_appointment_datetime ON appointments(appointment_datetime);
                CREATE INDEX IF NOT EXISTS idx_queue_shop ON queues(barbershop_id);
            ''')
            db.session.commit()
            logger.info("✅ Database initialized successfully with PostGIS and indexes")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def get_session():
    """Get SQLAlchemy session"""
    return db.session

def get_connection_info():
    """Get database connection information"""
    try:
        result = db.session.execute('SELECT version()')
        postgis = db.session.execute('SELECT PostGIS_Version()')
        version = result.scalar()
        postgis_version = postgis.scalar()
        return {
            "status": "connected",
            "version": version,
            "postgis_version": postgis_version,
            "type": "postgresql"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "postgresql"
        }
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret"

__all__ = ['db', 'migrate', 'init_db', 'get_session', 'get_connection_info']