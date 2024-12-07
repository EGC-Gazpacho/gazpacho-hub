from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService
from app.modules.featuremodel.models import FeatureModel, FMMetaData


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", sorting="newest", publication_type="any", number_of_features=None, tags=[], **kwargs):
        return self.repository.filter(query, sorting, publication_type, number_of_features, tags, **kwargs)


class ModelService:
    def get_all_models(self):
        return FeatureModel.query.all()

    def filter(self, name=''):
        query = FeatureModel.query
        if name:
            query = query.join(FMMetaData).filter(FMMetaData.title.contains(name))
        return query.all()
