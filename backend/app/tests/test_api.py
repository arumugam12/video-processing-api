
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_upload_video():
    # TODO: Replace with a real video file path
    try:
        with open("test_video.mp4", "rb") as f:
            response = client.post("/videos/upload", files={"file": ("test_video.mp4", f, "video/mp4")})
        assert response.status_code == 200
        assert "video_id" in response.json()
        global uploaded_video_id
        uploaded_video_id = response.json()["video_id"]
    except FileNotFoundError:
        pytest.skip("test_video.mp4 not found")

def test_list_videos():
    response = client.get("/videos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_download_original():
    # TODO: Replace with a real video_id
    video_id = "some-video-id"
    response = client.get(f"/videos/{video_id}/download")
    assert response.status_code in (200, 404)

def test_trim_job():
    # TODO: Replace with a real video_id
    video_id = "some-video-id"
    response = client.post("/trim", json={"video_id": video_id, "start_time": 0, "end_time": 1})
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_text_overlay_job():
    # TODO: Replace with a real video_id
    video_id = "some-video-id"
    response = client.post("/overlays", json={
        "video_id": video_id,
        "kind": "text",
        "text": "Test Text",
        "position_x": 10,
        "position_y": 10,
        "opacity": 1.0,
        "start_time": 0,
        "end_time": 1
    })
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_image_overlay_job():
    # TODO: Replace with a real video_id
    video_id = "some-video-id"
    response = client.post("/overlays", json={
        "video_id": video_id,
        "kind": "image",
        "image_url": "https://raw.githubusercontent.com/github/explore/main/topics/docker/docker.png",
        "position_x": 10,
        "position_y": 10,
        "opacity": 1.0,
        "start_time": 0,
        "end_time": 1
    })
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_watermark_job():
    # TODO: Replace with a real video_id
    video_id = "some-video-id"
    response = client.post("/watermark", json={
        "video_id": video_id,
        "kind": "watermark",
        "image_url": "https://raw.githubusercontent.com/github/explore/main/topics/docker/docker.png",
        "position_x": 100.0,
        "position_y": 100.0,
        "opacity": 1.0
    })
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_transcode_job():
    # TODO: Replace with a real video_id
    video_id = "some-video-id"
    response = client.post("/transcode", json={"video_id": video_id, "qualities": ["1080p", "720p", "480p"]})
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_job_status():
    # TODO: Replace with a real job_id
    job_id = "some-job-id"
    response = client.get(f"/jobs/status/{job_id}")
    assert response.status_code in (200, 404)

def test_job_result():
    # TODO: Replace with a real job_id
    job_id = "some-job-id"
    response = client.get(f"/jobs/result/{job_id}")
    assert response.status_code in (200, 400, 404)

def test_list_processed():
    # TODO: Replace with a real video_id
    video_id = "some-video-id"
    response = client.get(f"/videos/{video_id}/processed")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert isinstance(response.json(), list)

def test_download_by_quality():
    # TODO: Replace with a real video_id and quality
    video_id = "some-video-id"
    quality = "1080p"
    response = client.get(f"/videos/{video_id}/download/{quality}")
    assert response.status_code in (200, 404)
