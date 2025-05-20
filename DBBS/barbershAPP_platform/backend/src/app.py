from flask import Flask, jsonify
from flask_cors import CORS
from flask_mail import Mail
from config import Mail
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from celery import Celery
from dotenv import load_dotenv
import logging
import os
from typing import Any, Optional
from src.database import db
from src.config.validator import check_config
from src.config.settings import get_config
from src.middleware.validation import validate_config
from src.db_cli import db_cli
from src.api.routes.availability import availability_bp





# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
mail = Mail()
jwt = JWTManager()

def create_celery(app: Flask) -> Celery:
    """Create and configure Celery instance"""
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions"""
    db.init_app(app)
    migrate = Migrate(app, db)  
    mail.init_app(app)
    jwt.init_app(app)
    redis_client = FlaskRedis()
    redis_client.init_app(app)
    CORS(app)

def init_services(app: Flask) -> None:
    """Initialize business services"""
    from src.services.GISService import GISService
    from src.services.tasks import queue_service
    from src.services.GISService import GISService
    from src.services.tasks import queue_service
    from src.config.firebase_config import FirebaseConfig
    
    FirebaseConfig.init_app()
    gis_service = GISService()
    gis_service.init_app(app)
    queue_service.init_app(app)

def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints"""
    from src.api.routes.booking import booking_bp
    from src.api.routes.appointments import appointments_bp
    from src.api.routes import register_routes
    
    app.register_blueprint(booking_bp, url_prefix='/api/v1/booking')
    app.register_blueprint(appointments_bp, url_prefix='/api/v1/appointments')
    register_routes(app)

def register_error_handlers(app: Flask) -> None:
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

def register_cli_commands(app: Flask) -> None:
    """Register CLI commands"""
    @app.cli.command("init-db")
    def init_db():
        """Initialize database tables"""
        from src.database import db
        with app.app_context():
            db.create_all()
            logger.info("✅ Database tables created successfully")

def create_app(config: Optional[dict] = None) -> Flask:
    app = Flask(__name__)
    CORS(app)

    env_file = '.env.prod' if os.getenv('FLASK_ENV') == 'production' else '.env'
    load_dotenv(env_file)
    
    app.config.update(
   
        
        # Simplified GIS Configuration
        GIS_QUERY_URL=os.getenv('GIS_QUERY_URL'),
        GIS_QUERY_PARAMS=os.getenv('GIS_QUERY_PARAMS'),
        GOOGLE_MAPS_API_KEY=os.getenv('GOOGLE_MAPS_API_KEY'),
        
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'dev'),
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_PORT=os.getenv('MAIL_PORT', 587),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
        CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND'),
        ARCGIS_API_KEY=os.getenv('ARCGIS_API_KEY'),
       # Redis Configuration
        REDIS_URL=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
     
    ) 
    config_class = get_config()
    app.config.from_object(config_class)
    app.config['CONFIG_CLASS'] = config_class 
    app.cli.add_command(db_cli)
    app.register_blueprint(availability_bp, url_prefix='/api')

    
    # Override config if provided
    if config:
        app.config.update(config)
        
    check_config(
        app,
        raise_on_warnings=(app.config.get('ENV') == 'production')
    )
    

    
    with app.app_context():
        # Initialize components
        init_extensions(app)
        init_services(app)
        register_blueprints(app)
        register_error_handlers(app)
        register_cli_commands(app)
        
        
        # Initialize Celery
        app.celery = create_celery(app)
    
    @app.before_request
    @validate_config
    def validate_app_config():
        pass
    
    return app

def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints"""
    from src.api.routes.booking import booking_bp
    from src.api.routes.appointments import appointments_bp
    from src.api.routes.healthcheck import health_bp  # Add this line
    from src.api.routes import register_routes
    
    # Register health check first
    app.register_blueprint(health_bp, url_prefix='/api/v1/health')
    app.register_blueprint(booking_bp, url_prefix='/api/v1/booking')
    app.register_blueprint(appointments_bp, url_prefix='/api/v1/appointments')
    register_routes(app)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)