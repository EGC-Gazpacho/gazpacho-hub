from locust import HttpUser, task, between
import logging
import random

# Configure logging level for detailed output
logging.basicConfig(level=logging.INFO)


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login at the start of a simulated session."""
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

    @task(4)
    def rate_dataset(self):
        """Simulates rating one dataset."""
        dataset_id = random.randint(1, 4)
        rating = random.randint(0, 5)
        response = self.client.post(f"/datasets/{dataset_id}/rate", json={"rating": rating})

        if response.status_code == 200:
            print(f"Dataset {dataset_id} rated: {rating}")
        elif response.status_code == 400:
            print(f"Error: Failed when rating: {response.json()}")
        elif response.status_code == 401:
            print("Unauthenticated user.")

    @task(3)
    def get_dataset_average_rating(self):
        """Simulates viewing the average rating of one dataset."""
        dataset_id = random.randint(1, 4)
        response = self.client.get(f"/datasets/{dataset_id}/average-rating")

        if response.status_code == 200:
            average_rating = response.json().get("average_rating")
            print(f"Average rating -{average_rating}- for Dataset {dataset_id}")
        elif response.status_code == 404:
            print(f"Dataset {dataset_id} not found.")
        else:
            print(f"Error: UnExpectedError: {response.status_code}")

    def on_stop(self):
        """Logout at the end of a simulated session."""
        with self.client.get("/logout", catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Logout successful.")
            else:
                logging.error(f"Logout failed: {response.status_code}")
                response.failure("Logout error.")
