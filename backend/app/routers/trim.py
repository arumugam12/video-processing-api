import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Job, JobStatusEnum
from ..schemas import TrimRequest, JobResponse
from ..tasks import task_trim


router = APIRouter()


@router.post("", response_model=JobResponse)
def create_trim(req: TrimRequest, db: Session = Depends(get_db)):
    job = Job(task_name="video.trim", status=JobStatusEnum.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    task_trim.delay(str(job.id), str(req.video_id), req.start_time, req.end_time)
    return JobResponse(job_id=job.id, status=job.status)


