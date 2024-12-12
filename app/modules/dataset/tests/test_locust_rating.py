from locust import HttpUser, task, between


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 5)

    @task(2)
    def load_tasks(self):
        print("Cargando la lista de tareas...")
        response = self.client.get("/tasks")
        if response.status_code == 200:
            print("Lista de tareas cargada correctamente.")
        else:
            print(f"Error al cargar la lista de tareas: {response.status_code}")

    @task(1)
    def create_task(self):
        print("Creando una nueva tarea...")
        response = self.client.post("/tasks", json={"title": "Tarea generada por Locust"})
        if response.status_code == 201:
            print("Tarea creada correctamente.")
        else:
            print(f"Error al crear la tarea: {response.status_code}")