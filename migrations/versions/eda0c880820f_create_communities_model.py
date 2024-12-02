"""create_communities_model

Revision ID: eda0c880820f
Revises: 001
Create Date: 2024-10-25 18:09:57.908238

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'eda0c880820f'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('community',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_community',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('community_id', sa.Integer(), nullable=False),
    sa.Column('joined_at', sa.DateTime(), nullable=True),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['community_id'], ['community.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'community_id')
    )
    op.drop_table('webhook')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('webhook',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('user_community')
    op.drop_table('community')
    # ### end Alembic commands ###