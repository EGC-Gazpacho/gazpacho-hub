import pytest
from unittest.mock import patch,MagicMock


@pytest.fixture
def client():
    from app import create_app  # Ajusta según la estructura de tu proyecto
    app = create_app()
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True  # Deshabilita la autenticación si es necesario
    with app.test_client() as client:
        yield client


def test_download_dataset_formats(client):
    # Mock del servicio DataSetService
    with patch('app.modules.dataset.services.DataSetService') as MockDataSetService:
        mock_dataset_service = MockDataSetService.return_value
        mock_dataset = MagicMock()
        mock_dataset.user_id = 1
        mock_dataset.id = 6  # ID del dataset específico
        mock_dataset_service.get_or_404.return_value = mock_dataset

        # Formatos a probar
        formats = ["json", "yaml", "xml"]

        for file_format in formats:
            # Realizar la solicitud para descargar en el formato actual
            response = client.get(f'/dataset/download_informat/{file_format}/6')

            # Validar la respuesta HTTP
            assert response.status_code == 200, f"Failed to download dataset as {file_format}."
            assert response.mimetype == "application/zip", f"Unexpected MIME type for {file_format}."
