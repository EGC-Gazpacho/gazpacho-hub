from flask import logging
from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class FilteringBehavior(TaskSet):

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234",
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")

    @task(2)
    def filter_by_query(self):
        """
        Perform a filtering operation with a query.
        """
        print("Performing filtering by query...")
        response = self.client.post("/explore", json={"query": "ai"})
        if response.status_code == 200:
            print("Filtering by query successful.")
        else:
            print(f"Error filtering by query: {response.status_code}")

    @task(1)
    def filter_by_features(self):
        """
        Perform a filtering operation by number of features.
        """
        print("Performing filtering by number of features...")
        response = self.client.post("/explore", json={"number_of_features": 50})
        if response.status_code == 200:
            print("Filtering by number of features successful.")
        else:
            print(f"Error filtering by number of features: {response.status_code}")

    @task(1)
    def filter_by_products(self):
        """
        Perform a filtering operation by number of products.
        """
        print("Performing filtering by number of products...")
        response = self.client.post("/explore", json={"number_of_products": 84})
        if response.status_code == 200:
            print("Filtering by number of products successful.")
        else:
            print(f"Error filtering by number of products: {response.status_code}")

    @task(1)
    def combined_filter(self):
        """
        Perform a combined filtering operation.
        """
        print("Performing combined filtering...")
        response = self.client.post(
            "/explore", json={"query": "ml", "number_of_features": 50}
        )
        if response.status_code == 200:
            print("Combined filtering successful.")
        else:
            print(f"Error in combined filtering: {response.status_code}")

    def on_stop(self):
        """
        Cierra sesión al terminar la sesión simulada.
        """
        with self.client.get("/logout", catch_response=True) as response:
            if response.status_code == 200:
                logging.info("Logout successful.")
            else:
                logging.error(f"Logout failed: {response.status_code}")
                response.failure("Logout error.")


class FilteringUser(HttpUser):
    tasks = [FilteringBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
