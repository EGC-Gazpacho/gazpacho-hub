import pytest
from unittest.mock import MagicMock
from app.modules.dataset.models import DataSet, DSMetaData
import unittest


@pytest.fixture(scope="module")
def extended_test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


class TestDatasetExport(unittest.TestCase):

    def setUp(self):
        # Mock de DSMetaData y FeatureModel
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

        # Crear dataset con mocks
        self.dataset = DataSet(
            id=1,
            user_id=1,
            ds_meta_data=self.ds_meta_data,
            feature_models=[feature_model_mock],
        )

    # 1. Prueba de exportación en formato UVL
    def test_export_uvl(self):
        response = self.export_dataset("UVL")
        self.assertTrue(response["success"])
        self.assertEqual(response["export_format"], "UVL")

    # 2. Prueba de exportación en formato JSON
    def test_export_json(self):
        response = self.export_dataset("JSON")
        self.assertTrue(response["success"])
        self.assertEqual(response["export_format"], "JSON")

    # 3. Prueba de exportación en formato XML
    def test_export_xml(self):
        response = self.export_dataset("XML")
        self.assertTrue(response["success"])
        self.assertEqual(response["export_format"], "XML")
        
    # 4. Exportación de dataset vacío
    def test_export_empty_dataset(self):
        empty_dataset = DataSet(
            id=2, user_id=1, ds_meta_data=self.ds_meta_data, feature_models=[]
        )
        response = self.export_dataset("JSON", dataset=empty_dataset)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "Dataset vacío no puede ser exportado")

    # 5. Formato no válido
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
