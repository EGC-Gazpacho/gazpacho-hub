from io import BytesIO
import pytest
from unittest.mock import MagicMock, patch
import requests
from app.modules.github.services import GitHubService
from app.modules.github.repositories import GitHubRepository
from app import db
from app.modules.auth.models import User


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


@patch('requests.get')
def test_check_repository_exists_found(mock_get, github_service):
    mock_get.return_value.status_code = 200

    owner = 'test_user'
    repo_name = 'test_repo'

    result = github_service.check_repository_exists(owner, repo_name, 'access_token')

    assert result
    mock_get.assert_called_once_with(f"https://api.github.com/repos/{owner}/{repo_name}",
                                     headers={'Authorization': 'token access_token'})


# Test to check if the repository does not exist
@patch('requests.get')
def test_check_repository_exists_not_found(mock_get, github_service):
    mock_get.return_value.status_code = 404

    owner = 'test_user'
    repo_name = 'nonexistent_repo'

    result = github_service.check_repository_exists(owner, repo_name, 'access_token')

    assert not result
    mock_get.assert_called_once_with(
        f"https://api.github.com/repos/{owner}/{repo_name}",
        headers={'Authorization': 'token access_token'}
    )


# Test to manage the exception when the request fails
@patch('requests.get')
def test_check_repository_exists_error(mock_get, github_service):
    mock_get.side_effect = Exception("Network error")

    owner = 'test_user'
    repo_name = 'test_repo'

    with pytest.raises(Exception):
        github_service.check_repository_exists(owner, repo_name, 'access_token')


# Test to check if branch exists
@patch('requests.get')
def test_check_branch_exists_found(mock_get, github_service):
    mock_get.return_value.status_code = 200

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'access_token'

    result = github_service.check_branch_exists(owner, repo_name, branch, access_token)

    assert result

    mock_get.assert_called_once_with(
        f"https://api.github.com/repos/{owner}/{repo_name}/branches/{branch}",
        headers={'Authorization': f'token {access_token}'}
    )

# Test to check if the branch does not exist


@patch('requests.get')
def test_check_branch_exists_not_found(mock_get, github_service):
    mock_get.return_value.status_code = 404

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'nonexistent_branch'
    access_token = 'access_token'

    result = github_service.check_branch_exists(owner, repo_name, branch, access_token)

    assert not result

    mock_get.assert_called_once_with(
        f"https://api.github.com/repos/{owner}/{repo_name}/branches/{branch}",
        headers={'Authorization': f'token {access_token}'}
    )

# Test to check if the branch exists and token is invalid


@patch('requests.get')
def test_check_branch_exists_error(mock_get, github_service):
    mock_get.return_value.status_code = 401

    owner = 'test_user'
    repo_name = 'test_repo'
    access_token = 'inaccess_token'
    branch = 'main'

    with pytest.raises(requests.exceptions.HTTPError, match="Unauthorized - Invalid or expired access token."):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)

    mock_get.assert_called_once_with(
        f"https://api.github.com/repos/{owner}/{repo_name}/branches/{branch}",
        headers={'Authorization': f'token {access_token}'}
    )

# Test to manage the exception HTTPError when the request fails


@patch('requests.get')
def test_http_error(mock_get, github_service):
    mock_get.return_value.status_code = 500
    mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'access_token'

    with pytest.raises(requests.exceptions.HTTPError):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)


# Test to manage the exception when the request fails
@patch('requests.get')
def test_check_branch_exists_connection_error(mock_get, github_service):
    mock_get.side_effect = requests.exceptions.ConnectionError

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'access_token'

    with pytest.raises(requests.exceptions.RequestException, match="ConnectionError: Could not connect to GitHub."):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)

# Test to manage the exception when the request times out


@patch('requests.get')
def test_check_branch_exists_timeout_error(mock_get, github_service):
    mock_get.side_effect = requests.exceptions.Timeout

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'access_token'

    with pytest.raises(requests.exceptions.RequestException,
                       match="TimeoutError: The request to GitHub exceeded the timeout."):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)

# Test to manage the exception when the request fails with an unexpected error


@patch('requests.get')
def test_request_exception(mock_get, github_service):
    mock_get.side_effect = requests.exceptions.RequestException("Unexpected error")

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'access_token'

    with pytest.raises(requests.exceptions.RequestException, match="Unexpected error"):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)


# Test for successful repository creation
@patch('requests.post')
def test_create_repo_success(mock_post):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"name": "test_repo", "message": "Created successfully."}

    repo_name = "test_repo"
    token = "access_token"

    result = github_service.create_repo(repo_name, token)

    assert result is True
    mock_post.assert_called_once_with(
        "https://api.github.com/user/repos",
        json={"name": repo_name, "private": False, "description": "Repository created through the API"},
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"}
    )


# Test for repository creation failure due to bad credentials
@patch('requests.post')
def test_create_repo_failure(mock_post, github_service):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"message": "Bad credentials"}

    repo_name = "test_repo"
    token = "inaccess_token"

    result = github_service.create_repo(repo_name, token)

    assert result is False
    mock_post.assert_called_once_with(
        "https://api.github.com/user/repos",
        json={"name": repo_name, "private": False, "description": "Repository created through the API"},
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"}
    )


# Test for failed repository creation (general error)
@patch('requests.post')
def test_create_repo_general_error(mock_post, github_service):
    mock_post.return_value.status_code = 500
    mock_post.return_value.json.return_value = {"message": "Internal Server Error"}

    repo_name = "test_repo"
    token = "access_token"

    result = github_service.create_repo(repo_name, token)

    assert result is False
    mock_post.assert_called_once_with(
        "https://api.github.com/user/repos",
        json={"name": repo_name, "private": False, "description": "Repository created through the API"},
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"}
    )


# Test for handling a connection error
@patch('requests.post')
def test_create_repo_connection_error(mock_post, github_service):
    mock_post.side_effect = requests.exceptions.ConnectionError

    repo_name = "test_repo"
    token = "access_token"

    with pytest.raises(requests.exceptions.ConnectionError):
        github_service.create_repo(repo_name, token)


# Test for handling timeout error
@patch('requests.post')
def test_create_repo_timeout_error(mock_post, github_service):
    mock_post.side_effect = requests.exceptions.Timeout

    repo_name = "test_repo"
    token = "access_token"

    with pytest.raises(requests.exceptions.Timeout):
        github_service.create_repo(repo_name, token)


# Test for upload a dataset to github with success
@patch('requests.put')
@patch('builtins.open', new_callable=MagicMock)
def test_upload_dataset_to_github_success(mock_open, mock_put, github_service):
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {
        'message': 'File uploaded successfully',
        'url': 'https://github.com/test_owner/test_repo/test_dataset'
    }

    owner = "test_owner"
    repo_name = "test_repo"
    branch = "main"
    token = "access_token"
    commit_message = "Adding dataset"
    license = "MIT"
    repo_type = 'existing'

    dataset = MagicMock()
    dataset.name.return_value = "test_dataset"

    mock_file = MagicMock()
    mock_file.get_path.return_value = 'test_file.txt'
    mock_file.name = 'test_file.txt'

    dataset.feature_models = [MagicMock(files=[mock_file])]

    fake_file_content = b"Fake file content for testing"
    mock_open.return_value.__enter__.return_value = BytesIO(fake_file_content)

    result = github_service.upload_dataset_to_github(
        owner, repo_name, branch, dataset, token, commit_message, license, repo_type)

    assert result == ('File uploaded successfully', 200)
    mock_put.assert_called()
    mock_open.assert_called()


# Test for failure in uploading dataset to GitHub
@patch('requests.put')
@patch('builtins.open', new_callable=MagicMock)
def test_upload_dataset_to_github_file_upload_failure(mock_open, mock_put, github_service):
    mock_put.return_value.status_code = 400
    mock_put.return_value.text = "Bad Request"
    mock_put.return_value.ok = False

    # Mock the file content
    fake_file_content = b"Fake file content for testing"
    mock_open.return_value.__enter__.return_value = BytesIO(fake_file_content)

    owner = "test_owner"
    repo_name = "test_repo"
    branch = "main"
    token = "access_token"
    commit_message = "Adding dataset"
    license = "MIT"
    repo_type = 'existing'

    dataset = MagicMock()
    dataset.name.return_value = "test_dataset"
    dataset.feature_models = [MagicMock(files=[MagicMock(get_path=lambda: 'test_file.txt', name='test_file.txt')])]

    file_mock = dataset.feature_models[0].files[0]
    file_mock.name = 'test_file.txt'

    with pytest.raises(requests.exceptions.HTTPError):
        github_service.upload_dataset_to_github(
            owner,
            repo_name,
            branch,
            dataset,
            token,
            commit_message,
            license,
            repo_type)

    mock_put.assert_called()
    mock_open.assert_called()


# Test for successfully uploading dataset to a new repo on GitHub
@patch('requests.put')
@patch('app.modules.github.services.GitHubService.create_repo')
@patch('builtins.open', new_callable=MagicMock)
def test_upload_dataset_to_github_new_repo(mock_open, mock_create_repo, mock_put, github_service):
    mock_create_repo.return_value = True

    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {
        'message': 'File uploaded successfully',
        'url': 'https://github.com/test_owner/test_repo/test_dataset'}

    fake_file_content = b"Fake file content for testing"
    mock_open.return_value.__enter__.return_value = BytesIO(fake_file_content)

    owner = "test_owner"
    repo_name = "test_repo"
    branch = "main"
    token = "access_token"
    commit_message = "Adding dataset"
    license = "MIT"
    repo_type = 'new'

    dataset = MagicMock()
    dataset.name.return_value = "test_dataset"
    dataset.feature_models = [MagicMock(files=[MagicMock(get_path=lambda: 'test_file.txt', name='test_file.txt')])]

    result = github_service.upload_dataset_to_github(
        owner, repo_name, branch, dataset, token, commit_message, license, repo_type)

    assert result == ('File uploaded successfully', 200)
    mock_create_repo.assert_called_with(repo_name, token)
    mock_put.assert_called()
    mock_open.assert_called()


# Test to delete a repository that does exist in GitHub with success
@patch('requests.delete')
def test_delete_repo_success(mock_delete, github_service):
    mock_delete.return_value.status_code = 204
    mock_delete.return_value.ok = True

    owner = "test_owner"
    repo_name = "test_repo"
    token = "access_token"

    result = github_service.delete_repo(owner, repo_name, token)

    assert result == ('Repository deleted successfully', 204)

    mock_delete.assert_called()

# Test to delete a repository that does exist in GitHub with not success


@patch('requests.delete')
def test_delete_repo_failure(mock_delete, github_service):
    mock_delete.return_value.status_code = 400
    mock_delete.return_value.json.return_value = {'message': 'Bad Request'}
    mock_delete.return_value.ok = False

    owner = "test_owner"
    repo_name = "test_repo"
    token = "access_token"

    result = github_service.delete_repo(owner, repo_name, token)

    assert not result

    mock_delete.assert_called_once()

# Test to delete a repository that does not exist in GitHub with success


@patch('requests.get')
@patch('requests.delete')
def test_delete_file_success(mock_delete, mock_get, github_service):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'sha': '123456abcdef'}

    mock_delete.return_value.status_code = 200
    mock_delete.return_value.ok = True

    token = "access_token"
    repo_owner = "test_owner"
    repo_name = "test_repo"
    file_path = "path/to/file.txt"
    branch = "main"
    commit_message = "Delete file from repository"

    result = github_service.delete_file_from_repo(token, repo_owner, repo_name, file_path, branch, commit_message)

    assert result == ('File deleted successfully', 200)

    mock_get.assert_called_once()
    mock_delete.assert_called_once()

# Test to delete a repository that does not exist in GitHub with not success


@patch('requests.get')
@patch('requests.delete')
def test_delete_file_not_found(mock_delete, mock_get, github_service):
    mock_get.return_value.status_code = 404
    mock_get.return_value.json.return_value = {'message': 'Not Found'}

    token = "access_token"
    repo_owner = "test_owner"
    repo_name = "test_repo"
    file_path = "path/to/file.txt"
    branch = "main"
    commit_message = "Delete file from repository"

    result = github_service.delete_file_from_repo(token, repo_owner, repo_name, file_path, branch, commit_message)

    assert not result

    mock_get.assert_called_once()
    mock_delete.assert_not_called()