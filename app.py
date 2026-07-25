from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from moviepy.editor import AudioFileClip
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
CORS(app, origins=cors_origins)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DOWNLOAD_FOLDER = Path(os.getenv("DOWNLOAD_FOLDER", "downloads/youtube"))
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

YOUTUBE_URL_PATTERN = re.compile(
    r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
    r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%?]{11})"
)
VIDEO_FORMATS = {"highest", "1080p", "720p", "360p"}
AUDIO_FORMATS = {"mp3", "wav"}


def api_response(message: str, *, error: bool = False, status: int = 200, **data: Any):
    payload = {"message": message, "error": error, **data}
    return jsonify(payload), status


def request_value(name: str, default: str = "") -> str:
    """Read a value from either form data or a JSON request body."""
    value = request.form.get(name)
    if value is None:
        payload = request.get_json(silent=True) or {}
        value = payload.get(name, default)
    return str(value or default).strip()


@app.get("/")
def home():
    return jsonify(
        {
            "name": "YouTube Downloader API",
            "status": "ok",
            "endpoint": "POST /download",
            "formats": sorted(VIDEO_FORMATS | AUDIO_FORMATS),
        }
    )


@app.post("/download")
def download_video():
    video_url = request_value("video_url")
    resolution_or_format = request_value("resolution", "highest").lower()

    if not video_url:
        return api_response(
            "Please provide a YouTube video URL.", error=True, status=400
        )

    if not YOUTUBE_URL_PATTERN.match(video_url):
        return api_response("Invalid YouTube URL.", error=True, status=400)

    if resolution_or_format not in VIDEO_FORMATS | AUDIO_FORMATS:
        return api_response(
            "Invalid resolution or format selected.", error=True, status=400
        )

    try:
        youtube = YouTube(video_url)

        if resolution_or_format in VIDEO_FORMATS:
            streams = youtube.streams.filter(progressive=True, file_extension="mp4")
            stream = (
                streams.get_highest_resolution()
                if resolution_or_format == "highest"
                else streams.filter(res=resolution_or_format).first()
            )

            if stream is None:
                return api_response(
                    "The selected resolution is not available.",
                    error=True,
                    status=404,
                )

            downloaded_path = Path(
                stream.download(output_path=str(DOWNLOAD_FOLDER))
            )
            return api_response(
                "Video downloaded successfully.",
                filename=downloaded_path.name,
                format="mp4",
            )

        audio_stream = youtube.streams.get_audio_only()
        temporary_path = Path(
            audio_stream.download(output_path=str(DOWNLOAD_FOLDER))
        )
        output_path = temporary_path.with_suffix(f".{resolution_or_format}")

        clip = AudioFileClip(str(temporary_path))
        try:
            clip.write_audiofile(str(output_path), logger=None)
        finally:
            clip.close()

        temporary_path.unlink(missing_ok=True)
        return api_response(
            f"Audio ({resolution_or_format.upper()}) downloaded successfully.",
            filename=output_path.name,
            format=resolution_or_format,
        )

    except AgeRestrictedError:
        return api_response(
            "This video is age-restricted and cannot be downloaded.",
            error=True,
            status=403,
        )
    except Exception:
        logger.exception("Download request failed")
        return api_response(
            "The download could not be completed.", error=True, status=500
        )


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
