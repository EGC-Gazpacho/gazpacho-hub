import pytest
from unittest.mock import patch
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


def test_filter_edge_case_empty_query(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        mock_filter.return_value = []

        result = explore_service.filter(query="")

        assert result == []
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, [], **{})


def test_filter_large_number_of_tags(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = [f"tag{i}" for i in range(100)]
        mock_filter.return_value = ['dataset_large_tags']

        result = explore_service.filter(tags=tags)

        assert result == ['dataset_large_tags']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, tags, **{})


def test_filter_special_characters_in_query(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "@#*&^%$"
        mock_filter.return_value = []

        result = explore_service.filter(query=query)

        assert result == []
        mock_filter.assert_called_once_with(query, 'newest', 'any', None, None, [], **{})


def test_filter_combination_publication_and_features(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        publication_type = "journal"
        number_of_features = 50
        mock_filter.return_value = ['dataset_pub_features']

        result = explore_service.filter(publication_type=publication_type, number_of_features=number_of_features)

        assert result == ['dataset_pub_features']
        mock_filter.assert_called_once_with("", 'newest', publication_type, number_of_features, None, [], **{})


def test_filter_no_results(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        mock_filter.return_value = []

        result = explore_service.filter(query="nonexistent")

        assert result == []
        mock_filter.assert_called_once_with("nonexistent", 'newest', 'any', None, None, [], **{})


def test_filter_with_null_values(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        mock_filter.return_value = ['dataset_null_handling']

        result = explore_service.filter(query=None, tags=None)

        assert result == ['dataset_null_handling']
        mock_filter.assert_called_once_with(None, 'newest', 'any', None, None, None, **{})


def test_filter_case_insensitivity_query(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "Machine Learning"
        mock_filter.return_value = ['dataset_case_insensitive']

        result = explore_service.filter(query=query)

        assert result == ['dataset_case_insensitive']
        mock_filter.assert_called_once_with(query, 'newest', 'any', None, None, [], **{})


def test_filter_edge_case_special_tag_matching(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = ["*special_tag*"]
        mock_filter.return_value = ['dataset_special_tag']

        result = explore_service.filter(tags=tags)

        assert result == ['dataset_special_tag']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, tags, **{})


def test_filter_high_number_of_features(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        number_of_features = 1000000
        mock_filter.return_value = ['dataset_high_features']

        result = explore_service.filter(number_of_features=number_of_features)

        assert result == ['dataset_high_features']
        mock_filter.assert_called_once_with("", 'newest', 'any', number_of_features, None, [], **{})


def test_filter_high_number_of_products(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        number_of_products = 1000000
        mock_filter.return_value = ['dataset_high_products']

        result = explore_service.filter(number_of_products=number_of_products)

        assert result == ['dataset_high_products']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, number_of_products, [], **{})


def test_filter_invalid_tag_format(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = ["invalid tag format"]
        mock_filter.return_value = []

        result = explore_service.filter(tags=tags)

        assert result == []
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, tags, **{})


def test_filter_partial_matches_query(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "partial match"
        mock_filter.return_value = ['dataset_partial']

        result = explore_service.filter(query=query)

        assert result == ['dataset_partial']
        mock_filter.assert_called_once_with(query, 'newest', 'any', None, None, [], **{})


def test_filter_empty_tags(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = []
        mock_filter.return_value = ['dataset_empty_tags']

        result = explore_service.filter(tags=tags)

        assert result == ['dataset_empty_tags']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, tags, **{})


def test_filter_combination_query_and_tags(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "AI"
        tags = ["machine learning", "big data"]
        mock_filter.return_value = ['dataset_query_tags']

        result = explore_service.filter(query=query, tags=tags)

        assert result == ['dataset_query_tags']
        mock_filter.assert_called_once_with(query, 'newest', 'any', None, None, tags, **{})


def test_filter_edge_case_empty_features_and_products(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        number_of_features = 0
        number_of_products = 0
        mock_filter.return_value = []

        result = explore_service.filter(number_of_features=number_of_features, number_of_products=number_of_products)

        assert result == []
        mock_filter.assert_called_once_with("", 'newest', 'any', number_of_features, number_of_products, [], **{})


def test_filter_combined_high_tags_and_features(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = [f"tag{i}" for i in range(50)]
        number_of_features = 500
        mock_filter.return_value = ['dataset_high_tags_features']

        result = explore_service.filter(tags=tags, number_of_features=number_of_features)

        assert result == ['dataset_high_tags_features']
        mock_filter.assert_called_once_with("", 'newest', 'any', number_of_features, None, tags, **{})


def test_filter_high_publication_and_products(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        publication_type = "conference"
        number_of_products = 10000
        mock_filter.return_value = ['dataset_high_pub_products']

        result = explore_service.filter(publication_type=publication_type, number_of_products=number_of_products)

        assert result == ['dataset_high_pub_products']
        mock_filter.assert_called_once_with("", 'newest', publication_type, None, number_of_products, [], **{})


def test_filter_mixed_valid_and_invalid_tags(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = ["valid_tag", "???invalid!!!"]
        mock_filter.return_value = ['dataset_valid']

        result = explore_service.filter(tags=tags)

        assert result == ['dataset_valid']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, tags, **{})


def test_filter_combined_query_and_high_features(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "AI advancements"
        number_of_features = 10000
        mock_filter.return_value = ['dataset_query_high_features']

        result = explore_service.filter(query=query, number_of_features=number_of_features)

        assert result == ['dataset_query_high_features']
        mock_filter.assert_called_once_with(query, 'newest', 'any', number_of_features, None, [], **{})


def test_filter_combined_publication_type_and_tags(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        publication_type = "journal"
        tags = ["AI", "data analysis"]
        mock_filter.return_value = ['dataset_pub_tags']

        result = explore_service.filter(publication_type=publication_type, tags=tags)

        assert result == ['dataset_pub_tags']
        mock_filter.assert_called_once_with("", 'newest', publication_type, None, None, tags, **{})


def test_filter_combined_all_parameters(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "AI future"
        sorting = "oldest"
        publication_type = "conference"
        number_of_features = 20
        number_of_products = 30
        tags = ["machine learning", "big data"]
        mock_filter.return_value = ['dataset_all_params']

        result = explore_service.filter(
            query=query,
            sorting=sorting,
            publication_type=publication_type,
            number_of_features=number_of_features,
            number_of_products=number_of_products,
            tags=tags
        )

        assert result == ['dataset_all_params']
        mock_filter.assert_called_once_with(
            query, sorting, publication_type, number_of_features, number_of_products, tags, **{}
        )


def test_filter_no_parameters_provided(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        mock_filter.return_value = ['dataset_no_params']

        result = explore_service.filter()

        assert result == ['dataset_no_params']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, None, [], **{})


def test_filter_empty_publication_type(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        publication_type = ""
        mock_filter.return_value = []

        result = explore_service.filter(publication_type=publication_type)

        assert result == []
        mock_filter.assert_called_once_with("", 'newest', publication_type, None, None, [], **{})


def test_filter_tags_and_products_combined(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        tags = ["big data"]
        number_of_products = 50
        mock_filter.return_value = ['dataset_tags_products']

        result = explore_service.filter(tags=tags, number_of_products=number_of_products)

        assert result == ['dataset_tags_products']
        mock_filter.assert_called_once_with("", 'newest', 'any', None, number_of_products, tags, **{})


def test_filter_invalid_query_combined_with_valid_tags(explore_service):
    with patch.object(explore_service.repository, 'filter') as mock_filter:
        query = "???invalid_query??"
        tags = ["AI"]
        mock_filter.return_value = ['dataset_invalid_query_tags']

        result = explore_service.filter(query=query, tags=tags)

        assert result == ['dataset_invalid_query_tags']
        mock_filter.assert_called_once_with(query, 'newest', 'any', None, None, tags, **{})
