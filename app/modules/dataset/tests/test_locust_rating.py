from locust import HttpUser, task, between
import logging
import random

# Configure logging level for detailed output
logging.basicConfig(level=logging.INFO)


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        credentials = {
            "email": "user2@example.com",
            "password": "1234"
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

    @task(3)
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
        dataset_id = 6
        rating = random.randint(1, 5)
        payload = {"rating": rating}

        if not self.is_authenticated():  # Implement a session validation check
            logging.info("Session expired. Re-authenticating.")
            self.on_start()  # Re-login

        csrf_token = self.get_csrf_token()  # Implement a method to fetch the token
        headers = {"X-CSRFToken": csrf_token}
        with self.client.post(f"/datasets/{dataset_id}/rate",
                              json=payload, headers=headers, catch_response=True) as response:
            # Process response
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if response_data.get("message") == "Rating added/updated":
                        logging.info(f"Rating {rating} for dataset {dataset_id} submitted successfully.")
                    else:
                        logging.error(f"Unexpected response: {response.text}")
                        response.failure(f"Unexpected response: {response.text}")
                except ValueError:
                    logging.error(f"Non-JSON response received: {response.text}")
                    response.failure("Non-JSON response received.")
            else:
                logging.error(f"Rating failed for dataset {dataset_id}: {response.status_code}")
                response.failure(f"Rating error: {response.text}")
        logging.info(f"Session cookies: {self.client.cookies.get_dict()}")

    def on_stop(self):
        """Logout at the end of a simulated session."""
        with self.client.get("/logout", catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Logout successful.")
            else:
                logging.error(f"Logout failed: {response.status_code}")
                response.failure("Logout error.")
