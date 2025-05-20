from firebase_admin import firestore # type: ignore
from typing import Callable, Dict, Any
import logging
import asyncio

logger = logging.getLogger(__name__)

class FirebaseListeners:
    def __init__(self):
        self.db = firestore.client()
        self._watch_refs = {}

    async def watch_queue_changes(self, shop_id: str, callback: Callable[[Dict[str, Any]], None]):
        """Watch for queue changes in a shop"""
        doc_ref = self.db.collection('shops').document(shop_id)
        
        def on_snapshot(doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                try:
                    data = doc.to_dict()
                    asyncio.create_task(callback(data))
                except Exception as e:
                    logger.error(f"Error processing queue update: {e}")

        self._watch_refs[shop_id] = doc_ref.on_snapshot(on_snapshot)

    async def stop_watching(self, shop_id: str):
        """Stop watching a specific shop's queue"""
        if shop_id in self._watch_refs:
            self._watch_refs[shop_id].unsubscribe()
            del self._watch_refs[shop_id]