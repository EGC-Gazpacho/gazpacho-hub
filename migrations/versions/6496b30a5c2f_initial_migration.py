"""Initial migration

Revision ID: 6496b30a5c2f
Revises: 001
Create Date: 2024-12-15 18:15:17.721899

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6496b30a5c2f'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ds_metrics', schema=None) as batch_op:
        batch_op.alter_column('number_of_features',
               existing_type=mysql.VARCHAR(length=120),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('number_of_products',
               existing_type=mysql.VARCHAR(length=120),
               type_=sa.Integer(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ds_metrics', schema=None) as batch_op:
        batch_op.alter_column('number_of_products',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=120),
               existing_nullable=True)
        batch_op.alter_column('number_of_features',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=120),
               existing_nullable=True)

    # ### end Alembic commands ###
