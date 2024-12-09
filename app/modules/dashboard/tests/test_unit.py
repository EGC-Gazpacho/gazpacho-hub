import pytest 
from app.modules.dashboard.repositories import DashboardRepository
from app.modules.dashboard.services import DashboardService
from app.modules.dataset.repositories import DSDownloadRecordRepository, DSViewRecordRepository, DataSetRepository
from unittest.mock import patch
from sqlalchemy.orm.query import Query
from app import create_app, db
from app.modules.dashboard.repositories import DashboardRepository
from app.modules.auth.models import User
from app.modules.conftest import login, logout

@pytest.fixture
def dashboard_repository():
    app = create_app()
    with app.app_context():
        repository = DashboardRepository()
        yield repository


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        user_test = User(email = 'user@example.com', password = 'password')
        db.session.add(user_test)
        db.session.commit()
        pass 
    yield test_client


@patch('app.modules.dataset.repositories.DataSetRepository.count_unsynchronized_datasets')
@patch('app.modules.dataset.repositories.DataSetRepository.count_synchronized_datasets')
@patch('app.modules.dataset.repositories.DSViewRecordRepository.total_dataset_views')
@patch('app.modules.dataset.repositories.DSDownloadRecordRepository.total_dataset_downloads')
def test_get_detailed_statistics(    
                                     mock_total_dataset_downloads,
                                     mock_total_dataset_views,
                                     mock_count_synchronized_datasets,
                                     mock_count_unsynchronized_datasets):
    
        mock_total_dataset_downloads.return_value = 100
        mock_total_dataset_views.return_value = 200
        mock_count_synchronized_datasets.return_value = 50
        mock_count_unsynchronized_datasets.return_value = 30
    
        service = DashboardService()
        result = service.get_detailed_statistics()

        mock_total_dataset_downloads.assert_called_once()
        mock_total_dataset_views.assert_called_once()
        mock_count_synchronized_datasets.assert_called_once()
        mock_count_unsynchronized_datasets.assert_called_once()

        expected_result = {
            "total_downloads": 100,
            "total_views": 200,
            "total_synchronized_datasets": 50,
            "total_unsynchronized_datasets": 30,
        }
        assert result == expected_result




@patch('app.modules.dashboard.repositories.DashboardRepository.get_author_names_and_dataset_counts')
def test_service_get_all_author_names_and_dataset_counts(mock_get_author_names_and_dataset_counts):
    mock_data = [
        ("Author 1", 5),
        ("Author 2", 3)
    ]
    mock_get_author_names_and_dataset_counts.return_value = mock_data
    
    service = DashboardService()
    author_names, dataset_counts = service.get_all_author_names_and_dataset_counts()
    
    assert author_names == ["Author 1", "Author 2"]
    assert dataset_counts == [5, 3]
    mock_get_author_names_and_dataset_counts.assert_called_once()

@patch('app.modules.dashboard.repositories.DashboardRepository.get_views_per_dataset')
def test_service_get_views_per_dataset_lists(mock_get_views_per_dataset):
    mock_data = [
        ("Dataset 1", 5),
        ("Dataset 2", 9)
    ]
    mock_get_views_per_dataset.return_value = mock_data
    
    service = DashboardService()
    author_names, dataset_counts = service.get_views_per_dataset_lists()
    
    assert author_names == ["Dataset 1", "Dataset 2"]
    assert dataset_counts == [5, 9]
    mock_get_views_per_dataset.assert_called_once()


@patch('app.modules.dashboard.repositories.DashboardRepository.get_downloads_per_dataset')
def test_service_get_downloads_per_dataset_lists(mock_get_downloads_per_dataset):
    mock_data = [
        ("Dataset 1", 5),
        ("Dataset 2", 9)
    ]
    mock_get_downloads_per_dataset.return_value = mock_data
    
    service = DashboardService()
    author_names, dataset_counts = service.get_downloads_per_dataset_lists()
    
    assert author_names == ["Dataset 1", "Dataset 2"]
    assert dataset_counts == [5, 9]
    mock_get_downloads_per_dataset.assert_called_once()

@patch('app.modules.dashboard.repositories.DashboardRepository.get_last_12_months_downloads')
def test_service_get_downloads_per_month(mock_get_last_12_months_downloads):
    mock_data = [

        ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12'],
        [0,3,3,6,1,0,0,0,1,0,0,0]
    ]
    mock_get_last_12_months_downloads.return_value = mock_data
    
    service = DashboardService()
    months, downloads = service.get_downloads_per_month()
    
    assert months == ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12']
    assert downloads == [0,3,3,6,1,0,0,0,1,0,0,0]
    mock_get_last_12_months_downloads.assert_called_once()


@patch('app.modules.dashboard.repositories.DashboardRepository.get_last_12_months_views')
def test_service_get_views_per_month(mock_get_last_12_months_views):
    mock_data = [

        ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12'],
        [0,3,3,6,1,0,0,0,1,0,0,0]
    ]
    mock_get_last_12_months_views.return_value = mock_data
    
    service = DashboardService()
    months, views = service.get_views_per_month()
    
    assert months == ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12']
    assert views == [0,3,3,6,1,0,0,0,1,0,0,0]
    mock_get_last_12_months_views.assert_called_once()

@patch('app.modules.dashboard.repositories.DashboardRepository.get_views_per_dataset_user_logued')
def test_service_get_views_per_dataset_user_logued(mock_get_views_per_dataset_user_logued):
    mock_data = [
        ("Dataset 1", 5),
        ("Dataset 2", 9)
    ]
    mock_get_views_per_dataset_user_logued.return_value = mock_data
    
    service = DashboardService()
    datasets, views = service.get_views_per_dataset_user_logued()
    
    assert datasets == ["Dataset 1", "Dataset 2"]
    assert views == [5, 9]
    mock_get_views_per_dataset_user_logued.assert_called_once()

@patch('app.modules.dashboard.repositories.DashboardRepository.get_downloads_per_dataset_user_logued')
def test_service_get_downloads_per_dataset_user_logued(mock_get_downloads_per_dataset_user_logued):
    mock_data = [
        ("Dataset 1", 5),
        ("Dataset 2", 9)
    ]
    mock_get_downloads_per_dataset_user_logued.return_value = mock_data
    
    service = DashboardService()
    datasets, views = service.get_downloads_per_dataset_user_logued()
    
    assert datasets == ["Dataset 1", "Dataset 2"]
    assert views == [5, 9]
    mock_get_downloads_per_dataset_user_logued.assert_called_once()



@patch('app.modules.dashboard.repositories.DashboardRepository.get_last_12_months_views_for_user')
def test_service_get_downloads_per_month_user_logued(mock_get_last_12_months_views_for_user):
    mock_data = [

        ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12'],
        [0,3,3,6,1,0,0,0,1,0,0,0]
    ]
    mock_get_last_12_months_views_for_user.return_value = mock_data
    
    service = DashboardService()
    months, downloads = service.get_downloads_per_month_user_logued()
    
    assert months == ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12']
    assert downloads == [0,3,3,6,1,0,0,0,1,0,0,0]
    mock_get_last_12_months_views_for_user.assert_called_once()


@patch('app.modules.dashboard.repositories.DashboardRepository.get_last_12_months_downloads_user_logued')
def test_service_get_views_per_month_user_logued(mock_get_last_12_months_downloads_user_logued):
    mock_data = [

        ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12'],
        [0,3,3,6,1,0,0,0,1,0,0,0]
    ]
    mock_get_last_12_months_downloads_user_logued.return_value = mock_data
    
    service = DashboardService()
    months, downloads = service.get_views_per_month_user_logued()
    
    assert months == ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12']
    assert downloads == [0,3,3,6,1,0,0,0,1,0,0,0]
    mock_get_last_12_months_downloads_user_logued.assert_called_once()

def test_route(test_client):
    login_response = login(test_client, 'user@example.com', 'password')
    assert login_response.status_code == 200, "Login was not successful"
    mock_statistics = {
        "total_downloads": 100,
        "total_views": 200,
        "total_synchronized_datasets": 50,
        "total_unsynchronized_datasets": 30,
        "total_datasets": 80
    }

    mock_author_names = ['author1', 'author2']
    mock_dataset_counts = [10, 5]

    mock_datasets_names_views = ['dataset1', 'dataset2']
    mock_datasets_views = [100, 50]

    mock_datasets_names_downloads = ['dataset1', 'dataset2']
    mock_datasets_downloads = [200, 150]

    mock_month = ['2024-01', '2024-02']
    mock_downloads = [300, 250]

    mock_month_views = ['2024-01', '2024-02']
    mock_views = [500, 400]

    mock_datasets_names_user = ['dataset1', 'dataset2']
    mock_datasets_views_user = [120, 90]

    mock_datasets_names_user_downloads = ['dataset1', 'dataset2']
    mock_datasets_download_user = [210, 180]

    mock_month_views_user = ['2024-01', '2024-02']
    mock_views_user = [110, 80]

    mock_month_downloads_user = ['2024-01', '2024-02']
    mock_downloads_user = [220, 200]
 
    with patch('app.modules.dashboard.services.DashboardService.get_detailed_statistics', return_value=mock_statistics), \
         patch('app.modules.dashboard.services.DashboardService.get_all_author_names_and_dataset_counts', return_value=(mock_author_names, mock_dataset_counts)), \
         patch('app.modules.dashboard.services.DashboardService.get_views_per_dataset_lists', return_value=(mock_datasets_names_views, mock_datasets_views)), \
         patch('app.modules.dashboard.services.DashboardService.get_downloads_per_dataset_lists', return_value=(mock_datasets_names_downloads, mock_datasets_downloads)), \
         patch('app.modules.dashboard.services.DashboardService.get_downloads_per_month', return_value=(mock_month, mock_downloads)), \
         patch('app.modules.dashboard.services.DashboardService.get_views_per_month', return_value=(mock_month_views, mock_views)), \
         patch('app.modules.dashboard.services.DashboardService.get_views_per_dataset_user_logued', return_value=(mock_datasets_names_user, mock_datasets_views_user)), \
         patch('app.modules.dashboard.services.DashboardService.get_downloads_per_dataset_user_logued', return_value=(mock_datasets_names_user_downloads, mock_datasets_download_user)), \
         patch('app.modules.dashboard.services.DashboardService.get_downloads_per_month_user_logued', return_value=(mock_month_downloads_user, mock_downloads_user)), \
         patch('app.modules.dashboard.services.DashboardService.get_views_per_month_user_logued', return_value=(mock_month_views_user, mock_views_user)):

        response = test_client.get('/dashboard')

        assert response.status_code == 200

        assert b'author1' in response.data
        assert b'author2' in response.data

        assert b'2024-01' in response.data
        assert b'2024-02' in response.data
        
        assert b'100' in response.data  
        assert b'200' in response.data  

        assert b'dataset1' in response.data
        assert b'dataset2' in response.data

        assert b'100' in response.data  
        assert b'50' in response.data  
        assert b'200' in response.data  
        assert b'150' in response.data  

        assert b'300' in response.data  
        assert b'250' in response.data  

        
        assert b'500' in response.data  
        assert b'400' in response.data  
    logout(test_client)
       