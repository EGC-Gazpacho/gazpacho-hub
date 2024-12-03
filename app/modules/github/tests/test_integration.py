import pytest
import os
from unittest.mock import MagicMock
from app.modules.github.services import GitHubService
from app.modules.dataset.services import DataSetService


class TestGitHubService:

    @pytest.fixture(autouse=True)
    def github_setup(self, monkeypatch):
    
        self.token = os.getenv("GITHUB_TOKEN")  # GitHub Token
        self.invalid_token = "invalid_token"  
        self.repo_owner = "rafduqcol"
        self.repo_name = "uvl_repo_tests"
        self.branch = "main"
        self.commit_message = "Test commit"
        self.license = "MIT"

        # Dataset fetched from the service
        monkeypatch.setattr(
                "app.modules.dataset.services.DataSetService.get_or_404",
                lambda id: {"id": id, "name": "Sample Dataset"}
            )

        self.dataset = DataSetService.get_or_404(1)  # ID=1 mocked above
    

    # Test for repository creation failure
    def test_create_repo_fail(self):

        result = GitHubService.create_repo(self.repo_name, self.invalid_token)
        assert result is False, "Repository creation should have failed"

    #Test for repository creation success
    def test_create_repo_success(self):
    
        result = GitHubService.create_repo(self.repo_name, self.token)
        assert result is True, "Repository creation should have succeeded"
        
    
    
    
  