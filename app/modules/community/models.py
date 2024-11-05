from datetime import datetime, timezone
from app import db


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    member_associations = db.relationship('UserCommunity', back_populates='community')
    members = db.relationship('User', secondary='user_community', viewonly=True)

    def __repr__(self):
        return f'Communities<{self.id}>, Name={self.name}'


class UserCommunity(db.Model):
    __tablename__ = 'user_community'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), primary_key=True)

    joined_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    role = db.Column(db.String(50))

    user = db.relationship('User', back_populates='community_associations')
    community = db.relationship('Community', back_populates='member_associations')
