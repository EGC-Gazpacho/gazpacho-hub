from locust import HttpUser, task, between


class PasswordRecoveryUser(HttpUser):
    wait_time = between(1, 3)

    @task(1)
    def password_recovery(self):
        """Simula un usuario que envía una solicitud de recuperación de contraseña."""
        response = self.client.post("/password_recovery", data={"email": "test@example.com"})
        assert response.status_code == 200  # Verifica que la respuesta sea OK

    @task(2)
    def password_reset(self):
        """Simula un usuario que restablece su contraseña con un token válido."""
        # Aquí, deberías tener un token válido pre-generado
        valid_token = "valid_token_for_testing"
        response = self.client.post(f"/password_reset/{valid_token}", data={"new_password": "newpassword123"})
        assert response.status_code == 200  # Verifica que la contraseña se haya restablecido correctamente
