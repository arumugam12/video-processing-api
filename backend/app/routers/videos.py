import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Video, Job, JobStatusEnum, ProcessedVideo
from ..schemas import VideoCreateResponse, VideoListItem
from ..services.storage import save_upload_file
from ..tasks import task_extract_metadata


router = APIRouter()


@router.post("/upload", response_model=VideoCreateResponse)
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    tmp_path = Path(f"/tmp/{uuid.uuid4()}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    stored_path = save_upload_file(tmp_path, file.filename)
    video = Video(filename= file.filename, original_path=str(stored_path), mime_type=file.content_type)
    db.add(video)
    db.commit()
    db.refresh(video)

    job = Job(task_name="video.extract_metadata", status=JobStatusEnum.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    task_extract_metadata.delay(str(job.id), str(video.id))
    return VideoCreateResponse(
        id=video.id,
        filename=video.filename,
        duration_seconds=video.duration_seconds,
        size_bytes=video.size_bytes,
        upload_time=video.upload_time,
    )


@router.get("", response_model=list[VideoListItem])
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(Video.upload_time.desc()).all()
    return [
        VideoListItem(
            id=v.id,
            filename=v.filename,
            duration_seconds=v.duration_seconds,
            size_bytes=v.size_bytes,
            upload_time=v.upload_time,
        )
        for v in videos
    ]


@router.get("/{video_id}/download")
def download_original(video_id: uuid.UUID, db: Session = Depends(get_db)):
    video = db.query(Video).get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video.original_path, media_type=video.mime_type or "application/octet-stream", filename=video.filename)


@router.get("/{video_id}/processed")
def list_processed(video_id: uuid.UUID, db: Session = Depends(get_db)):
    video = db.query(Video).get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    items = (
        db.query(ProcessedVideo)
        .filter(ProcessedVideo.original_video_id == video_id)
        .order_by(ProcessedVideo.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(p.id),
            "process_type": p.process_type,
            "quality": p.quality,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "created_at": p.created_at,
            "output_path": p.output_path,
        }
        for p in items
    ]


@router.get("/{video_id}/download/{quality}")
def download_by_quality(video_id: uuid.UUID, quality: str, db: Session = Depends(get_db)):
    video = db.query(Video).get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    pv = (
        db.query(ProcessedVideo)
        .filter(
            ProcessedVideo.original_video_id == video_id,
            ProcessedVideo.process_type == "transcode",
            ProcessedVideo.quality == quality,
        )
        .order_by(ProcessedVideo.created_at.desc())
        .first()
    )
    if not pv:
        raise HTTPException(status_code=404, detail="Processed quality not found")
    return FileResponse(pv.output_path, filename=f"{quality}_{video.filename}")


