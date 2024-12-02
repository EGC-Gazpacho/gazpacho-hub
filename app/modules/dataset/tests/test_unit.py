from flask import url_for
import pytest


def test_download_all_endpoint(test_client):
    """Testea que el endpoint de descarga devuelva un código 200."""
    # Simula la función que genera el archivo ZIP

    response = test_client.get('/dataset/download/all')
    assert response.status_code == 200


def test_download_all_is_zip(test_client):
    
    """Testea que el contenido devuelto sea un archivo ZIP."""
    
    response = test_client.get('/dataset/download/all')
    
    assert response.data is not None
    assert response.content_type == 'application/zip'