from app.modules.dataset.models import DataSet
from core.repositories.BaseRepository import BaseRepository
from app.modules.dataset.models import (
    Author,
    DSMetaData,
    DataSet
)
from sqlalchemy import func
class DashboardRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)  # Utilizamos DataSet en lugar de Notepad para contar los datasets

    def get_dataset_count(self):
        return DataSet.query.count()
    
    def get_author_names_and_dataset_counts(self):
        result = (
            Author.query
            .outerjoin(DSMetaData, Author.ds_meta_data_id == DSMetaData.id)  # Realiza una left join
            .with_entities(Author.name, func.count(DSMetaData.id).label('dataset_count'))
            .group_by(Author.name)
            .order_by(func.count(DSMetaData.id).desc()) 
            .all()
        )
        return result
