from src.database.db import db
from datetime import datetime
from .base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

class Barber(BaseModel):
    """Barber model for managing barber information"""
    __tablename__ = 'barbers'
    __table_args__ = {'extend_existing': True}
    
    # Personal info
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    barbershop_id = db.Column(db.Integer, db.ForeignKey('barbershops.id'), nullable=False)
    status = db.Column(db.String(20), default='available')
    
    # Relationships
    appointments = db.relationship('Appointment', backref='barber', lazy=True)
    availability = db.relationship('Availability', backref='barber', lazy=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert to dictionary representation"""
        base_dict = super().to_dict()
        barber_dict = {
            'name': self.name,
            'email': self.email,
            'barbershop_id': self.barbershop_id,
            'status': self.status
        }
        return {**base_dict, **barber_dict}