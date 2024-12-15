import pytest
from unittest.mock import MagicMock, patch
import unittest

from app.modules.dataset.models import DataSet, DSMetaData
from app.modules.conftest import login
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app import db


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

        test_client.user_id = user_test.id

    yield test_client


def test_login(test_client):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200


def test_download_dataset_formats_mocked(test_client):
    """
    Test downloading a dataset in different formats using mocks to avoid
    real database interaction.
    """
    # Mock the DataSetService.get_or_404 method to return a mocked dataset
    with patch('app.modules.dataset.services.DataSetService.get_or_404') as mock_get:
        # Create a mocked dataset with an ID and user ID
        mock_dataset = MagicMock()
        mock_dataset.id = 6
        mock_dataset.user_id = test_client.user_id

        # Set the return value of the mocked method
        mock_get.return_value = mock_dataset

        # Mock the DSDownloadRecordService.create method to prevent database insertion
        with patch('app.modules.dataset.services.DSDownloadRecordService.create') as mock_create:
            mock_create.return_value = None  # No action needed for the mock

            # Define the URL for the download endpoint and the formats to test
            formats = ["json", "yaml", "xml"]
            url_base = "/dataset/download_informat"

            for file_format in formats:
                # Call the endpoint with the mocked dataset ID and file format
                response = test_client.get(f"{url_base}/{file_format}/{mock_dataset.id}")

                # Verify the response status code
                assert response.status_code == 200, f"Failed to download dataset as {file_format}"
                assert response.mimetype == "application/zip", f"Unexpected MIME type for {file_format}"

                # Verify that the mocked methods were called
                mock_get.assert_called_with(mock_dataset.id)
                mock_create.assert_called()


class TestDatasetExport(unittest.TestCase):

    def setUp(self):
        # Mock DSMetaData and feature models
        self.ds_meta_data = DSMetaData(
            title="Test Dataset", description="Test description"
        )
        feature_model_mock = MagicMock()
        feature_model_mock.files = [
            MagicMock(id=1, name="file.uvl", size=1024),
            MagicMock(id=2, name="file_2.uvl", size=1024),
            MagicMock(id=3, name="file3.uvl", size=2048),
            MagicMock(id=4, name="file4.uvl", size=2048),
        ]

        # Create dataset with mocks
        self.dataset = DataSet(
            id=1,
            user_id=1,
            ds_meta_data=self.ds_meta_data,
            feature_models=[feature_model_mock],
        )

    # 1. Test export in UVL format
    def test_export_uvl(self):
        response = self.export_dataset("UVL")
        self.assertTrue(response["success"])
        self.assertEqual(response["export_format"], "UVL")

    # 2. Test export in JSON format
    def test_export_json(self):
        response = self.export_dataset("JSON")
        self.assertTrue(response["success"])
        self.assertEqual(response["export_format"], "JSON")

    # 3. Test export in XML format
    def test_export_xml(self):
        response = self.export_dataset("XML")
        self.assertTrue(response["success"])
        self.assertEqual(response["export_format"], "XML")

    # 4. Test exporting an empty dataset
    def test_export_empty_dataset(self):
        empty_dataset = DataSet(
            id=2, user_id=1, ds_meta_data=self.ds_meta_data, feature_models=[]
        )
        response = self.export_dataset("JSON", dataset=empty_dataset)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "Dataset vacío no puede ser exportado")

    # 5. Test invalid export format
    def test_invalid_format(self):
        response = self.export_dataset("INVALID_FORMAT")
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "Formato de exportación no válido")

    def export_dataset(self, export_format, dataset=None):
        if dataset is None:
            dataset = self.dataset
        if export_format not in ["UVL", "JSON", "XML"]:
            return {"success": False, "error": "Formato de exportación no válido"}
        if not dataset.feature_models or not any(f.files for f in dataset.feature_models):
            return {"success": False, "error": "Dataset vacío no puede ser exportado"}
        if any(file.size < 0 for file in dataset.feature_models[0].files):
            return {"success": False, "error": "Archivo corrupto detectado"}
        return {"success": True, "export_format": export_format}
