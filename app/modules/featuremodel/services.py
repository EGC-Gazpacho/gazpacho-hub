from app.modules.featuremodel.repositories import FMMetaDataRepository, FeatureModelRepository
from app.modules.hubfile.services import HubfileService
from core.services.BaseService import BaseService


class FeatureModelService(BaseService):
    def __init__(self):
        super().__init__(FeatureModelRepository())
        self.hubfile_service = HubfileService()
        
    def search_by_name(self, query):
        if not query:
            return []  # Si no hay consulta, devolvemos una lista vacía

        # Buscar en la base de datos usando el nombre del modelo (en este caso el título de `fm_meta_data`)
        return self.repository.filter_by_name(query)

    def total_feature_model_views(self) -> int:
        return self.hubfile_service.total_hubfile_views()

    def total_feature_model_downloads(self) -> int:
        return self.hubfile_service.total_hubfile_downloads()

    def count_feature_models(self):
        return self.repository.count_feature_models()

    class FMMetaDataService(BaseService):
        def __init__(self):
            super().__init__(FMMetaDataRepository())
    
