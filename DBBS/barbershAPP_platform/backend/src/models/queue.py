from src.database.db import db
from datetime import datetime
from .base import BaseModel

class Queue(BaseModel):
    """Queue model for managing barbershop waiting lists"""
    __tablename__ = 'queues'
    
    # Foreign Keys
    barbershop_id = db.Column(db.Integer, db.ForeignKey('barbershops.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Queue specific fields
    position = db.Column(db.Integer, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='waiting')
    estimated_wait_time = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        """Convert queue instance to dictionary"""
        base_dict = super().to_dict()
        queue_dict = {
            'barbershop_id': self.barbershop_id,
            'user_id': self.user_id,
            'position': self.position,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'status': self.status,
            'estimated_wait_time': self.estimated_wait_time
        }
        return {**base_dict, **queue_dict}