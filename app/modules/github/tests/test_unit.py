import pytest
from unittest.mock import patch
from app.modules.github.services import GitHubService
from app.modules.github.repositories import GitHubRepository


@pytest.fixture(scope='module')
def github_service():
    # Crear una instancia de GitHubRepository
    repo = GitHubRepository(name="my_repo", owner="my_user")
    # Pasar el repositorio a GitHubService
    return GitHubService(repository=repo)


# Test cuando el repositorio existe
@patch('requests.get')
def test_check_repository_exists_found(mock_get, github_service):
    # Simula la respuesta de la API de GitHub con status_code 200
    mock_get.return_value.status_code = 200
    
    owner = 'rafduqcol'
    repo_name = 'uvl'
    
    # Llama a la función que estamos probando
    result = github_service.check_repository_exists(owner, repo_name, 'fake_access_token')
    
    # Verifica que la función devuelve True cuando el repositorio existe
    assert not result
    mock_get.assert_called_once_with(f"https://api.github.com/repos/{owner}/{repo_name}", 
                                     headers={'Authorization': 'token fake_access_token'})


# Test cuando el repositorio no existe
@patch('requests.get')
def test_check_repository_exists_not_found(mock_get, github_service):
    # Simula la respuesta de la API de GitHub con status_code 404
    mock_get.return_value.status_code = 404
    
    owner = 'rafduqcol'
    repo_name = 'nonexistent_repo'
    
    # Llama a la función que estamos probando
    result = github_service.check_repository_exists(owner, repo_name, 'fake_access_token')
    
    # Verifica que la función devuelve False cuando el repositorio no existe
    assert not result
    mock_get.assert_called_once_with(
        f"https://api.github.com/repos/{owner}/{repo_name}",
        headers={'Authorization': 'token fake_access_token'}
    )


# Test para manejar errores en la petición
@patch('requests.get')
def test_check_repository_exists_error(mock_get, github_service):
    # Simula una excepción en la petición
    mock_get.side_effect = Exception("Network error")
    
    owner = 'rafduqcol'
    repo_name = 'uvl'
    
    # Verifica que la función maneja la excepción correctamente
    with pytest.raises(Exception):
        github_service.check_repository_exists(owner, repo_name, 'fake_access_token')
