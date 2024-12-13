"""empty message

Revision ID: e3ca5ad3f3b2
Revises: 4793b2b584aa
Create Date: 2024-12-10 13:51:21.107661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3ca5ad3f3b2'
down_revision = '4793b2b584aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('checksum', sa.String(length=120), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('feature_model_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['feature_model_id'], ['feature_model.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file_download_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.Column('download_date', sa.DateTime(), nullable=False),
    sa.Column('download_cookie', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file_view_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('view_date', sa.DateTime(), nullable=True),
    sa.Column('view_cookie', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ds_meta_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ds_meta_data', schema=None) as batch_op:
        batch_op.drop_column('rating')

    op.drop_table('file_view_record')
    op.drop_table('file_download_record')
    op.drop_table('file')
    # ### end Alembic commands ###
