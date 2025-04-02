import click
from .database import db
from .services.country_data import seed_countries

@click.command('seed-countries')
def seed_countries_command():
    """Seed countries from external API"""
    from . import create_app
    app = create_app()
    
    with app.app_context():
        if seed_countries():
            click.echo("Successfully seeded countries")
        else:
            click.echo("Failed to seed countries")

@click.command('init-db')
def init_db_command():
    """Initialize the database"""
    from . import create_app
    app = create_app()
    
    with app.app_context():
        db.create_all()
        click.echo("Initialized the database")