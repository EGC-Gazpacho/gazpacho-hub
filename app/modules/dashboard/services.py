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
