from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class TestCargarlistado:
    def setup_method(self, method):
        # Set up options for Chromium
        chrome_options = Options()
        chrome_options.binary_location = '/usr/bin/chromium-browser'  # Update this path as needed

        # Create a service object for the ChromeDriver
        service = Service('/usr/bin/chromedriver')  # Ensure this is the correct path to your ChromeDriver

        # Initialize the WebDriver with the Chromium options
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_cargarlistado(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1048)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("juagonluc1@alum.us.es")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("281102")
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(9) .align-middle:nth-child(2)").click()
        self.driver.find_element(By.LINK_TEXT, "González, Juan Antonio").click()
        self.driver.find_element(By.CSS_SELECTOR, ".dropdown-item:nth-child(2)").click()
