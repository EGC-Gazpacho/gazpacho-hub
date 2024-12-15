from locust import HttpUser, task, between
import random


class ExploreModelBehavoiur(HttpUser):
    wait_time = between(1, 2)

    @task(2)
    def view_models(self):
        with self.client.get("/explore.explore2_models", catch_response=True) as response:
            if response.status_code == 200:
                print("Explore models page loaded successfully.")
            else:
                print(f"Error loading explore models page: {response.status_code}")
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def download_specific_model(self):
        file_id = random.randint(1, 100)
        with self.client.get(f"/file/download/{file_id}", catch_response=True) as response:
            if response.status_code == 200:
                print(f"Model {file_id} loaded successfully.")
            elif response.status_code == 404:
                print(f"Model {file_id} not found.")
            else:
                print(f"Error loading file {file_id}: {response.status_code}")
                response.failure(f"Got status code {response.status_code}")
