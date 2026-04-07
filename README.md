# TodoFlow — Manage your tasks with priority, status, and deadlines in one place

![Python Version](https://img.shields.io/badge/python-3.11-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

---

## Overview

TodoFlow is a fullstack web application built with Flask and a lightweight HTML/JS frontend that lets you create, organize, and track todo items end-to-end. Each task carries a title, description, due date, numerical priority, and a status of **New**, **In Process**, **Deferred**, or **Complete**. Overdue items are visually flagged so nothing slips through the cracks.

---

## Features

- **Add todo items** with a title and optional description
- **Set a completion due date** for every task
- **Assign a numerical priority** to rank tasks by importance
- **Track status** across four stages: `New`, `In Process`, `Deferred`, or `Complete`
- **View all todos** in a sortable, paginated list
- **Filter** todos by status or priority
- **Edit** existing todo items at any time
- **Delete** todo items you no longer need
- **Visual indicator** highlights todos that are past their due date

---

## Prerequisites

| Requirement | Minimum Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| Docker & Docker Compose | 24+ |
| Git | Any recent version |

---

## Quick Start

### Option 1 — Docker (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/todo-flow-app.git
cd todo-flow-app

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env as needed (see Configuration section below)

# 3. Build and start all services
docker compose up --build
```

The app will be available at **http://localhost:5173** (frontend) and **http://localhost:5000** (API).

---

### Option 2 — Local Development

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask run --port 5000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Using Make**

```bash
make install   # Install all dependencies
make dev       # Start both backend and frontend in development mode
make build     # Build production assets
```

---

## API Reference

| Method | Path | Description | Auth Required |
|--------|------|-------------|:---:|
| `GET` | `/api/todos` | Retrieve all todo items (supports filter & sort query params) | No |
| `POST` | `/api/todos` | Create a new todo item | No |
| `GET` | `/api/todos/<id>` | Retrieve a single todo by ID | No |
| `PUT` | `/api/todos/<id>` | Update an existing todo item | No |
| `DELETE` | `/api/todos/<id>` | Delete a todo item by ID | No |

### Query Parameters for `GET /api/todos`

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by status value | `?status=In+Process` |
| `priority` | integer | Filter by priority level | `?priority=1` |
| `sort` | string | Sort field (`priority`, `due_date`) | `?sort=due_date` |
| `order` | string | Sort direction (`asc`, `desc`) | `?order=asc` |

### Request Body — Create / Update Todo (`application/json`)

```json
{
  "title": "Write unit tests",
  "description": "Cover all API endpoints with pytest",
  "due_date": "2025-09-01",
  "priority": 1,
  "status": "New"
}
```

---

## Configuration

Copy `.env.example` to `.env` and adjust values before starting the app.

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask runtime environment (`development` / `production`) | `development` |
| `FLASK_PORT` | Port the Flask backend listens on | `5000` |
| `SECRET_KEY` | Secret key used for Flask session signing | `change-me` |
| `DATABASE_URL` | Database connection string (SQLite / Postgres) | `sqlite:///todos.db` |
| `CORS_ORIGINS` | Allowed CORS origins for the frontend | `http://localhost:5173` |
| `VITE_API_BASE_URL` | Base URL the frontend uses to reach the API | `http://localhost:5000` |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore` by default.

---

## Testing

**Backend tests (pytest)**

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
pytest --verbose
```

**With coverage report**

```bash
pytest --cov=main --cov-report=term-missing
```

**Via Make**

```bash
make test
```

> The latest security scan (Bandit + Safety) reports **HIGH: 0 · MEDIUM: 0 · LOW: 76** — all checks passed. ✅

---

## Security

Please review our security policy and responsible disclosure process in [SECURITY.md](SECURITY.md) before reporting vulnerabilities. Do **not** open a public GitHub issue for security-related findings.

---

## License

This project is licensed under the [MIT License](LICENSE).