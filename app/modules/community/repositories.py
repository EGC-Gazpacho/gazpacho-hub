from app.modules.community.models import Community, JoinRequest, UserCommunity, UserRole
from core.repositories.BaseRepository import BaseRepository
from app import db


class CommunityRepository(BaseRepository):
    def __init__(self):
        super().__init__(Community)

    def get_all(self):
        return self.model.query.all()

    def get_community_by_id(self, community_id):
        return self.model.query.get(community_id)


class UserCommunityRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserCommunity)

    def is_user_member_of_community(self, user_id, community_id):
        return self.model.query.filter_by(user_id=user_id, community_id=community_id).first() is not None

    def get_user_community(self, user_id, community_id):
        return self.model.query.filter_by(user_id=user_id, community_id=community_id).first()

    def add_user_to_community(self, user_id, community_id, role=UserRole.MEMBER):
        return self.create(user_id=user_id, community_id=community_id, role=role)

    def delete(self, user_id, community_id):
        association = self.model.query.filter_by(user_id=user_id, community_id=community_id).first()
        if association:
            db.session.delete(association)
            db.session.commit()

    def delete_all_by_community_id(self, community_id):
        self.model.query.filter_by(community_id=community_id).delete()

    def update_role(self, user_id, community_id, role):
        association = self.model.query.filter_by(user_id=user_id, community_id=community_id).first()
        if association:
            association.role = role
            db.session.commit()


class JoinRequestRepository(BaseRepository):
    def __init__(self):
        super().__init__(JoinRequest)

    def get_request_by_id(self, request_id):
        return self.model.query.filter_by(id=request_id).first()

    def is_request_already_made(self, user_id, community_id):
        return self.model.query.filter_by(user_id=user_id, community_id=community_id).first() is not None
