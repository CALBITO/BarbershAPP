import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _pool = None

    @classmethod
    def init_pool(cls, min_conn=1, max_conn=10):
        """Initialize the connection pool"""
        try:
            cls._pool = SimpleConnectionPool(
                min_conn,
                max_conn,
                dbname=os.getenv('DB_NAME', 'barbershop_db'),
                user=os.getenv('DB_USER', 'CALBITO33'),
                password=os.getenv('DB_PASSWORD', 'N8t3rdvZn'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
            logger.info("✅ Database pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize pool: {e}")
            raise

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Get a connection from the pool"""
        if not cls._pool:
            cls.init_pool()
        
        conn = cls._pool.getconn()
        try:
            yield conn
        finally:
            cls._pool.putconn(conn)