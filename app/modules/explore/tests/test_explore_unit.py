import pytest
from flask import url_for
from app import create_app, db
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile
from app.modules.dataset.models import PublicationType, DataSet, DSMetaData
from app.modules.auth.models import User
from datetime import datetime


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://default_user:default_password@127.0.0.1:3306/uvlhubdb_test'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Create a User instance
            user = User(email='test99@example.com', password='password')
            db.session.add(user)
            db.session.commit()

            # Create DSMetaData instances
            ds_meta_data1 = DSMetaData(
                title='DataSet 1',
                description='Description for DataSet 1',
                publication_type=PublicationType.BOOK
            )
            ds_meta_data2 = DSMetaData(
                title='DataSet 2',
                description='Description for DataSet 2',
                publication_type=PublicationType.JOURNAL_ARTICLE
            )

            # Create DataSet instances
            data_set1 = DataSet(
                user_id=user.id,
                ds_meta_data=ds_meta_data1,
                created_at=datetime.now()
            )
            data_set2 = DataSet(
                user_id=user.id,
                ds_meta_data=ds_meta_data2,
                created_at=datetime.now()
            )

            # Create FMMetaData instances
            fm_meta_data1 = FMMetaData(
                title='Test Model 1',
                uvl_filename='test1.uvl',
                description='Description for Test Model 1',
                publication_type=PublicationType.JOURNAL_ARTICLE
            )
            fm_meta_data2 = FMMetaData(
                title='Another Model',
                uvl_filename='test2.uvl',
                description='Description for Another Model',
                publication_type=PublicationType.BOOK
            )

            # Create FeatureModel instances
            model1 = FeatureModel(fm_meta_data=fm_meta_data1, data_set=data_set1)
            model2 = FeatureModel(fm_meta_data=fm_meta_data2, data_set=data_set2)

            # Create Hubfile instances
            file1 = Hubfile(name='test1.uvl', size=1234, feature_model=model1, checksum='1234')
            file2 = Hubfile(name='test2.uvl', size=5678, feature_model=model2, checksum='5678')

            # Add instances to the session
            db.session.add_all([user, ds_meta_data1, ds_meta_data2, data_set1, data_set2,
                                fm_meta_data1, fm_meta_data2, model1, model2, file1, file2])
            db.session.commit()

            yield client

            db.session.remove()
            db.reflect()
            db.drop_all()


def test_model_search_by_name(test_client):
    # Test for the search query 'Test Model 1'
    response = test_client.get(url_for('explore.explore2_models', query='Test Model 1'))
    assert response.status_code == 200
    assert b'Test Model 1' in response.data
    assert b'Another Model' not in response.data


def test_model_search_non_existent(test_client):
    # Test for a non-existent model
    response = test_client.get(url_for('explore.explore2_models', query='NonExistentModel'))
    assert response.status_code == 200


def test_model_search_partial_match(test_client):
    # Test for a partial match
    response = test_client.get(url_for('explore.explore2_models', query='Test'))
    assert response.status_code == 200
    assert b'Test Model 1' in response.data
    assert b'Another Model' not in response.data


def test_model_search_case_insensitivity(test_client):
    # Test for case insensitivity
    response = test_client.get(url_for('explore.explore2_models', query='test model 1'))
    assert response.status_code == 200
    assert b'Test Model 1' in response.data
    assert b'Another Model' not in response.data


def test_model_search_multiple_matches(test_client):
    # Test for multiple matches
    response = test_client.get(url_for('explore.explore2_models', query='Model'))
    assert response.status_code == 200
    assert b'Test Model 1' in response.data
    assert b'Another Model' in response.data
