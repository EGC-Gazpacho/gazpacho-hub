from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

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
        result = community_service.create_community(
            user=current_user,
            name=form.name.data,
            description=form.description.data
        )
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
    is_member = community_service.is_user_community_member(current_user, community_id)
    is_creator = community_service.is_user_community_creator(current_user, community_id)
    return render_template('community/show.html', community=community, is_member=is_member, is_creator=is_creator)


@community_bp.route('/community/edit/<int:community_id>', methods=['GET', 'POST'])
@login_required
def edit_community(community_id):
    if not community_service.is_user_community_creator(current_user, community_id):
        flash("Only the community creator can edit this community.", "error")
        return redirect(url_for('community.get_community', community_id=community_id))
    community = community_service.get_or_404(community_id)
    form = CommunityForm(obj=community)
    if form.validate_on_submit():
        result = community_service.edit_community(
            user=current_user,
            community_id=community_id,
            form=form
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
    if not community_service.is_user_community_creator(current_user, community_id):
        flash("Only the community creator can delete this community.", "error")
        return redirect(url_for('community.get_community', community_id=community_id))
    result = community_service.delete_community(current_user, community_id)
    if result:
        flash('Community deleted successfully!', 'success')
    else:
        flash('Error deleting community', 'error')
    return redirect(url_for('community.index'))


@community_bp.route('/community/join/<int:community_id>', methods=['POST'])
@login_required
def join_community(community_id):
    success, message = community_service.join_community(current_user, community_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('community.get_community', community_id=community_id))


@community_bp.route('/community/leave/<int:community_id>', methods=['POST'])
@login_required
def leave_community(community_id):
    success, message = community_service.leave_community(current_user, community_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('community.get_community', community_id=community_id))


@community_bp.route('/user-communities', methods=['GET'])
@login_required
def user_communities():
    user_community = community_service.get_user_communities(current_user)
    communities = [
        {
            'id': uc.community.id,
            'name': uc.community.name,
            'description': uc.community.description,
            'joined_at': uc.joined_at
        }
        for uc in user_community
    ]
    return render_template('community/user_communities.html', communities=communities)
