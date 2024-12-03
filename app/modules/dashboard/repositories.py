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
from flask_login import current_user


class DashboardRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet) 

    def get_dataset_count(self):
        return DataSet.query.count()

    def get_author_names_and_dataset_counts(self):
        result = (
            Author.query
            .outerjoin(DSMetaData, Author.ds_meta_data_id == DSMetaData.id)  
            .with_entities(Author.name, func.count(DSMetaData.id).label('dataset_count'))
            .group_by(Author.name)
            .order_by(func.count(DSMetaData.id).desc())  
            .all()
        )
        return result
    def get_views_per_dataset(self):
        result = (
            DataSet.query
            .join(DSMetaData, DataSet.ds_meta_data_id == DSMetaData.id)  
            .outerjoin(DSViewRecord, DataSet.id == DSViewRecord.dataset_id)  
            .with_entities(DSMetaData.title, func.count(DSViewRecord.id).label('view_count'))  
            .group_by(DSMetaData.id)  
            .order_by(func.count(DSViewRecord.id).desc())  
            .limit(10)  
            .all()  
        )
        return result
    def get_downloads_per_dataset(self):
        result = (
            DataSet.query
            .join(DSMetaData, DataSet.ds_meta_data_id == DSMetaData.id)  
            .outerjoin(DSDownloadRecord, DataSet.id == DSDownloadRecord.dataset_id)  
            .with_entities(DSMetaData.title, func.count(DSDownloadRecord.id).label('view_count'))  
            .group_by(DSMetaData.id)  
            .order_by(func.count(DSDownloadRecord.id).desc())  
            .limit(10)  
            .all()  
        )
        return result
    
    def get_last_12_months_downloads(self):
        today = datetime.today()
        months = []
        download_counts = []
        for i in range(12):
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
    
    def get_last_12_months_views(self):
        today = datetime.today()
        months = []
        view_counts = []
        
        for i in range(12):
            first_day_of_month = today.replace(day=1) - timedelta(days=i * 30)
            first_day_of_month_str = first_day_of_month.strftime('%Y-%m-01')
            
            result = (
                DSViewRecord.query
                .filter(func.date(DSViewRecord.view_date) >= first_day_of_month_str)
                .filter(func.date(DSViewRecord.view_date) < (first_day_of_month + timedelta(days=32)).strftime('%Y-%m-01'))
                .count()
            )
            months.append(first_day_of_month.strftime('%Y-%m'))  
            view_counts.append(result)  
        
        months.reverse()  
        view_counts.reverse() 

        return months, view_counts
    
    def get_views_per_dataset_user_logued(self):
        result = (
            DataSet.query
            .join(DSMetaData, DataSet.ds_meta_data_id == DSMetaData.id)  
            .outerjoin(DSViewRecord, DataSet.id == DSViewRecord.dataset_id)  
            .filter(DataSet.user_id == current_user.id) 
            .with_entities(DSMetaData.title, func.count(DSViewRecord.id).label('view_count'))  
            .group_by(DSMetaData.id)  
            .order_by(func.count(DSViewRecord.id).desc())
            .limit(10)  
            .all()  
        )
        return result
    def get_downloads_per_dataset_user_logued(self):
        result = (
            DataSet.query
            .join(DSMetaData, DataSet.ds_meta_data_id == DSMetaData.id)  
            .outerjoin(DSDownloadRecord, DataSet.id == DSDownloadRecord.dataset_id)  
            .filter(DataSet.user_id == current_user.id) 
            .with_entities(DSMetaData.title, func.count(DSDownloadRecord.id).label('view_count'))  
            .group_by(DSMetaData.id)  
            .order_by(func.count(DSDownloadRecord.id).desc())
            .limit(10)  
            .all()  
        )
        return result
            
            
