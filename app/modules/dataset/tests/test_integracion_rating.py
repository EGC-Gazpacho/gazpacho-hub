import pytest
from unittest.mock import patch, MagicMock
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app import db


@pytest.fixture(scope="module")
def test_client_with_ratings(test_client):
    """
    Extends the test_client fixture to add specific data for DSRatingService testing.
    """
    with test_client.application.app_context():
        # Create a test user
        user_test = User(email="rater@example.com", password="password123")
        db.session.add(user_test)
        db.session.commit()

        # Add a user profile
        profile = UserProfile(user_id=user_test.id, name="Rater", surname="Example")
        db.session.add(profile)
        db.session.commit()

        # Store user ID in the test client
        test_client.user_id = user_test.id

    yield test_client


def test_add_or_update_rating_mocked(test_client_with_ratings):
    """
    Test adding or updating a dataset rating using mocks.
    """
    with patch('app.services.DSRatingService.add_or_update_rating') as mock_add_rating:
        # Mock the return value of the service
        mock_add_rating.return_value = MagicMock(
            id=1, ds_meta_data_id=1, user_id=test_client_with_ratings.user_id, rating=4
        )

        # Call the rating endpoint
        response = test_client_with_ratings.post(
            '/datasets/1/rate',
            json={'rating': 4}
        )

        # Assert response and mock calls
        assert response.status_code == 200, "Failed to add or update rating"
        assert response.json['message'] == "Rating added/updated"
        mock_add_rating.assert_called_once_with(1, test_client_with_ratings.user_id, 4)


def test_get_average_rating_mocked(test_client_with_ratings):
    """
    Test retrieving average rating for a dataset using mocks.
    """
    with patch('app.services.DSRatingService.get_dataset_average_rating') as mock_avg_rating:
        # Mock the average rating
        mock_avg_rating.return_value = 4.5

        # Call the average rating endpoint
        response = test_client_with_ratings.get('/datasets/1/average-rating')

        # Assert response and mock calls
        assert response.status_code == 200, "Failed to retrieve average rating"
        assert response.json['average_rating'] == 4.5
        mock_avg_rating.assert_called_once_with(1)


def test_invalid_rating_value(test_client_with_ratings):
    """
    Test endpoint response for invalid rating values.
    """
    invalid_ratings = [-1, 0, 6, "string"]
    for invalid_rating in invalid_ratings:
        # Call the rating endpoint with invalid data
        response = test_client_with_ratings.post(
            '/datasets/1/rate',
            json={'rating': invalid_rating}
        )

        # Assert response for invalid input
        assert response.status_code == 400, f"Accepted invalid rating {invalid_rating}"
        assert "Invalid rating value" in response.json['message']


def test_view_dataset_with_average_rating_mocked(test_client_with_ratings):
    """
    Test viewing a dataset with its average rating using mocks.
    """
    with patch('app.services.DataSetService.get_dataset_by_id') as mock_get_dataset, \
            patch('app.services.DSRatingService.get_dataset_average_rating') as mock_avg_rating:

        # Mock the dataset and average rating
        mock_dataset = MagicMock(id=1, ds_meta_data=MagicMock(rating=None))
        mock_get_dataset.return_value = mock_dataset
        mock_avg_rating.return_value = 4.0

        # Call the view dataset endpoint
        response = test_client_with_ratings.get('/datasets/1')

        # Assert response and mock calls
        assert response.status_code == 200, "Failed to view dataset"
        mock_get_dataset.assert_called_once_with(1)
        mock_avg_rating.assert_called_once_with(1)
