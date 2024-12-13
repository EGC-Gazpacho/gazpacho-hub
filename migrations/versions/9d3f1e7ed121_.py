"""empty message

Revision ID: 9d3f1e7ed121
Revises: 7aa0eded7774
Create Date: 2024-12-10 15:44:56.417391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d3f1e7ed121'
down_revision = '7aa0eded7774'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('community',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('type', sa.Enum('PUBLIC', 'PRIVATE', name='communitytype'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('deposition',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dep_metadata', sa.JSON(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('doi', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('doi')
    )
    op.create_table('doi_mapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dataset_doi_old', sa.String(length=120), nullable=True),
    sa.Column('dataset_doi_new', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number_of_models', sa.String(length=120), nullable=True),
    sa.Column('number_of_features', sa.String(length=120), nullable=True),
    sa.Column('number_of_products', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fm_metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('solver', sa.Text(), nullable=True),
    sa.Column('not_solver', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('zenodo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_meta_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deposition_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('publication_type', sa.Enum('NONE', 'ANNOTATION_COLLECTION', 'BOOK', 'BOOK_SECTION', 'CONFERENCE_PAPER', 'DATA_MANAGEMENT_PLAN', 'JOURNAL_ARTICLE', 'PATENT', 'PREPRINT', 'PROJECT_DELIVERABLE', 'PROJECT_MILESTONE', 'PROPOSAL', 'REPORT', 'SOFTWARE_DOCUMENTATION', 'TAXONOMIC_TREATMENT', 'TECHNICAL_NOTE', 'THESIS', 'WORKING_PAPER', 'OTHER', name='publicationtype'), nullable=False),
    sa.Column('publication_doi', sa.String(length=120), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('dataset_doi', sa.String(length=120), nullable=True),
    sa.Column('tags', sa.String(length=120), nullable=True),
    sa.Column('ds_metrics_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ds_metrics_id'], ['ds_metrics.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fm_meta_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uvl_filename', sa.String(length=120), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('publication_type', sa.Enum('NONE', 'ANNOTATION_COLLECTION', 'BOOK', 'BOOK_SECTION', 'CONFERENCE_PAPER', 'DATA_MANAGEMENT_PLAN', 'JOURNAL_ARTICLE', 'PATENT', 'PREPRINT', 'PROJECT_DELIVERABLE', 'PROJECT_MILESTONE', 'PROPOSAL', 'REPORT', 'SOFTWARE_DOCUMENTATION', 'TAXONOMIC_TREATMENT', 'TECHNICAL_NOTE', 'THESIS', 'WORKING_PAPER', 'OTHER', name='publicationtype'), nullable=False),
    sa.Column('publication_doi', sa.String(length=120), nullable=True),
    sa.Column('tags', sa.String(length=120), nullable=True),
    sa.Column('uvl_version', sa.String(length=120), nullable=True),
    sa.Column('fm_metrics_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fm_metrics_id'], ['fm_metrics.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('join_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('community_id', sa.Integer(), nullable=False),
    sa.Column('requested_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['community_id'], ['community.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_community',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('community_id', sa.Integer(), nullable=False),
    sa.Column('joined_at', sa.DateTime(), nullable=True),
    sa.Column('role', sa.Enum('MEMBER', 'ADMIN', 'CREATOR', name='userrole'), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['community.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'community_id')
    )
    op.create_table('user_profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('orcid', sa.String(length=19), nullable=True),
    sa.Column('affiliation', sa.String(length=100), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('surname', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('affiliation', sa.String(length=120), nullable=True),
    sa.Column('orcid', sa.String(length=120), nullable=True),
    sa.Column('ds_meta_data_id', sa.Integer(), nullable=True),
    sa.Column('fm_meta_data_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id'], ),
    sa.ForeignKeyConstraint(['fm_meta_data_id'], ['fm_meta_data.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('data_set',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ds_meta_data_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ds_meta_data_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=False),
    sa.Column('rated_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_download_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.Column('download_date', sa.DateTime(), nullable=False),
    sa.Column('download_cookie', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['dataset_id'], ['data_set.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_view_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.Column('view_date', sa.DateTime(), nullable=False),
    sa.Column('view_cookie', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['dataset_id'], ['data_set.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feature_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data_set_id', sa.Integer(), nullable=False),
    sa.Column('fm_meta_data_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['data_set_id'], ['data_set.id'], ),
    sa.ForeignKeyConstraint(['fm_meta_data_id'], ['fm_meta_data.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
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
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file_view_record')
    op.drop_table('file_download_record')
    op.drop_table('file')
    op.drop_table('feature_model')
    op.drop_table('ds_view_record')
    op.drop_table('ds_download_record')
    op.drop_table('ds_rating')
    op.drop_table('data_set')
    op.drop_table('author')
    op.drop_table('user_profile')
    op.drop_table('user_community')
    op.drop_table('join_request')
    op.drop_table('fm_meta_data')
    op.drop_table('ds_meta_data')
    op.drop_table('zenodo')
    op.drop_table('user')
    op.drop_table('fm_metrics')
    op.drop_table('ds_metrics')
    op.drop_table('doi_mapping')
    op.drop_table('deposition')
    op.drop_table('community')
    # ### end Alembic commands ###
