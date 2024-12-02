from flask import render_template
from flask_login import login_required
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
    #General
    author_names, dataset_counts = dashboardService.get_all_author_names_and_dataset_counts()
    datasets_names, datasets_views = dashboardService.get_views_per_dataset_lists()
    month , downloads = dashboardService.get_downloads_per_month()

    #User
    datasets_names_user, datasets_views_user = dashboardService.get_views_per_dataset_user_logued()

    return render_template('dashboard/index.html', 
                           author_names=author_names, 
                           datasets_count=dataset_counts, 
                           datasets_names=datasets_names, 
                           datasets_views=datasets_views,
                           months=month,
                           downloads=downloads,
                           datasets_names_user=datasets_names_user,
                           datasets_views_user=datasets_views_user,
                           )
