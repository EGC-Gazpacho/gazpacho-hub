from app.modules.explore.repositories import ExploreRepository, FMMetaData
from app.modules.featuremodel.models import FeatureModel
from core.services.BaseService import BaseService


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(
        self,
        query="",
        sorting="newest",
        publication_type="any",
        number_of_features=None,
        number_of_products=None,
        tags=[],
        **kwargs
    ):
        return self.repository.filter(
            query, sorting, publication_type, number_of_features, number_of_products, tags, **kwargs
        )


class ModelService:
    def get_all_models(self):
        return FeatureModel.query.all()

    def filter(self, name=''):
        query = FeatureModel.query
        if name:
            query = query.join(FMMetaData).filter(FMMetaData.title.contains(name))
        return query.all()
    
