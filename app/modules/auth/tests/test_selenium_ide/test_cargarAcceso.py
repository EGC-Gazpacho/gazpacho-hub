from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class TestCargarDataset:
    def setup_method(self, method):
        chrome_options = Options()
        chrome_options.binary_location = '/usr/bin/chromium-browser'
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_carga_dataset(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1048)

        # Navegar y realizar login
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").send_keys("juagonluc1@alum.us.es")
        self.driver.find_element(By.ID, "password").send_keys("281102")
        self.driver.find_element(By.ID, "submit").click()

        # Navegar hacia el dataset específico
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(11) > .sidebar-link").click()
        self.driver.find_element(By.LINK_TEXT, "Ir a Dataset 1").click()
