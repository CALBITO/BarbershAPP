from flask import Blueprint, jsonify, current_app
from src.database import get_session
from redis import Redis
import logging
from datetime import datetime
from src.config import RedisConfig

# Configure logging
logger = logging.getLogger(__name__)
health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check endpoint"""
    start_time = datetime.utcnow()
    
    # Get component status
    db_status = check_database()
    redis_status = check_redis()
    
    health_status = {
        "status": "healthy",
        "timestamp": start_time.isoformat(),
        "components": {
            "database": db_status,
            "redis": redis_status
        },
        "version": "0.1.0"
    }
    
    # Check if any component is in error state
    components = health_status["components"]
    if any(components[k].get("status") == "error" for k in components):
        health_status["status"] = "degraded"
        status_code = 503
    else:
        status_code = 200
    
    # Add response time
    health_status["response_time_ms"] = round(
        (datetime.utcnow() - start_time).total_seconds() * 1000, 2
    )
    
    return jsonify(health_status), status_code

def check_database():
    """Check database connectivity"""
    try:
        session = get_session()
        session.execute('SELECT 1')
        session.commit()
        logger.info("Database health check passed")
        return {
            "status": "connected",
            "type": "postgresql",
            "connection": "postgresql://***@" + current_app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1]
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "error", "type": "postgresql", "error": str(e)}

def check_redis():
    """Check Redis connectivity"""
    try:
        redis = Redis(**RedisConfig.REDIS_CONFIG)
        redis.ping()
        redis_info = redis.info()
        logger.info("Redis health check passed")
        return {
            "status": "connected",
            "host": RedisConfig.REDIS_CONFIG['host'],
            "port": RedisConfig.REDIS_CONFIG['port'],
            "version": redis_info.get('redis_version'),
            "memory_used": f"{redis_info.get('used_memory_human', '0B')}"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {"status": "error", "error": str(e)}