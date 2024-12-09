'''
from selenium.webdriver.chrome.service import Service as ChromeService
import time
from core.selenium.common import initialize_driver, close_driver
from selenium import webdriver


def test_explore_models_page():
    driver = initialize_driver()
    try:
        driver.get("http://localhost:5000/explore2/models")
        time.sleep(2)

        # Check if the page title is correct
        assert "Explore Models" in driver.title, "Page title does not match"
    finally:
        close_driver(driver)

def test_search_models():
    driver = initialize_driver()
    try:
        driver.get("http://localhost:5000/explore")
        time.sleep(2)

        # Perform a search
        search_input = driver.find_element(By.ID, "query")
        search_input.send_keys("Model1")
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)

        # Check if the search results are displayed
        results = driver.find_elements(By.CLASS_NAME, "card-title")
        assert len(results) > 0, "No results found for search query 'Model1'"

        # Check if the correct model is displayed
        assert "Model1" in results[0].text, "Search result does not match 'Model1'"
    finally:
        close_driver(driver)

def test_search_no_results():
    driver = initialize_driver()
    try:
        driver.get("http://localhost:5000/explore")
        time.sleep(2)

        # Perform a search
        search_input = driver.find_element(By.ID, "query")
        search_input.send_keys("NonExistentModel")
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)

        # Check if no results are displayed
        results = driver.find_elements(By.CLASS_NAME, "card-title")
        assert len(results) == 0, "Results found for search query 'NonExistentModel'"
    finally:
        close_driver(driver)
'''
