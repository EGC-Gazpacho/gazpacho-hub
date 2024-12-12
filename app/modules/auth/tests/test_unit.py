import pytest
from flask import url_for
from unittest.mock import patch

from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository
from app.modules.profile.repositories import UserProfileRepository
from app.modules.dataset.repositories import DataSetRepository


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


def test_login_success(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login", data=dict(email="bademail@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="basspassword"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup", data=dict(surname="Foo", email="test@example.com", password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup", data=dict(name="Test", surname="Foo", email=email, password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for("public.index"), "Signup was unsuccessful"


def test_service_create_with_profie_success(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "service_test@example.com",
        "password": "test1234",
    }

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


def test_service_create_with_profile_fail_no_email(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "",
        "password": "1234",
    }

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_fail_no_password(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "test@example.com",
        "password": "",
    }

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_get_all(test_client):
    mock_users = [
        {"id": 1, "name": "UserProfile 1"},
        {"id": 2, "name": "UserProfile 2"},
        {"id": 3, "name": "UserProfile 3"},
    ]

    with patch('app.modules.auth.repositories.UserRepository.get_all', return_value=mock_users):
        repository = UserRepository()
        result = repository.get_all()

        assert len(result) >= 3
        assert result == mock_users


def test_user_without_datasets(test_client):
    mock_users = [
        {"id": 1, "name": "UserProfile 1"},
        {"id": 2, "name": "UserProfile 2"},
        {"id": 3, "name": "UserProfile 3"},
    ]

    mock_datasets = [
        {
            "title": "Dataset Example 1",
            "id": 1,
            "created_at": "2024-12-10T12:00:00",
            "created_at_timestamp": 1733832000,
            "description": "Description for dataset 1",
            "authors": [
                {"id": 1, "name": "Author 1"},
                {"id": 2, "name": "Author 2"},
            ],
            "publication_type": "Research Article",
            "publication_doi": "10.1234/example.1",
            "dataset_doi": "10.5678/zenodo.1",
            "tags": ["science", "data", "example"],
            "url": "https://uvlhub.example.com/dataset/1",
            "download": "http://localhost/dataset/download/1",
            "zenodo": "https://zenodo.org/record/12345",
            "files": [
                {"id": 1, "name": "file1.txt", "size": 1024},
                {"id": 2, "name": "file2.csv", "size": 2048},
            ],
            "files_count": 2,
            "total_size_in_bytes": 3072,
            "total_size_in_human_format": "3.07 KB",
        },
        {
            "title": "Dataset Example 2",
            "id": 2,
            "created_at": "2024-11-01T08:00:00",
            "created_at_timestamp": 1733030400,
            "description": "Description for dataset 2",
            "authors": [{"id": 3, "name": "Author 3"}],
            "publication_type": "Conference Paper",
            "publication_doi": "10.1234/example.2",
            "dataset_doi": None,
            "tags": ["conference", "presentation"],
            "url": "https://uvlhub.example.com/dataset/2",
            "download": "http://localhost/dataset/download/2",
            "zenodo": None,
            "files": [
                {"id": 3, "name": "slides.pdf", "size": 5120},
            ],
            "files_count": 1,
            "total_size_in_bytes": 5120,
            "total_size_in_human_format": "5.12 KB",
        },
    ]
    with patch('app.modules.auth.repositories.UserRepository.get_all', return_value=mock_users):
        with patch('app.modules.dataset.repositories.DataSetRepository.get_synchronized', return_value=mock_datasets):
            repository = UserRepository()
            repository2 = DataSetRepository()
            user = repository.get_all()
            result = repository2.get_unsynchronized(user[2]["id"])
            assert len(result) == 0


def test_user_with_datasets(test_client):
    mock_users = [
        {"id": 7, "name": "UserProfile 3"},
        {"id": 8, "name": "UserProfile 4"},
        {"id": 10, "name": "UserProfile 5"},
    ]

    mock_datasets = [
        {
            "title": "Dataset Example 1",
            "id": 1,
            "created_at": "2024-12-10T12:00:00",
            "created_at_timestamp": 1733832000,
            "description": "Description for dataset 1",
            "authors": [
                {"id": 1, "name": "Author 1"},
                {"id": 2, "name": "Author 2"},
            ],
            "publication_type": "Research Article",
            "publication_doi": "10.1234/example.1",
            "dataset_doi": "10.5678/zenodo.1",
            "tags": ["science", "data", "example"],
            "url": "https://uvlhub.example.com/dataset/1",
            "download": "http://localhost/dataset/download/1",
            "zenodo": "https://zenodo.org/record/12345",
            "files": [
                {"id": 1, "name": "file1.txt", "size": 1024},
                {"id": 2, "name": "file2.csv", "size": 2048},
            ],
            "files_count": 2,
            "total_size_in_bytes": 3072,
            "total_size_in_human_format": "3.07 KB",
        },
        {
            "title": "Dataset Example 2",
            "id": 2,
            "created_at": "2024-11-01T08:00:00",
            "created_at_timestamp": 1733030400,
            "description": "Description for dataset 2",
            "authors": [{"id": 3, "name": "Author 3"}],
            "publication_type": "Conference Paper",
            "publication_doi": "10.1234/example.2",
            "dataset_doi": None,
            "tags": ["conference", "presentation"],
            "url": "https://uvlhub.example.com/dataset/2",
            "download": "http://localhost/dataset/download/2",
            "zenodo": None,
            "files": [
                {"id": 3, "name": "slides.pdf", "size": 5120},
            ],
            "files_count": 1,
            "total_size_in_bytes": 5120,
            "total_size_in_human_format": "5.12 KB",
        },
    ]

    with patch('app.modules.auth.repositories.UserRepository.get_all', return_value=mock_users):
        with patch('app.modules.dataset.repositories.DataSetRepository.get_synchronized', return_value=mock_datasets):
            repository = UserRepository()
            repository2 = DataSetRepository()
            user = repository.get_all()
            result = repository2.get_synchronized(user[0]["id"])
            assert len(result) == 2


def test_user_not_found(test_client):
    mock_users = [
        {"id": 1, "name": "UserProfile 1"},
        {"id": 2, "name": "UserProfile 2"},
        {"id": 3, "name": "UserProfile 3"},
    ]

    with patch('app.modules.auth.repositories.UserRepository.get_all', return_value=mock_users):
        repository2 = DataSetRepository()
        # Simulamos que no existe el usuario con el id 999
        result = repository2.get_unsynchronized(999)  # ID que no existe

        # Verificamos que el resultado sea vacío
        assert result == [], "Se esperaba un resultado vacío, ya que el usuario no existe."
