from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from core.environment.host import get_host_for_selenium_testing
import time

def initialize_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

class TestDashboard:
    def setup_method(self, method):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def test_selenium_dashboard(self):
        host = get_host_for_selenium_testing()
        self.driver.get(f'{host}/login')
        

        time.sleep(4)

        self.driver.set_window_size(1156, 674)
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        time.sleep(4)
        login_button = self.driver.find_element(By.ID, "submit")
        login_button.click()

        time.sleep(4)
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click()
        time.sleep(4)

        self.driver.find_element(By.ID, "dropdownGeneral").click()
        self.driver.find_element(By.ID, "toggleStatisticsButton").click()
        self.driver.find_element(By.ID, "dropdownGeneral").click()
        self.driver.find_element(By.CSS_SELECTOR, ".show > li:nth-child(2) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownGeneral").click()
        self.driver.find_element(By.CSS_SELECTOR, ".show > li:nth-child(3) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownGeneral").click()
        self.driver.find_element(By.CSS_SELECTOR, ".show > li:nth-child(4) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownGeneral").click()
        self.driver.find_element(By.CSS_SELECTOR, "li:nth-child(5) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownGeneral").click()
        self.driver.find_element(By.CSS_SELECTOR, "li:nth-child(6) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownUsuario").click()
        self.driver.find_element(By.CSS_SELECTOR, ".show > li:nth-child(1) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownUsuario").click()
        self.driver.find_element(By.CSS_SELECTOR, ".show > li:nth-child(2) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownUsuario").click()
        self.driver.find_element(By.CSS_SELECTOR, ".show > li:nth-child(3) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownUsuario").click()
        self.driver.find_element(By.CSS_SELECTOR, ".show > li:nth-child(4) > .dropdown-item").click()
        self.driver.find_element(By.ID, "dropdownGeneral").click()
        self.driver.find_element(By.ID, "toggleStatisticsButton").click()
