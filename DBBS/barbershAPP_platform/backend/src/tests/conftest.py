import pytest
from pathlib import Path
import sys
import os
from src.app import create_app
from src.database.db import db, init_db

# Add project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

@pytest.fixture(scope='session')
def app():
    """Create test Flask application"""
    _app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-key'
    })
    
    
    with _app.app_context():
        init_db(_app)
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app):
    """Create fresh database session for tests"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        session = db.create_scoped_session(
            options=dict(bind=connection, binds={})
        )
        
        db.session = session
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()