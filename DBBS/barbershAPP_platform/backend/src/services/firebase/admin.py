from firebase_admin import auth, firestore  # type: ignore
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class FirebaseAdmin:
    def __init__(self):
        self.db = firestore.client()

    async def create_barber_account(self, email: str, phone: str, shop_id: str) -> Dict:
        """Create a new barber account"""
        try:
            user = auth.create_user(
                email=email,
                phone_number=phone,
                email_verified=False
            )

            await self.db.collection('users').document(user.uid).set({
                'role': 'barber',
                'shop_id': shop_id,
                'created_at': firestore.SERVER_TIMESTAMP,
                'active': True
            })

            return {'uid': user.uid, 'status': 'created'}
        except Exception as e:
            logger.error(f"Error creating barber account: {e}")
            raise

    async def update_shop_status(self, shop_id: str, is_open: bool) -> bool:
        """Update shop operating status"""
        try:
            await self.db.collection('shops').document(shop_id).update({
                'is_open': is_open,
                'last_updated': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            logger.error(f"Error updating shop status: {e}")
            return False