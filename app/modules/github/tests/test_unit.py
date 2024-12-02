import pytest
from unittest.mock import MagicMock, patch

import requests
from app.modules.github.services import GitHubService
from app.modules.github.repositories import GitHubRepository


@pytest.fixture(scope='module')
def github_service():
    repo = GitHubRepository(name="my_repo", owner="my_user")
    return GitHubService(repository=repo)


# Test to check if the repository exists
@patch('requests.get')
def test_check_repository_exists_found(mock_get, github_service):
    mock_get.return_value.status_code = 200
    
    owner = 'test_user'
    repo_name = 'test_repo'
    
    result = github_service.check_repository_exists(owner, repo_name, 'access_token')
    print(result)
    
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


#Test to check if branch exists
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


    with pytest.raises(requests.exceptions.RequestException, match="TimeoutError: The request to GitHub exceeded the timeout."):
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
import pytest
from unittest.mock import patch
import requests
from app.modules.github.services import GitHubService


# Test for successful repository creation
@patch('requests.post')
def test_create_repo_success(mock_post):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"name": "test_repo", "message": "Created successfully."}
    
    repo_name = "test_repo"
    token = "access_token"
    
    result = GitHubService.create_repo(repo_name, token)
    
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
        
        
#Test to update the dataset to a repo that does exist in GitHub with success
@patch('requests.put')
def test_upload_dataset_to_github_success(mock_put, github_service):
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {'message': 'File uploaded successfully', 'url': 'https://github.com/test_owner/test_repo/test_dataset'}
    
    owner = "test_owner"
    repo_name = "test_repo"
    branch = "main"
    token = "valid_token"
    commit_message = "Adding dataset"
    license = "MIT"
    repo_type = 'existing'
    
    dataset = MagicMock()
    dataset.name.return_value = "test_dataset"
    dataset.feature_models = [MagicMock(files=[MagicMock(get_path=lambda: 'test_file.txt', name='test_file.txt')])]
    
    result = github_service.upload_dataset_to_github(owner, repo_name, branch, dataset, token, commit_message, license, repo_type)

    assert result == ('File uploaded successfully', 200)
    mock_put.assert_called()  

#Test to update the dataset to a repo that does exist in GitHub with not success
import pytest
from unittest.mock import patch, MagicMock
import requests

# Test para subir el dataset con fallo en la carga del archivo
@patch('requests.put')
def test_upload_dataset_to_github_file_upload_failure(mock_put, github_service):
   
    mock_put.return_value.status_code = 400  
    mock_put.return_value.text = "Bad Request"  
    mock_put.return_value.ok = False  
    
    owner = "test_owner"
    repo_name = "test_repo"
    branch = "main"
    token = "valid_token"
    commit_message = "Adding dataset"
    license = "MIT"
    repo_type = 'existing'  
     
    
    dataset = MagicMock()
    dataset.name.return_value = "test_dataset"
    dataset.feature_models = [MagicMock(files=[MagicMock(get_path=lambda: 'test_file.txt', name='test_file.txt')])]
    
    file_mock = dataset.feature_models[0].files[0]
    file_mock.name = 'test_file.txt'  
    
    with pytest.raises(requests.exceptions.HTTPError):
        github_service.upload_dataset_to_github(owner, repo_name, branch, dataset, token, commit_message, license, repo_type)
    
    mock_put.assert_called()  


#Test to update the dataset to a repo that does not exist in GitHub with success
@patch('requests.put')
@patch('app.modules.github.services.GitHubService.create_repo')  
def test_upload_dataset_to_github_new_repo(mock_create_repo, mock_put, github_service):
    mock_create_repo.return_value = True  
    
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {'message': 'File uploaded successfully', 'url': 'https://github.com/test_owner/test_repo/test_dataset'}
    
    owner = "test_owner"
    repo_name = "test_repo"
    branch = "main"
    token = "valid_token"
    commit_message = "Adding dataset"
    license = "MIT"
    repo_type = 'new'  
    
    dataset = MagicMock()
    dataset.name.return_value = "test_dataset"
    dataset.feature_models = [MagicMock(files=[MagicMock(get_path=lambda: 'test_file.txt', name='test_file.txt')])]
    
    result = github_service.upload_dataset_to_github(owner, repo_name, branch, dataset, token, commit_message, license, repo_type)
    
    assert result == ('File uploaded successfully', 200)
    
    mock_create_repo.assert_called_with(repo_name, token)
    
    mock_put.assert_called()
    
# Test to update the dataset to repo that does not exist in GitHub with not success
@patch('requests.put')
@patch('app.modules.github.services.GitHubService.create_repo')  
def test_upload_dataset_to_github_new_repo_creation_failure(mock_create_repo, mock_put, github_service):
    mock_create_repo.return_value = False
    
    owner = "test_owner"
    repo_name = "test_repo"
    branch = "main"
    token = "valid_token"
    commit_message = "Adding dataset"
    license = "MIT"
    repo_type = 'new'  
    
    dataset = MagicMock()
    dataset.name.return_value = "test_dataset"
    dataset.feature_models = [MagicMock(files=[MagicMock(get_path=lambda: 'test_file.txt', name='test_file.txt')])]
    
    result = github_service.upload_dataset_to_github(owner, repo_name, branch, dataset, token, commit_message, license, repo_type)

    assert result == ('Error: Could not create repository test_repo.', 400)
    
    mock_create_repo.assert_called_with(repo_name, token)
    
    mock_put.assert_not_called()


