import pytest
from unittest.mock import patch
from flask import url_for
from app import create_app


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'
    with app.test_client() as client:
        with app.app_context():
            yield client


@patch('app.modules.explore.services.ModelService.filter')
def test_model_search_by_name(mock_filter, test_client):
    mock_filter.return_value = [
        {
            "id": 1,
            "data_set_id": 10,
            "data_set_title": "Dataset Title 1",
            "fm_meta_data": {
                "uvl_filename": "model1.uvl",
                "title": "Feature Model 1",
                "description": "Description of Feature Model 1",
                "publication_type": "ARTICLE",
                "publication_doi": "10.1234/model1",
                "tags": "tag1,tag2",
                "uvl_version": "1.0"
            }
        }
    ]

    response = test_client.get(url_for('explore.explore2_models', query='Feature Model 1'))

    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Another Model' not in response.data
    mock_filter.assert_called_once_with(name='Feature Model 1')


@patch('app.modules.explore.services.ModelService.filter')
def test_model_search_partial_match(mock_filter, test_client):
    mock_filter.return_value = [
        {
            "id": 1,
            "data_set_id": 10,
            "data_set_title": "Dataset Title 1",
            "fm_meta_data": {
                "uvl_filename": "model1.uvl",
                "title": "Feature Model 1",
                "description": "Description of Feature Model 1",
                "publication_type": "ARTICLE",
                "publication_doi": "10.1234/model1",
                "tags": "tag1,tag2",
                "uvl_version": "1.0"
            }
        }
    ]

    response = test_client.get(url_for('explore.explore2_models', query='Model'))

    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Another Model' not in response.data
    mock_filter.assert_called_once_with(name='Model')


@patch('app.modules.explore.services.ModelService.filter')
def test_model_search_non_existent(mock_filter, test_client):
    mock_filter.return_value = []

    response = test_client.get(url_for('explore.explore2_models', query='NonExistentModel'))

    assert response.status_code == 200
    assert b'NonExistentModel' not in response.data
    mock_filter.assert_called_once_with(name='NonExistentModel')


@patch('app.modules.explore.services.ModelService.filter')
def test_model_search_case_insensitivity(mock_filter, test_client):
    mock_filter.return_value = [
        {
            "id": 1,
            "data_set_id": 10,
            "data_set_title": "Dataset Title 1",
            "fm_meta_data": {
                "uvl_filename": "model1.uvl",
                "title": "Feature Model 1",
                "description": "Description of Feature Model 1",
                "publication_type": "ARTICLE",
                "publication_doi": "10.1234/model1",
                "tags": "tag1,tag2",
                "uvl_version": "1.0"
            }
        }
    ]

    response = test_client.get(url_for('explore.explore2_models', query='feature Model 1'))

    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Another Model' not in response.data
    mock_filter.assert_called_once_with(name='feature Model 1')


@patch('app.modules.explore.services.ModelService.filter')
def test_model_search_multiple_matches(mock_filter, test_client):
    mock_filter.return_value = [
        {
            "id": 1,
            "data_set_id": 10,
            "data_set_title": "Dataset Title 1",
            "fm_meta_data": {
                "uvl_filename": "model1.uvl",
                "title": "Feature Model 1",
                "description": "Description of Feature Model 1",
                "publication_type": "ARTICLE",
                "publication_doi": "10.1234/model1",
                "tags": "tag1,tag2",
                "uvl_version": "1.0"
            }
        },
        {
            "id": 2,
            "data_set_id": 11,
            "data_set_title": "Dataset Title 2",
            "fm_meta_data": {
                "uvl_filename": "model2.uvl",
                "title": "Feature Model 2",
                "description": "Description of Feature Model 2",
                "publication_type": "CONFERENCE",
                "publication_doi": "10.1234/model2",
                "tags": "tag3,tag4",
                "uvl_version": "2.0"
            }
        }
    ]

    response = test_client.get(url_for('explore.explore2_models', query='Model'))

    assert response.status_code == 200
    assert b'Feature Model 1' in response.data
    assert b'Feature Model 2' in response.data
    assert b'Another Model' not in response.data
    mock_filter.assert_called_once_with(name='Model')
