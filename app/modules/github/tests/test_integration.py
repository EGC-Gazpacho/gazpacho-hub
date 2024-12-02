import os
import pytest
from app import create_app, db
from app.modules.github.services import GitHubService
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def app():
    app = create_app()  # Suponiendo que tienes una función create_app que crea la aplicación
    with app.app_context():
        db.drop_all()  # Limpiar la base de datos antes de las pruebas
        db.create_all()  # Esto creará todas las tablas necesarias
    yield app
    # Limpiar la base de datos después de las pruebas si es necesario
    with app.app_context():
        db.drop_all()  # Limpiar la base de datos


@pytest.fixture(scope="module")
def test_client(app):
    """
    Extiende la fixture test_client para agregar datos adicionales específicos para las pruebas del módulo.
    """
    with app.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield app.test_client()


class TestGitHubIntegration:

    @pytest.fixture(autouse=True)
    def setUp(self, test_client):
        self.token = os.getenv("UPLOAD_TOKEN_GITHUB")  # Obtener el token desde la variable de entorno
        self.repo_owner = "rafduqcol"  
        self.repo_name = "uvl_repo_tests"  
        self.github_api_url = "https://api.github.com/user/repos"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Content-Type": "application/json"
        }

    # # Test for successful repository creation
    def test_create_repo(self, test_client):
        result = GitHubService.create_repo(self.repo_name, self.token)
        assert result is True, "Failed to create repository"  
        
    # Test for failed repository creation
    def test_create_repo_fail(self, test_client):
        result = GitHubService.create_repo(self.repo_name, "invalid_token")
        assert result is False, "Failed to create repository"
        
    # Test to check if the repository exists
    def test_check_repository_exists_found(self, test_client):
        result = GitHubService.check_repository_exists(self.repo_owner, self.repo_name, self.token)
        assert result, "Repository should exist"

    # Test to check if the repository does not exist
    def test_check_repository_exists_not_found(self, test_client):
        result = GitHubService.check_repository_exists(self.repo_owner, 'nonexistent_repo', self.token)
        assert not result, "Repository should not exist"




            
            
            
        
        
        
        
        
        
        
        
        
        
        

    # def test_delete_repo(self, test_client):
    #     result = GitHubService.delete_repo(self.token, self.repo_owner, "uvl_repo_tests")
