from app.modules.community.models import Community, CommunityType, UserCommunity, UserRole
from core.seeders.BaseSeeder import BaseSeeder
from app.modules.auth.models import User


class CommunitySeeder(BaseSeeder):

    priority = 10  # Lower priority

    def run(self):
        # Retrieve users
        user1 = User.query.filter_by(email='user1@example.com').first()
        user2 = User.query.filter_by(email='user2@example.com').first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        community_data = [
            Community(
                name='First Community',
                description='This is the first community',
                type=CommunityType.PUBLIC
            )
        ]

        seeded_community = self.seed(community_data)

        user_community_data = [
            UserCommunity(
                user_id=user1.id,
                community_id=seeded_community[0].id,
                role=UserRole.CREATOR
            )
        ]

        self.seed(user_community_data)
