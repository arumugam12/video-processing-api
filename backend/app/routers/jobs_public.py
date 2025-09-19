import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Job


router = APIRouter()


@router.get("/status/{job_id}")
def public_status(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": str(job.id), "status": job.status, "error": job.error}


@router.get("/result/{job_id}")
def public_result(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "finished" or not job.result_path:
        raise HTTPException(status_code=400, detail="Result not ready")
    return FileResponse(job.result_path, filename=f"result_{job.id}.mp4")




