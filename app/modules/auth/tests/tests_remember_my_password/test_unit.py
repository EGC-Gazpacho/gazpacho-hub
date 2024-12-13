import pytest
from unittest.mock import patch
from app.modules.auth.services import AuthenticationService
from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from flask import Flask


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'testsecretkey'
    app.config['BASE_URL'] = 'http://localhost'  # Asegúrate de incluir la base URL para la recuperación
    return app


@pytest.fixture
def auth_service(app):
    # Creamos el servicio usando la app, pero no necesitamos acceder a app a través de auth_service
    return AuthenticationService()


@pytest.fixture
def mock_get_by_email():
    # Mock de la función get_by_email del repositorio de usuarios
    with patch.object(UserRepository, 'get_by_email') as mock:
        yield mock


@pytest.fixture
def mock_send_email():
    # Mock para enviar el correo electrónico
    with patch.object(AuthenticationService, 'send_recovery_email') as mock:
        yield mock


def test_login_fail(app, auth_service, mock_get_by_email):
    mock_get_by_email.return_value = None
    with app.app_context():
        result = auth_service.login("test@example.com", "wrongpassword")
    assert result is False


def test_is_email_available(app, auth_service, mock_get_by_email):
    mock_get_by_email.return_value = None  # Simula que el email no está registrado
    with app.app_context():
        result = auth_service.is_email_available("test@example.com")
    assert result is True

    mock_get_by_email.return_value = User(id=1, email="test@example.com", password="password")
    with app.app_context():  # Asegúrate de que el contexto esté activado
        result = auth_service.is_email_available("test@example.com")
    assert result is False


def test_generate_recovery_token(app, auth_service):
    user = User(id=1, email="test@example.com", password="password")
    with app.app_context():
        token = auth_service.generate_recovery_token(user)
    assert token is not None  # Verifica que el token es generado


def test_verify_recovery_token(app, auth_service):
    user = User(id=1, email="test@example.com", password="password")
    with app.app_context():
        token = auth_service.generate_recovery_token(user)
        user_id = auth_service.verify_recovery_token(token)
    assert user_id == user.id  # Verifica que el token es válido


def test_send_recovery_email_success(app, auth_service, mock_send_email):
    token = "fake_token"
    email = "test@example.com"
    with app.app_context():
        mock_send_email.return_value = True
        result = auth_service.send_recovery_email(email, token)
    assert result is True  # Verifica que el correo se envió correctamente


def test_send_recovery_email_fail(app, auth_service, mock_send_email):
    token = "fake_token"
    email = "test@example.com"
    with app.app_context():
        mock_send_email.side_effect = Exception("Email sending failed")
        with pytest.raises(Exception):
            auth_service.send_recovery_email(email, token)  # Verifica que la excepción es lanzada
