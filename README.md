# Intergalactic Cargo Portal

Full-stack cargo manifest portal with JWT authentication, role-based access, and a React dashboard.

**Stack:** Django · DRF · SimpleJWT (RS256) · SQLite · uv · React (Vite)

**Repository:** [Prasad8543/cargo-portal](https://github.com/Prasad8543/cargo-portal)

---

## Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)
- Node.js 18+ and npm
- Redis (optional — cache init degrades gracefully if unavailable)

---

## Backend Setup

```bash
cd backend

# Generate JWT keys (first time only)
./scripts/generate_jwt_keys.sh

uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

API: **http://127.0.0.1:8000**

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard: **http://127.0.0.1:5173**

The Vite dev server proxies `/api/v1/*` requests to the Django backend on port 8000.

Optional: set `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env` if not using the proxy.

---

## Demo Accounts

| Email | Role | Notes |
|-------|------|-------|
| `commander@nebula-corp.com` | Admin | Upload manifests, weights in **KG** |
| `pilot@example.com` | Standard | View-only table, weights in **LBS** |

Sign up via the UI — `@nebula-corp.com` emails are auto-assigned **Admin**.

Password must meet backend rules (min 8 chars, upper, lower, special character).

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/signup/` | Public | Register user |
| POST | `/api/v1/login/` | Public | Login and receive JWT |
| POST | `/api/v1/logout/` | Bearer token in header | Blacklist access token in Redis cache |
| GET | `/api/v1/users/` | Admin JWT | List users |
| GET | `/api/v1/users/{id}/` | JWT | User details |
| POST | `/api/v1/upload/` | Admin JWT | Upload `manifest.txt` (form-data field: `manifest`) |
| GET | `/api/v1/cargo/` | JWT | List cargo records |

Protected requests:

```
Authorization: Bearer <access_token>
```

---

## Frontend Features (Task 3)

- Login / Signup screen with role-based routing to dashboard
- **Admin:** File Upload button + cargo table (weights in **KG**)
- **Standard:** Cargo table only — upload controls are **not rendered** in the DOM
- Table sorted heaviest → lightest; **Earth** destinations pinned to the bottom
- Standard users see weights converted to **LBS** (KG × 2.20462)

---

## Sample Manifest

Use `sample-data/manifest.txt` for upload testing. Legacy format:

```
[2026-03-29] || CRG-001 :: 500 >> Mars Base Alpha
```

Parsing rules:
- `Sector-7` in destination → weight × 1.45
- Round to nearest whole number
- Skip if result is a prime number

---

## Project Structure

```
cargo-portal/
├── backend/
│   ├── accounts/       # Auth, users, roles
│   ├── cargo/          # Manifest upload & cargo APIs
│   ├── core/           # JWT, validators, pagination
│   ├── config/         # Django settings
│   └── pyproject.toml
├── frontend/
│   └── src/            # React app (Vite)
├── sample-data/
└── README.md
```

---

## Environment Variables (Backend)

| Variable | Default | Description |
|----------|---------|-------------|
| `PASSWORD_MIN_LENGTH` | `8` | Minimum password length |
| `PASSWORD_MAX_LENGTH` | `128` | Maximum password length |
| `DJANGO_SECRET_KEY` | dev default | Django secret key |
| `REDIS_URL` | `redis://127.0.0.1:6379/1` | Redis cache URL |
