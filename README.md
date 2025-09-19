Backend Engineer Assignment – Video Processing APIs

This repository contains a FastAPI backend implementing all the levels in the assignment: upload + metadata, trimming, overlays/watermark, async job queue with status/result, and multiple output qualities. It includes Postgres schema + Alembic migration, ffmpeg integration, Docker setup, and OpenAPI docs.

Run with Docker
1) Install Docker Desktop and start it.
2) From repo root:
   docker compose up --build
3) Open docs at http://localhost:8000/docs

Demo script (what to record)
1) Upload: POST /videos/upload with a small MP4.
2) List: GET /videos and show metadata populated after a moment.
3) Trim: POST /trim, copy job_id → poll GET /status/{job_id} → GET /result/{job_id} to download.
4) Text overlay (e.g., Arumugam_): POST /overlays with text and fontfile → status → result.
5) Watermark: POST /watermark with image_url → status → result.
6) Multiple qualities: POST /transcode with [1080p,720p,480p] → status → result.
7) Show files under ./data/processed.

Local development (optional)
- See backend/README.md for running without Docker.

Submission
- Push to GitHub and email the repo link and demo video to arush@buttercut.ai with subject: "Backend Engineer {Your Name}".




