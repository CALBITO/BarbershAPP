from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from src.models import Barbershop, Barber, Queue 
from src.services.geo import GeoService
from src.services.tasks import QueueService
from src.database.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from src.services.GISService import GISService

# Initialize blueprints once
shop_bp = Blueprint('shop', __name__)
locations_bp = Blueprint('locations', __name__)

# Initialize services once
geo_service = GeoService()
queue_service = QueueService()
gis_service = GISService()

def init_services(app):
    """Initialize services with app configuration"""
    gis_service.init_app(app)
    if hasattr(geo_service, 'init_app'):
        geo_service.init_app(app)
    if hasattr(queue_service, 'init_app'):
        queue_service.init_app(app)

def is_local_environment():
    """Check if running in local environment"""
    return current_app.config['TESTING'] or current_app.config['DEBUG']

@shop_bp.before_request
def setup_services():
    """Configure services based on environment"""
    if is_local_environment():
        geo_service.api_key = "test-key"
        queue_service.redis_url = "memory://"
    else:
        if not gis_service.api_key:
            init_services(current_app)
        if not geo_service.api_key:
            geo_service.api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
        if not queue_service.redis_url:
            queue_service.redis_url = current_app.config.get('REDIS_URL')

@shop_bp.route('/shops', methods=['GET'])
def get_shops():
    """Get all barbershops or search by location"""
    try:
        if is_local_environment():
            shops = Barbershop.query.all()
        elif 'lat' in request.args and 'lng' in request.args:
            lat = float(request.args.get('lat'))
            lng = float(request.args.get('lng'))
            radius = float(request.args.get('radius', 5000))
            shops = geo_service.find_nearby_shops(lat, lng, radius)
        else:
            shops = Barbershop.query.all()
        return jsonify([shop.to_dict() for shop in shops])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shop_bp.route('/shops/<int:shop_id>', methods=['GET'])
def get_shop(shop_id):
    """Get details for a specific shop"""
    shop = Barbershop.query.get_or_404(shop_id)
    return jsonify(shop.to_dict())

@shop_bp.route('/shops', methods=['POST'])
@jwt_required()
def create_shop():
    """Create a new barbershop"""
    try:
        data = request.json
        shop = Barbershop(
            name=data['name'],
            address=data['address'],
            phone=data['phone'],
            location=f"POINT({data['longitude']} {data['latitude']})"
        )
        db.session.add(shop)
        db.session.commit()
        return jsonify({
            'success': True,
            'shop': shop.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

        @shop_bp.route('/shops/<int:shop_id>/queue', methods=['POST'])
        @jwt_required()
        def add_to_queue(shop_id):
            """Add a customer to the shop's queue"""
            try:
                user_id = get_jwt_identity()
                data = request.json
                barber_id = data.get('barber_id')

                # Add user to the queue
                queue_entry = queue_service.add_to_queue(shop_id, user_id, barber_id)
                return jsonify({
                    'success': True,
                    'queue_entry': queue_entry.to_dict()
                }), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @shop_bp.route('/shops/<int:shop_id>/queue', methods=['GET'])
        @jwt_required()
        def get_queue(shop_id):
            """Get the queue for a specific shop"""
            try:
                queue = queue_service.get_queue(shop_id)
                return jsonify([entry.to_dict() for entry in queue])
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @shop_bp.route('/shops/<int:shop_id>/queue/<int:queue_id>', methods=['DELETE'])
        @jwt_required()
        def remove_from_queue(shop_id, queue_id):
            """Remove a customer from the shop's queue"""
            try:
                queue_service.remove_from_queue(shop_id, queue_id)
                return jsonify({'success': True}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500