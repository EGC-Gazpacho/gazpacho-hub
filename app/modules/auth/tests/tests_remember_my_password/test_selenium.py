import time
from selenium.webdriver.common.by import By
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


class TestRememberMyPassword:

    def setup_method(self):
        """Se ejecuta antes de cada test para inicializar el driver."""
        self.driver = initialize_driver()

    def teardown_method(self):
        """Se ejecuta después de cada test para cerrar el driver."""
        close_driver(self.driver)

    def test_remember_my_password_success(self):
        """Test: Verificar la recuperación de contraseña exitosa con un correo registrado."""
        host = get_host_for_selenium_testing()
        self.driver.get(f'{host}/login')  # Navegar a la página de login

        time.sleep(3)

        self.driver.set_window_size(1156, 674)
        # Clic en el enlace "Forgot Password"
        self.driver.find_element(By.LINK_TEXT, "Forgot your password?").click()

        time.sleep(3)

        # Llenar el formulario de recuperación con un correo registrado
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("romerito3rubn@gmail.com")

        # Clic en el botón "Submit"
        self.driver.find_element(By.XPATH, '//button[text()="Send Recovery Link"]').click()

        time.sleep(4)

        # Verificar que el mensaje de éxito esté presente
        success_message = self.driver.find_element(By.CSS_SELECTOR, "li.success")
        assert success_message.text == "A recovery link has been sent to your email."

    def test_remember_my_password_error(self):
        """Test: Verificar la recuperación de contraseña con un correo no registrado."""
        host = get_host_for_selenium_testing()
        self.driver.get(f'{host}/login')  # Navegar a la página de login

        time.sleep(3)

        self.driver.set_window_size(1156, 674)
        # Clic en el enlace "Forgot Password"
        self.driver.find_element(By.LINK_TEXT, "Forgot your password?").click()

        time.sleep(3)

        # Llenar el formulario de recuperación con un correo no registrado
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("nonexistentuser@example.com")

        # Clic en el botón "Submit"
        self.driver.find_element(By.XPATH, '//button[text()="Send Recovery Link"]').click()

        time.sleep(4)

        # Verificar que el mensaje de error esté presente
        error_message = self.driver.find_element(By.CSS_SELECTOR, "li.error")
        assert error_message.text == "Email not registered."
