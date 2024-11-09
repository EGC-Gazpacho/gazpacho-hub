import os
from flask_login import login_required, current_user
from flask import app, jsonify, redirect, render_template, request
import logging
from app.modules.github import github_bp
from app.modules.github.forms import DataSetFormGithub
from app.modules.dataset.services import DataSetService
from app.modules.github.services import upload_to_github

logger = logging.getLogger(__name__)

dataset_service = DataSetService()


@github_bp.route("/github/upload", methods=["GET", "POST"])
@login_required
def create_dataset_github():
    form = DataSetFormGithub()  
    if request.method == "POST":
        try:

            if 'file' not in request.files:
                raise ValueError("No file part in the request")

            file = request.files['file']
            if file.filename == '':
                raise ValueError("No selected file")

            if not file.filename.endswith('.uvl'):
                raise ValueError("Only .uvl files are allowed")

            dataset = file.read()

            commit_message = request.form['commit_message']
            owner = request.form['owner']
            repo_name = request.form['repo_name']
            repo_type = request.form['repo_type']
            access_token = request.form['access_token']
            license = request.form['license']            
            
            
            
            upload_to_github(owner, repo_name, file.filename, dataset, access_token, commit_message)

            return jsonify({"message": "Dataset created and uploaded to GitHub successfully"}), 200
        
        except Exception as exc:
            logger.exception(f"Exception while creating dataset or uploading to GitHub: {exc}")
            return jsonify({"error": str(exc)}), 400

    return render_template("upload_dataset_github.html", form=form)

@github_bp.route('/github/dropzone', methods=['POST'])
def dropzone():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        return jsonify({"error": "Invalid file format"}), 400
