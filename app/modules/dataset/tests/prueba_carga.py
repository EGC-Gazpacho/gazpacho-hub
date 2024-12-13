from locust import HttpUser, task, between
import logging

# Configurar el nivel de log para capturar más detalles
logging.basicConfig(level=logging.INFO)


class NotepadUser(HttpUser):
    wait_time = between(1, 3)  # Menor intervalo para pruebas más intensivas

    def on_start(self):
        """Inicio de sesión al comenzar la sesión simulada."""
        credentials = {
            "email": "user@example.com",
            "password": "test1234"
        }
        with self.client.post("/login", data=credentials, catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Login successful.")
            else:
                logging.error(f"Login failed: {response.status_code}")
                response.failure(f"Login error: {response.text}")

    @task(3)
    def view_dataset(self):
        """Simula la vista de un dataset."""
        doi = "10.1234/dataset4"  # Cambiar para simular diferentes DOIs
        with self.client.get(f"/doi/{doi}/", catch_response=True) as response:
            if response.status_code == 200 and "dataset" in response.text.lower():
                logging.info(f"Dataset {doi} loaded successfully.")
            else:
                logging.error(f"Error loading dataset {doi}: {response.status_code}")
                response.failure(f"Dataset load failed: {response.text}")

    @task(2)
    def download_formats(self):
        """Simula la descarga en múltiples formatos."""
        formats = ["json", "yaml", "xml"]
        dataset_id = 6
        url = "/dataset/download_informat/"
        for file_format in formats:
            with self.client.get(f"{url}{file_format}/{dataset_id}", catch_response=True) as response:
                if response.status_code == 200:
                    # Validar que el contenido sea un ZIP para los formatos correctos
                    if "application/zip" in response.headers.get("Content-Type", ""):
                        logging.info(f"Downloaded dataset in {file_format} format successfully.")
                    else:
                        logging.error(f"Invalid content for {file_format}: {response.headers.get('Content-Type')}")
                        response.failure("Invalid file content.")
                else:
                    logging.error(f"Failed to download dataset in {file_format}: {response.status_code}")
                    response.failure(f"Download error: {response.text}")

    def on_stop(self):
        """Cierra sesión al terminar la sesión simulada."""
        with self.client.get("/logout", catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Logout successful.")
            else:
                logging.error(f"Logout failed: {response.status_code}")
                response.failure("Logout error.")
