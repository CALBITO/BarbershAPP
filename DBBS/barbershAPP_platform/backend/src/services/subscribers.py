from firebase_admin import firestore #type: ignore
from typing import List, Dict

async def get_barber_subscribers(barber_id: str) -> List[Dict]:
    """Get all subscribers for a barber"""
    db = firestore.client()
    subscribers_ref = db.collection('subscriptions')\
                       .where('barber_id', '==', barber_id)\
                       .where('active', '==', True)
    
    subscribers = []
    async for doc in subscribers_ref.stream():
        subscriber_data = doc.to_dict()
        user_ref = db.collection('users').document(subscriber_data['user_id'])
        user_data = (await user_ref.get()).to_dict()
        
        subscribers.append({
            'token': user_data.get('fcm_token'),
            'language': user_data.get('language', 'en'),
            'user_id': subscriber_data['user_id']
        })
    
    return subscribers