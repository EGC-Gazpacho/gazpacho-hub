import base64
import requests


def upload_to_github(owner, repo_name, filename, dataset, token, commit_message, license, repo_type):
    """
    Sube un archivo a un repositorio de GitHub usando la API.
    Si el repositorio no existe, lo crea primero.
    """

    # Primero, verificamos si el repositorio existe
    # Si no existe, lo creamos
    if repo_type == 'new':
        repo_created = create_repo(owner, repo_name, token)
        if not repo_created:
            return f"Error: No se pudo crear el repositorio {repo_name}.", 400

    github_api = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{filename}"

    encoded_content = base64.b64encode(dataset).decode('utf-8')

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": "main",
        "license": license
    }

    response = requests.put(github_api, json=data, headers=headers)
    if response.status_code == 201:
        print("Archivo subido correctamente.")
        return "File uploaded successfully", 200
    else:
        print(f"Error al subir el archivo: {response.json().get('message')}")
        return f"Error: {response.status_code} - {response.text}", response.status_code


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
        "private": False,  # Cambia a True si quieres que el repositorio sea privado
        "description": "Repositorio creado a través de la API"
    }

    response = requests.post(github_api, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Repositorio '{repo_name}' creado correctamente.")
        return True
    else:
        print(f"Error al crear el repositorio: {response.json().get('message')}")
        return False
