import base64
import requests


def upload_dataset_to_github(owner, repo_name, dataset, token, commit_message, license, repo_type):
    """
    Subir un dataset como una carpeta a un repositorio de GitHub usando la API.
    Crea una carpeta con el nombre del dataset y dentro de ella sube todos los archivos asociados a ese dataset.
    Si el repositorio no existe, lo crea primero.
    """

    if repo_type == 'new':
        repo_created = create_repo(owner, repo_name, token)
        if not repo_created:
            return f"Error: No se pudo crear el repositorio {repo_name}.", 400

    github_api = f"https://api.github.com/repos/{owner}/{repo_name}/contents/"

    dataset_name = dataset.name()  # Acceso correcto al atributo
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
            "branch": "main",
            "licene": license
        }

        github_api_with_file = f"{github_api}{file_data['path']}"
        response = requests.put(github_api_with_file, json=data, headers=headers)

        if response.status_code == 201:
            print(f"Archivo {file_data['path']} subido correctamente.")
        else:
            print(f"Error al subir el archivo {file_data['path']}: {response.json().get('message')}")

    return "Files uploaded successfully", 200


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
