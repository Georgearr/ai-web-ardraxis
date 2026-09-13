# DRAX

**Digital Resource Assistant of ARDRAXIS**

AI Assistant resmi untuk OSIS SMA Ignatius Global School.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application Server | Python 3.11+, Flask (`app.py`) |
| Frontend Assets | HTML5, CSS3, JavaScript / Next.js Static Export |
| AI Providers | DeepSeek, OpenRouter, OpenAI, Gemini |
| Data | Google Sheets (gspread) |
| Cache | In-memory (cachetools TTLCache) |
| Deployment | cPanel (Setup Python App / WSGI / Passenger), Linux VPS (Gunicorn) |

---

## Project Structure

```
draxis/
├── app.py             ← Main Application Entry Point (Flask + Static + API)
├── passenger_wsgi.py  ← cPanel Phusion Passenger WSGI entry point
├── wsgi.py            ← Standard WSGI entry point
├── requirements.txt   ← Python dependencies
├── backend/           ← Flask API logic & AI services
├── main-page/         ← Landing page & static web assets
├── frontend/          ← Next.js source UI
└── deploy/            ← Deployment scripts & cPanel Setup Guide
```

---

## Setup & Deployment

### 1. Direct Python Host (cPanel / Shared Hosting)

Untuk hosting cPanel berbasis **Setup Python App**:
- **Application Startup File**: `app.py`
- **Application Entry Point**: `app` (atau `application`)

Panduan lengkap cPanel tersedia di: [cpanel_setup_guide.md](file:///e:/WEBSITE%20OSIS%20SMA%20IGS/ai-web-ardraxis/deploy/cpanel_setup_guide.md)

### 2. Local Run (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run main python application
python app.py
```

Server berjalan di `http://localhost:5001`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `GET` | `/api/v1/suggestions` | Quick prompt suggestions |
| `POST` | `/api/v1/chat` | Ask a question (body: `{"message": "..."}`) |

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
