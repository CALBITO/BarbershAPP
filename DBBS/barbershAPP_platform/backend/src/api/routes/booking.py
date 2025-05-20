from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, time, timedelta
from src.database import db
from src.models.appointment import Appointment
from src.models.availability import Availability
from src.models.barber import Barber
from src.models.queue import Queue
from src.database.db import db
from src.services.tasks import QueueService

booking_bp = Blueprint('booking', __name__)
queue_service = QueueService()



def leave_queue(shop_id):
    return jsonify({'message': 'Left queue'})

def generate_time_slots(date):
    """Generate available time slots for a given date"""
    slots = []
    start = time(9, 0)  # 9 AM
    end = time(17, 0)   # 5 PM
    slot_duration = timedelta(minutes=30)
    
    current = datetime.combine(date, start)
    end_dt = datetime.combine(date, end)
    
    while current < end_dt:
        slots.append(current)
        current += slot_duration
    
    return slots

# ...existing code...

@booking_bp.route('/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment"""
    data = request.json
    try:
        appointment = Appointment(
            barber_id=data['barber_id'],
            barbershop_id=data['barbershop_id'],
            client_name=data['client_name'],
            client_email=data.get('client_email'),
            client_phone=data.get('client_phone'),
            appointment_datetime=datetime.fromisoformat(data['datetime']),
            status='scheduled'
        )
        db.session.add(appointment)
        db.session.commit()

        #  notification logic
        queue_service.send_notification.delay(
            appointment_id=appointment.id,
            notification_type='email' if appointment.client_email else 'sms'
        )
        
        return jsonify(appointment.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@booking_bp.route('/barbers/<int:barber_id>/available-slots', methods=['GET'])
def get_available_slots(barber_id):
    """Get available appointment slots for a barber"""
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400
        
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get barber's availability
        availability = Availability.query.filter_by(
            barber_id=barber_id,
            date=target_date,
            is_available=True
        ).first()
        
        if not availability:
            return jsonify([])
        
        # Get booked appointments
        booked_slots = Appointment.query.filter_by(
            barber_id=barber_id,
            appointment_datetime=target_date
        ).all()
        
        # Generate available slots
        all_slots = generate_time_slots(target_date)
        available_slots = [
            slot.strftime('%H:%M')
            for slot in all_slots 
            if slot not in [appt.appointment_datetime for appt in booked_slots]
        ]
        
        return jsonify(available_slots)
    except Exception as e:
        return jsonify({"error": str(e)}), 400