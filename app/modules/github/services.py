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

        if not response.ok:
            raise requests.exceptions.HTTPError(f"Error {response.status_code}: {response.text}", response=response)

    return response.json().get('message'), response.status_code


def check_repository_exists(owner, repo_name, access_token):
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


def check_branch_exists(owner, repo_name, branch, access_token):

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
            raise requests.exceptions.HTTPError("Unauthorized - Token de acceso inválido o expirado.")
        else:
            response.raise_for_status()  

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP al verificar la rama: {http_err}")
        raise 

    except requests.exceptions.ConnectionError:
        print("Error de conexión al intentar acceder a la API de GitHub.")
        raise requests.exceptions.RequestException("ConnectionError: No se pudo conectar con GitHub.")

    except requests.exceptions.Timeout:
        print("La solicitud a GitHub excedió el tiempo de espera.")
        raise requests.exceptions.RequestException("TimeoutError: La solicitud a GitHub excedió el tiempo de espera.")

    except requests.exceptions.RequestException as req_err:
        print(f"Error inesperado al verificar la rama: {req_err}")
        raise 


def create_repo(owner, repo_name, token):

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
