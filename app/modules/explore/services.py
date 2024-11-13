from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService
from app.modules.featuremodel.models import FeatureModel


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", sorting="newest", publication_type="any", number_of_features=None, tags=[], **kwargs):
        return self.repository.filter(query, sorting, publication_type, number_of_features, tags, **kwargs)
  
    
class ModelService:
    def get_all_models(self):
        return FeatureModel.query.all()

    def filter(self, **criteria):
        query = FeatureModel.query
        if 'name' in criteria:
            query = query.filter(FeatureModel.name.contains(criteria['name']))
        # Agregar más filtros según sea necesario
        return query.all()
