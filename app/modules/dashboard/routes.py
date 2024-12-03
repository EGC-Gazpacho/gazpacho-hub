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
    statistics = dashboardService.get_detailed_statistics()
    author_names, dataset_counts = dashboardService.get_all_author_names_and_dataset_counts()
    datasets_names_views, datasets_views = dashboardService.get_views_per_dataset_lists()
    datasets_names_downloads, datasets_downloads  = dashboardService.get_downloads_per_dataset_lists()
    month , downloads = dashboardService.get_downloads_per_month()
    month_views, views = dashboardService.get_views_per_month()

    #User
    datasets_names_user, datasets_views_user = dashboardService.get_views_per_dataset_user_logued()
    datasets_names_user_downloads, datasets_download_user = dashboardService.get_downloads_per_dataset_user_logued()

    return render_template('dashboard/index.html', 
                           statistics=statistics,
                           author_names=author_names, 
                           datasets_count=dataset_counts, 
                           datasets_names_views=datasets_names_views, 
                           datasets_views=datasets_views,
                           datasets_names_downloads=datasets_names_downloads,
                           datasets_downloads=datasets_downloads,
                           months=month,
                           downloads=downloads,
                           datasets_names_user=datasets_names_user,
                           datasets_views_user=datasets_views_user,
                           months_views=month_views,
                           views_per_month=views,
                           datasets_names_user_downloads=datasets_names_user_downloads,
                           datasets_download_user=datasets_download_user
                           )
