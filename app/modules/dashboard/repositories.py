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
        # Obtener la fecha actual
        today = datetime.today()
        
        # Inicializamos las listas de meses y descargas
        months = []
        download_counts = []

        # Iterar sobre los últimos 5 meses (mes actual + 4 anteriores)
        for i in range(5):
            # Calcular el primer día de cada mes (mes actual, mes-1, ..., mes-4)
            first_day_of_month = today.replace(day=1) - timedelta(days=i * 30)
            first_day_of_month_str = first_day_of_month.strftime('%Y-%m-01')  # Fecha en formato 'YYYY-MM-01'

            # Consultar las descargas para ese mes
            result = (
                DSDownloadRecord.query
                .filter(func.date(DSDownloadRecord.download_date) >= first_day_of_month_str)
                .filter(func.date(DSDownloadRecord.download_date) < (first_day_of_month + timedelta(days=32)).strftime('%Y-%m-01'))
                .count()
            )
            
            # Añadir el mes y el número de descargas a las listas
            months.append(first_day_of_month.strftime('%Y-%m'))  # Añadimos el mes en formato 'YYYY-MM'
            download_counts.append(result)  # Añadimos el número de descargas en ese mes

        # Invertir las listas para que las fechas más antiguas estén a la izquierda
        months.reverse()
        download_counts.reverse()

        return months, download_counts

            
