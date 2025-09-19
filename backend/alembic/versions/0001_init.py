"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2025-09-18

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

    op.create_table(
        'videos',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_path', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('upload_time', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'processed_videos',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('original_video_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('process_type', sa.String(), nullable=False),
        sa.Column('quality', sa.String(), nullable=True),
        sa.Column('start_time', sa.Float(), nullable=True),
        sa.Column('end_time', sa.Float(), nullable=True),
        sa.Column('output_path', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'overlay_configs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('processed_video_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('processed_videos.id'), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('fontfile', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('image_path', sa.String(), nullable=True),
        sa.Column('video_path', sa.String(), nullable=True),
        sa.Column('position_x', sa.Integer(), nullable=True),
        sa.Column('position_y', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.Float(), nullable=True),
        sa.Column('end_time', sa.Float(), nullable=True),
        sa.Column('opacity', sa.Float(), nullable=True),
    )

    op.create_table(
        'jobs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('result_path', sa.String(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('payload', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('related_video_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id'), nullable=True),
        sa.Column('related_processed_video_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('processed_videos.id'), nullable=True),
    )


def downgrade():
    op.drop_table('jobs')
    op.drop_table('overlay_configs')
    op.drop_table('processed_videos')
    op.drop_table('videos')




