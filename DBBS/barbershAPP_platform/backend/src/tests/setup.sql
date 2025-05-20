"""Initial schema

Revision ID: initial
Create Date: 2024-05-14
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

def upgrade() -> None:
    # Create barbershops table
    op.create_table(
        'barbershops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('location', Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables
CREATE TABLE IF NOT EXISTS barbershops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    location GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS barbers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    barbershop_id INTEGER REFERENCES barbershops(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    barber_id INTEGER REFERENCES barbers(id) ON DELETE CASCADE,
    barbershop_id INTEGER REFERENCES barbershops(id) ON DELETE CASCADE,
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255),
    client_phone VARCHAR(20),
    appointment_datetime TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS queues (
    id SERIAL PRIMARY KEY,
    barber_id INTEGER REFERENCES barbers(id) ON DELETE CASCADE,
    barbershop_id INTEGER REFERENCES barbershops(id) ON DELETE CASCADE,
    queue_size INTEGER DEFAULT 0,
    estimated_wait_time INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS availability (
    id SERIAL PRIMARY KEY,
    barber_id INTEGER REFERENCES barbers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_barbershop_location ON barbershops USING GIST (location);
CREATE INDEX idx_barber_shop ON barbers(barbershop_id);
CREATE INDEX idx_appointment_datetime ON appointments(appointment_datetime);
CREATE INDEX idx_queue_shop ON queues(barbershop_id);
CREATE INDEX idx_availability_date ON availability(date);