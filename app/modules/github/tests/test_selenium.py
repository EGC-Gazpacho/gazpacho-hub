from selenium import webdriver


class TestUploadDataSetToGitHub:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}
        
    
    def teardown_method(self, method):
        self.driver.quit()