from flask import Blueprint, jsonify, request
from datetime import datetime
from src.utils.auth_decorator import require_auth
from src.models.appointment import Appointment
from src.database.db import db
from src.services.Mail import MailService
from src.schemas.appointment import AppointmentSchema #type: ignore
from marshmallow import ValidationError #type: ignore
import logging

logger = logging.getLogger(__name__)
appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments', methods=['GET'])
@require_auth
def get_appointments():
    """Get all appointments for the authenticated user"""
    try:
        user_id = request.user.get('id')
        appointments = Appointment.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'appointments': [apt.to_dict() for apt in appointments]
        })
    except Exception as e:
        logger.error(f"Error fetching appointments: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch appointments'}), 500

@appointments_bp.route('/appointments', methods=['POST'])
@require_auth
def create_appointment():
    """Create a new appointment"""
    try:
        data = request.get_json()
        schema = AppointmentSchema()
        
        # Validate request data
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'messages': err.messages
            }), 400

        # Create new appointment
        new_appointment = Appointment(
            user_id=request.user.get('id'),
            shop_id=validated_data['shop_id'],
            service=validated_data['service'],
            date=datetime.fromisoformat(validated_data['date'])
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        # Send confirmation email
        try:
            MailService.send_appointment_confirmation(
                email=request.user.get('email'),
                appointment_details={
                    'name': request.user.get('name'),
                    'date': new_appointment.date.strftime('%Y-%m-%d'),
                    'time': new_appointment.date.strftime('%H:%M'),
                    'service': new_appointment.service,
                    'shop': new_appointment.shop.name
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send confirmation email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Appointment created successfully',
            'appointment': new_appointment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating appointment: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create appointment'}), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@require_auth
def update_appointment(appointment_id):
    """Update an existing appointment"""
    try:
        user_id = request.user.get('id')
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=user_id).first()
        
        if not appointment:
            return jsonify({
                'success': False,
                'error': 'Appointment not found or unauthorized'
            }), 404
        
        data = request.get_json()
        schema = AppointmentSchema(partial=True)
        
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'messages': err.messages
            }), 400
            
        if 'date' in validated_data:
            appointment.date = datetime.fromisoformat(validated_data['date'])
        if 'service' in validated_data:
            appointment.service = validated_data['service']
        if 'status' in validated_data:
            appointment.status = validated_data['status']
            
        db.session.commit()
        
        # Send update notification
        try:
            MailService.send_appointment_update(
                email=request.user.get('email'),
                appointment_details={
                    'name': request.user.get('name'),
                    'date': appointment.date.strftime('%Y-%m-%d'),
                    'time': appointment.date.strftime('%H:%M'),
                    'service': appointment.service,
                    'shop': appointment.shop.name,
                    'status': appointment.status
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send update email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating appointment: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update appointment'}), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@require_auth
def cancel_appointment(appointment_id):
    """Cancel an existing appointment"""
    try:
        user_id = request.user.get('id')
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=user_id).first()
        
        if not appointment:
            return jsonify({
                'success': False,
                'error': 'Appointment not found or unauthorized'
            }), 404
            
        appointment.status = 'cancelled'
        db.session.commit()
        
        # Send cancellation notification
        try:
            MailService.send_appointment_cancellation(
                email=request.user.get('email'),
                appointment_details={
                    'name': request.user.get('name'),
                    'date': appointment.date.strftime('%Y-%m-%d'),
                    'time': appointment.date.strftime('%H:%M'),
                    'service': appointment.service,
                    'shop': appointment.shop.name
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send cancellation email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cancelling appointment: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to cancel appointment'}), 500