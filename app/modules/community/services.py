from app.modules.community.models import CommunityType, UserRole
from app.modules.community.repositories import CommunityRepository, JoinRequestRepository, UserCommunityRepository
from core.services.BaseService import BaseService


class CommunityService(BaseService):
    def __init__(self):
        super().__init__(CommunityRepository())
        self.user_community_repository = UserCommunityRepository()
        self.join_request_repository = JoinRequestRepository()

    def get_all(self):
        return self.repository.get_all()

    def is_user_community_member(self, user_id, community_id):
        return self.user_community_repository.is_user_member_of_community(user_id, community_id)

    def is_user_community_creator(self, user_id, community_id):
        association = self.user_community_repository.get_user_community(user_id, community_id)
        return association and association.role == UserRole.CREATOR

    def is_user_community_admin(self, user_id, community_id):
        association = self.user_community_repository.get_user_community(user_id, community_id)
        return association and association.role == UserRole.ADMIN

    def edit_community(self, user, community_id, form):
        if not self.is_user_community_creator(user.id, community_id):
            return False, 'Only the creator can edit this community.'

        community = self.repository.get_community_by_id(community_id)
        if community:
            self.update(community_id, **form.data)
            return True, 'Community updated successfully.'
        return False, 'Community not found.'

    def delete_community(self, user, community_id):
        if not self.is_user_community_creator(user.id, community_id):
            return False, 'Only the community creator can delete this community.'

        try:
            self.user_community_repository.delete_all_by_community_id(community_id)
            self.repository.delete(community_id)
            return True, 'Community and all associated members have been deleted.'
        except Exception as e:
            return False, f'An error occurred while deleting the community: {e}'

    def join_community(self, user, community_id):
        community = self.repository.get_community_by_id(community_id)
        if not community:
            return False, 'Community does not exist.'

        if self.user_community_repository.is_user_member_of_community(user.id, community_id):
            return False, 'You are already a member of this community.'

        try:
            self.user_community_repository.add_user_to_community(user.id, community_id)
            return True, f'You have successfully joined the community: {community.name}'
        except Exception as e:
            return False, f'An error occurred while trying to join the community. Please try again: {e}'

    def leave_community(self, user, community_id):
        community = self.repository.get_community_by_id(community_id)
        if not community:
            return False, 'Community does not exist.'

        if not self.user_community_repository.is_user_member_of_community(user.id, community_id):
            return False, 'You are not a member of this community.'

        if self.is_user_community_creator(user.id, community_id):
            return False, 'You cannot leave a community you created.'

        try:
            self.user_community_repository.delete(user.id, community_id)
            return True, f'You have successfully left the community: {community.name}'
        except Exception as e:
            return False, f'An error occurred while trying to leave the community. Please try again: {e}'

    def create_community(self, user, name, type, description=None):
        new_community = self.repository.create(name=name, type=type, description=description)
        try:
            self.user_community_repository.add_user_to_community(
                user_id=user.id,
                community_id=new_community.id,
                role=UserRole.CREATOR
            )
            return True, f'Community "{name}" created successfully.'
        except Exception as e:
            return False, f'An error occurred while creating the community: {e}'

    def request_join_community(self, user, community_id):
        community = self.repository.get_community_by_id(community_id)
        if not community:
            return False, 'Community does not exist.'

        if community.type != CommunityType.PRIVATE:
            return False, 'Requests can only be made to private communities.'

        if self.user_community_repository.is_user_member_of_community(user.id, community_id):
            return False, 'You are already a member of this community.'

        if self.join_request_repository.is_request_already_made(user.id, community_id):
            return False, 'You have already requested to join this community.'

        try:
            self.join_request_repository.create(user_id=user.id, community_id=community_id)
            return True, f'Request to join {community.name} successfully sent.'
        except Exception as e:
            return False, f'An error occurred while trying to request to join community. Please try again: {e}'

    def accept_join_request(self, user, request_id):
        join_request = self.join_request_repository.get_request_by_id(request_id)
        if not join_request:
            return False, 'Join request does not exist.'

        if (
            not self.is_user_community_admin(user.id, join_request.community_id) and
            not self.is_user_community_creator(user.id, join_request.community_id)
        ):
            return False, 'Only admins or creator can accept join requests.'

        try:
            self.user_community_repository.add_user_to_community(join_request.user_id, join_request.community_id)
            self.join_request_repository.delete(request_id)
            return True, 'Join request accepted successfully.'
        except Exception as e:
            return False, f'An error occurred while accepting request to join community. Please try again: {e}'

    def reject_join_request(self, user, request_id):
        join_request = self.join_request_repository.get_request_by_id(request_id)
        if not join_request:
            return False, 'Join request does not exist.'

        if (
            not self.is_user_community_admin(user.id, join_request.community_id) and
            not self.is_user_community_creator(user.id, join_request.community_id)
        ):
            return False, 'Only admins or creator can reject join requests.'

        try:
            self.join_request_repository.delete(request_id)
            return True, 'Join request rejected successfully.'
        except Exception as e:
            return False, f'An error occurred while rejecting request to join community. Please try again: {e}'

    def remove_member(self, user, community_id, user_id):
        community = self.repository.get_community_by_id(community_id)
        if not community:
            return False, 'Community does not exist.'

        if not self.user_community_repository.is_user_member_of_community(user_id, community_id):
            return False, 'User is not a member of this community.'

        if (
            not self.is_user_community_admin(user.id, community_id) and
            not self.is_user_community_creator(user.id, community_id)
        ):
            return False, 'Only admins or creator can remove members.'

        if self.is_user_community_creator(user_id, community_id):
            return False, 'You cannot remove the creator of the community.'

        try:
            self.user_community_repository.delete(user_id, community_id)
            return True, 'User removed successfully.'
        except Exception as e:
            return False, f'An error occurred while removing member of the community. Please try again: {e}'

    def promote_member(self, user, community_id, user_id):
        community = self.repository.get_community_by_id(community_id)
        if not community:
            return False, 'Community does not exist.'

        if not self.user_community_repository.is_user_member_of_community(user_id, community_id):
            return False, 'User is not a member of this community.'

        if (
            not self.is_user_community_admin(user.id, community_id) and
            not self.is_user_community_creator(user.id, community_id)
        ):
            return False, 'Only admins or creator can remove members.'

        if self.is_user_community_creator(user_id, community_id):
            return False, 'You cannot remove the creator of the community.'

        try:
            self.user_community_repository.update_role(user_id, community_id, UserRole.ADMIN)
            return True, 'User removed successfully.'
        except Exception as e:
            return False, f'An error occurred while removing member of the community. Please try again: {e}'

    def user_request_pending(self, user_id, community_id):
        return self.join_request_repository.is_request_already_made(user_id, community_id)
