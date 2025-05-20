from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from flask import current_app
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger('alembic.env')

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models for 'autogenerate' support
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import *  # Import all models
from database.db import db

# Set target metadata for autogenerate support
target_metadata = db.metadata

def get_url() -> str:
    """Get database URL from environment or fall back to default"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/barbershop_dev"
    )

def include_object(object, name, type_, reflected, compare_to):
    """Filter objects to include in autogeneration"""
    # Exclude specific tables if needed
    excluded_tables = ['spatial_ref_sys']  # PostGIS table
    if type_ == "table" and name in excluded_tables:
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
            compare_server_default=True
        )

        with context.begin_transaction():
            try:
                context.run_migrations()
                logger.info("Migrations completed successfully")
            except Exception as e:
                logger.error(f"Error during migration: {e}")
                raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()