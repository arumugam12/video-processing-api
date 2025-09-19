import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class VideoCreateResponse(BaseModel):
    id: uuid.UUID
    filename: str
    duration_seconds: int | None = None
    size_bytes: int | None = None
    upload_time: datetime

    class Config:
        orm_mode = True

class VideoListItem(BaseModel):
    id: uuid.UUID
    filename: str
    duration_seconds: Optional[float]
    size_bytes: Optional[int]
    upload_time: datetime

    class Config:
        orm_mode = True


class TrimRequest(BaseModel):
    video_id: uuid.UUID
    start_time: float
    end_time: float


class OverlayRequest(BaseModel):
    video_id: uuid.UUID
    kind: str  # text|image|video|watermark
    text: Optional[str] = None
    fontfile: Optional[str] = None
    language: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    position_x: int = 10
    position_y: int = 10
    start_time: float = 0.0
    end_time: Optional[float] = None
    opacity: float = 1.0


class TranscodeRequest(BaseModel):
    video_id: uuid.UUID
    qualities: List[str]  # ["1080p","720p","480p"]


class JobResponse(BaseModel):
    job_id: uuid.UUID
    status: str




