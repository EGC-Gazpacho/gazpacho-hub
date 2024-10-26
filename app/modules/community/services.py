from app.modules.community.repositories import CommunityRepository, UserCommunityRepository
from core.services.BaseService import BaseService


class CommunityService(BaseService):
    def __init__(self):
        super().__init__(CommunityRepository())
        self.user_community_repository = UserCommunityRepository()

    def get_all(self):
        return self.repository.get_all()

    def is_user_community_member(self, user, community_id):
        return self.user_community_repository.is_user_member_of_community(user.id, community_id)

    def is_user_community_creator(self, user, community_id):
        association = self.user_community_repository.get_user_community(user.id, community_id)
        return association and association.role == "Creator"

    def edit_community(self, user, community_id, form):
        if not self.is_user_community_creator(user, community_id):
            return False, 'Only the creator can edit this community.'

        community = self.repository.get_community_by_id(community_id)
        if community:
            self.update(community_id, **form.data)
            return True, 'Community updated successfully.'
        return False, 'Community not found.'
    
    def delete_community(self, user, community_id):
        if not self.is_user_community_creator(user, community_id):
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

        try:
            self.user_community_repository.delete(user.id, community_id)
            return True, f'You have successfully left the community: {community.name}'
        except Exception as e:
            return False, f'An error occurred while trying to leave the community. Please try again: {e}'

    def create_community(self, user, name, description=None):
        new_community = self.repository.create(name=name, description=description)
        try:
            self.user_community_repository.add_user_to_community(
                user_id=user.id,
                community_id=new_community.id,
                role="Creator"
            )
            return True, f'Community "{name}" created successfully.'
        except Exception as e:
            return False, f'An error occurred while creating the community: {e}'
