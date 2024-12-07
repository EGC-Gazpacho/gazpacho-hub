from flask import render_template, request, jsonify, Blueprint, send_file

from app.modules.explore import explore_bp
from app.modules.explore.forms import ExploreForm, ModelForm
from app.modules.explore.services import ExploreService, ModelService
import os
import tempfile
from zipfile import ZipFile


@explore_bp.route('/explore', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        query = request.args.get('query', '')
        form = ExploreForm()
        return render_template('explore/index.html', form=form, query=query)

    if request.method == 'POST':
        criteria = request.get_json()
        datasets = ExploreService().filter(**criteria)
        return jsonify([dataset.to_dict() for dataset in datasets])


@explore_bp.route('/explore2/models', methods=['GET'])
def explore2_models():
    query = request.args.get('query', '')
    if request.headers.get('Accept') == 'application/json':
        models = ModelService().filter(name=query)
        return jsonify([model.to_dict() for model in models])
    else:
        models = ModelService().filter(name=query)
        return render_template('explore2/index.html', models=models)

@explore_bp.route('/explore2/models/download', methods=['GET'])
def download_all_models():
    models = ModelService().get_all_models()
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'models.zip')

    with ZipFile(zip_path, 'w') as zipf:
        for model in models:
            model_path = os.path.join(temp_dir, f"{model.id}.json")
            with open(model_path, 'w') as model_file:
                model_file.write(model.to_json())
            zipf.write(model_path, os.path.basename(model_path))

    return send_file(zip_path, as_attachment=True, mimetype='application/zip')

@explore_bp.route('/explore3/models', methods=['GET'])
def explore3_models():
    query = request.args.get('query', '')
    models = ModelService().filter(name=query)
    return jsonify([model.to_dict() for model in models])
