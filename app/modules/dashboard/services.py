from app.modules.dashboard.repositories import DashboardRepository
from core.services.BaseService import BaseService
from app.modules.dataset.repositories import DSDownloadRecordRepository, DSViewRecordRepository, DataSetRepository
from app.modules.dataset.models import DSDownloadRecord, DSViewRecord
from datetime import datetime, timedelta
from sqlalchemy import desc


class DashboardService(BaseService):
    def __init__(self, repo=None):
        self.repository = repo or DashboardRepository()


    def get_all_dataset(self):
        return self.repository.count(self)
    
    def get_detailed_statistics(self):
        download_repo = DSDownloadRecordRepository()
        view_repo = DSViewRecordRepository()
        dataset_repo = DataSetRepository()

        total_downloads = download_repo.total_dataset_downloads()
        total_views = view_repo.total_dataset_views()
        total_synchronized_datasets = dataset_repo.count_synchronized_datasets()
        total_unsynchronized_datasets = dataset_repo.count_unsynchronized_datasets()

        total_datasets = dataset_repo.model.query.count()
        
        one_month_ago = datetime.now() - timedelta(days=30)
        datasets_last_month = dataset_repo.model.query.filter(
            dataset_repo.model.created_at >= one_month_ago
        ).count()

        last_download = download_repo.model.query.order_by(desc(DSDownloadRecord.download_date)).first()
        last_download_date = last_download.download_date if last_download else None

        last_view = view_repo.model.query.order_by(desc(DSViewRecord.view_date)).first()
        last_view_date = last_view.view_date if last_view else None

        statistics = {
            "total_downloads": total_downloads,
            "total_views": total_views,
            "total_synchronized_datasets": total_synchronized_datasets,
            "total_unsynchronized_datasets": total_unsynchronized_datasets,
            "total_datasets": total_datasets,
            "datasets_last_month": datasets_last_month,
            "last_download_date": last_download_date,
            "last_view_date": last_view_date
        }
        print(statistics)
        return statistics

    def get_all_author_names_and_dataset_counts(self):
        author_data = DashboardRepository.get_author_names_and_dataset_counts(self)
        author_names = [data.name for data in author_data]
        dataset_counts = [data.dataset_count for data in author_data]
        return author_names, dataset_counts
    
    def get_views_per_dataset_lists(self):
        result = DashboardRepository.get_views_per_dataset(self)
        dataset_names = [item[0] for item in result]  
        dataset_views = [item[1] for item in result]  
        return dataset_names, dataset_views
    
    def get_downloads_per_dataset_lists(self):
        result = DashboardRepository.get_downloads_per_dataset(self)
        dataset_names = [item[0] for item in result]  
        dataset_downloads = [item[1] for item in result]  
        return dataset_names, dataset_downloads
    
    def get_downloads_per_month(self):
        listas = DashboardRepository.get_last_12_months_downloads(self)
        return listas 
    
    def get_views_per_month(self):
        listas = DashboardRepository.get_last_12_months_views(self)
        return listas 

    def get_views_per_dataset_user_logued(self):
        result = DashboardRepository.get_views_per_dataset_user_logued(self)
        dataset_names_user = [item[0] for item in result]  
        dataset_views_user = [item[1] for item in result] 

        return dataset_names_user, dataset_views_user
    
    def get_downloads_per_dataset_user_logued(self):
        result = DashboardRepository.get_downloads_per_dataset_user_logued(self)
        dataset_names_user = [item[0] for item in result]  
        dataset_download_user = [item[1] for item in result] 

        return dataset_names_user, dataset_download_user
