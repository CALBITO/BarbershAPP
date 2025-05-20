import requests
from src.models import Barbershop
from flask import current_app
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class IntegrationService:
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.config = {}

    def init_app(self, app):
        """Initialize service with Flask app config"""
        self.base_url = self.base_url or app.config.get('API_BASE_URL')
        self.config = {
            'timeout': app.config.get('API_TIMEOUT', 30),
            'retry_attempts': app.config.get('API_RETRY_ATTEMPTS', 3)
        }
    @staticmethod
    def fetch_barbershop_data(api_url: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Fetch barbershop data from external API."""
        try:
            response = requests.get(api_url, params=params)
            return response.json() if response.ok else None
        except Exception as e:
            current_app.logger.error(f"API request failed: {e}")
            return None

    def sync_barbershop_data(self) -> bool:
        """Synchronize barbershop data from external API to local database."""
        try:
            data = self.fetch_barbershop_data(f"{self.base_url}/barbershops", {})
            if data:
                for shop_data in data:
                    shop = Barbershop.query.filter_by(external_id=shop_data['id']).first()
                    if not shop:
                        shop = Barbershop()
                    shop.update_from_dict(shop_data)
                current_app.db.session.commit()
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error syncing barbershop data: {e}")
            return False

__all__ = ['IntegrationService', 'QueueService', 'celery']