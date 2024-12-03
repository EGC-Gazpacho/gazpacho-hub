from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", sorting="newest",
                 publication_type="any", number_of_features=None
                ,number_of_products=None, tags=[], **kwargs):
        return self.repository.filter(query, sorting, publication_type
                                        ,number_of_features
                                        ,number_of_products, tags, **kwargs)
