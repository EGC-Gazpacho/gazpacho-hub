from flask import render_template, request, jsonify

from app.modules.explore import explore_bp
from app.modules.explore.forms import ExploreForm, ModelForm
from app.modules.explore.services import ExploreService, ModelService


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
    form = ModelForm()
    models = ModelService().get_all_models()  # Obtener todos los modelos
    if request.is_json:
        return jsonify([model.to_dict() for model in models])
    return render_template('explore2/index.html', form=form, query=query, models=models)
