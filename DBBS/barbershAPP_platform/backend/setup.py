from typing import List
from setuptools import setup, find_packages # type: ignore

def get_requirements() -> List[str]:
    return [
        "flask>=2.0.0",
        "flask-sqlalchemy>=3.0.0",
        "flask-migrate>=4.0.0",
        "flask-cors>=4.0.0",
        "flask-jwt-extended>=4.0.0",
        "flask-redis>=0.4.0",
        "celery>=5.0.0",
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=1.0.0",
        "geoalchemy2>=0.13.0",
        "redis>=4.0.0",
        "twilio==8.0.0",
        "geojson==3.0.1",  # Fixed geojson version
        "arcgis>=2.0.0"    
    ]

if __name__ == '__main__':
    setup(
        name="barbershAPP_platform",
        version="0.1",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        python_requires=">=3.9",
        install_requires=get_requirements(),
        include_package_data=True
    )