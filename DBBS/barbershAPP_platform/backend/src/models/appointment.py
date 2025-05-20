from datetime import datetime
from src.database.db import db
from .base import BaseModel

class Appointment(BaseModel):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    barber_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='appointments')
    barber = db.relationship('Barber', backref='appointments')

    def to_dict(self):
        base_dict = super().to_dict()
        appointment_dict = {
            'appointment_datetime': self.appointment_datetime.isoformat(),
            'status': self.status,
            'barber': self.barber.to_dict() if self.barber else None,
        }
        return {**base_dict, **appointment_dict}