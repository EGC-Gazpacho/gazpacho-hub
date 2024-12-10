import pytest
from flask import url_for
from app import create_app, db


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://uvlhub_user:uvlhub_password@127.0.0.1:3306/uvlhubdb_test' 
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_model_search_by_name(test_client):
    # Test for the search query 'Test Model 1'
    response = test_client.get(url_for('explore.explore2_models', query='Feature Model 1'))
    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Another Model' not in response.data


def test_model_search_non_existent(test_client):
    # Test for a non-existent model
    response = test_client.get(url_for('explore.explore2_models', query='NonExistentModel'))
    assert response.status_code == 200


def test_model_search_partial_match(test_client):
    # Test for a partial match
    response = test_client.get(url_for('explore.explore2_models', query='Feature Model'))
    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Another Model' not in response.data


def test_model_search_case_insensitivity(test_client):
    # Test for case insensitivity
    response = test_client.get(url_for('explore.explore2_models', query='feature model 1'))
    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Another Model' not in response.data


def test_model_search_multiple_matches(test_client):
    # Test for multiple matches
    response = test_client.get(url_for('explore.explore2_models', query='Model'))
    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Feature Model 2' in response.data
