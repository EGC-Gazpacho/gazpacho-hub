import pytest
from unittest.mock import patch
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

        # Log in the test client
        test_client.post('/login', json={
            'email': "rater@example.com",
            'password': "password123"
        })

        # Store user ID in the test client
        test_client.user_id = user_test.id

    yield test_client


@pytest.fixture
def auth_headers(test_client_with_ratings):
    """Simulate authentication headers for the logged-in user."""
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {test_client_with_ratings.user_id}'
    }


def test_rate_dataset_success(test_client_with_ratings, auth_headers):
    with patch('app.modules.dataset.services.DSRatingService.add_or_update_rating') as mock_add_rating, \
         patch('app.modules.dataset.services.DSRatingService.get_dataset_average_rating') as mock_avg_rating:

        mock_add_rating.return_value = None
        mock_avg_rating.return_value = 4.0

        response = test_client_with_ratings.post(
            '/datasets/1/rate',
            json={'rating': 5},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json['message'] == 'Rating added/updated'
        assert response.json['average_rating'] == 4.0
        mock_add_rating.assert_called_once_with(1, test_client_with_ratings.user_id, 5)
        mock_avg_rating.assert_called_once_with(1)
