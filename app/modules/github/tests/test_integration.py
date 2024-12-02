import os
from unittest.mock import MagicMock
import pytest
from app import create_app, db
from app.modules.github.services import GitHubService
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


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
        self.branch = "main"
        self.commit_message = "Test commit"
        self.license = "MIT"
        
        self.dataset = MagicMock()
        self.dataset.name.return_value = "test_dataset"
        self.dataset.feature_models = [MagicMock(files=[MagicMock(get_path=lambda: 'test_file.txt', name='test_file.txt')])]
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
        
    # Test without successful repository creation
    def test_upload_dataset_to_github_fail(self, test_client):
        result_message, status_code  = GitHubService.upload_dataset_to_github(
            self.repo_owner,
            self.repo_name,
            'main',
            self.dataset, 
            "invalid_token", 
            self.commit_message,
            self.license,
            "existing"
            
        )
        print("holaaa", status_code)
        assert status_code == 404, f"Expected status code 404, but got {status_code}"



    # Test for successful repository creation
    def test_upload_dataset_to_github(self, test_client):
        result_message, status_code  = GitHubService.upload_dataset_to_github(
            self.repo_owner,
            self.repo_name,
            'main',
            self.dataset, 
            self.token, 
            self.commit_message,
            self.license,
            "existing"
            
        )
        assert status_code == 201, f"Expected status code 201, but got {status_code}"
        GitHubService.delete_repo(self.token, self.repo_owner, self.repo_name)
        
    # Test to check if the branch exists
    def test_check_branch_exists_found(self, test_client):
        result = GitHubService.check_branch_exists(self.repo_owner, self.repo_name, 'main', self.token)
        assert result, "Branch should exist"

    # Test to check if the branch does not exist
    def test_check_branch_exists_not_found(self, test_client):
        result = GitHubService.check_branch_exists(self.repo_owner, self.repo_name, 'nonexistent_branch', self.token)
        assert not result, "Branch should not exist"

    


                
            
            
        
        
        
        
        
        
        
        
        
        
        

    def test_delete_repo(self, test_client):
        result = GitHubService.delete_repo(self.token, self.repo_owner, "uvl_repo_tests")
