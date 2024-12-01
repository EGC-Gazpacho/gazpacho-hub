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

    author_names, dataset_counts = dashboardService.get_all_author_names_and_dataset_counts()
    datasets_names, datasets_views = dashboardService.get_visits_per_dataset_lists()
    month , downloads = dashboardService.get_downloads_per_month()

    print(datasets_names)
    print(datasets_views)

    return render_template('dashboard/index.html', 
                           ndatasets=ndatasets, 
                           nauthors=nauthors,
                           author_names=author_names, 
                           datasets_count=dataset_counts, 
                           form=form, 
                           datasets_names=datasets_names, 
                           datasets_views=datasets_views,
                           months=month,
                           downloads=downloads
                           )
