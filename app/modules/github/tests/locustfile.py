from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing


class GitHubBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def index(self):
        # Realizar la solicitud GET al índice
        response = self.client.get("/github/upload/2")

        if response.status_code != 200:
            print(f"GitHub index failed: {response.status_code}")

    @task(2)
    def upload(self):
        data = {
            "commit_message": "Initial commit",
            "owner": "test_owner",
            "repo_name": "test_repo",
            "branch": "main",
            "repo_type": "new",
            "access_token": "your_access_token",
            "license": "MIT"
        }

        response = self.client.post("/github/upload/2", data=data)

        if response.status_code != 200:
            print(f"GitHub upload failed: {response.status_code}")
        else:
            print(f"GitHub upload successful: {response.status_code}")


class GitHubUser(HttpUser):
    tasks = [GitHubBehavior]  # Establecer las tareas a ejecutar
    min_wait = 5000  # Tiempo mínimo de espera entre tareas (en milisegundos)
    max_wait = 9000  # Tiempo máximo de espera entre tareas (en milisegundos)
    host = get_host_for_locust_testing()  # Obtener la URL del servidor de pruebas
