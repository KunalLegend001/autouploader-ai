# AutoUploader — AI Video Clip Agent 🚀

> **Turn any long-form video into viral short clips — fully automated with AI.**
> 
> Works like Opus Clip + Repurpose.io + Buffer, but self-hosted and fully customizable.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoUploader System                       │
├─────────────────┬───────────────────┬───────────────────────┤
│  Frontend       │  Backend (API)    │  AI Pipeline          │
│  Next.js 15     │  FastAPI          │  GPT-4 + Whisper      │
│  Port: 3000     │  Port: 8000       │  FFmpeg               │
├─────────────────┴───────────────────┴───────────────────────┤
│  Queue          │  Database         │  Storage              │
│  Redis + Celery │  PostgreSQL       │  AWS S3               │
└─────────────────┴───────────────────┴───────────────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| 🎯 **AI Clip Detection** | GPT-4 analyzes transcript, scores moments by viral potential |
| 📝 **Auto Captions** | Whisper timestamps → FFmpeg ASS subtitle burn-in |
| 📱 **Vertical Format** | Smart blur-pad 9:16 conversion (1080×1920) |
| 🎬 **AI B-Roll** | Keywords → Pexels stock footage → PiP overlay |
| 📤 **Auto-Posting** | YouTube Shorts, TikTok, Instagram Reels, Facebook Reels |
| 📊 **Analytics** | Views, likes, shares, engagement across all platforms |
| ⏱️ **Scheduler** | Celery + Redis queue with scheduled posting |
| 🔒 **Rate Limiting** | 30 clips/month, 3 channels per user (configurable) |

---

## Quick Start (Docker)

```bash
# 1. Clone and configure
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 2. Spin up everything
docker-compose up -d

# 3. Open
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

## Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install deps
pip install -r requirements.txt

# Copy and configure env
cp .env.example .env

# Start API server
uvicorn main:app --reload --port 8000

# Start Celery worker (in another terminal)
celery -A app.celery_app worker -Q clips -c 2 --loglevel=info

# Start Celery beat scheduler
celery -A app.celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens on http://localhost:3000
```

---

## API Keys Required

| Service | Purpose | Get it at |
|---------|---------|-----------|
| OpenAI | GPT-4 + Whisper | [platform.openai.com](https://platform.openai.com) |
| YouTube Data API v3 | Channel videos | [console.cloud.google.com](https://console.cloud.google.com) |
| Meta Graph API | Instagram + Facebook | [developers.facebook.com](https://developers.facebook.com) |
| TikTok API | TikTok posting | [developers.tiktok.com](https://developers.tiktok.com) |
| Pexels API | B-roll footage | [pexels.com/api](https://www.pexels.com/api) |
| AWS S3 | Video storage | [aws.amazon.com](https://aws.amazon.com) |

---

## AI Pipeline Flow

```
YouTube URL
    │
    ▼ yt-dlp download
Video File (MP4)
    │
    ▼ FFmpeg audio extraction → Whisper API
Transcript + Timestamps
    │
    ▼ GPT-4 (viral moment scoring)
5 Best Segments (start/end/score)
    │
    ├─── FFmpeg cut → Raw clips
    ├─── FFmpeg blur-pad → 9:16 vertical
    ├─── Whisper ASS → Caption burn-in
    ├─── Pexels API → B-roll PiP overlay
    │
    ▼ Upload to S3
Ready Clips (30-90 seconds each)
    │
    ▼ Celery queue
Auto-post to:
  ├── YouTube Shorts
  ├── TikTok
  ├── Instagram Reels
  └── Facebook Reels
```

---

## File Structure

```
AutoUploader/
├── backend/
│   ├── main.py                     # FastAPI app entry
│   ├── app/
│   │   ├── ai/
│   │   │   ├── pipeline.py         # Main AI orchestrator
│   │   │   ├── transcriber.py      # Whisper API
│   │   │   ├── clip_selector.py    # GPT-4 viral selector
│   │   │   ├── caption_burner.py   # FFmpeg ASS captions
│   │   │   ├── broll_inserter.py   # Pexels B-roll PiP
│   │   │   └── video_formatter.py  # FFmpeg utils
│   │   ├── tasks/
│   │   │   ├── clip_tasks.py       # Celery clip generation
│   │   │   ├── posting_tasks.py    # Celery auto-posting
│   │   │   └── analytics_tasks.py  # Hourly analytics sync
│   │   ├── services/
│   │   │   ├── youtube_downloader.py
│   │   │   ├── youtube_poster.py
│   │   │   ├── meta_poster.py
│   │   │   └── tiktok_poster.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── channels.py
│   │   │   ├── clips.py
│   │   │   ├── posting.py
│   │   │   └── analytics.py
│   │   ├── models.py               # SQLAlchemy
│   │   ├── schemas.py              # Pydantic
│   │   ├── config.py               # Settings
│   │   ├── auth.py                 # JWT
│   │   └── database.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Landing page
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── dashboard/
│   │       ├── layout.tsx          # Sidebar + auth guard
│   │       ├── page.tsx            # Dashboard overview
│   │       ├── generate/page.tsx   # Clip generation
│   │       ├── clips/page.tsx      # My Clips
│   │       ├── channels/page.tsx   # YouTube channels
│   │       ├── posting/page.tsx    # Post queue
│   │       └── analytics/page.tsx  # Analytics
│   ├── lib/
│   │   ├── api.ts                  # Axios client
│   │   └── auth-context.tsx        # Auth state
│   ├── Dockerfile
│   └── .env.local
└── docker-compose.yml
```

---

## Environment Configuration

```env
# backend/.env
OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=AIza...
PEXELS_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/autouploader
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-32-char-secret
MAX_CLIPS_PER_MONTH=30
MAX_CHANNELS_PER_USER=3
```

---

## FFmpeg Requirements

FFmpeg must be installed and on PATH:

**Windows:** Download from [ffmpeg.org](https://ffmpeg.org) and add to PATH

**Linux/Mac:**
```bash
apt install ffmpeg     # Debian/Ubuntu
brew install ffmpeg    # macOS
```

---

## License

MIT — Build something amazing with it! 🚀
