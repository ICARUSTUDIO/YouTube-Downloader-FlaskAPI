# YouTube Downloader Flask API

A small Flask API that accepts a YouTube URL and downloads an available progressive MP4 stream or converts the audio stream to MP3/WAV on the server.

## Highlights

- JSON and form-data request support
- MP4 downloads at the highest available progressive resolution or a requested resolution
- MP3 and WAV audio conversion
- URL and format validation
- Structured JSON responses with appropriate HTTP status codes
- Configurable CORS, download directory, logging, host, and port
- Production-safe error responses while retaining server-side logs

## Technology

- Python 3.10+
- Flask
- PyTube
- MoviePy
- Flask-CORS
- FFmpeg for audio conversion

## Setup

```bash
git clone https://github.com/ICARUSTUDIO/YouTube-Downloader-FlaskAPI.git
cd YouTube-Downloader-FlaskAPI
python -m venv .venv
```

Activate the environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

MoviePy requires FFmpeg for MP3/WAV conversion. Install FFmpeg through your operating system's package manager and ensure it is available on `PATH`.

## Run

```bash
python app.py
```

The API starts at `http://127.0.0.1:5000` by default.

## API

### Health and capability information

```http
GET /
```

### Download media

```http
POST /download
Content-Type: application/json
```

```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "resolution": "720p"
}
```

Supported values for `resolution` are:

- `highest`
- `1080p`
- `720p`
- `360p`
- `mp3`
- `wav`

Form data is also supported:

```bash
curl -X POST http://127.0.0.1:5000/download \
  -F "video_url=https://www.youtube.com/watch?v=VIDEO_ID" \
  -F "resolution=highest"
```

A successful request returns the saved filename:

```json
{
  "message": "Video downloaded successfully.",
  "error": false,
  "filename": "example.mp4",
  "format": "mp4"
}
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `5000` | Server port |
| `FLASK_DEBUG` | `0` | Set to `1` only for local debugging |
| `DOWNLOAD_FOLDER` | `downloads/youtube` | Server-side media directory |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Python logging level |

## Important usage note

Only download media you own or are authorised to download. The project is intended as a learning and portfolio demonstration; users are responsible for complying with platform terms and applicable copyright law.

## Production considerations

Before deploying publicly, add authentication, rate limiting, request quotas, scheduled cleanup for downloaded files, malware scanning where appropriate, restricted CORS origins, and a production WSGI server such as Gunicorn.
