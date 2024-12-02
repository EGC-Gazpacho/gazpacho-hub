import pytest
from unittest.mock import patch

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
    access_token = 'valid_access_token'

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
    access_token = 'valid_access_token'

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
    access_token = 'invalid_access_token'
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
    access_token = 'valid_access_token'

    with pytest.raises(requests.exceptions.HTTPError):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)

    
# Test to manage the exception when the request fails
@patch('requests.get')
def test_check_branch_exists_connection_error(mock_get, github_service):
    mock_get.side_effect = requests.exceptions.ConnectionError

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'valid_access_token'


    with pytest.raises(requests.exceptions.RequestException, match="ConnectionError: Could not connect to GitHub."):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)

# Test to manage the exception when the request times out
@patch('requests.get')
def test_check_branch_exists_timeout_error(mock_get, github_service):
    mock_get.side_effect = requests.exceptions.Timeout

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'valid_access_token'


    with pytest.raises(requests.exceptions.RequestException, match="TimeoutError: The request to GitHub exceeded the timeout."):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)  
        
# Test to manage the exception when the request fails with an unexpected error
@patch('requests.get')
def test_request_exception(mock_get, github_service):
    mock_get.side_effect = requests.exceptions.RequestException("Unexpected error")

    owner = 'test_user'
    repo_name = 'test_repo'
    branch = 'main'
    access_token = 'valid_access_token'

    with pytest.raises(requests.exceptions.RequestException, match="Unexpected error"):
        github_service.check_branch_exists(owner, repo_name, branch, access_token)