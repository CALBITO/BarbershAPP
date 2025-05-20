from firebase_admin import firestore # type: ignore
from typing import List, Dict

class FirebaseUpdates:
    db = firestore.client()
    
    @classmethod
    async def enhance_shop_data(cls, shops: List[Dict]) -> List[Dict]:
        """Add real-time data to shop results"""
        enhanced = []
        
        for shop in shops:
            # Get real-time shop data
            shop_ref = cls.db.collection('shops').document(str(shop['id']))
            real_time_data = shop_ref.get().to_dict() or {}
            
            # Merge PostGIS and real-time data
            enhanced.append({
                **shop,
                'queue_length': real_time_data.get('queue_length', 0),
                'wait_time': real_time_data.get('estimated_wait', 0),
                'available_barbers': real_time_data.get('available_barbers', []),
                'last_updated': real_time_data.get('last_updated')
            })
        
        return enhanced