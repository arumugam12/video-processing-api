import uuid
from pathlib import Path
from datetime import datetime
from celery import states

from .celery_app import celery_app
from .database import SessionLocal
from .models import Job, JobStatusEnum, Video, ProcessedVideo, ProcessTypeEnum, OverlayConfig
from .services.storage import allocate_processed_path, download_to_temp
from .services.ffmpeg_service import (
    run_ffprobe,
    trim_video,
    apply_text_overlay,
    apply_image_overlay,
    apply_video_overlay,
    transcode_to_quality,
)


def _set_job_status(db, job: Job, status: str, result_path: str | None = None, error: str | None = None):
    job.status = status
    job.updated_at = datetime.utcnow()
    if result_path:
        job.result_path = result_path
    if error:
        job.error = error
    db.commit()
    db.refresh(job)


@celery_app.task(name="video.extract_metadata")
def task_extract_metadata(job_id: str, video_id: str):
    db = SessionLocal()
    try:
        job = db.query(Job).get(uuid.UUID(job_id))
        if not job:
            job = Job(id=uuid.UUID(job_id), task_name="video.extract_metadata", status=JobStatusEnum.STARTED)
            db.add(job)
            db.commit()
            db.refresh(job)

        video = db.query(Video).get(uuid.UUID(video_id))
        if not video:
            _set_job_status(db, job, JobStatusEnum.FAILED, error="Video not found")
            return str(job.id)

        duration, size = run_ffprobe(Path(video.original_path))
        video.duration_seconds = duration
        video.size_bytes = size
        db.commit()

        _set_job_status(db, job, JobStatusEnum.FINISHED)
        return str(job.id)
    except Exception as e:
        db.rollback()
        try:
            job = job if 'job' in locals() else None
            if job:
                _set_job_status(db, job, JobStatusEnum.FAILED, error=str(e))
        finally:
            db.close()
        raise
    finally:
        db.close()


@celery_app.task(name="video.trim")
def task_trim(job_id: str, video_id: str, start: float, end: float):
    db = SessionLocal()
    job = db.query(Job).get(uuid.UUID(job_id))
    if not job:
        job = Job(id=uuid.UUID(job_id), task_name="video.trim", status=JobStatusEnum.STARTED)
        db.add(job)
        db.commit()
        db.refresh(job)
    try:
        video = db.query(Video).get(uuid.UUID(video_id))
        if not video:
            _set_job_status(db, job, JobStatusEnum.FAILED, error="Video not found")
            return str(job.id)

        output = allocate_processed_path(".mp4")
        trim_video(Path(video.original_path), start, end, output)

        processed = ProcessedVideo(
            original_video_id=video.id,
            process_type=ProcessTypeEnum.TRIM,
            start_time=start,
            end_time=end,
            output_path=str(output),
        )
        db.add(processed)
        db.commit()

        _set_job_status(db, job, JobStatusEnum.FINISHED, result_path=str(output))
        return str(job.id)
    except Exception as e:
        db.rollback()
        _set_job_status(db, job, JobStatusEnum.FAILED, error=str(e))
        raise
    finally:
        db.close()


@celery_app.task(name="video.overlay")
def task_overlay(job_id: str, video_id: str, kind: str, config: dict):
    db = SessionLocal()
    job = db.query(Job).get(uuid.UUID(job_id))
    if not job:
        job = Job(id=uuid.UUID(job_id), task_name="video.overlay", status=JobStatusEnum.STARTED)
        db.add(job)
        db.commit()
        db.refresh(job)
    try:
        video = db.query(Video).get(uuid.UUID(video_id))
        if not video:
            _set_job_status(db, job, JobStatusEnum.FAILED, error="Video not found")
            return str(job.id)

        output = allocate_processed_path(".mp4")
        base = Path(video.original_path)
        x = int(config.get("position_x", 10))
        y = int(config.get("position_y", 10))
        start = float(config.get("start_time", 0))
        end = config.get("end_time")
        end_f = float(end) if end is not None else None
        opacity = float(config.get("opacity", 1.0))

        if kind == "text":
            text = config.get("text", "")
            fontfile = config.get("fontfile")
            apply_text_overlay(base, output, text, x, y, start, end_f, fontfile, opacity)
        elif kind in ("image", "watermark"):
            image_url = config.get("image_url")
            if not image_url:
                raise ValueError("image_url required for image/watermark overlay")
            temp_img = download_to_temp(image_url, ".png")
            apply_image_overlay(base, output, temp_img, x, y, start, end_f, opacity)
        elif kind == "video":
            video_url = config.get("video_url")
            if not video_url:
                raise ValueError("video_url required for video overlay")
            temp_vid = download_to_temp(video_url, ".mp4")
            apply_video_overlay(base, output, temp_vid, x, y, start, end_f)
        else:
            raise ValueError("Unsupported overlay kind")

        processed = ProcessedVideo(
            original_video_id=video.id,
            process_type=ProcessTypeEnum.OVERLAY if kind != "watermark" else ProcessTypeEnum.WATERMARK,
            output_path=str(output),
        )
        db.add(processed)
        db.commit()

        overlay_cfg = OverlayConfig(
            processed_video_id=processed.id,
            kind=kind,
            text=config.get("text"),
            fontfile=config.get("fontfile"),
            language=config.get("language"),
            image_path=None,
            video_path=None,
            position_x=x,
            position_y=y,
            start_time=start,
            end_time=end_f,
            opacity=opacity,
        )
        db.add(overlay_cfg)
        db.commit()
        _set_job_status(db, job, JobStatusEnum.FINISHED, result_path=str(output))
        return str(job.id)
    except Exception as e:
        db.rollback()
        _set_job_status(db, job, JobStatusEnum.FAILED, error=str(e))
        raise
    finally:
        db.close()


QUALITY_TO_HEIGHT = {"1080p": 1080, "720p": 720, "480p": 480}


@celery_app.task(name="video.transcode")
def task_transcode(job_id: str, video_id: str, qualities: list[str]):
    db = SessionLocal()
    job = db.query(Job).get(uuid.UUID(job_id))
    if not job:
        job = Job(id=uuid.UUID(job_id), task_name="video.transcode", status=JobStatusEnum.STARTED)
        db.add(job)
        db.commit()
        db.refresh(job)
    try:
        video = db.query(Video).get(uuid.UUID(video_id))
        if not video:
            _set_job_status(db, job, JobStatusEnum.FAILED, error="Video not found")
            return str(job.id)

        last_output: str | None = None
        for q in qualities:
            height = QUALITY_TO_HEIGHT.get(q)
            if not height:
                continue
            output = allocate_processed_path(f"_{q}.mp4")
            transcode_to_quality(Path(video.original_path), output, height)
            processed = ProcessedVideo(
                original_video_id=video.id,
                process_type=ProcessTypeEnum.TRANSCODE,
                quality=q,
                output_path=str(output),
            )
            db.add(processed)
            db.commit()
            last_output = str(output)

        _set_job_status(db, job, JobStatusEnum.FINISHED, result_path=last_output)
        return str(job.id)
    except Exception as e:
        db.rollback()
        _set_job_status(db, job, JobStatusEnum.FAILED, error=str(e))
        raise
    finally:
        db.close()


