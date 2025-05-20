from flask import Blueprint, request, jsonify
from src.services.firebase.storage import FirebaseStorageService
from src.services.firebase.storage_paths import StoragePaths
from src.middleware.firebase_auth import require_firebase_auth

images_bp = Blueprint('images', __name__)
storage_service = FirebaseStorageService.get_instance()

@images_bp.route('/upload/profile', methods=['POST'])
@require_firebase_auth
def upload_profile_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
        
    file = request.files['image']
    user_id = request.user['uid']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    url = storage_service.upload_image(
        folder=StoragePaths.PROFILES,
        user_id=user_id,
        file_data=file.read(),
        content_type=file.content_type,
        original_filename=file.filename
    )
    
    if url:
        return jsonify({'url': url}), 200
    return jsonify({'error': 'Upload failed'}), 500