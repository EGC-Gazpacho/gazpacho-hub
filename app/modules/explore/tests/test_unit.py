import pytest
from unittest.mock import patch, MagicMock
from app.modules.explore.services import ExploreService

@pytest.fixture
def explore_service():
    return ExploreService()

def test_filter_query(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "machine learning"
        mock_filter.return_value = ['dataset1', 'dataset2']

        result = explore_service.filter(query=query)

        assert result == ['dataset1', 'dataset2']
        mock_filter.assert_called_once_with(query, 'newest', 'any', None, None, [], **{})

def test_filter_sorting(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        sorting = "oldest"
        mock_filter.return_value = []

        result = explore_service.filter(sorting=sorting)

        assert result == []
        mock_filter.assert_called_once_with("", sorting, 'any', None, None, [], **{})

def test_filter_publication_type(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        publication_type = "journal"
        mock_filter.return_value = ['dataset1']

        result = explore_service.filter(publication_type=publication_type)

        assert result == ['dataset1']
        mock_filter.assert_called_once_with("", 'newest', publication_type, None, None, [], **{})

def test_filter_with_multiple_parameters(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "AI"
        sorting = "newest"
        publication_type = "conference"
        number_of_features = 10
        number_of_products = 5
        tags = ["neural networks", "deep learning"]

        mock_filter.return_value = ['dataset1', 'dataset2']

        result = explore_service.filter(
            query=query,
            sorting=sorting,
            publication_type=publication_type,
            number_of_features=number_of_features,
            number_of_products=number_of_products,
            tags=tags
        )

        assert result == ['dataset1', 'dataset2']
        mock_filter.assert_called_once_with(
            query, sorting, publication_type, number_of_features, number_of_products, tags, **{}
        )

def test_filter_invalid_parameters(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        mock_filter.side_effect = ValueError("Invalid parameters")

        with pytest.raises(ValueError, match="Invalid parameters"):
            explore_service.filter(query=None, sorting="invalid_sort")

def test_filter_number_of_features(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        number_of_features = 10
        mock_filter.return_value = ['dataset1']

        result = explore_service.filter(number_of_features=number_of_features)

        assert result == ['dataset1']
        mock_filter.assert_called_once_with("", 'newest', 'any', number_of_features, None, [], **{})

def test_filter_number_of_products(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        number_of_products = 20
        mock_filter.return_value = ['dataset2']

        result = explore_service.filter(number_of_products=number_of_products)

        assert result == ['dataset2']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, number_of_products, [], **{})

def test_filter_tags(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = ["AI", "big data"]
        mock_filter.return_value = ['dataset3']

        result = explore_service.filter(tags=tags)

        assert result == ['dataset3']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, tags, **{})

def test_filter_combined_with_number_features_and_products(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        number_of_features = 15
        number_of_products = 30
        mock_filter.return_value = ['dataset4', 'dataset5']

        result = explore_service.filter(number_of_features=number_of_features, number_of_products=number_of_products)

        assert result == ['dataset4', 'dataset5']
        mock_filter.assert_called_once_with("", 'newest', 'any', number_of_features, number_of_products, [], **{})
