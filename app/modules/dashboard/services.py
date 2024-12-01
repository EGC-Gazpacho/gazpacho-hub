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
    
    def get_visits_per_dataset_lists(self):
        result = DashboardRepository.get_visits_per_dataset(self)
        dataset_names = [item[0] for item in result]  
        dataset_visits = [item[1] for item in result]  
        return dataset_names, dataset_visits
    def get_downloads_per_month(self):
        print( "llega servicio")
        listas = DashboardRepository.get_last_5_months_downloads(self)
        print(listas)
        return listas 
