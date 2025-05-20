from src.database.db import db
from datetime import datetime

class BaseModel(db.Model):
    """Base model class that other models will inherit from"""
    __abstract__ = True
    __table_args__ = {'extend_existing': True}
    
    # Common columns for all models
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def save(self):
        """Save the current instance to the database"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    def delete(self):
        """Delete the current instance from the database"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by ID"""
        return cls.query.get(id)