from pathlib import Path
import shutil
import uuid
import requests

from ..config import settings


def ensure_storage() -> None:
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    (settings.storage_root / "uploads").mkdir(parents=True, exist_ok=True)
    (settings.storage_root / "processed").mkdir(parents=True, exist_ok=True)
    (settings.storage_root / "temp").mkdir(parents=True, exist_ok=True)


def save_upload_file(src_path: Path, original_filename: str) -> Path:
    ensure_storage()
    unique_name = f"{uuid.uuid4()}_{original_filename}"
    dest = settings.storage_root / "uploads" / unique_name
    shutil.copy2(src_path, dest)
    return dest


def download_to_temp(url: str, suffix: str) -> Path:
    ensure_storage()
    temp_path = settings.storage_root / "temp" / f"{uuid.uuid4()}{suffix}"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return temp_path


def allocate_processed_path(suffix: str) -> Path:
    ensure_storage()
    return settings.storage_root / "processed" / f"{uuid.uuid4()}{suffix}"




