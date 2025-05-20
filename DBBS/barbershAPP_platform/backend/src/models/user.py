from src.database.db import db
from datetime import datetime
from .base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseModel):
    """User model for managing customer accounts"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # Removed invalid SQLite option
    
    # User information
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    
    # Relationships
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    queue_entries = db.relationship('Queue', backref='user', lazy=True)

    def set_password(self, password):
        """Set hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary representation"""
        base_dict = super().to_dict()
        user_dict = {
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone
        }
        return {**base_dict, **user_dict}