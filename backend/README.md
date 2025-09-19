Video Processing API (FastAPI + Celery + Postgres + Redis)

Overview
This backend provides APIs to upload videos, process them with ffmpeg (trimming, overlays, watermark), generate multiple qualities, and retrieve results via async jobs.

Stack
- FastAPI (HTTP APIs)
- Celery + Redis (async jobs)
- Postgres + SQLAlchemy (storage)
- ffmpeg/ffprobe (media processing)

Quick Start (Docker)
1) Prereqs: Docker Desktop installed and running.
2) From repo root:
   docker compose up --build
3) Open docs:
   http://localhost:8000/docs

Services
- api: FastAPI app at :8000
- worker: Celery worker
- db: Postgres
- redis: Redis broker/backend

Key Endpoints
- POST /videos/upload: upload video file
- GET /videos: list uploaded
- GET /videos/{id}/download: download original
- POST /trim: { video_id, start_time, end_time } → returns job_id
- POST /overlays: text/image/video overlay → returns job_id
- POST /watermark: watermark overlay → returns job_id
- POST /transcode: { video_id, qualities: [1080p,720p,480p] } → job_id
- GET /jobs/status/{job_id}: job status
- GET /jobs/result/{job_id}: download result

Demo Flow
1) Upload a video via /videos/upload (use a small mp4).
2) Watch /videos to see metadata (duration/size auto-filled by background task).
3) Create a trim: POST /trim, note job_id.
4) Poll /jobs/status/{job_id} until finished, then GET /jobs/result/{job_id}.
5) Create text overlay (e.g., {kind:"text", text:"arumugam", fontfile:"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"}).
6) Create watermark with image_url pointing to an accessible PNG.
7) Transcode to [1080p,720p,480p].

Local Dev (without Docker)
1) Python 3.11 with ffmpeg installed.
2) Create and activate venv, then:
   pip install -r requirements.txt
3) Set env (see .env.example) and run Postgres + Redis locally.
4) Start API:
   uvicorn app.main:app --reload
5) Start worker in another terminal:
   celery -A app.celery_app.celery_app worker --loglevel=INFO

Storage
All media stored under /app/data (mounted to ./data via docker-compose).

Migrations
Alembic is included; initial metadata is auto-created on startup for convenience. For production, generate and apply migrations.




