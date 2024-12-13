from app.modules.auth.models import User
from app import db
import pytest
from unittest.mock import patch


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture for the module.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        test_client.user_id = user_test.id

    yield test_client


def test_rate_dataset_valid(test_client):
    """
    Test rating a dataset with valid input.
    """
    with patch('app.modules.dataset.services.ds_rating_service.add_or_update_rating') as mock_add_update, \
         patch('app.modules.dataset.services.ds_rating_service.get_dataset_average_rating') as mock_get_avg:
        mock_add_update.return_value = None  # Mock does not perform any operation
        mock_get_avg.return_value = 4.2  # Mock returns a pre-defined average rating

        # Test a valid rating
        response = test_client.post(
            '/datasets/1/rate',
            json={'rating': 4},
            headers={'Authorization': f"Bearer valid_token"}
        )
        assert response.status_code == 200
        assert response.json['message'] == 'Rating added/updated'
        assert response.json['average_rating'] == 4.2

        # Ensure the mocks were called correctly
        mock_add_update.assert_called_with(1, test_client.user_id, 4)
        mock_get_avg.assert_called_with(1)


def test_rate_dataset_invalid_rating(test_client):
    """
    Test rating a dataset with invalid values.
    """
    # No need to mock services for validation failures
    invalid_ratings = ['abc', 0, 6]

    for rating in invalid_ratings:
        response = test_client.post(
            '/datasets/1/rate',
            json={'rating': rating},
            headers={'Authorization': f"Bearer valid_token"}
        )
        assert response.status_code == 400
        assert 'Invalid rating value' in response.json['message']


def test_rate_dataset_service_failure(test_client):
    """
    Test handling of exceptions in the rating service.
    """
    with patch('app.modules.dataset.services.ds_rating_service.add_or_update_rating') as mock_add_update:
        mock_add_update.side_effect = Exception('Service error')

        response = test_client.post(
            '/datasets/1/rate',
            json={'rating': 3},
            headers={'Authorization': f"Bearer valid_token"}
        )
        assert response.status_code == 500
        assert 'Service error' in response.json['error']


def test_get_average_rating(test_client):
    """
    Test fetching the average rating for a dataset.
    """
    with patch('app.modules.dataset.services.ds_rating_service.get_dataset_average_rating') as mock_get_avg:
        mock_get_avg.return_value = 4.5  # Mock average rating

        response = test_client.get('/datasets/1/average-rating')
        assert response.status_code == 200
        assert response.json['average_rating'] == 4.5

        # Ensure the mock was called correctly
        mock_get_avg.assert_called_with(1)


def test_get_average_rating_no_data(test_client):
    """
    Test fetching average rating when no ratings exist.
    """
    with patch('app.modules.dataset.services.ds_rating_service.get_dataset_average_rating') as mock_get_avg:
        mock_get_avg.return_value = None  # No ratings available

        response = test_client.get('/datasets/1/average-rating')
        assert response.status_code == 200
        assert response.json['average_rating'] is None

        # Ensure the mock was called correctly
        mock_get_avg.assert_called_with(1)
