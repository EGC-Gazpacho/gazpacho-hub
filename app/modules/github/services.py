import base64
import requests
from core.services.BaseService import BaseService


class GitHubService(BaseService):   
    
    def __init__(self, repository):
        super().__init__(repository)
        
    @staticmethod
    def upload_dataset_to_github(owner, repo_name, branch, dataset, token, commit_message, license, repo_type):
        """
        Upload dataset files to a GitHub repository.
        """
        if repo_type == 'new':
            print(f"Creating repository: {repo_name}")
            repo_created = GitHubService.create_repo(repo_name, token)
            if not repo_created:
                return f"Error: Could not create repository {repo_name}.", 400

        github_api = f"https://api.github.com/repos/{owner}/{repo_name}/contents/"

        dataset_name = dataset.name()
        files_content = []

        for fm in dataset.feature_models:
            for file in fm.files:
                print(f"Uploading file: {file.__dict__}")
                file_path = file.get_path()

                with open(file_path, "rb") as f:
                    encoded_content = base64.b64encode(f.read()).decode('utf-8')

                file_data = {
                    'path': f"{dataset_name}/{file.name}",
                    'content': encoded_content,
                }
                files_content.append(file_data)

        headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }

        for file_data in files_content:
            data = {
                "message": commit_message,
                "content": file_data['content'],
                "branch": branch,
                "license": license
            }

            github_api_with_file = f"{github_api}{file_data['path']}"
            response = requests.put(github_api_with_file, json=data, headers=headers)

            if not response.ok:
                raise requests.exceptions.HTTPError(f"Error {response.status_code}: {response.text}", response=response)

        return response.json().get('message'), response.status_code

    @staticmethod
    def check_repository_exists(owner, repo_name, access_token):
        """
        Check if a repository exists on GitHub.
        """
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {
            "Authorization": f"token {access_token}"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return True  
            elif response.status_code == 404:
                return False 
            else:
                response.raise_for_status()  
        except requests.exceptions.RequestException as e:
            raise e

    @staticmethod
    def check_branch_exists(owner, repo_name, branch, access_token):
        """
        Check if a branch exists in a GitHub repository.
        """
        url = f"https://api.github.com/repos/{owner}/{repo_name}/branches/{branch}"
        headers = {
            "Authorization": f"token {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            print(f"HTTP Status: {response.status_code}")

            if response.status_code == 200:
                return True  
            elif response.status_code == 404:
                return False  
            elif response.status_code == 401:
                raise requests.exceptions.HTTPError("Unauthorized - Invalid or expired access token.")
            else:
                response.raise_for_status()  

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error when checking branch: {http_err}")
            raise 

        except requests.exceptions.ConnectionError:
            print("Connection error while trying to access GitHub API.")
            raise requests.exceptions.RequestException("ConnectionError: Could not connect to GitHub.")

        except requests.exceptions.Timeout:
            print("Request to GitHub timed out.")
            raise requests.exceptions.RequestException(
                "TimeoutError: The request to GitHub exceeded the timeout."
            )

        except requests.exceptions.RequestException as req_err:
            print(f"Unexpected error when checking branch: {req_err}")
            raise 

    @staticmethod
    def create_repo(repo_name, token):
        """
        Create a repository on GitHub.
        """
        github_api = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }

        data = {
            "name": repo_name,
            "private": False,
            "description": "Repository created through the API"
        }

        response = requests.post(github_api, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Repository '{repo_name}' created successfully.")
            return True
        else:
            print(f"Error creating repository: {response.json().get('message')}")
            return False


    @staticmethod
    def delete_repo(token, repo_owner, repo_name):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            print(f"The repository '{repo_name}' was deleted successfully.")
            return ('Repository deleted successfully', 204)  # Aquí se devuelve la tupla
        else:
            print(f"Error deleting the repository: {response.json().get('message')}")
            return False


    
