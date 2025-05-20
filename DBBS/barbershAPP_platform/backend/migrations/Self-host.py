import os
import subprocess
from datetime import datetime

def backup_and_migrate():
    """Backup current DB and migrate to new system"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Backup current database
    backup_file = f'backup_{timestamp}.sql'
    subprocess.run([
        'pg_dump',
        '-h', 'localhost',
        '-U', 'calbito',
        '-d', 'barbershop_db',
        '-f', backup_file
    ])
    
    # Can be used later to migrate to self-hosted if needed
    return backup_file

if __name__ == '__main__':
    backup_and_migrate()