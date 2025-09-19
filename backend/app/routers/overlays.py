import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Job, JobStatusEnum
from ..schemas import OverlayRequest, JobResponse
from ..tasks import task_overlay


router = APIRouter()


@router.post("", response_model=JobResponse)
def create_overlay(req: OverlayRequest, db: Session = Depends(get_db)):
    job = Job(task_name="video.overlay", status=JobStatusEnum.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    task_overlay.delay(str(job.id), str(req.video_id), req.kind, req.dict())
    return JobResponse(job_id=job.id, status=job.status)


