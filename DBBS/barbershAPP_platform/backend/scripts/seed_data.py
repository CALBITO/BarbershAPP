from datetime import datetime, timedelta
from src.app import create_app
from src.models import Shop, Service, User, Barber, Appointment, db
from pathlib import Path
import json
from src.models.barbershop import Shop
from src.database.db import db

def load_barbershop_data():
    """Load initial barbershop data from JSON"""
    data_path = Path(__file__).parent.parent / 'data' / 'bbs_data.JSON'
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
            
        for shop in data:
            attrs = shop['attributes']
            geom = shop['geometry']
            
            new_shop = Shop(
                name=attrs['BARBERSHOP'],
                address=attrs['ADDRESS'],
                phone=attrs['PHONE'],
                latitude=float(attrs['LATITUDE']),
                longitude=float(attrs['LONGITUDE']),
                ward=int(float(attrs['WARD'])),
                zipcode=attrs['ZIPCODE']
            )
            db.session.add(new_shop)
        
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Error loading barbershop data: {e}")
        db.session.rollback()
        return False

def seed_database():
    """Initialize database with seed data"""
    try:
        # Clear existing data
        Shop.query.delete()
        
        # Load barbershop data
        success = load_barbershop_data()
        
        return success
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False