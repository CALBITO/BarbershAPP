import pytest
from datetime import datetime, timedelta
from src.models import Appointment, Barbershop, User
from src.database.db import db


@pytest.fixture(scope='function')
def test_user(app, session):
    """Create a test user"""
    with app.app_context():
        user = User(
            email="test@example.com",
            username="testuser",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()

def test_create_booking(app, client, session, test_user, test_shop):
    """Test creating a new booking"""
    with app.app_context():
        appointment_data = {
            'barbershop_id': test_shop.id,
            'service': 'haircut',
            'appointment_datetime': (datetime.now() + timedelta(days=1)).isoformat(),
            'notes': 'Test booking'
        }
        
        response = client.post(
            '/api/v1/appointments',
            json=appointment_data,
            headers={'Authorization': f'Bearer {test_user.generate_token()}'}
        )
        
        assert response.status_code == 201

@pytest.fixture(scope='function')
def test_shop(app, session):
    """Create a test barbershop"""
    with app.app_context():
        shop = Barbershop(
            name="Test Barbershop",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            latitude=42.3601,
            longitude=-71.0589,
            phone="555-0123",
            email="shop@test.com"
        )
        session.add(shop)
        session.commit()
        yield shop
        session.delete(shop)
        session.commit()

@pytest.fixture(scope='function')
def test_appointment(app, session, test_user, test_shop):
    """Create a test appointment"""
    with app.app_context():
        appointment = Appointment(
            user_id=test_user.id,
            barbershop_id=test_shop.id,
            service='haircut',
            appointment_datetime=datetime.now() + timedelta(days=1),
            status='scheduled'
        )
        session.add(appointment)
        session.commit()
        yield appointment
        session.delete(appointment)
        session.commit()

def test_get_appointments(app, client, test_user, test_appointment):
    """Test retrieving user appointments"""
    with app.app_context():
        response = client.get(
            '/api/v1/appointments',
            headers={'Authorization': f'Bearer {test_user.generate_token()}'}
        )
        
        assert response.status_code == 200
        assert 'appointments' in response.json
        assert len(response.json['appointments']) > 0
        assert response.json['appointments'][0]['id'] == test_appointment.id

def test_cancel_appointment(app, client, test_user, test_appointment):
    """Test canceling an appointment"""
    with app.app_context():
        response = client.delete(
            f'/api/v1/appointments/{test_appointment.id}',
            headers={'Authorization': f'Bearer {test_user.generate_token()}'}
        )
        
        assert response.status_code == 200
        assert response.json['success'] is True
        
        # Verify appointment status is updated
        canceled_appointment = Appointment.query.get(test_appointment.id)
        assert canceled_appointment.status == 'canceled'

def test_invalid_booking_date(app, client, test_user, test_shop):
    """Test booking validation for invalid dates"""
    with app.app_context():
        appointment_data = {
            'barbershop_id': test_shop.id,
            'service': 'haircut',
            'appointment_datetime': datetime.now().isoformat(),  # Same day booking
            'notes': 'Test booking'
        }
        
        response = client.post(
            '/api/v1/appointments',
            json=appointment_data,
            headers={'Authorization': f'Bearer {test_user.generate_token()}'}
        )
        
        assert response.status_code == 400
        assert response.json['success'] is False
        assert 'error' in response.json
        assert 'appointment date' in response.json['error'].lower()

def test_double_booking(app, client, test_user, test_shop, test_appointment):
    """Test prevention of double booking"""
    with app.app_context():
        # Try to book at the same time
        appointment_data = {
            'barbershop_id': test_shop.id,
            'service': 'haircut',
            'appointment_datetime': test_appointment.appointment_datetime.isoformat(),
            'notes': 'Double booking attempt'
        }
        
        response = client.post(
            '/api/v1/appointments',
            json=appointment_data,
            headers={'Authorization': f'Bearer {test_user.generate_token()}'}
        )
        
        assert response.status_code == 409
        assert response.json['success'] is False
        assert 'conflict' in response.json['error'].lower()