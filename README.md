Backend Engineer Assignment – Video Processing APIs (FastAPI + Celery + Postgres + Redis)

This repository contains a FastAPI backend implementing all the levels in the assignment: upload + metadata, trimming, overlays/watermark, async job queue with status/result, and multiple output qualities. It includes Postgres schema + Alembic migration, ffmpeg integration, Docker setup, and OpenAPI docs.

Stack
- FastAPI (HTTP APIs)
- Celery + Redis (async jobs)
- Postgres + SQLAlchemy (storage)
- ffmpeg/ffprobe (media processing)

Services
- api: FastAPI app at :8000
- worker: Celery worker
- db: Postgres
- redis: Redis broker/backend

Run with Docker
1) Install Docker Desktop and start it.
2) From repo root:
   docker compose up --build
3) Open docs at http://localhost:8000/docs

Local Dev (without Docker)
1) Python 3.11 with ffmpeg installed.
2) Create and activate venv, then:
   pip install -r requirements.txt
3) Set env (see .env.example) and run Postgres + Redis locally.
4) Start API:
   uvicorn app.main:app --reload
5) Start worker in another terminal:
   celery -A app.celery_app.celery_app worker --loglevel=INFO

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

Demo script
1) Upload: POST /videos/upload with a small MP4.
2) List: GET /videos and show metadata populated after a moment.
3) Trim: POST /trim, copy job_id → poll GET /status/{job_id} → GET /result/{job_id} to download.
4) Text overlay (e.g., Arumugam_): POST /overlays with text and fontfile → status → result.
5) Watermark: POST /watermark with image_url → status → result.
6) Multiple qualities: POST /transcode with [1080p,720p,480p] → status → result.
7) Show files under ./data/processed.

Storage
All media stored under /app/data (mounted to ./data via docker-compose).

Migrations
Alembic is included; initial metadata is auto-created on startup for convenience. For production, generate and apply migrations.

Local development (optional)
- See backend/README.md for running without Docker.