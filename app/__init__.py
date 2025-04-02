from flask import Flask
from flask_migrate import Migrate
from .config import Config
from .database import db

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register CLI commands
    from .cli import init_db_command, seed_countries_command
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_countries_command)
    
    # Register blueprints
    from .routes import routes
    app.register_blueprint(routes)
    
    return app