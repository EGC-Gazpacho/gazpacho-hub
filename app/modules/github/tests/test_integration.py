from datetime import datetime
import pytest
import os
from app.modules.github.services import GitHubService
from app import create_app, db
from app.modules.dataset.models import Author, DSMetaData, DSMetrics, DataSet, PublicationType
from app.modules.auth.models import User



class TestGitHubService:

    @pytest.fixture(autouse=True)
    def github_setup(self, test_client):
        """
        Setup inicial para las pruebas.
        """
        app = create_app()  # Asegúrate de tener la aplicación correctamente configurada
        
        # Establecer el contexto de la aplicación fuera de test_client
        with app.app_context():
            dataset = DataSet.query.filter_by(id=1).first()
            db.session.add(dataset)
            print("DATASET_1", dataset)

            
            author = Author(
            name="John Doe",
            affiliation="University of Example",
            orcid="0000-0000-0000-0000"
                )

            # Crear un DSMetrics (con métricas del dataset)
            ds_metrics = DSMetrics(
                number_of_models="10",
                number_of_features="50"
            )

            # Crear un DSMetaData (con metadatos del dataset)
            ds_meta_data = DSMetaData(
                deposition_id=123456,
                title="Example Dataset",
                description="This is an example dataset for testing.",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN,  # Asumimos que es un plan de gestión de datos
                publication_doi="10.1234/56789",
                dataset_doi="10.5678/98765",
                tags="example, dataset, test",
                ds_metrics=ds_metrics,
                authors=[author]  # Asocias el autor previamente creado
            )

            # Crear un DataSet (asociado a DSMetaData)
            data_set = DataSet(
                user_id=1,  # Supón que el ID del usuario es 1
                ds_meta_data=ds_meta_data,  # Asociamos los metadatos
                created_at=datetime.utcnow()
            )

            # Guardar todo en la base de datos
            db.session.add(author)
            db.session.add(ds_metrics)
            db.session.add(ds_meta_data)
            db.session.add(data_set)
            db.session.commit()
            
            self.dataset = data_set
            
            print("Dataset creado", data_set)
            
            # Configuración inicial de variables
            self.token = os.getenv("GITHUB_TOKEN")  # GitHub Token, asegurarse de que esté en el entorno
            self.invalid_token = "invalid_token"
            self.repo_owner = "rafduqcol"
            self.repo_name = "uvl_repo_tests"
            self.branch = "main"
            self.commit_message = "Test commit"
            self.license = "MIT"
            
            # Eliminar el usuario existente si existe
            existing_user = User.query.filter_by(email="user@example.com").first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            # Crear un usuario de prueba
            user = User(email="user@example.com", password="test1234")
            db.session.add(user)
            db.session.commit()
        
        # Crear el cliente de prueba una vez se configure el entorno
        self.client = test_client  # Asigna el cliente a `self.client`

    def test_create_repo_fail(self):
        result = GitHubService.create_repo(self.repo_name, self.invalid_token)
        assert not result, "La creación del repositorio debería haber fallado"

    def test_create_repo_success(self):
        result = GitHubService.create_repo(self.repo_name, self.token)
        assert result, "La creación del repositorio debería haber tenido éxito"
    
    def test_check_repository_exists_found(self):
        result = GitHubService.check_repository_exists(self.repo_owner, self.repo_name, self.token)
        assert result, "El repositorio debería existir"

    def test_check_repository_exists_not_found(self):
        result = GitHubService.check_repository_exists("no_exists", self.repo_name, self.token)
        assert not result, "El repositorio no debería existir"
        
        # Test for failed dataset upload
    def test_upload_dataset_to_github_fail(self):
        with db.session.begin():
            # Reasociar el objeto a la sesión
            # Ahora se puede acceder al atributo relacionado
            result_message, status_code = GitHubService.upload_dataset_to_github(
                self.repo_owner,
                self.repo_name,
                self.branch,
                self.dataset,
                self.invalid_token,
                self.commit_message,
                self.license,
                "existing"
            )
        print(result_message, status_code)
        assert status_code == 404, f"Expected status code 404, but got {status_code}"

    def test_delete_repo(self):
        result = GitHubService.delete_repo(self.token, self.repo_owner, self.repo_name)
        assert result, "La eliminación del repositorio debería haber tenido éxito"
