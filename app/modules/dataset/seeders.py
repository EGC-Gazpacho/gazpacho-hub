import os
import shutil
import random
from app.modules.auth.models import User
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from app.modules.hubfile.models import Hubfile
from core.seeders.BaseSeeder import BaseSeeder
from app.modules.dataset.models import (
    DataSet,
    DSMetaData,
    PublicationType,
    DSMetrics,
    Author,
    DSDownloadRecord,
    DSViewRecord
)
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv


class DataSetSeeder(BaseSeeder):

    priority = 2  # Lower priority

    def run(self):
        # Retrieve users
        user1 = User.query.filter_by(email='user1@example.com').first()
        user2 = User.query.filter_by(email='user2@example.com').first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        # Create DSMetrics instance
        ds_metrics = DSMetrics(number_of_models='5', number_of_features='50', number_of_products='50')
        seeded_ds_metrics = self.seed([ds_metrics])[0]

        # Create DSMetaData instances
        ds_meta_data_list = [
            DSMetaData(
                deposition_id=1 + i,
                title=f'Sample dataset {i + 1}',
                description=f'Description for dataset {i + 1}',
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
                publication_doi=f'10.1234/dataset{i + 1}',
                dataset_doi=f'10.1234/dataset{i + 1}',
                tags='tag1, tag2',
                ds_metrics_id=seeded_ds_metrics.id
            ) for i in range(10)  # 10 datasets para el usuario 1
        ]
        seeded_ds_meta_data = self.seed(ds_meta_data_list)

        # Create Author instances and associate with DSMetaData
        authors = [
            Author(
                name=f'Author {i + 1}',
                affiliation=f'Affiliation {i + 1}',
                orcid=f'0000-0000-0000-000{i}',
                ds_meta_data_id=seeded_ds_meta_data[i % 10].id
            ) for i in range(10)
        ]
        self.seed(authors)

        # Create DataSet instances and associate them with user1
        datasets = [
            DataSet(
                user_id=user1.id,
                ds_meta_data_id=seeded_ds_meta_data[i].id,
                created_at=datetime.now(timezone.utc) - timedelta(days=i * 5)  # Fechas pasadas para cada dataset
            ) for i in range(10)
        ]
        seeded_datasets = self.seed(datasets)

        # Crear fechas pasadas distribuidas a lo largo de los últimos meses
        current_time = datetime.now(timezone.utc)
        past_dates = [current_time - timedelta(days=i) for i in range(30, 0, -1)]  # 30 fechas pasadas, 1 por día

        # Para cada dataset de usuario 1, agregar descargas y vistas con números dispares
        for dataset in seeded_datasets:
            # Generar un número aleatorio de descargas entre 3 y 9 para cada dataset
            num_downloads = random.randint(3, 9)  # Número de descargas aleatorio entre 3 y 9

            # Asociamos las descargas
            for i in range(num_downloads):
                download_date = random.choice(past_dates)  # Escoge una fecha aleatoria
                self.seed([DSDownloadRecord(
                    user_id=user1.id,
                    dataset_id=dataset.id,
                    download_date=download_date,
                    download_cookie=f'cookie_{dataset.id}_download_{i + 1}'
                )])

            # Generar un número aleatorio de vistas entre 2 y 5 para cada dataset
            num_views = random.randint(2, 5)  # Número de vistas aleatorio entre 2 y 5

            # Asociamos las vistas
            for i in range(num_views):
                view_date = random.choice(past_dates)  # Escoge una fecha aleatoria para vistas
                self.seed([DSViewRecord(
                    user_id=user1.id,
                    dataset_id=dataset.id,
                    view_date=view_date,
                    view_cookie=f'cookie_{dataset.id}_view_{i + 1}'
                )])

        # Asumir que hay 12 archivos UVL, crear FMMetaData y FeatureModel correspondientes
        fm_meta_data_list = [
            FMMetaData(
                uvl_filename=f'file{i + 1}.uvl',
                title=f'Feature Model {i + 1}',
                description=f'Description for feature model {i + 1}',
                publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
                publication_doi=f'10.1234/fm{i + 1}',
                tags='tag1, tag2',
                uvl_version='1.0'
            ) for i in range(12)
        ]
        seeded_fm_meta_data = self.seed(fm_meta_data_list)

        # Crear Author instances y asociarlas con FMMetaData
        fm_authors = [
            Author(
                name=f'Author {i + 5}',
                affiliation=f'Affiliation {i + 5}',
                orcid=f'0000-0000-0000-000{i + 5}',
                fm_meta_data_id=seeded_fm_meta_data[i].id
            ) for i in range(12)
        ]
        self.seed(fm_authors)

        # Crear los modelos de características
        feature_models = [
            FeatureModel(
                data_set_id=seeded_datasets[i // 3].id,
                fm_meta_data_id=seeded_fm_meta_data[i].id
            ) for i in range(12)
        ]
        seeded_feature_models = self.seed(feature_models)

        # Crear archivos, asociarlos con FeatureModels y copiarlos
        load_dotenv()
        working_dir = os.getenv('WORKING_DIR', '')
        src_folder = os.path.join(working_dir, 'app', 'modules', 'dataset', 'uvl_examples')
        for i in range(12):
            file_name = f'file{i + 1}.uvl'
            feature_model = seeded_feature_models[i]
            dataset = next(ds for ds in seeded_datasets if ds.id == feature_model.data_set_id)
            user_id = dataset.user_id

            dest_folder = os.path.join(working_dir, 'uploads', f'user_{user_id}', f'dataset_{dataset.id}')
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copy(os.path.join(src_folder, file_name), dest_folder)

            file_path = os.path.join(dest_folder, file_name)

            uvl_file = Hubfile(
                name=file_name,
                checksum=f'checksum{i + 1}',
                size=os.path.getsize(file_path),
                feature_model_id=feature_model.id
            )
            self.seed([uvl_file])
