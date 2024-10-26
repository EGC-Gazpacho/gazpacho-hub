from app.modules.community.models import Community, UserCommunity
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

    def add_user_to_community(self, user_id, community_id, role="Member"):
        return self.create(user_id=user_id, community_id=community_id, role=role)

    def delete(self, user_id, community_id):
        association = self.model.query.filter_by(user_id=user_id, community_id=community_id).first()
        if association:
            db.session.delete(association)
            db.session.commit()

    def delete_all_by_community_id(self, community_id):
        self.model.query.filter_by(community_id=community_id).delete()
