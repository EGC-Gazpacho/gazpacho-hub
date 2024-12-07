from flask_login import login_required
from flask import jsonify, render_template, request
import logging

import requests
from app.modules.github import github_bp
from app.modules.github.forms import DataSetFormGithub
from app.modules.dataset.services import DataSetService
from app.modules.github.services import GitHubService  # Asegúrate de importar el servicio

logger = logging.getLogger(__name__)

dataset_service = DataSetService()


@github_bp.route("/github/upload/<int:dataset_id>", methods=["GET", "POST"])
@login_required
def create_dataset_github(dataset_id):
    form = DataSetFormGithub()
    dataset = dataset_service.get_or_404(dataset_id)

    if request.method == "POST":
        commit_message = request.form['commit_message']
        owner = request.form['owner']
        repo_name = request.form['repo_name']
        branch = request.form['branch']
        repo_type = request.form['repo_type']
        access_token = request.form['access_token']
        license = request.form['license']

        if repo_type != 'new':
            try:
                # Usar GitHubService para verificar si el repositorio existe
                repo_exists = GitHubService.check_repository_exists(owner, repo_name, access_token)
                if not repo_exists:
                    return jsonify({
                        "error": "Repository not found. Verify the repository owner and name.",
                        "code": 404
                    }), 404

            except requests.exceptions.HTTPError as e:
                return jsonify({"error": f"GitHub API error: {str(e)}", "code": 401}), 401
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Connection error: {str(e)}", "code": 500}), 500

            try:
                # Usar GitHubService para verificar si la rama existe
                branch_exists = GitHubService.check_branch_exists(owner, repo_name, branch, access_token)
                if not branch_exists:
                    return jsonify({
                        "error": f"Branch {branch} not found. Verify the branch name.",
                        "code": 404
                    }), 404
            except requests.exceptions.HTTPError as e:
                return jsonify({"error": f"GitHub API error: {str(e)}", "code": 401}), 401
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Connection error: {str(e)}", "code": 500}), 500

        try:
            # Usar GitHubService para cargar el dataset al repositorio de GitHub
            response_message, status_code = GitHubService.upload_dataset_to_github(
                owner, repo_name, branch, dataset, access_token, commit_message, license, repo_type
            )
            return jsonify({"message": response_message}), status_code

        except requests.exceptions.HTTPError as e:
            error_message = str(e)
            print(f"HTTPError: {error_message}")

            if "401" in error_message or "Unauthorized" in error_message:
                return jsonify({
                    "error": "Bad credentials. Verify your access token.",
                    "code": 401
                }), 401

            elif "422" in error_message or "Unprocessable Entity" in error_message:
                return jsonify({
                    "error": "A dataset with the same name already exists in the repository.",
                    "code": 422
                }), 422

            else:
                return jsonify({
                    "error": f"An unexpected error occurred: {error_message}",
                    "code": 500
                }), 500

        except requests.exceptions.RequestException as e:
            return jsonify({
                "error": f"Failed to connect to GitHub API: {str(e)}",
                "code": 500
            }), 500
        

    return render_template("upload_dataset_github.html", form=form, dataset=dataset)
