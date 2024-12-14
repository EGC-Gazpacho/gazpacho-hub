import pytest
import os
from app.modules.github.services import GitHubService
from app.modules.github.repositories import GitHubRepository
from app import create_app


@pytest.fixture(scope='module')
def github_service():
    """
    Provide a GitHubService instance with a mocked repository for testing.
    """
    repo = GitHubRepository(name="my_repo", owner="my_user")
    return GitHubService(repository=repo)


class TestGitHubService:
    @pytest.fixture(autouse=True)
    def github_setup(self):
        """
        Automatically set up shared test configurations before each test.
        """
        self.token = os.getenv("GITHUB_TOKEN")
        self.invalid_token = "invalid_token"
        self.repo_owner = "rafduqcol"
        self.repo_name = "uvl_repo_tests"
        self.branch = "main"
        self.commit_message = "Test commit"
        self.license = "MIT"

    @pytest.fixture(scope='module')
    def app_context(self):
        """
        Provide app context for tests requiring Flask app initialization.
        """
        app = create_app()
        with app.app_context():
            yield app

    @pytest.fixture(scope='function', autouse=True)
    def cleanup_repository(self, github_service):
        """
        Clean up the repository after each test to avoid interference.
        """
        yield
        try:
            github_service.delete_repo(self.token, self.repo_owner, self.repo_name)
        except Exception:
            pass  # Ignore cleanup failures if the repo doesn't exist

    @pytest.fixture(scope="session", autouse=True)
    def increase_recursion_limit(self):
        """
        Temporarily increase Python's recursion limit for tests.
        """
        import sys
        sys.setrecursionlimit(3000)
        yield
        sys.setrecursionlimit(1000)  # Reset to default after tests

    # Test to check if repository creation fails with an invalid token
    @pytest.mark.github
    def test_create_repo_fail(self, github_service):
        result = github_service.create_repo(self.repo_name, self.invalid_token)
        assert not result, "La creación del repositorio debería haber fallado"

    # Test to check if repository creation succeeds with a valid token
    @pytest.mark.github
    def test_create_repo_success(self, github_service):
        result = github_service.create_repo(self.repo_name, self.token)
        assert result, "La creación del repositorio debería haber tenido éxito"

    # Test to check if the repository exists
    @pytest.mark.github
    def test_check_repository_exists_found(self, github_service):
        result = github_service.check_repository_exists(self.repo_owner, self.repo_name, self.token)
        assert result, "El repositorio debería existir"

    # Test to check if the repository does not exist
    @pytest.mark.github
    def test_check_repository_exists_not_found(self, github_service):
        result = github_service.check_repository_exists("no_exists", self.repo_name, self.token)
        assert not result, "El repositorio no debería existir"

    # Test to check if deleting a repository fails with an invalid token
    @pytest.mark.github
    def test_delete_repo_fail(self, github_service):
        result = github_service.delete_repo(self.invalid_token, self.repo_owner, self.repo_name)
        assert not result, "La eliminación del repositorio debería haber fallado"

    # Test to check if deleting a repository succeeds with a valid token
    @pytest.mark.github
    def test_delete_repo_success(self, github_service):
        result = github_service.delete_repo(self.token, self.repo_owner, self.repo_name)
        assert result == ('Repository deleted successfully', 204), "La eliminación del repositorio debería ser exitosa"
