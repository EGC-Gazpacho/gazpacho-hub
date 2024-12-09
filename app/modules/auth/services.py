import os
import jwt
from datetime import datetime, timedelta
from flask import current_app
from flask_login import login_user, current_user
from flask_mail import Message
from app import mail

from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.profile.models import UserProfile
from app.modules.profile.repositories import UserProfileRepository
from core.configuration.configuration import uploads_folder_name
from core.services.BaseService import BaseService


class AuthenticationService(BaseService):
    def __init__(self):
        super().__init__(UserRepository())
        self.user_profile_repository = UserProfileRepository()

    def login(self, email, password, remember=True):
        user = self.repository.get_by_email(email)
        if user is not None and user.check_password(password):
            login_user(user, remember=remember)
            return True
        return False

    def is_email_available(self, email: str) -> bool:
        return self.repository.get_by_email(email) is None

    def create_with_profile(self, **kwargs):
        try:
            email = kwargs.pop("email", None)
            password = kwargs.pop("password", None)
            name = kwargs.pop("name", None)
            surname = kwargs.pop("surname", None)

            if not email:
                raise ValueError("Email is required.")
            if not password:
                raise ValueError("Password is required.")
            if not name:
                raise ValueError("Name is required.")
            if not surname:
                raise ValueError("Surname is required.")

            user_data = {
                "email": email,
                "password": password
            }

            profile_data = {
                "name": name,
                "surname": surname,
            }

            user = self.create(commit=False, **user_data)
            profile_data["user_id"] = user.id
            self.user_profile_repository.create(**profile_data)
            self.repository.session.commit()
        except Exception as exc:
            self.repository.session.rollback()
            raise exc
        return user

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updated_instance = self.update(user_profile_id, **form.data)
            return updated_instance, None
        return None, form.errors

    def get_user_by_email(self, email):
        """Obtiene un usuario basado en su correo electrónico."""
        return self.repository.get_by_email(email)

    def get_authenticated_user(self) -> User | None:
        if current_user.is_authenticated:
            return current_user
        return None

    def get_authenticated_user_profile(self) -> UserProfile | None:
        if current_user.is_authenticated:
            return current_user.profile
        return None

    def temp_folder_by_user(self, user: User) -> str:
        return os.path.join(uploads_folder_name(), "temp", str(user.id))
    
    def list_users(self) -> User:
            return self.repository.get_all()

    def generate_recovery_token(self, user):
        """Genera un token de recuperación para el usuario"""
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({'user_id': user.id, 'exp': expiration}, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token

    def verify_recovery_token(self, token):
        """Verifica el token de recuperación"""
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('user_id')
            return user_id
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def update_password(self, user_id, new_password):
        """Actualiza la contrasena del usuario"""
        user = self.repository.get_by_id(user_id)
        if user:
            user.set_password(new_password)
            self.repository.session.commit()
            return True
        return False

    def send_recovery_email(self, to, token):
        """Envía un correo electrónico con el enlace de recuperacion de contrasena"""
        subject = "Recuperacion de contraseña"
        recovery_url = f"{current_app.config['BASE_URL']}/password_reset/{token}"
        body = f"Por favor, haz clic en el siguiente enlace para restablecer tu contraseña: {recovery_url}"

        msg = Message(subject=subject, recipients=[to])
        msg.body = body  # No es necesario codificarlo a UTF-8, ya lo maneja flask_mail automáticamente
        msg.charset = 'utf-8'
        print("hola3", msg.body, msg.subject)
        try:
            mail.send(msg)  # Enviar el correo
            return True  # Correo enviado correctamente
        except Exception as e:
            current_app.logger.error(f"Error al enviar correo: {str(e)}")  # Registrar error
            raise e  # Volver a lanzar el error para manejarlo en el controlador
