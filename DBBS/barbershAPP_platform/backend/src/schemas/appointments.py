from marshmallow import Schema, fields, validate, validates, ValidationError #type: ignore
from datetime import datetime

class AppointmentSchema(Schema):
    """Schema for appointment validation"""
    id = fields.Integer(dump_only=True)  # Read-only field
    user_id = fields.Integer(dump_only=True)  # Set by auth decorator
    shop_id = fields.Integer(required=True)
    service = fields.String(required=True)
    date = fields.DateTime(required=True)
    status = fields.String(
        validate=validate.OneOf(['scheduled', 'confirmed', 'completed', 'cancelled']),
        default='scheduled'
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('date')
    def validate_date(self, value):
        """Validate appointment date is in the future"""
        if value <= datetime.now():
            raise ValidationError('Appointment date must be in the future')