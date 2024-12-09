from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def test_explore_models_page():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Step 1: Go to explore page
        driver.get(f'{host}/explore')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(4)

        # Step 2: Press the button that says Search Models
        search_models_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search Models')]")
        search_models_button.click()

        # Wait a little while to ensure that the action has been completed
        time.sleep(4)

        # Step 3: Now it goes to the explore models page because of the button
        assert 'explore2/models' in driver.current_url, 'Did not navigate to explore models page'

        # Step 4: The models are shown and it should insert in the search bar Feature Model 11, for example
        search_bar = driver.find_element(By.ID, 'query')
        search_bar.send_keys('Feature Model 11')
        search_bar.send_keys(Keys.RETURN)

        # Wait a little while to ensure that the search has been completed
        time.sleep(4)

        # Step 5: It checks that the model appears
        try:
            print('Looking for model Feature Model 11...')
            time.sleep(1)
            model_element = driver.find_element(By.XPATH, "//h5[contains(@class, 'card-title') and contains(text(), 'Feature Model 11')]")
            assert model_element.is_displayed(), 'Model Feature Model 11 not found'
            print('Feature Model 11 found')
        except NoSuchElementException:
            print(driver.page_source)  # Print the page source for debugging
            raise AssertionError('Model Feature Model 11 not found')

        # Step 6: Look for the download button
        try:
            print('Looking for download button...')
            time.sleep(1)
            download_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div/div[1]/div/div[11]/div/div/a")
            assert download_button.is_displayed(), 'Download button not found'
            print('Download button detected')
        except NoSuchElementException:
            print(driver.page_source)  # Print the page source for debugging
            raise AssertionError('Download button not found')
        
        # Step 7: Click the download button
        print('Checking the path of the download button...')
        time.sleep(1)
        download_url = download_button.get_attribute("href")
        print(f"Download URL: {download_url}")

        # Ensure the URL matches the expected format for downloading files
        expected_url_part = f"{host}/file/download"
        assert expected_url_part in download_url, f"Download URL does not match expected format. Found: {download_url}"

        # Click the button and verify the behavior
        
    finally:
        # Close the browser
        close_driver(driver)


# Call the test function
test_explore_models_page()