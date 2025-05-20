from flask import Blueprint, request, jsonify
from src.firebase.admin import FirebaseAdmin #type: ignore
from src.services.firebase.listeners import FirebaseListeners, firestore
from src.middleware.firebase_auth import require_firebase_auth
import logging

logger = logging.getLogger(__name__)
queue_bp = Blueprint('queue', __name__)
admin = FirebaseAdmin()
listeners = FirebaseListeners()

@queue_bp.route('/queue/<shop_id>/join', methods=['POST'])
@require_firebase_auth
async def join_queue():
    """Add client to shop queue"""
    try:
        shop_id = request.view_args['shop_id']
        user_id = request.user['uid']
        
        queue_ref = admin.db.collection('queues').document(shop_id)
        queue_data = queue_ref.get().to_dict() or {'waiting': []}
        
        position = len(queue_data['waiting']) + 1
        
        await queue_ref.update({
            'waiting': firestore.ArrayUnion([{
                'user_id': user_id,
                'joined_at': firestore.SERVER_TIMESTAMP,
                'position': position
            }])
        })
        
        return jsonify({'position': position}), 200
    except Exception as e:
        logger.error(f"Error joining queue: {e}")
        return jsonify({'error': str(e)}), 500