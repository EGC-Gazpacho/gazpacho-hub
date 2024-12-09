import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from core.selenium.common import initialize_driver, close_driver
from selenium.webdriver.common.action_chains import ActionChains
from core.environment.host import get_host_for_selenium_testing
from app.modules.github.services import GitHubService

class TestUploadDataSetToGitHub:
    
    def setup_method(self):
        self.token = os.getenv("GITHUB_ACCESS_TOKEN")
    

    # Test the creation of a dataset in GitHub with success
    def test_create_dataset_github(self):
        
        
        
        driver = initialize_driver()
        
        try:
            host = get_host_for_selenium_testing()
            driver.get(f'{host}/login')
            
            time.sleep(4)
            
            driver.maximize_window()
            driver.find_element(By.ID, "email").click()
            driver.find_element(By.ID, "email").send_keys("user1@example.com")
            driver.find_element(By.ID, "password").send_keys("1234")
            driver.find_element(By.ID, "submit").click()
            driver.find_element(By.LINK_TEXT, "Explore").click()
            
            time.sleep(4)
            
            driver.find_element(By.LINK_TEXT, "Backup dataset to GitHub").click()
            driver.find_element(By.ID, "commit_message").click()
            driver.find_element(By.ID, "commit_message").send_keys("Esto es un test de Selenium")
            driver.find_element(By.ID, "owner").click()
            driver.find_element(By.ID, "owner").send_keys("rafduqcol")
            driver.find_element(By.ID, "repo_name").click()
            driver.find_element(By.ID, "repo_name").send_keys("uvl_test_repo")
            driver.find_element(By.ID, "branch").click()
            dropdown = driver.find_element(By.ID, "repo_type")
            dropdown.find_element(By.XPATH, "//option[. = 'New Repository']").click()
            element = driver.find_element(By.ID, "repo_type")
            actions = ActionChains(driver)
            actions.move_to_element(element).click_and_hold().perform()
            element = driver.find_element(By.ID, "repo_type")
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            element = driver.find_element(By.ID, "repo_type")
            actions = ActionChains(driver)
            actions.move_to_element(element).release().perform()
            driver.find_element(By.ID, "access_token").click()
            driver.find_element(By.ID, "access_token").send_keys(self.token)
            driver.find_element(By.ID, "upload_button_github").click()
            
            # Check if the dataset was uploaded to GitHub
            time.sleep(4)
            
            response = GitHubService.check_repository_exists("rafduqcol", "uvl_test_repo", self.token)
            assert response 

        finally:
            close_driver(driver)
            GitHubService.delete_repo(
                self.token, 
                "rafduqcol",        
                "uvl_test_repo")
            
    
            
