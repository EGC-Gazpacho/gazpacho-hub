from flask import logging
from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class CommunityBehavior(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        """
        Log in to prepare for subsequent community actions.
        """
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234",
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")

    @task
    def view_communities(self):
        """
        View the list of communities.
        """
        response = self.client.get("/community")
        if response.status_code != 200:
            print(f"Failed to fetch community list: {response.status_code}")

    @task
    def view_user_communities(self):
        """
        View the communities the user is part of.
        """
        response = self.client.get("/user-communities")
        if response.status_code != 200:
            print(f"Failed to fetch user communities: {response.status_code}")

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


class CommunityUser(HttpUser):
    tasks = [CommunityBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
