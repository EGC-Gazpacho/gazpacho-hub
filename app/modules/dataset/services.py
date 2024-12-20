import logging
import os
import hashlib
import shutil
import tempfile
from typing import Optional
import uuid
from zipfile import ZipFile
from flamapy.metamodels.fm_metamodel.transformations import UVLReader, GlencoeWriter, SPLOTWriter
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat, DimacsWriter
from flask import abort, request

from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DSViewRecord, DataSet, DSMetaData, DSMetrics, DSRating
from app.modules.dataset.repositories import (
    AuthorRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
    DataSetRepository,
    DSRatingRepository
)
from app.modules.featuremodel.repositories import FMMetaDataRepository, FeatureModelRepository
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository
)
from core.services.BaseService import BaseService
from datetime import datetime


logger = logging.getLogger(__name__)


def calculate_checksum_and_size(file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file:
        content = file.read()
        hash_md5 = hashlib.md5(content).hexdigest()
        return hash_md5, file_size


def parse_uvl(file_path):
    features = []
    constraints = []
    feature_hierarchy = {}

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Track hierarchy for feature organization
    current_parent = None
    for line in lines:
        line = line.strip()

        # Identify feature sections
        if line.startswith("features"):
            continue
        elif line.startswith("constraints"):
            # Stop collecting features and move to constraints
            break
        elif line in ["mandatory", "optional", "alternative", "or"]:
            current_parent = line
            feature_hierarchy[current_parent] = []
        else:
            # Extract features (ignoring quotes if any)
            feature = line.replace('"', '')
            if feature:
                features.append(feature)
                if current_parent:
                    feature_hierarchy[current_parent].append(feature)

    # Extract constraints section
    constraints_section = False
    for line in lines:
        line = line.strip()
        if line.startswith("constraints"):
            constraints_section = True
            continue
        if constraints_section:
            constraints.append(line)

    return {
        "features": features,
        "feature_hierarchy": feature_hierarchy,
        "constraints": constraints
    }


def calculate_number_of_products(feature_hierarchy, constraints):
    # Start with mandatory features (1 configuration)
    product_count = 1

    # Add optional features (each has 2 states: included or excluded)
    product_count *= 2 ** len(feature_hierarchy["optional"])

    # Handle "alternative" groups (1 choice per group)
    product_count *= len(feature_hierarchy["alternative"])

    # Handle "or" groups (any combination except empty set)
    product_count *= (2 ** len(feature_hierarchy["or"])) - 1

    return product_count


class DataSetService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        self.feature_model_repository = FeatureModelRepository()
        self.author_repository = AuthorRepository()
        self.dsmetadata_repository = DSMetaDataRepository()
        self.fmmetadata_repository = FMMetaDataRepository()
        self.dsdownloadrecord_repository = DSDownloadRecordRepository()
        self.hubfiledownloadrecord_repository = HubfileDownloadRecordRepository()
        self.hubfilerepository = HubfileRepository()
        self.dsviewrecord_repostory = DSViewRecordRepository()
        self.hubfileviewrecord_repository = HubfileViewRecordRepository()
        self.dsrating_repository = DSRatingRepository()

    def move_feature_models(self, dataset: DataSet):
        current_user = AuthenticationService().get_authenticated_user()
        source_dir = current_user.temp_folder()

        working_dir = os.getenv("WORKING_DIR", "")
        dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")

        os.makedirs(dest_dir, exist_ok=True)

        for feature_model in dataset.feature_models:
            uvl_filename = feature_model.fm_meta_data.uvl_filename
            shutil.move(os.path.join(source_dir, uvl_filename), dest_dir)

    def is_synchronized(self, dataset_id: int) -> bool:
        return self.repository.is_synchronized(dataset_id)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_synchronized(current_user_id)

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_unsynchronized(current_user_id)

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return self.repository.get_unsynchronized_dataset(current_user_id, dataset_id)

    def latest_synchronized(self):
        return self.repository.latest_synchronized()

    def count_synchronized_datasets(self):
        return self.repository.count_synchronized_datasets()

    def count_feature_models(self):
        return self.feature_model_service.count_feature_models()

    def count_authors(self) -> int:
        return self.author_repository.count()

    def count_dsmetadata(self) -> int:
        return self.dsmetadata_repository.count()

    def total_dataset_downloads(self) -> int:
        return self.dsdownloadrecord_repository.total_dataset_downloads()

    def total_dataset_views(self) -> int:
        return self.dsviewrecord_repostory.total_dataset_views()

    def create_from_form(self, form, current_user) -> DataSet:
        main_author = {
            "name": f"{current_user.profile.surname}, {current_user.profile.name}",
            "affiliation": current_user.profile.affiliation,
            "orcid": current_user.profile.orcid,
        }
        try:
            logger.info(f"Creating dsmetadata...: {form.get_dsmetadata()}")
            dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())
            for author_data in [main_author] + form.get_authors():
                author = self.author_repository.create(
                    commit=False,
                    ds_meta_data_id=dsmetadata.id,
                    **author_data
                )
                dsmetadata.authors.append(author)

            dataset = self.create(
                commit=False,
                user_id=current_user.id,
                ds_meta_data_id=dsmetadata.id
            )

            total_features = 0
            total_models = len(form.feature_models)
            total_products = 0

            for feature_model in form.feature_models:
                uvl_filename = feature_model.uvl_filename.data
                fmmetadata = self.fmmetadata_repository.create(
                    commit=False,
                    **feature_model.get_fmmetadata()
                )
                for author_data in feature_model.get_authors():
                    author = self.author_repository.create(
                        commit=False,
                        fm_meta_data_id=fmmetadata.id,
                        **author_data
                    )
                    fmmetadata.authors.append(author)

                fm = self.feature_model_repository.create(
                    commit=False,
                    data_set_id=dataset.id,
                    fm_meta_data_id=fmmetadata.id
                )

                file_path = os.path.join(current_user.temp_folder(), uvl_filename)
                checksum, size = calculate_checksum_and_size(file_path)
                parse_result = parse_uvl(file_path)
                feature_count = len(parse_result["features"])
                total_features += feature_count

                product_count = calculate_number_of_products(
                    parse_result["feature_hierarchy"],
                    parse_result["constraints"]
                )
                total_products += product_count

                file = self.hubfilerepository.create(
                    commit=False,
                    name=uvl_filename,
                    checksum=checksum,
                    size=size,
                    feature_model_id=fm.id
                )
                fm.files.append(file)

            dsmetrics = DSMetrics(
                number_of_models=str(total_models),
                number_of_features=total_features,
                number_of_products=total_products
            )
            dsmetadata.ds_metrics = dsmetrics

            dataset.ds_meta_data = dsmetadata

            self.repository.session.commit()
        except Exception as exc:
            logger.info(f"Exception creating dataset from form...: {exc}")
            self.repository.session.rollback()
            raise exc
        return dataset

    # Los datasets contienen los archivos en formato UVL, los cuales se deben convertir a otros formatos

    def convert_uvl_to_formats(self, uvl_file_path: str, output_formats: list) -> dict:
        """
        Convierte un archivo UVL a múltiples formatos (Glencoe, Dinamacs, SPLOT).

        :param uvl_file_path: Ruta del archivo UVL de entrada.
        :param output_formats: Lista de formatos a los que convertir (Glencoe, Dinamacs, SPLOT).
        :return: Diccionario con las rutas de los archivos convertidos.
        """
        fm = UVLReader(uvl_file_path).transform()
        converted_files = {}

        for format_name in output_formats:
            temp_file = tempfile.NamedTemporaryFile(suffix=f'.{format_name.lower()}', delete=False)
            output_file_path = temp_file.name

            try:
                if format_name == "Glencoe":
                    GlencoeWriter(output_file_path, fm).transform()
                elif format_name == "SPLOT":
                    SPLOTWriter(output_file_path, fm).transform()
                elif format_name == "Dinamacs":
                    sat = FmToPysat(fm).transform()
                    DimacsWriter(output_file_path, sat).transform()
                else:
                    raise ValueError(f"Formato no soportado: {format_name}")

                converted_files[format_name] = output_file_path
            except Exception as exc:
                logger.error(f"Error al convertir {uvl_file_path} a {format_name}: {exc}")
                temp_file.close()
                os.remove(output_file_path)
                raise exc

        return converted_files

    def zip_all_datasets(self) -> str:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "all_datasets.zip")
        supported_formats = ["Glencoe", "Dinamacs", "SPLOT"]

        datasets_found = False

        with ZipFile(zip_path, "w") as zipf:
            for user_dir in os.listdir("uploads"):
                user_path = os.path.join("uploads", user_dir)

                if os.path.isdir(user_path) and user_dir.startswith("user_"):
                    for dataset_dir in os.listdir(user_path):
                        dataset_path = os.path.join(user_path, dataset_dir)

                        if os.path.isdir(dataset_path) and dataset_dir.startswith("dataset_"):
                            dataset_id = int(dataset_dir.split("_")[1])

                            if self.is_synchronized(dataset_id):
                                datasets_found = True  # Se encontró al menos un dataset sincronizado
                                for subdir, _, files in os.walk(dataset_path):
                                    for file in files:
                                        if file.endswith(".uvl"):
                                            uvl_file_path = os.path.join(subdir, file)

                                            # Añadir el archivo UVL original al ZIP
                                            uvl_relative_path = os.path.join(
                                                dataset_dir, "UVL", file
                                            )
                                            zipf.write(uvl_file_path, arcname=uvl_relative_path)

                                            # Convertir a otros formatos y añadirlos al ZIP
                                            converted_files = self.convert_uvl_to_formats(
                                                uvl_file_path, supported_formats
                                            )
                                            for fmt, converted_file in converted_files.items():
                                                fmt_relative_path = os.path.join(
                                                    dataset_dir, fmt, os.path.basename(converted_file)
                                                )
                                                zipf.write(converted_file, arcname=fmt_relative_path)

        # Si no se encontraron datasets, devolver un error 404
        if not datasets_found:
            abort(404, description="No synchronized datasets found.")

        return zip_path

    def update_dsmetadata(self, id, **kwargs):
        return self.dsmetadata_repository.update(id, **kwargs)

    def get_uvlhub_doi(self, dataset: DataSet) -> str:
        domain = os.getenv('DOMAIN', 'localhost')
        return f'http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}'


class AuthorService(BaseService):
    def __init__(self):
        super().__init__(AuthorRepository())


class DSDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(DSDownloadRecordRepository())


class DSMetaDataService(BaseService):
    def __init__(self):
        super().__init__(DSMetaDataRepository())

    def update(self, id, **kwargs):
        return self.repository.update(id, **kwargs)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.repository.filter_by_doi(doi)


class DSViewRecordService(BaseService):
    def __init__(self):
        super().__init__(DSViewRecordRepository())

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.repository.the_record_exists(dataset, user_cookie)

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.repository.create_new_record(dataset, user_cookie)

    def create_cookie(self, dataset: DataSet) -> str:

        user_cookie = request.cookies.get("view_cookie")
        if not user_cookie:
            user_cookie = str(uuid.uuid4())

        existing_record = self.the_record_exists(dataset=dataset, user_cookie=user_cookie)

        if not existing_record:
            self.create_new_record(dataset=dataset, user_cookie=user_cookie)

        return user_cookie


class DOIMappingService(BaseService):
    def __init__(self):
        super().__init__(DOIMappingRepository())

    def get_new_doi(self, old_doi: str) -> str:
        doi_mapping = self.repository.get_new_doi(old_doi)
        if doi_mapping:
            return doi_mapping.dataset_doi_new
        else:
            return None


class SizeService():

    def __init__(self):
        pass

    def get_human_readable_size(self, size: int) -> str:
        if size < 1024:
            return f'{size} bytes'
        elif size < 1024 ** 2:
            return f'{round(size / 1024, 2)} KB'
        elif size < 1024 ** 3:
            return f'{round(size / (1024 ** 2), 2)} MB'
        else:
            return f'{round(size / (1024 ** 3), 2)} GB'


class DSRatingService(BaseService):
    def __init__(self):
        super().__init__(DSRatingRepository())

    def add_or_update_rating(self, dsmetadata_id: int, user_id: int, rating_value: int) -> DSRating:
        # Verificar si ya existe una calificación para este usuario y dataset
        existing_rating = self.repository.get_user_rating(dsmetadata_id, user_id)

        if existing_rating:
            # Actualiza la calificación existente
            existing_rating.rating = rating_value
            existing_rating.rated_date = datetime.utcnow()
        else:
            # Crea una nueva calificación
            existing_rating = self.repository.create(
                commit=False,
                ds_meta_data_id=dsmetadata_id,
                user_id=user_id,
                rating=rating_value,
                rated_date=datetime.utcnow()
            )

        self.repository.session.commit()
        return existing_rating

    def get_dataset_average_rating(self, dsmetadata_id: int) -> float:
        return self.repository.get_average_rating(dsmetadata_id)

    def get_total_ratings(self, dsmetadata_id: int) -> int:
        return self.repository.count_ratings(dsmetadata_id)

    def get_datasets_with_rating(self, current_user_id):
        datasets = self.repository.get_synchronized(current_user_id)
        for dataset in datasets:
            dataset.ds_meta_data.rating = self.dsrating_repository.get_average_rating(dataset.ds_meta_data.id)
        return datasets
