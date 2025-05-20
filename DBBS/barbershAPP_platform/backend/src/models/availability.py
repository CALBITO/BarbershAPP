from src.database.db import db
from datetime import datetime, time
from .base import BaseModel

class Availability(BaseModel):
    """Model for managing barber availability schedules"""
    __tablename__ = 'availability'
    __table_args__ = {
        'extend_existing': True,
        'sqlite_autoincrement': True
    }
    
    # Foreign Keys
    barber_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    
    # Schedule fields
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Convert availability to dictionary representation"""
        base_dict = super().to_dict()
        availability_dict = {
            'barber_id': self.barber_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_available': self.is_available
        }
        return {**base_dict, **availability_dict}

    @classmethod
    def create_weekly_schedule(cls, barber_id, start_time, end_time):
        """Create default weekly availability for a barber"""
        schedules = []
        for day in range(7):  # 0-6 for Monday-Sunday
            availability = cls(
                barber_id=barber_id,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                is_available=True
            )
            schedules.append(availability)
        return schedules