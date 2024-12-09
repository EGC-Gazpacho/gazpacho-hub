"""sumary_line

Keyword arguments:
argument -- description
Return: return_description
""

import pytest
from unittest.mock import patch
from app import create_app, db
from app.modules.featuremodel.services import FeatureModelService
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile
from flask import url_for
@pytest.fixture(scope='module')
def test_client():
    #Extends the test_client fixture to add additional specific data for module testing.
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def mock_models():
    model1 = FeatureModel(fm_meta_data=FMMetaData(title='Model1'))
    model2 = FeatureModel(fm_meta_data=FMMetaData(title='Model2'))
    file1 = Hubfile(name='file1.uvl', size=1024, model=model1)
    file2 = Hubfile(name='file2.uvl', size=2048, model=model2)
    return [model1, model2, file1, file2]

def test_explore_models_page(test_client, mock_models):
    with patch.object(FeatureModelService, 'get_all', return_value=mock_models[:2]):
        response = test_client.get(url_for('explore.index'))
        assert response.status_code == 200
        assert b"Explore Models" in response.data
        assert b"Model1" in response.data
        assert b"Model2" in response.data

def test_search_model_success(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
        response = test_client.get(url_for('explore.index', query='Model1'))
        assert response.status_code == 200
        assert b"Model1" in response.data
        assert b"Model2" not in response.data

def test_search_model_no_results(test_client):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[]):
        response = test_client.get(url_for('explore.index', query='NonExistentModel'))
        assert response.status_code == 200
        assert b"No models found" in response.data

def test_download_model(test_client, mock_models):
    with patch.object(FeatureModelService, 'get_by_id', return_value=mock_models[0]):
        response = test_client.get(url_for('hubfile.download_file', file_id=mock_models[0].id))
        assert response.status_code == 200
        assert response.headers['Content-Disposition'] == f'attachment; filename=
        {mock_models[0].fm_meta_data.title}.uvl'

def test_model_file_display(test_client, mock_models):
    with patch.object(FeatureModelService, 'get_all', return_value=mock_models[:2]):
        response = test_client.get(url_for('explore.index'))
        assert response.status_code == 200
        assert b"file1.uvl" in response.data
        assert b"1 KB" in response.data  # Assuming size is formatted as "1 KB"
        assert b"file2.uvl" in response.data
        assert b"2 KB" in response.data  # Assuming size is formatted as "2 KB"

def test_model_file_download_link(test_client, mock_models):
    with patch.object(FeatureModelService, 'get_all', return_value=mock_models[:2]):
        response = test_client.get(url_for('explore.index'))
        assert response.status_code == 200
        assert b'href="/hubfile/download_file?file_id=' in response.data

def test_model_search_with_file(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
        response = test_client.get(url_for('explore.index', query='file1.uvl'))
        assert response.status_code == 200
        assert b"Model1" in response.data
        assert b"file1.uvl" in response.data

def test_model_search_with_partial_title(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=mock_models[:2]):
        response = test_client.get(url_for('explore.index', query='Model'))
        assert response.status_code == 200
        assert b"Model1" in response.data
        assert b"Model2" in response.data

def test_model_search_with_partial_file_name(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=mock_models[:2]):
        response = test_client.get(url_for('explore.index', query='file'))
        assert response.status_code == 200
        assert b"file1.uvl" in response.data
        assert b"file2.uvl" in response.data

def test_model_search_with_size(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
        response = test_client.get(url_for('explore.index', query='1024'))
        assert response.status_code == 200
        assert b"file1.uvl" in response.data
        assert b"file2.uvl" not in response.data

def test_model_search_with_nonexistent_size(test_client):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[]):
        response = test_client.get(url_for('explore.index', query='9999'))
        assert response.status_code == 200
        assert b"No models found" in response.data

def test_model_search_with_title_and_file(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
        response = test_client.get(url_for('explore.index', query='Model1 file1.uvl'))
        assert response.status_code == 200
        assert b"Model1" in response.data
        assert b"file1.uvl" in response.data

def test_model_search_with_title_and_size(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
        response = test_client.get(url_for('explore.index', query='Model1 1024'))
        assert response.status_code == 200
        assert b"Model1" in response.data
        assert b"file1.uvl" in response.data

def test_model_search_with_file_and_size(test_client, mock_models):
    @pytest.fixture(scope='module')
    def test_client():

        #Extends the test_client fixture to add additional specific data for module testing.

        app = create_app()
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = 'localhost'  # Add SERVER_NAME configuration
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()

    @pytest.fixture
    def mock_models():
        model1 = FeatureModel(fm_meta_data=FMMetaData(title='Model1'))
        model2 = FeatureModel(fm_meta_data=FMMetaData(title='Model2'))
        file1 = Hubfile(name='file1.uvl', size=1024)
        file2 = Hubfile(name='file2.uvl', size=2048)
        model1.files.append(file1)
        model2.files.append(file2)
        return [model1, model2, file1, file2]

    def test_explore_models_page(test_client, mock_models):
        with patch.object(FeatureModelService, 'get_all', return_value=mock_models[:2]):
            response = test_client.get(url_for('explore.index'))
            assert response.status_code == 200
            assert b"Explore Models" in response.data
            assert b"Model1" in response.data
            assert b"Model2" in response.data

    def test_search_model_success(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
            response = test_client.get(url_for('explore.index', query='Model1'))
            assert response.status_code == 200
            assert b"Model1" in response.data
            assert b"Model2" not in response.data

    def test_search_model_no_results(test_client):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[]):
            response = test_client.get(url_for('explore.index', query='NonExistentModel'))
            assert response.status_code == 200
            assert b"No models found" in response.data

    def test_download_model(test_client, mock_models):
        with patch.object(FeatureModelService, 'get_by_id', return_value=mock_models[0]):
            response = test_client.get(url_for('hubfile.download_file', file_id=mock_models[0].id))
            assert response.status_code == 200
            assert response.headers['Content-Disposition'] == f'attachment;
                filename={mock_models[0].fm_meta_data.title}.uvl'

    def test_model_file_display(test_client, mock_models):
        with patch.object(FeatureModelService, 'get_all', return_value=mock_models[:2]):
            response = test_client.get(url_for('explore.index'))
            assert response.status_code == 200
            assert b"file1.uvl" in response.data
            assert b"1 KB" in response.data  # Assuming size is formatted as "1 KB"
            assert b"file2.uvl" in response.data
            assert b"2 KB" in response.data  # Assuming size is formatted as "2 KB"

    def test_model_file_download_link(test_client, mock_models):
        with patch.object(FeatureModelService, 'get_all', return_value=mock_models[:2]):
            response = test_client.get(url_for('explore.index'))
            assert response.status_code == 200
            assert b'href="/hubfile/download_file?file_id=' in response.data

    def test_model_search_with_file(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
            response = test_client.get(url_for('explore.index', query='file1.uvl'))
            assert response.status_code == 200
            assert b"Model1" in response.data
            assert b"file1.uvl" in response.data

    def test_model_search_with_partial_title(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=mock_models[:2]):
            response = test_client.get(url_for('explore.index', query='Model'))
            assert response.status_code == 200
            assert b"Model1" in response.data
            assert b"Model2" in response.data

    def test_model_search_with_partial_file_name(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=mock_models[:2]):
            response = test_client.get(url_for('explore.index', query='file'))
            assert response.status_code == 200
            assert b"file1.uvl" in response.data
            assert b"file2.uvl" in response.data

    def test_model_search_with_size(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
            response = test_client.get(url_for('explore.index', query='1024'))
            assert response.status_code == 200
            assert b"file1.uvl" in response.data
            assert b"file2.uvl" not in response.data

    def test_model_search_with_nonexistent_size(test_client):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[]):
            response = test_client.get(url_for('explore.index', query='9999'))
            assert response.status_code == 200
            assert b"No models found" in response.data

    def test_model_search_with_title_and_file(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
            response = test_client.get(url_for('explore.index', query='Model1 file1.uvl'))
            assert response.status_code == 200
            assert b"Model1" in response.data
            assert b"file1.uvl" in response.data

    def test_model_search_with_title_and_size(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
            response = test_client.get(url_for('explore.index', query='Model1 1024'))
            assert response.status_code == 200
            assert b"Model1" in response.data
            assert b"file1.uvl" in response.data

    def test_model_search_with_file_and_size(test_client, mock_models):
    with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
        response = test_client.get(url_for('explore.index', query='file1.uvl 1024'))
        assert response.status_code == 200
        assert b"Model1" in response.data
        assert b"file1.uvl" in response.data

    def test_model_search_with_all_parameters(test_client, mock_models):
        with patch.object(FeatureModelService, 'search_by_name', return_value=[mock_models[0]]):
            response = test_client.get(url_for('explore.index', query='Model1 file1.uvl 1024'))
            assert response.status_code == 200
            assert b"Model1" in response.data
            assert b"file1.uvl" in response.data
"""
