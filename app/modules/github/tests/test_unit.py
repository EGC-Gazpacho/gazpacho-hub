from unittest.mock import patch
from app.modules.github.repositories import GitHubRepository
import pytest
import requests
from app.modules.auth.models import User
from app.modules.github.services import GitHubService
import os
from app import db
from app.modules.conftest import login, logout


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        pass
    yield test_client

@pytest.fixture(scope='module')
def github_service():
    repo = GitHubRepository(name="my_repo", owner="my_user")
    return GitHubService(repository=repo)


@pytest.fixture
def mock_dataset():
    return {"id": 1, "name": "Test Dataset", "files": ["file1.txt", "file2.txt"]}

# Test the route get create_dataset_github


def test_create_dataset_github(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    with requests.patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        response = test_client.get("/github/upload/1")
        assert response.status_code == 200
        logout(test_client)

# Test the route create_dataset_github with success


def test_create_dataset_github_succes(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=True):
            with patch.object(GitHubService, 'upload_dataset_to_github', return_value=("Upload successful", 200)):
                response = test_client.post("/github/upload/1", data={
                    'commit_message': 'Test commit',
                    'owner': 'rafduqcol',
                    'repo_name': 'uvl',
                    'branch': 'main',
                    'repo_type': 'new',
                    'access_token': os.getenv("GITHUB_TOKEN"),
                    'license': 'MIT'
                })

                assert response.status_code == 200
                assert response.json["message"] == "Upload successful"
                logout(test_client)


# Test the route create_dataset_github with a new repository
def test_create_new_repo(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

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
                logout(test_client)


# Test the route create_dataset_github with a repository that does not exist
def test_repository_not_found(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

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
            logout(test_client)


# Tests the route create_dataset_github with a branch that does not exist
def test_branch_not_found(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

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
                logout(test_client)

# Tests the route create_dataset_github with a connection error


def test_upload_dataset_error(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=True):
            with patch.object(GitHubService, 'check_branch_exists', return_value=True):
                with patch.object(GitHubService, 'upload_dataset_to_github',
                                  side_effect=requests.exceptions.RequestException("Error de conexión")):
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
                    logout(test_client)

# Test the route create_dataset_github with a bad token


def test_bad_token(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        with patch.object(GitHubService, 'check_repository_exists', return_value=True):
            with patch.object(GitHubService, 'check_branch_exists', return_value=True):
                with patch.object(GitHubService, 'upload_dataset_to_github',
                                  side_effect=requests.exceptions.HTTPError("Error 401: Bad credentials")):
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
                    logout(test_client)

# Test the route create_dataset_github with a dataset that already exists in the repository


def test_create_dataset_github_already_exists(test_client, mock_dataset):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

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
                logout(test_client)
