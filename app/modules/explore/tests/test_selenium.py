from selenium.webdriver.common.by import By
import time
from core.selenium.common import initialize_driver, close_driver

def test_explore_models_page():
    driver = initialize_driver()
    try:
        driver.get("http://localhost:5000/explore")
        time.sleep(2)
        
        search_input = driver.find_element(By.ID, "query")
        search_input.send_keys("test")
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)
        
        results = driver.find_elements(By.CLASS_NAME, "card-title")
        assert len(results) > 0, "No results found"
        
        download_button = driver.find_element(By.CLASS_NAME, "btn-primary")
        assert download_button.is_displayed(), "Download button not found"
    finally:
        close_driver(driver)