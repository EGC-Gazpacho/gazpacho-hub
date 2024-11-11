# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class TestDownloadindifferentformatsselenium():
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
  
  def test_downloadindifferentformatsselenium(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(1854, 1011)
    self.driver.find_element(By.LINK_TEXT, "Sample dataset 3").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .xml").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .json").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .yaml").click()
    self.driver.get("http://localhost:5000/")
    self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .xml").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .json").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .yaml").click()
    self.driver.get("http://localhost:5000/")
    self.driver.find_element(By.LINK_TEXT, "Dataset prueba").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .xml").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .json").click()
    self.driver.find_element(By.LINK_TEXT, "Download in .yaml").click()
    
  
   
  
