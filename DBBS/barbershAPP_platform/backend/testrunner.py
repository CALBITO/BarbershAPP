import os
import sys
import pytest
from pathlib import Path

def main():
    """Run all tests with proper configuration"""
    # Add backend directory to Python path
    backend_dir = Path(__file__).parent
    sys.path.append(str(backend_dir))

    # Set environment variables
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_APP"] = "src.app:create_app()"
    
    # Run pytest with verbose output
    sys.exit(pytest.main(["-v", "tests"]))

if __name__ == "__main__":
    main()