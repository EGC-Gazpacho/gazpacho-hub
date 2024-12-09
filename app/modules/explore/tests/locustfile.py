"""
from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing

class ExploreBehavior(TaskSet):
    @task
    def explore_page(self):
        self.client.get("/explore")

class ExploreUser(HttpUser):
    tasks = [ExploreBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
"""
