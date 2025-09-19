from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Job, JobStatusEnum
from ..schemas import OverlayRequest, JobResponse
from ..tasks import task_overlay


router = APIRouter()


@router.post("", response_model=JobResponse)
def create_watermark(req: OverlayRequest, db: Session = Depends(get_db)):
    payload = req.dict()
    payload["kind"] = "watermark"
    job = Job(task_name="video.overlay", status=JobStatusEnum.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    task_overlay.delay(str(job.id), str(req.video_id), "watermark", payload)
    return JobResponse(job_id=job.id, status=job.status)


