import click
from flask.cli import with_appcontext
from scripts.seed_data import seed_database

@click.group()
def db_cli():
    """Database management commands."""
    pass

@db_cli.command('seed')
@with_appcontext
def seed_db():
    """Seed the database with initial barbershop data."""
    if seed_database():
        click.echo('✅ Database seeded successfully')
    else:
        click.echo('❌ Error seeding database')