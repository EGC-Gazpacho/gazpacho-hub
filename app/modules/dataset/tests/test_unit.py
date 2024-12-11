import pytest
from unittest.mock import patch
from flask import url_for
from app import create_app
import io

@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'
    with app.test_client() as client:
        with app.app_context():
            yield client

@patch('app.modules.dataset.services.DataSetService.zip_all_datasets')
def test_download_all_endpoint(mock_generar_zip, test_client):
    """Testea que el endpoint de descarga devuelva un código 200."""
    mock_generar_zip.return_value = io.BytesIO(b'simulated zip content')

    response = test_client.get('/dataset/download/all')

    assert response.status_code == 200
    mock_generar_zip.assert_called_once()

@patch('app.modules.dataset.services.DataSetService.zip_all_datasets')
def test_download_all_is_zip(mock_generar_zip, test_client):
    """Testea que el contenido devuelto sea un archivo ZIP."""
    mock_generar_zip.return_value = io.BytesIO(b'simulated zip content')

    response = test_client.get('/dataset/download/all')

    assert response.data == b'simulated zip content'
    assert response.content_type == 'application/zip'
    mock_generar_zip.assert_called_once()
