from locust import HttpUser, task, between
import logging
import random
import re

logging.basicConfig(level=logging.INFO)


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 3)
    csrf_token = None

    def login(self):
        """Perform login and extract CSRF token."""
        credentials = {
            "email": "user@example.com",
            "password": "test1234"
        }
        with self.client.post("/login", data=credentials, catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Login successful.")
                self.csrf_token = self.extract_csrf_token(response.text)
                logging.info(f"CSRF token extracted: {self.csrf_token}")
                return True
            else:
                logging.error(f"Login failed: {response.status_code}")
                response.failure(f"Login error: {response.text}")
                return False

    def extract_csrf_token(self, html):
        """Extract CSRF token from HTML."""
        match = re.search(r'name="csrf_token" value="([^"]+)"', html)
        return match.group(1) if match else None

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
        """Simulate logging in and rating a dataset."""
        if not self.login():  # Re-login before rating
            logging.error("Re-login failed. Cannot proceed with rating.")
            return

        dataset_id = 6  # Replace with the actual dataset ID
        rating = random.randint(1, 5)
        payload = {"rating": rating, "csrf_token": self.csrf_token}

        logging.info(f"Sending rating {rating} for dataset {dataset_id}.")
        with self.client.post(f"/datasets/{dataset_id}/rate", json=payload, catch_response=True) as response:
            if "application/json" in response.headers.get("Content-Type", ""):
                try:
                    response_data = response.json()
                    if response_data.get("message") == "Rating added/updated":
                        logging.info(f"Rating {rating} for dataset {dataset_id} submitted successfully.")
                        logging.info(f"Average rating: {response_data.get('average_rating')}")
                    else:
                        logging.error(f"Unexpected response: {response.text}")
                        response.failure(f"Unexpected response: {response.text}")
                except ValueError:
                    logging.error(f"Failed to parse JSON: {response.text}")
                    response.failure("Invalid JSON response.")
            else:
                logging.error(f"Non-JSON response received: {response.text}")
                response.failure("Non-JSON response received.")

    def on_stop(self):
        """Logout at the end of a simulated session."""
        with self.client.get("/logout", catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Logout successful.")
            else:
                logging.error(f"Logout failed: {response.status_code}")
                response.failure("Logout error.")
