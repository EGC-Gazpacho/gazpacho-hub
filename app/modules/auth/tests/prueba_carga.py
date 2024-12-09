from locust import HttpUser, TaskSet, task, between
from core.locust.common import get_csrf_token, fake
from core.environment.host import get_host_for_locust_testing
import logging

class ListUsers(HttpUser):
    wait_time = between(1, 5)
    def on_start(self):
        credentials = {
            "email":"user@example.com",
            "password":"test1234"
        }
        with self.client.post("/login", data=credentials, catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Login succesful.")
            else:
                logging.error(f"Login failed: {response.status_code}")
                response.failure(f"Login error: {response.text}")

    @task
    def access_page(self):
        print("Accediendo a la pagina de listado de usuarios...")
        with self.client.get("/listarUsuarios", catch_response=True) as response:
            if response.status_code == 200:
                print("Pagina cargada con exito")
            else:
                print(f"Error al cargar la pagina: {response.status_code}")

    def on_stop(self):
        """Cierra la sesion"""
        with self.client.get("/logout",catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Logout successful")
            else:
                logging.error(f"Logout failed: {response.status_code}")
                response.failure("Logout error.")