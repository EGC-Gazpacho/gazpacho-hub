from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app.modules.community.forms import CommunityForm
from app.modules.community import community_bp
from app.modules.community.services import CommunityService


community_service = CommunityService()


@community_bp.route('/community', methods=['GET'])
@login_required
def index():
    form = CommunityForm()
    communities = community_service.get_all()
    return render_template('community/index.html', communities=communities, form=form)


@community_bp.route('/community/create', methods=['GET', 'POST'])
@login_required
def create_community():
    form = CommunityForm()
    if form.validate_on_submit():
        result = community_service.create(name=form.name.data, description=form.description.data)
        return community_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='community.index',
            success_msg='Community created successfully!',
            error_template='community/create.html',
            form=form
        )
    return render_template('community/create.html', form=form)


@community_bp.route('/community/<int:community_id>', methods=['GET'])
@login_required
def get_community(community_id):
    community = community_service.get_or_404(community_id)

    return render_template('community/show.html', community=community)


@community_bp.route('/community/edit/<int:community_id>', methods=['GET', 'POST'])
@login_required
def edit_community(community_id):
    community = community_service.get_or_404(community_id)

    form = CommunityForm(obj=community)
    if form.validate_on_submit():
        result = community_service.update(
            community_id,
            name=form.name.data,
            description=form.description.data
        )
        return community_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='community.index',
            success_msg='Community updated successfully!',
            error_template='community/edit.html',
            form=form
        )
    return render_template('community/edit.html', form=form, community=community)


@community_bp.route('/community/delete/<int:community_id>', methods=['POST'])
@login_required
def delete_community(community_id):
    result = community_service.delete(community_id)
    if result:
        flash('Community deleted successfully!', 'success')
    else:
        flash('Error deleting community', 'error')

    return redirect(url_for('community.index'))
