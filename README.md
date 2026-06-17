# DRAX

**Digital Resource Assistant of ARDRAXIS**

AI Assistant resmi untuk OSIS SMA Ignatius Global School.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, TailwindCSS, shadcn/ui |
| Backend | Flask, Python |
| AI | Gemini (google-generativeai) |
| Data | Google Sheets (gspread) |
| Cache | In-memory (cachetools TTLCache, 60s refresh) |
| Deployment | Linux VPS, Nginx, Gunicorn, systemd |

---

## Project Structure

```
draxis/
├── frontend/          ← Next.js 15 application
├── backend/           ← Flask API server
├── deploy/            ← Nginx, systemd, deployment scripts
├── scripts/           ← Utility scripts
└── docs/              ← Documentation
```

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Cloud service account with Google Sheets API enabled
- Gemini API key

### 1. Clone and Configure

```bash
git clone <repo-url> draxis
cd draxis
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `GOOGLE_SHEET_ID` | Google Sheets ID (from sheet URL) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON of the service account key |
| `FRONTEND_URL` | Frontend origin for CORS (default: `http://localhost:3000`) |

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Copy `.env.local.example` to `.env.local`:

```bash
cp .env.local.example .env.local
```

### 4. Initialize Google Sheets

```bash
cd backend
source .venv/bin/activate
python ../scripts/seed_sheets.py
```

This creates the **Members** and **Events** worksheets with proper headers.

---

## Run (Development)

### Backend

```bash
cd backend
source .venv/bin/activate
python app.py
```

Server starts at `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm run dev
```

App starts at `http://localhost:3000`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `GET` | `/api/v1/suggestions` | Quick prompt suggestions |
| `POST` | `/api/v1/chat` | Ask a question (body: `{"message": "..."}`) |

---

## Build (Production)

### Backend

```bash
cd backend
source .venv/bin/activate
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 wsgi:app
```

### Frontend

```bash
cd frontend
npm run build
npm start
```

---

## Deploy to VPS

1. Copy files to `/var/www/draxis/`
2. Run backend setup (venv + pip install)
3. Run frontend setup (npm ci + npm run build)
4. Copy systemd units: `sudo cp deploy/systemd/*.service /etc/systemd/system/`
5. Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable drax-backend drax-frontend
sudo systemctl start drax-backend drax-frontend
```

6. Configure Nginx: `sudo cp deploy/nginx/draxis.conf /etc/nginx/sites-available/draxis`
7. Enable site: `sudo ln -s /etc/nginx/sites-available/draxis /etc/nginx/sites-enabled/`
8. Get SSL certificate: `sudo certbot --nginx -d draxis.osissmaigs.com`
9. Reload Nginx: `sudo systemctl reload nginx`

Or use the automated deploy script:

```bash
sudo bash deploy/deploy.sh
```

---

## Environment Variables (Production)

Set these in the systemd service files or in `/etc/environment`:

- `GEMINI_API_KEY`
- `GOOGLE_SHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `FLASK_ENV=production`
- `SECRET_KEY` (random string)
- `FRONTEND_URL` (production URL)
- `NEXT_PUBLIC_API_URL` (production API URL)
- `CACHE_TTL_SECONDS=60`
- `RATE_LIMIT_PER_MINUTE=10`

---

## Monitoring

- Logs: `/var/log/nginx/drax-*.log` and `backend/app.log`
- Health check: `GET /api/v1/health` (monitor with cron every 5 min)
- Backups: `deploy/backup.sh` (daily tarball to `/var/backups/draxis/`)
- Error tracking: Sentry-ready (add `sentry-sdk` to requirements)

---

## Data Flow

```
User → Browser → Next.js Frontend → Flask API
                                         ├─ Cache (60s TTL)
                                         ├─ Google Sheets (on miss)
                                         └─ Gemini API (context + question)
                                              └─ Response → Frontend → User
```

---

## License

MIT
