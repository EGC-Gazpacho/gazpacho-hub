from app.modules.dashboard.repositories import DashboardRepository
from core.services.BaseService import BaseService


class DashboardService(BaseService):
    def __init__(self):
        super().__init__(DashboardRepository())

    def get_all_dataset(self):
        return self.repository.count(self)

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
    def get_downloads_per_month(self):
        listas = DashboardRepository.get_last_12_months_downloads(self)
        return listas 

    def get_views_per_dataset_user_logued(self):
        result = DashboardRepository.get_views_per_dataset_user_logued(self)
        dataset_names_user = [item[0] for item in result]  
        dataset_views_user = [item[1] for item in result] 

        return dataset_names_user, dataset_views_user
