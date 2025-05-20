from datetime import datetime
from src.database.db import db
from src.models.base import BaseModel  # Fix the import path
from geoalchemy2 import Geometry

class Barbershop(BaseModel):
    __tablename__ = 'barbershops'
    
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(Geometry('POINT'), nullable=False)
    
    # Relationships
    barbers = db.relationship("Barber", backref="barbershop", lazy=True)
    appointments = db.relationship("Appointment", backref="shop", lazy=True)
    current_queue = db.relationship("Queue", uselist=False, backref="shop", lazy=True)