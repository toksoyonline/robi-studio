# Robi Studio Platform

Complete starter platform with:
- Student panel
- Parent panel
- Admin panel
- Simulation engine
- Premium lessons system

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Database: SQLite

## Project Structure

```
app/
  api/routes.py            # API endpoints
  services/simulation.py   # Simulation engine logic
  database.py              # SQLite initialization and seeding
  schemas.py               # Request models
  main.py                  # FastAPI app + static frontend serving
frontend/
  index.html
  css/styles.css
  js/common.js
  pages/student.html
  pages/parent.html
  pages/admin.html
data/
  robi_studio.db           # Auto-created on startup
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit:
- `http://localhost:8000/`
- `http://localhost:8000/student`
- `http://localhost:8000/parent`
- `http://localhost:8000/admin`

## Core APIs
- `GET /api/students/{id}/dashboard`
- `GET /api/parents/{id}/overview`
- `GET /api/admin/overview`
- `POST /api/simulation/run`
- `POST /api/premium/update`
- `POST /api/lessons`
- `POST /api/enrollments/update`
