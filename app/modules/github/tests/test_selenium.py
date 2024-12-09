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
        self.token = os.getenv("GITHUB_TOKEN")
    

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
            
            
    # Test the creation of a dataset in GitHub without success bad token
    def test_create_dataset_github_bad_token(self):
        
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
            driver.find_element(By.ID, "access_token").click()
            driver.find_element(By.ID, "access_token").send_keys("bad_token")
            driver.find_element(By.ID, "upload_button_github").click()
            
            # Check if the dataset was uploaded to GitHub
            time.sleep(4)
            
            error_element = driver.find_element(By.ID, "upload_github_error")
            assert error_element.is_displayed(), "El mensaje de error no se muestra."
            
            error_message = driver.find_element(By.ID, "error_message").text
            expected_message = ("Error to upload the file: GitHub API error: 401 Client Error: Unauthorized "
                    "for url: https://api.github.com/repos/rafduqcol/uvl_test_repo")
            
            assert error_message == expected_message, f"El mensaje de error no coincide. Actual: {error_message}"

            
        finally:
            close_driver(driver)
            
            
            
            
     # Test the creation of a dataset in GitHub without success bad repo
    def test_create_dataset_github_bad_repo(self):
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
            driver.find_element(By.ID, "repo_name").send_keys("not_existing_uvl_repo")
            driver.find_element(By.ID, "access_token").click()
            driver.find_element(By.ID, "access_token").send_keys(self.token)
            driver.find_element(By.ID, "upload_button_github").click()

            time.sleep(4)

            error_element = driver.find_element(By.ID, "upload_github_error")
            assert error_element.is_displayed(), "El mensaje de error no se muestra."

            error_message = driver.find_element(By.ID, "error_message").text
            expected_message = ("Error to upload the file: Repository not found. Verify the repository owner and name.")
            assert error_message == expected_message, f"El mensaje de error no coincide. Actual: {error_message}"

        finally:
            close_driver(driver)
            
            
            
     # Test the creation of a dataset in GitHub with no succes, the dataset already exists
    def test_create_dataset_github_dataset_exists(self):
           
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
            
            driver.find_element(By.XPATH, "(//a[contains(text(),\'Backup dataset to GitHub\')])[1]").click()          
            driver.find_element(By.ID, "commit_message").click()
            driver.find_element(By.ID, "commit_message").send_keys("Esto es un test de Selenium")
            driver.find_element(By.ID, "owner").click()
            driver.find_element(By.ID, "owner").send_keys("rafduqcol")
            driver.find_element(By.ID, "repo_name").click()
            driver.find_element(By.ID, "repo_name").send_keys("uvl_test_repo")
            driver.find_element(By.ID, "access_token").click()
            driver.find_element(By.ID, "access_token").send_keys(self.token)
            driver.find_element(By.ID, "upload_button_github").click()
            
            # Check if the dataset was uploaded to GitHub
            time.sleep(4)
            
            error_element = driver.find_element(By.ID, "upload_github_error")
            assert error_element.is_displayed(), "El mensaje de error no se muestra."

            error_message = driver.find_element(By.ID, "error_message").text
            expected_message = ("Error to upload the file: A dataset with the same name already exists in the repository.")
            assert error_message == expected_message, f"El mensaje de error no coincide. Actual: {error_message}"
                        
        finally:
            close_driver(driver)
            
            
    # Test the creation of a dataset in GitHub in a new branch
    # Test the creation of a dataset in GitHub with no succes, the branch no exists
    def test_create_dataset_github_no_existing_branch(self):
           
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
            branch_field = driver.find_element(By.ID, "branch")
            branch_field.clear()
            branch_field.send_keys("not_existing_branch")
            driver.find_element(By.ID, "access_token").click()
            driver.find_element(By.ID, "access_token").send_keys(self.token)
            driver.find_element(By.ID, "upload_button_github").click()
            
            # Check if the dataset was uploaded to GitHub
            time.sleep(4)
            
            error_element = driver.find_element(By.ID, "upload_github_error")
            assert error_element.is_displayed(), "El mensaje de error no se muestra."

            error_message = driver.find_element(By.ID, "error_message").text
            expected_message = ("Error to upload the file: Branch not_existing_branch not found. Verify the branch name.")
            assert error_message == expected_message, f"El mensaje de error no coincide. Actual: {error_message}"
            
                        
        finally:
            close_driver(driver)
            GitHubService.delete_repo(
                "rafduqcol", 
                "uvl_test_repo", 
                self.token)
            
            
            
            
            
            
