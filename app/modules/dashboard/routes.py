from flask import render_template
from flask_login import login_required
from app.modules.dashboard.forms import DashboardForm
from app.modules.dashboard import dashboard_bp
from app.modules.dashboard.services import DashboardService
from app.modules.dataset.services import DataSetService

dashboardService = DashboardService()
datasetservice = DataSetService()

'''
READ ALL
'''


@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def index():
    form = DashboardForm()
    ndatasets = datasetservice.count_dsmetadata()
    nauthors = datasetservice.count_authors()

    # author_names = ["Juan", "Pedro", "Maria", "Ana"]
    # datasets_count = [2,3,4,7]

    author_names, dataset_counts = dashboardService.get_all_author_names_and_dataset_counts()
    print("Author Names:", author_names)
    print("Dataset Counts:", dataset_counts)

    return render_template('dashboard/index.html', ndatasets=ndatasets, nauthors=nauthors,
                           author_names=author_names, datasets_count=dataset_counts, form=form)
