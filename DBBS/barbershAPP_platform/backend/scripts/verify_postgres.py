import subprocess
import logging
import sys
import ctypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def verify_postgres():
    if not is_admin():
        logger.error("❌ Script must be run as administrator")
        if sys.executable:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        return False

    try:
        # Check service status
        status = subprocess.run(
            ['sc', 'query', 'postgresql-x64-17'], 
            capture_output=True, 
            text=True
        )
        
        if "RUNNING" not in status.stdout:
            logger.info("Starting PostgreSQL service...")
            subprocess.run(['sc', 'start', 'postgresql-x64-17'], check=True)
            logger.info("✅ PostgreSQL service started")
        else:
            logger.info("✅ PostgreSQL service is already running")
        
        # Verify connection
        import psycopg2
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        conn.close()
        logger.info("✅ PostgreSQL connection verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service verification failed: {str(e)}")
        return False

if __name__ == '__main__':
    verify_postgres()