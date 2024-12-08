import pytest 
from app.modules.dashboard.repositories import DashboardRepository
from app.modules.dashboard.services import DashboardService
from app.modules.dataset.repositories import DSDownloadRecordRepository, DSViewRecordRepository, DataSetRepository
from unittest.mock import patch ,MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm.query import Query

@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
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
        
        # Datos mock
        mock_total_dataset_downloads.return_value = 100
        mock_total_dataset_views.return_value = 200
        mock_count_synchronized_datasets.return_value = 50
        mock_count_unsynchronized_datasets.return_value = 30
        
        # Simulamos el resultado de la consulta de count()

        # Crear la instancia del servicio
        service = DashboardService()
        result = service.get_detailed_statistics()

        # Verificar que los métodos fueron llamados correctamente
        mock_total_dataset_downloads.assert_called_once()
        mock_total_dataset_views.assert_called_once()
        mock_count_synchronized_datasets.assert_called_once()
        mock_count_unsynchronized_datasets.assert_called_once()

        # Verificar que los resultados son correctos
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