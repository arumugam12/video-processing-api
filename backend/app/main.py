from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import videos, trim, overlays, watermark, transcode, jobs
from .routers import jobs_public


def create_app() -> FastAPI:
    description = (
        "APIs to upload videos, process them asynchronously using ffmpeg "
        "(trim, overlays, watermark), and generate multiple output qualities.\n\n"
        "Workflow: Upload → returns video_id; Create job (trim/overlay/transcode) → returns job_id; "
        "Check /status/{job_id} and download via /result/{job_id}."
    )
    app = FastAPI(title="Video Processing API", version="1.0.0", description=description)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(videos.router, prefix="/videos", tags=["videos"]) 
    app.include_router(trim.router, prefix="/trim", tags=["trim"]) 
    app.include_router(overlays.router, prefix="/overlays", tags=["overlays"]) 
    app.include_router(watermark.router, prefix="/watermark", tags=["watermark"]) 
    app.include_router(transcode.router, prefix="/transcode", tags=["transcode"]) 
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"]) 
    # Public job endpoints matching spec
    app.include_router(jobs_public.router, tags=["jobs"])

    return app


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


