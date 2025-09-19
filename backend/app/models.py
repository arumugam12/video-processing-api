import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Float,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    processed = relationship("ProcessedVideo", back_populates="original_video")


class ProcessTypeEnum(str):  # marker for values
    # mapped to sqlalchemy Enum via .name
    TRIM = "trim"
    OVERLAY = "overlay"
    WATERMARK = "watermark"
    TRANSCODE = "transcode"


class ProcessedVideo(Base):
    __tablename__ = "processed_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    process_type = Column(String, nullable=False)  # values of ProcessTypeEnum
    quality = Column(String, nullable=True)  # e.g., 1080p/720p/480p
    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)
    output_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    overlays = relationship("OverlayConfig", back_populates="processed_video")
    original_video = relationship("Video", back_populates="processed")


class OverlayKindEnum(str):  # marker for values
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    WATERMARK = "watermark"


class OverlayConfig(Base):
    __tablename__ = "overlay_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    processed_video_id = Column(UUID(as_uuid=True), ForeignKey("processed_videos.id"), nullable=False)
    kind = Column(String, nullable=False)

    # text overlay
    text = Column(Text, nullable=True)
    fontfile = Column(String, nullable=True)
    language = Column(String, nullable=True)

    # image/video overlay paths
    image_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)

    # placement and timing
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)
    opacity = Column(Float, nullable=True)

    processed_video = relationship("ProcessedVideo", back_populates="overlays")


class JobStatusEnum(str):  # marker for values
    QUEUED = "queued"
    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_name = Column(String, nullable=False)
    status = Column(String, default=JobStatusEnum.QUEUED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    result_path = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    payload = Column(JSONB, nullable=True)
    related_video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=True)
    related_processed_video_id = Column(UUID(as_uuid=True), ForeignKey("processed_videos.id"), nullable=True)


