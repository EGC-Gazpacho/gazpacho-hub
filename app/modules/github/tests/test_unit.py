import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_login import LoginManager, login_user
import requests
from app.modules.auth.models import User
from app.modules.github.services import GitHubService
from app.modules.github.routes import github_bp
import os
from app import db

@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        os.environ["GITHUB_TOKEN"] = "tu_token_de_github"  # Establecer el token de GitHub en el entorno
        test_client.application.config["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN")

        pass
    yield test_client


@pytest.fixture
def mock_dataset():
    return {"id": 1, "name": "Test Dataset", "files": ["file1.txt", "file2.txt"]}

# Test the route create_dataset_github with success
def test_create_dataset_github_succes(test_client, mock_dataset):
    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
    
        mock_get.return_value = mock_dataset

        response = test_client.get("/github/upload/1")

        assert response.status_code == 200

# Test the route create_dataset_github with a new repository
def test_create_new_repo(test_client, mock_dataset):
    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=False):
            with patch.object(GitHubService, 'upload_dataset_to_github', return_value=("Upload successful", 200)):
                response = test_client.post("/github/upload/1", data={
                    'commit_message': 'Test commit',
                    'owner': 'rafduqcol',
                    'repo_name': 'new_repo',
                    'branch': 'main',
                    'repo_type': 'new',
                    'access_token': os.getenv("GITHUB_TOKEN"),
                    'license': 'MIT'
                })

                assert response.status_code == 200
                assert response.json["message"] == "Upload successful"


# Test the route create_dataset_github with a repository that does not exist
def test_repository_not_found(test_client, mock_dataset):
    print("holaaa", os.getenv("GITHUB_TOKEN"))
    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=False):
            response = test_client.post("/github/upload/1", data={
                'commit_message': 'Test commit',
                'owner': 'rafduqcol',
                'repo_name': 'uvl',
                'branch': 'main',
                'repo_type': 'existing',
                'access_token': os.getenv("GITHUB_TOKEN"),
                'license': 'MIT'
            })

            assert response.status_code == 404
            assert response.json["error"] == "Repository not found. Verify the repository owner and name."

          
# Tests the route create_dataset_github with a branch that does not exist
def test_branch_not_found(test_client, mock_dataset):
    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=True):
            with patch.object(GitHubService, 'check_branch_exists', return_value=False):
                response = test_client.post("/github/upload/1", data={
                    'commit_message': 'Test commit',
                    'owner': 'rafduqcol',
                    'repo_name': 'uvl',
                    'branch': 'non_existent_branch',
                    'repo_type': 'existing',
                    'access_token': os.getenv("GITHUB_TOKEN"),
                    'license': 'MIT'
                })

                assert response.status_code == 404
                assert response.json["error"] == "Branch non_existent_branch not found. Verify the branch name."

# Tests the route create_dataset_github with a connection error
def test_upload_dataset_error(test_client, mock_dataset):
    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=True):
            with patch.object(GitHubService, 'check_branch_exists', return_value=True):
                with patch.object(GitHubService, 'upload_dataset_to_github', side_effect=requests.exceptions.RequestException("Error de conexión")):
                    response = test_client.post("/github/upload/1", data={
                        'commit_message': 'Test commit',
                        'owner': 'rafduqcol',
                        'repo_name': 'existing_repo',
                        'branch': 'main',
                        'repo_type': 'existing',
                        'access_token': os.getenv("GITHUB_TOKEN"),
                        'license': 'MIT'
                    })

                    assert response.status_code == 500
                    assert response.json["error"] == "Failed to connect to GitHub API: Error de conexión"

#Test the route create_dataset_github with a bad token
def test_bad_token(test_client, mock_dataset):
    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=True):
            with patch.object(GitHubService, 'check_branch_exists', return_value=True):
                with patch.object(GitHubService, 'upload_dataset_to_github', side_effect=requests.exceptions.HTTPError("Error 401: Bad credentials")):
                    response = test_client.post("/github/upload/1", data={
                        'commit_message': 'Test commit',
                        'owner': 'rafduqcol',
                        'repo_name': 'uvl',
                        'branch': 'main',
                        'repo_type': 'existing',
                        'access_token': 'bad_token',
                        'license': 'MIT'
                    })

                    assert response.status_code == 401
                    assert response.json["error"] == "Bad credentials. Verify your access token."
                    
#Test the route create_dataset_github with a dataset that already exists in the repository
def test_create_dataset_github_already_exists(test_client, mock_dataset):
      with patch.object(GitHubService, 'check_repository_exists', return_value=True):
            with patch.object(GitHubService, 'check_branch_exists', return_value=True):
                with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get, \
                    patch.object(GitHubService, 'upload_dataset_to_github') as mock_upload:

                    mock_get.return_value = mock_dataset

                    mock_upload.side_effect = requests.exceptions.HTTPError("422 Unprocessable Entity")

                    response = test_client.post("/github/upload/1", data={
                        'commit_message': 'Test commit',
                        'owner': 'rafduqcol',
                        'repo_name': 'uvl',
                        'branch': 'main',
                        'repo_type': 'existing',
                        'access_token': os.getenv("GITHUB_TOKEN"),
                        'license': 'MIT'
                    })
                    print(response.json)
                    assert response.status_code == 422
                    assert response.json["error"] == "A dataset with the same name already exists in the repository."
                    assert response.json["code"] == 422
