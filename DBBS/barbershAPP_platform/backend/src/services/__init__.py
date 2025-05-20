from .tasks import QueueService
from .integration import IntegrationService
from .GISService import GISService

# Create service instances without immediate initialization
queue_service = QueueService()
gis_service = GISService()
integration_service = IntegrationService()

def init_services(app):
    """Initialize all services with app context"""
    queue_service.init_app(app)
    gis_service.init_app(app)
    integration_service.init_app(app)

__all__ = [
    'queue_service',
    'gis_service', 
    'integration_service',
    'init_services'
]