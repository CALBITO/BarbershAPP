import subprocess
import logging
import os
import ctypes
from pathlib import Path
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_as_admin():
    """Re-run the script with admin privileges if needed"""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        logger.info("🔄 Requesting administrator privileges...")
        script = os.path.abspath(__file__)
        params = ' '.join(sys.argv[1:])
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        if ret > 32:
            logger.info("✅ Successfully elevated privileges")
            sys.exit(0)
        else:
            logger.error("❌ Failed to elevate privileges")
            sys.exit(1)

if __name__ == '__main__':
    run_as_admin()
    
def is_admin():
    """Check if script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def reset_postgres_password():
    if not is_admin():
        logger.error("❌ Script must be run as administrator")
        if sys.executable:
            # Re-run the script with admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, __file__, None, 1
            )
        return False

    try:
        # Use SC command instead of NET
        subprocess.run(['sc', 'stop', 'postgresql-x64-17'], check=True)
        
        pg_data = Path('C:/Program Files/PostgreSQL/17/data')
        if not pg_data.exists():
            logger.error(f"❌ PostgreSQL data directory not found at {pg_data}")
            return False
            
        pg_hba = pg_data / 'pg_hba.conf'
        backup_path = pg_data / 'pg_hba.conf.bak'
        
        # Backup existing config
        if pg_hba.exists():
            os.replace(pg_hba, backup_path)
        
        # Create temporary trust config
        with open(pg_hba, 'w') as f:
            f.write("""# TYPE  DATABASE        USER            ADDRESS     METHOD
local   all             postgres                     trust
host    all             all             127.0.0.1/32     trust
host    all             all             ::1/128          trust""")
        
        # Start service
        subprocess.run(['sc', 'start', 'postgresql-x64-17'], check=True)
        
        # Wait for service to start
        import time
        time.sleep(5)
        
        # Set new password
        new_password = 'postgres123'
        try:
            subprocess.run([
                'psql',
                '-U', 'postgres',
                '-d', 'postgres',
                '-c', f"ALTER USER postgres WITH PASSWORD '{new_password}';",
                '-h', 'localhost'
            ], check=True)
            logger.info(f"✅ Password reset successful. New password: {new_password}")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to set password. Make sure psql is in your PATH")
            return False
            
        # Restore original config
        if backup_path.exists():
            os.replace(backup_path, pg_hba)
            
        # Restart service
        subprocess.run(['sc', 'stop', 'postgresql-x64-17'], check=True)
        time.sleep(2)
        subprocess.run(['sc', 'start', 'postgresql-x64-17'], check=True)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Password reset failed: {str(e)}")
        return False

if __name__ == '__main__':
    reset_postgres_password()