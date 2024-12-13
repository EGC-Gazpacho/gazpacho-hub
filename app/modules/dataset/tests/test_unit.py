import pytest
from app import create_app
import io
from unittest.mock import patch
from datetime import datetime


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


@patch('app.modules.dataset.services.DataSetService.zip_all_datasets')
def test_download_all_filename(mock_generar_zip, test_client):
    """Testea que el archivo ZIP tenga un nombre específico con la fecha actual."""
    mock_generar_zip.return_value = io.BytesIO(b'simulated zip content')

    response = test_client.get('/dataset/download/all')

    # Generar el nombre esperado del archivo con la fecha actual
    current_date = datetime.now().strftime("%Y_%m_%d")
    expected_filename = f"attachment; filename=all_datasets_{current_date}.zip"

    # Verificar que el encabezado 'Content-Disposition' tenga el nombre esperado
    assert response.headers['Content-Disposition'] == expected_filename
    mock_generar_zip.assert_called_once()


@patch('os.listdir')
@patch('app.modules.dataset.services.DataSetService.is_synchronized')
def test_zip_all_datasets_no_datasets(mock_is_synchronized, mock_listdir, test_client):
    """Testea que la función devuelva un error 404 si no hay datasets sincronizados."""
    # Mockear el sistema de archivos para que no haya datasets sincronizados
    mock_listdir.side_effect = lambda path: [] if path == "uploads" else []
    mock_is_synchronized.return_value = False

    # Ejecutar la solicitud y verificar que la respuesta sea 404
    response = test_client.get('/dataset/download/all')

    # Verificar que el código de estado sea 404
    assert response.status_code == 404


@patch('os.listdir')
@patch('app.modules.dataset.services.DataSetService.is_synchronized')
def test_zip_all_datasets_no_users(mock_is_synchronized, mock_listdir, test_client):
    """Testea que no se genera un archivo ZIP si no hay directorios de usuarios."""
    # Mockear para que no haya directorios de usuarios
    mock_listdir.side_effect = lambda path: []  # No hay usuarios

    # Ejecutar la solicitud y verificar que se devuelve un error 404
    response = test_client.get('/dataset/download/all')

    # Verificar que el código de estado sea 404
    assert response.status_code == 404
