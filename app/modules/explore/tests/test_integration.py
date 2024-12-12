import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.dataset.models import DSMetaData, DSMetrics, DataSet, PublicationType

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add test datasets for filtering.
    """
    with test_client.application.app_context():
        # Create a test user
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        # Create test data with relationships
        dataset1 = DataSet(
            user_id=user_test.id,
            ds_meta_data=DSMetaData(
                deposition_id=1,
                title="AI Dataset",
                description="A dataset on AI.",
                publication_type=PublicationType.JOURNAL_ARTICLE,
                tags="ai,ml",
                ds_metrics=DSMetrics(number_of_models="10", number_of_features=50, number_of_products=5)
            )
        )
        dataset2 = DataSet(
            user_id=user_test.id,
            ds_meta_data=DSMetaData(
                deposition_id=2,
                title="ML Dataset",
                description="A dataset on ML.",
                publication_type=PublicationType.CONFERENCE_PAPER,
                tags="ml",
                ds_metrics=DSMetrics(number_of_models="5", number_of_features=30, number_of_products=2)
            )
        )
        dataset3 = DataSet(
            user_id=user_test.id,
            ds_meta_data=DSMetaData(
                deposition_id=3,
                title="Physics Dataset",
                description="A dataset on Physics.",
                publication_type=PublicationType.REPORT,
                tags="physics",
                ds_metrics=DSMetrics(number_of_models="2", number_of_features=10, number_of_products=1)
            )
        )

        # Add all datasets in one go
        db.session.add_all([dataset1, dataset2, dataset3])
        db.session.commit()


    yield test_client


def test_filter_by_query(test_client):
    """
    Test filtering datasets by query via POST request.
    """

    assert DataSet.query.count() > 0, "No datasets found in the database."

    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Perform a filtering request with query "ai"
    response = test_client.post('/explore', json={"query": "ai"}, follow_redirects=True)
    assert response.status_code == 200, "Filtering datasets by query failed."

    json_data = response.get_json()
    assert not any(dataset['title'] == "Physics Dataset" for dataset in json_data), "Physics Dataset incorrectly appeared in filtering results."

    logout(test_client)

def test_filter_by_features_count(test_client):
    """
    Test filtering datasets by features count via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post('/explore', json={"number_of_features": 50}, follow_redirects=True)
    assert response.status_code == 200, "Filtering datasets by features count failed."

    json_data = response.get_json()
    assert len(json_data) == 0, "Size is not 0"
    assert not any(dataset['title'] == "ML Dataset" for dataset in json_data), "ML Dataset was not found in the filtering results."
    assert not any(dataset['title'] == "Physics Dataset" for dataset in json_data), "Physics Dataset incorrectly appeared in filtering results."

    logout(test_client)

def test_combined_filtering(test_client):
    """
    Test filtering datasets with multiple parameters via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post('/explore', json={"query": "ml", "number_of_features": 20}, follow_redirects=True)
    assert response.status_code == 200, "Combined filtering request failed."

    json_data = response.get_json()
    assert not any(dataset['title'] == "Physics Dataset" for dataset in json_data), "Physics Dataset incorrectly appeared in filtering results."

    logout(test_client)

def test_no_filter_results(test_client):
    """
    Test filtering datasets with no matching results via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Perform a filtering request with a non-matching query
    response = test_client.post('/explore', json={"query": "nonexistent"}, follow_redirects=True)
    assert response.status_code == 200, "Filtering datasets with no results failed."

    json_data = response.get_json()
    assert len(json_data) == 0, "Nonexistent query returned unexpected results."

    logout(test_client)