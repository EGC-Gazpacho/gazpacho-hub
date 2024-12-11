import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm.query import Query
from app.modules.dataset.models import DataSet, DSMetaData, Author, DSMetrics, PublicationType
from app.modules.featuremodel.models import FMMetaData
from app.modules.explore.repository import ExploreRepository

class TestExploreRepositoryFilter(unittest.TestCase):
    def setUp(self):
        # Instanciar el repositorio y simular el modelo
        self.repo = ExploreRepository()
        self.repo.model = MagicMock()  # Simula el modelo DataSet

    @patch("app.modules.explore.repository.DSMetaData")  # Simular DSMetaData
    @patch("app.modules.explore.repository.FeatureModel")  # Simular FeatureModel
    @patch("app.modules.explore.repository.Author")  # Simular Author
    def test_filter_basic_query(self, MockAuthor, MockFeatureModel, MockDSMetaData):
        # Simula una consulta de SQLAlchemy
        mock_query = MagicMock(spec=Query)
        self.repo.model.query = mock_query

        # Simula el retorno de la consulta
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = ["dataset_1", "dataset_2"]

        # Ejecutar la función con un query básico
        result = self.repo.filter(query="example query")

        # Verifica que los métodos SQLAlchemy se llamen correctamente
        mock_query.join.assert_any_call(DataSet.ds_meta_data)
        mock_query.filter.assert_called()  # Verifica que .filter() sea llamado
        mock_query.order_by.assert_called()  # Verifica que .order_by() sea llamado
        mock_query.all.assert_called_once()  # Verifica que .all() sea llamado una vez

        # Verifica el resultado esperado
        self.assertEqual(result, ["dataset_1", "dataset_2"])

    @patch("app.modules.explore.repository.DSMetaData")  # Simular DSMetaData
    def test_filter_with_tags(self, MockDSMetaData):
        # Simula una consulta de SQLAlchemy
        mock_query = MagicMock(spec=Query)
        self.repo.model.query = mock_query

        # Simula el retorno de la consulta
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = ["dataset_with_tags"]

        # Ejecutar la función con tags
        result = self.repo.filter(query="tag_query", tags=["tag1", "tag2"])

        # Verifica que se agregaron los filtros correspondientes
        mock_query.filter.assert_any_call(DSMetaData.tags.ilike("%tag1%"))
        mock_query.filter.assert_any_call(DSMetaData.tags.ilike("%tag2%"))

        # Verifica el resultado esperado
        self.assertEqual(result, ["dataset_with_tags"])
    
    @patch("app.modules.explore.repository.DSMetaData")  # Simular DSMetaData
    def test_filter_with_sorting(self, MockDSMetaData):
        # Simula una consulta de SQLAlchemy
        mock_query = MagicMock(spec=Query)
        self.repo.model.query = mock_query

        # Simula el retorno de la consulta
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = ["dataset_sorted"]

        # Ejecutar la función con sorting por "oldest"
        result = self.repo.filter(query="", sorting="oldest")

        # Verifica que se usó el orden correcto
        mock_query.order_by.assert_called_once_with(self.repo.model.created_at.asc())

        # Verifica el resultado esperado
        self.assertEqual(result, ["dataset_sorted"])

    @patch("app.modules.explore.repository.DSMetaData")  # Simular DSMetaData
    def test_filter_with_publication_type(self, MockDSMetaData):
        # Simula una consulta de SQLAlchemy
        mock_query = MagicMock(spec=Query)
        self.repo.model.query = mock_query

        # Simula el retorno de la consulta
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = ["dataset_publication"]

        # Ejecutar la función con un tipo de publicación específico
        result = self.repo.filter(query="", publication_type="journal")

        # Verifica que el filtro para publication_type se agregó
        mock_query.filter.assert_any_call(DSMetaData.publication_type == "JOURNAL")

        # Verifica el resultado esperado
        self.assertEqual(result, ["dataset_publication"])

    @patch("app.modules.explore.repository.DSMetrics")  # Simular DSMetrics
    def test_filter_with_number_of_features(self, MockDSMetrics):
        # Simula una consulta de SQLAlchemy
        mock_query = MagicMock(spec=Query)
        self.repo.model.query = mock_query

        # Simula el retorno de la consulta
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = ["dataset_features"]

        # Ejecutar la función con un número específico de características
        result = self.repo.filter(query="", number_of_features=10)

        # Verifica que el filtro para number_of_features se agregó
        mock_query.filter.assert_any_call(DSMetrics.number_of_features == 10)

        # Verifica el resultado esperado
        self.assertEqual(result, ["dataset_features"])

    @patch("app.modules.explore.repository.DSMetrics")  # Simular DSMetrics
    def test_filter_with_number_of_products(self, MockDSMetrics):
        # Simula una consulta de SQLAlchemy
        mock_query = MagicMock(spec=Query)
        self.repo.model.query = mock_query

        # Simula el retorno de la consulta
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = ["dataset_products"]

        # Ejecutar la función con un número específico de productos
        result = self.repo.filter(query="", number_of_products=5)

        # Verifica que el filtro para number_of_products se agregó
        mock_query.filter.assert_any_call(DSMetrics.number_of_products == 5)

        # Verifica el resultado esperado
        self.assertEqual(result, ["dataset_products"])
