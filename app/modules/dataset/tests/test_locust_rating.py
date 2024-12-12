from locust import HttpUser, task, between
import logging
import random

# Configure logging level for detailed output
logging.basicConfig(level=logging.INFO)


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        credentials = {
            "email": "user@example.com",
            "password": "test1234"
        }
        with self.client.post("/login", data=credentials, catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Login successful.")
                # Verify authentication
                with self.client.get("/protected/resource", catch_response=True) as auth_check:
                    if auth_check.status_code == 200:
                        logging.info("Session authenticated.")
                    else:
                        logging.error("Authentication verification failed.")
                        auth_check.failure("Authentication verification failed.")
            else:
                logging.error(f"Login failed: {response.status_code}")
                response.failure(f"Login error: {response.text}")

    @task(1)
    def view_dataset(self):
        """Simulate viewing a dataset."""
        doi = "10.1234/dataset4"  # Change to simulate different DOIs
        with self.client.get(f"/doi/{doi}/", catch_response=True) as response:
            if response.status_code == 200 and "dataset" in response.text.lower():
                logging.info(f"Dataset {doi} loaded successfully.")
            else:
                logging.error(f"Error loading dataset {doi}: {response.status_code}")
                response.failure(f"Dataset load failed: {response.text}")

    @task(2)
    def rate_dataset(self):
        """Simulate rating a dataset."""
        dataset_id = 12  # Replace with the actual dataset ID you want to test
        rating = random.randint(1, 5)  # Generate a random rating between 1 and 5
        payload = {"rating": rating}

        with self.client.post(f"/datasets/{dataset_id}/rate", json=payload, catch_response=True) as response:
            try:
                if response.status_code == 200:
                    # Attempt to parse the JSON response
                    response_data = response.json()
                    if response_data.get("message") == "Rating added/updated":
                        logging.info(f"Rating {rating} for dataset {dataset_id} submitted successfully.")
                        logging.info(f"Average rating: {response_data.get('average_rating')}")
                    else:
                        logging.error(f"Unexpected response: {response.text}")
                        response.failure(f"Unexpected response: {response.text}")
                else:
                    logging.error(f"Rating failed for dataset {dataset_id}: {response.status_code}")
                    response.failure(f"Rating error: {response.text}")
            except ValueError:
                # Handle non-JSON response
                logging.error(f"Non-JSON response received: {response.text}")
                response.failure("Non-JSON response received.")
            logging.info(f"Raw response: {response.text}")

    def on_stop(self):
        """Logout at the end of a simulated session."""
        with self.client.get("/logout", catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Logout successful.")
            else:
                logging.error(f"Logout failed: {response.status_code}")
                response.failure("Logout error.")
