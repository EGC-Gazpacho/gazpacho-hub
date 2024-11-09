import base64
from flask import json
import requests


def upload_to_github(owner, repo_name, filename, dataset, token, commit_message):
    """
    Sube un archivo a un repositorio de GitHub usando la API.
    """
    
    github_api = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{filename}"
    print(github_api)

    encoded_content = base64.b64encode(dataset).decode('utf-8')  
    
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": "main"  
    }
    
    response = requests.put(github_api, json=data, headers=headers)
    if response.status_code == 201:
        print("Archivo subido correctamente.")
    else:
        print(f"Error al subir el archivo: {response.json().get('message')}")