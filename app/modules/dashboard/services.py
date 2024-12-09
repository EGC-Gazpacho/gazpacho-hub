from app.modules.dashboard.repositories import DashboardRepository
from core.services.BaseService import BaseService
from app.modules.dataset.repositories import DSDownloadRecordRepository, DSViewRecordRepository, DataSetRepository


class DashboardService(BaseService):
    def __init__(self, repo=None):
        self.repository = repo or DashboardRepository()

    def get_detailed_statistics(self):
        download_repo = DSDownloadRecordRepository()
        view_repo = DSViewRecordRepository()
        dataset_repo = DataSetRepository()

        total_downloads = download_repo.total_dataset_downloads()
        total_views = view_repo.total_dataset_views()
        total_synchronized_datasets = dataset_repo.count_synchronized_datasets()
        total_unsynchronized_datasets = dataset_repo.count_unsynchronized_datasets()

        statistics = {
            "total_downloads": total_downloads,
            "total_views": total_views,
            "total_synchronized_datasets": total_synchronized_datasets,
            "total_unsynchronized_datasets": total_unsynchronized_datasets,
        }
        return statistics

    def get_all_author_names_and_dataset_counts(self):
        author_data = DashboardRepository.get_author_names_and_dataset_counts(self)
        author_names = [item[0] for item in author_data]
        dataset_counts = [item[1] for item in author_data]
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

    def get_downloads_per_month_user_logued(self):
        listas = DashboardRepository.get_last_12_months_views_for_user(self)
        return listas

    def get_views_per_month_user_logued(self):
        listas = DashboardRepository.get_last_12_months_downloads_user_logued(self)
        return listas
