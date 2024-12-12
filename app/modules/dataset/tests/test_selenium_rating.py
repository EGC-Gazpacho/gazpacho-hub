# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class TestRating():
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

  def test_rating(self):
    # Test name: rating
    # Step # | name | target | value | comment
    # 1 | open | http://localhost:5000/doi/10.1234/dataset4/ |  | 
    self.driver.get("http://localhost:5000/doi/10.1234/dataset4/")
    # 2 | setWindowSize | 1050x731 |  | 
    self.driver.set_window_size(1050, 731)
    # 3 | click | css=.nav-link:nth-child(1) |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
    # 4 | click | id=email |  | 
    self.driver.find_element(By.ID, "email").click()
    # 5 | type | id=email | user1@example.com | 
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    # 6 | click | id=password |  | 
    self.driver.find_element(By.ID, "password").click()
    # 7 | type | id=password | 1234 | 
    self.driver.find_element(By.ID, "password").send_keys("1234")
    # 8 | click | id=submit |  | 
    self.driver.find_element(By.ID, "submit").click()
    # 9 | click | linkText=View dataset |  | 
    self.driver.find_element(By.LINK_TEXT, "View dataset").click()
    # 10 | click | css=#star-rating-12 > span:nth-child(4) |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#star-rating-12 > span:nth-child(4)").click()
    # 11 | click | id=rate-button-12 |  | 
    self.driver.find_element(By.ID, "rate-button-12").click()
    # 12 | click | css=#star-rating-12 > span:nth-child(5) |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#star-rating-12 > span:nth-child(5)").click()
    # 13 | click | id=rate-button-12 |  | 
    self.driver.find_element(By.ID, "rate-button-12").click()
