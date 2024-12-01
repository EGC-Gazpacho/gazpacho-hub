import base64
import requests


def upload_dataset_to_github(owner, repo_name, branch, dataset, token, commit_message, license, repo_type):

    if repo_type == 'new':
        repo_created = create_repo(owner, repo_name, token)
        if not repo_created:
            return f"Error: No se pudo crear el repositorio {repo_name}.", 400

    github_api = f"https://api.github.com/repos/{owner}/{repo_name}/contents/"

    dataset_name = dataset.name()  
    files_content = []

    for fm in dataset.feature_models:
        for file in fm.files:
            print(f"Subiendo archivo: {file.__dict__}") 
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
            "licene": license
        }

        github_api_with_file = f"{github_api}{file_data['path']}"
        response = requests.put(github_api_with_file, json=data, headers=headers)

    return response.json().get('message'), response.status_code


def check_branch_exists(owner, repo_name, branch, access_token):
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/branches/{branch}"
        
        headers = {
            "Authorization": f"token {access_token}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return True  
        elif response.status_code == 404:
            return False  
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as err:
        return {"error": f"An error occurred: {str(err)}"}, 500


def create_repo(owner, repo_name, token):
    """
    Crea un repositorio en GitHub usando la API.
    """
    github_api = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    data = {
        "name": repo_name,
        "private": False,  
        "description": "Repositorio creado a través de la API"
    }

    response = requests.post(github_api, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Repositorio '{repo_name}' creado correctamente.")
        return True
    else:
        print(f"Error al crear el repositorio: {response.json().get('message')}")
        return False


