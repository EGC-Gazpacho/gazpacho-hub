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
    """
    Creates the test client and adds some models to the database for testing.
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'
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
                created_at=datetime.utcnow()
            )
            data_set2 = DataSet(
                user_id=user.id,
                ds_meta_data=ds_meta_data2,
                created_at=datetime.utcnow()
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
            db.session.add_all([user, ds_meta_data1, ds_meta_data2, data_set1, data_set2, fm_meta_data1, fm_meta_data2, model1, model2, file1, file2])
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