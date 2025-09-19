from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Job, JobStatusEnum
from ..schemas import TranscodeRequest, JobResponse
from ..tasks import task_transcode


router = APIRouter()


@router.post("", response_model=JobResponse)
def create_transcode(req: TranscodeRequest, db: Session = Depends(get_db)):
    job = Job(task_name="video.transcode", status=JobStatusEnum.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    task_transcode.delay(str(job.id), str(req.video_id), req.qualities)
    return JobResponse(job_id=job.id, status=job.status)


