from core.repositories.BaseRepository import BaseRepository
from app.modules.dataset.models import (
    Author,
    DSMetaData,
    DataSet,
    DSViewRecord,
    DSDownloadRecord
)
from sqlalchemy import func
from datetime import datetime, timedelta


class DashboardRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet) 

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
    def get_visits_per_dataset(self):
        result = (
            DataSet.query
            .join(DSMetaData, DataSet.ds_meta_data_id == DSMetaData.id)  
            .outerjoin(DSViewRecord, DataSet.id == DSViewRecord.dataset_id)  
            .with_entities(DSMetaData.title, func.count(DSViewRecord.id).label('view_count'))  
            .group_by(DSMetaData.id)  
            .order_by(func.count(DSViewRecord.id).desc())  
            .all()  
        )
        return result 
    
    def get_last_5_months_downloads(self):
        today = datetime.today()
        months = []
        download_counts = []
        for i in range(5):
            first_day_of_month = today.replace(day=1) - timedelta(days=i * 30)
            first_day_of_month_str = first_day_of_month.strftime('%Y-%m-01')  
            result = (
                DSDownloadRecord.query
                .filter(func.date(DSDownloadRecord.download_date) >= first_day_of_month_str)
                .filter(func.date(DSDownloadRecord.download_date) < (first_day_of_month + timedelta(days=32)).strftime('%Y-%m-01'))
                .count()
            )
            months.append(first_day_of_month.strftime('%Y-%m'))  
            download_counts.append(result)  

        
        months.reverse()
        download_counts.reverse()

        return months, download_counts

            
