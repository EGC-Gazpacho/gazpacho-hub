import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_login import LoginManager
from app.modules.github.routes import github_bp


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass
    yield test_client


@pytest.fixture
def mock_dataset():
    return {"id": 1, "name": "Test Dataset", "files": ["file1.txt", "file2.txt"]}

# Test the route create_dataset_github with success
def create_dataset_github_succes(test_client, mock_dataset):
    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get:
        mock_get.return_value = mock_dataset

        response = test_client.get("/github/upload/1")

        assert response.status_code == 302
