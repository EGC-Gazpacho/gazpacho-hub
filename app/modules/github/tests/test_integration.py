import pytest
import os
from app.modules.github.services import GitHubService
from app.modules.github.repositories import GitHubRepository
from app import create_app


@pytest.fixture(scope='module')
def github_service():
    repo = GitHubRepository(name="my_repo", owner="my_user")
    return GitHubService(repository=repo)


class TestGitHubService:

    @pytest.fixture(autouse=True)
    def github_setup(self):
        self.token = os.getenv("GITHUB_TOKEN")

        app = create_app()

        with app.app_context():

            self.invalid_token = "invalid_token"
            self.repo_owner = "rafduqcol"
            self.repo_name = "uvl_repo_tests"
            self.branch = "main"
            self.commit_message = "Test commit"
            self.license = "MIT"

    # Test to check if repository creation fails with an invalid token
    def test_create_repo_fail(self, github_service):   
        result = github_service.create_repo(self.repo_name, self.invalid_token)
        assert not result, "La creación del repositorio debería haber fallado"

    # Test to check if repository creation succeeds with a valid token
    def test_create_repo_success(self, github_service):
        result = github_service.create_repo(self.repo_name, self.token)
        assert result, "La creación del repositorio debería haber tenido éxito"

    # Test to check if the repository exists
    def test_check_repository_exists_found(self, github_service):
        result = github_service.check_repository_exists(self.repo_owner, self.repo_name, self.token)
        assert result, "El repositorio debería existir"

    # Test to check if the repository does not exist
    def test_check_repository_exists_not_found(self, github_service):
        result = github_service.check_repository_exists("no_exists", self.repo_name, self.token)
        assert not result, "El repositorio no debería existir"

    # Test to check if deleting a repository fails with an invalid token
    def test_delete_repo_fail(self, github_service):
        result = github_service.delete_repo(self.invalid_token, self.repo_owner, self.repo_name)
        assert not result, "La eliminación del repositorio debería haber fallado"

    # Test to check if deleting a repository succeeds with a valid token
    def test_delete_repo_success(self, github_service):
        result = github_service.delete_repo(self.token, self.repo_owner, self.repo_name)
        assert result == ('Repository deleted successfully',
                          204), "La eliminación del repositorio debería haber tenido éxito"
