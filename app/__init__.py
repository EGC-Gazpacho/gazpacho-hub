import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
from core.configuration.configuration import get_app_version
from core.managers.module_manager import ModuleManager
from core.managers.config_manager import ConfigManager
from core.managers.error_handler_manager import ErrorHandlerManager
from core.managers.logging_manager import LoggingManager

# Load environment variables
load_dotenv()

# Create the instances
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()  # Instancia para Flask-Mail


def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration according to environment
    config_manager = ConfigManager(app)
    config_manager.load_config(config_name=config_name)

    # Initialize SQLAlchemy and Migrate with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))  # Asegúrate de convertir a entero
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'  # Convierte el valor a booleano
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Correo electrónico del remitente
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Contrasena o token de la cuenta de correo
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'romerito3rubn@gmail.com')  # Remitente
    app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5000')  # URL base para generar enlaces

    mail.init_app(app)  # Inicializa Flask-Mail

    # Register modules
    module_manager = ModuleManager(app)
    module_manager.register_modules()

    # Register login manager
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.modules.auth.models import User
        return User.query.get(int(user_id))

    # Set up logging
    logging_manager = LoggingManager(app)
    logging_manager.setup_logging()

    # Initialize error handler manager
    error_handler_manager = ErrorHandlerManager(app)
    error_handler_manager.register_error_handlers()

    # Injecting environment variables into jinja context
    @app.context_processor
    def inject_vars_into_jinja():
        return {
            'FLASK_APP_NAME': os.getenv('FLASK_APP_NAME'),
            'FLASK_ENV': os.getenv('FLASK_ENV'),
            'DOMAIN': os.getenv('DOMAIN', 'localhost'),
            'APP_VERSION': get_app_version()
        }

    return app


app = create_app()
