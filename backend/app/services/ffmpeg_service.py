import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

from ..config import settings


def run_ffprobe(file_path: Path) -> Tuple[Optional[float], Optional[int]]:
    try:
        # Duration
        dur_cmd = [
            settings.ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]
        out = subprocess.check_output(dur_cmd, stderr=subprocess.STDOUT).decode().strip().split("\n")
        duration = float(out[0]) if out and out[0] else None
        size = int(float(out[1])) if len(out) > 1 and out[1] else None
        return duration, size
    except Exception:
        return None, None


def trim_video(input_path: Path, start: float, end: float, output_path: Path) -> None:
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-ss",
        str(start),
        "-to",
        str(end),
        "-i",
        str(input_path),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.check_call(cmd)


def build_drawtext_filter(text: str, x: int, y: int, start: float, end: Optional[float], fontfile: Optional[str], opacity: float) -> str:
    enable = f"between(t,{start},{end})" if end is not None else f"gte(t,{start})"
    alpha = max(0.0, min(opacity, 1.0))
    font = f":fontfile='{fontfile}'" if fontfile else ""
    return f"drawtext=text='{text}':x={x}:y={y}{font}:fontcolor=red@{alpha}:fontsize=48:borderw=4:bordercolor=black:shadowx=3:shadowy=3:enable='{enable}'"


def overlay_image_filter(image_path: Path, x: int, y: int, start: float, end: Optional[float], opacity: float) -> List[str]:
    enable = f"between(t,{start},{end})" if end is not None else f"gte(t,{start})"
    alpha = max(0.0, min(opacity, 1.0))

    return [
        "-i", str(image_path),
        "-filter_complex",
        f"[1:v]format=rgba,colorchannelmixer=aa={alpha}[logo];"
        f"[0:v][logo]overlay={x}:{y}:enable='{enable}'[outv]",
        "-map", "[outv]",
        "-map", "0:a?",
        "-pix_fmt", "yuv420p"
    ]


def overlay_video_filter(overlay_path: Path, x: int, y: int, start: float, end: Optional[float]) -> List[str]:
    enable = f"between(t,{start},{end})" if end is not None else f"gte(t,{start})"
    return [
        "-i",
        str(overlay_path),
        "-filter_complex",
        f"[0:v][1:v]overlay=x={x}:y={y}:enable='{enable}'",
        "-pix_fmt",
        "yuv420p",
    ]


def apply_text_overlay(input_path: Path, output_path: Path, text: str, x: int, y: int, start: float, end: Optional[float], fontfile: Optional[str], opacity: float) -> None:
    drawtext = build_drawtext_filter(text, x, y, start, end, fontfile, opacity)
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-vf",
        drawtext,
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-level:v",
        "4.0",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.check_call(cmd)


def apply_image_overlay(input_path: Path, output_path: Path, image_path: Path, x: int, y: int, start: float, end: Optional[float], opacity: float) -> None:
 args = [
     settings.ffmpeg_path,
     "-y",
     "-i", str(input_path),
 ] + overlay_image_filter(image_path, x, y, start, end, opacity) + [
     "-c:v", "libx264",
     "-preset", "veryfast",
     "-crf", "23",
     "-c:a", "aac",
     "-b:a", "128k",
     "-movflags", "+faststart",
     str(output_path),
 ]
 subprocess.check_call(args)


def apply_video_overlay(input_path: Path, output_path: Path, overlay_path: Path, x: int, y: int, start: float, end: Optional[float]) -> None:
    args = [
        settings.ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
    ] + overlay_video_filter(overlay_path, x, y, start, end) + [
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-level:v",
        "4.0",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.check_call(args)


def transcode_to_quality(input_path: Path, output_path: Path, height: int) -> None:
    # Keep aspect ratio by setting scale=-2:height
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-vf",
        f"scale=-2:{height}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(output_path),
    ]
    subprocess.check_call(cmd)



