# Frantech v0.1.0

**Franchise Operations Platform** — Multi-location franchise owner management system with audit-first architecture.

## Architecture

### Backend
- **FastAPI** with async support
- **PostgreSQL** (no SQLite)
- **Redis** for task queue + caching
- **SQLAlchemy ORM** with Alembic migrations
- **JWT authentication** with organization context

### Frontend
- **React 18** with Vite
- **React Router** for navigation
- **Axios** for API calls
- **Tailwind CSS** for styling

### Infrastructure
- Docker Compose for local dev (PostgreSQL, Redis, FastAPI, React)
- Render.yaml for production deployment
- Health checks on all services

---

## Project Structure

```
frantech/
├── backend/
│   ├── app/
│   │   ├── models.py          # SQLAlchemy models (P0: AuditLog with hash chain)
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── database.py        # DB connection
│   │   ├── auth.py            # JWT + UserContext
│   │   ├── services/
│   │   │   └── audit.py       # Audit logging with hash-chain verification
│   │   └── __init__.py
│   ├── main.py                # FastAPI app + endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── migrations/            # Alembic (auto-created on first run)
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable components (Navigation, etc.)
│   │   ├── pages/             # Page components
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── render.yaml
├── .gitignore
└── README.md
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Development (Docker Compose)

```bash
cd frantech

# Start all services
docker-compose up

# Services will be available at:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:5173
# - API Docs: http://localhost:8000/docs
# - Postgres: localhost:5432
# - Redis: localhost:6379
```

### Database Initialization

On first run, tables are created automatically. To reset:

```bash
# Inside backend container or with Python venv
python
>>> from app.database import init_db
>>> init_db()
```

### Environment Variables

Backend (set in docker-compose.yml or .env):
```
DATABASE_URL=postgresql://frantech:frantech_dev@postgres:5432/frantech
REDIS_URL=redis://redis:6379/0
JWT_SECRET=dev-secret-key-change-in-prod
ENVIRONMENT=development
```

Frontend:
```
VITE_API_URL=http://localhost:8000
```

---

## P0: Audit System (Tamper-Proof)

### Design
Every mutation creates an immutable, tamper-evident audit log:

```python
AuditLog(
  id, timestamp, user_id, organization_id,
  action, entity_type, entity_id,
  payload_json,
  prev_hash,              # Hash of previous entry
  hash                    # SHA256(prev_hash + json(payload))
)
```

### Hash Chain
- **prev_hash**: SHA256 of the previous audit entry
- **hash**: SHA256(prev_hash + json(payload))
- **Verification**: Call `/audit-logs/verify` to detect tampering

### Implementation
All mutations flow through `audit_log()` in `app/services/audit.py`:

```python
audit_log(
    db=db,
    organization_id=user.organization_id,
    action="create",
    entity_type="location",
    entity_id=location.id,
    user_id=user.user_id,
    payload=location.__dict__,
)
```

---

## API Endpoints (MVP)

### Authentication
- `POST /auth/signup` — Create org + user
- `POST /auth/login` — Get JWT token

### Locations
- `GET /locations` — List locations
- `POST /locations` — Create location
- `GET /locations/{id}` — Get location
- `PATCH /locations/{id}` — Update location

### Work Orders
- `GET /work-orders` — List work orders
- `POST /work-orders` — Create work order

### Tasks
- `GET /tasks` — List tasks
- `POST /tasks` — Create task

### Financials
- `GET /financials/{location_id}` — Get financials
- `POST /financials/{location_id}` — Create financial record

### Audit
- `GET /audit-logs` — Get audit logs
- `GET /audit-logs/verify` — Verify chain integrity

### Dashboard
- `GET /dashboard/summary` — Get dashboard summary

### Health
- `GET /health` — Health check

---

## Frontend Pages

- **Dashboard** — Summary of locations, issues, compliance, revenue/expenses
- **Locations** — Create/manage locations
- **Work Orders** — Track maintenance work orders
- **Tasks** — Task assignment and tracking
- **Financials** — Financial records (placeholder)
- **Audit Logs** — Audit trail with integrity verification

---

## Build Order (Completed)

✅ 1. Audit system (P0) — Hash-chain audit_logs table
✅ 2. Core models + migrations
✅ 3. Auth middleware (JWT + org context)
✅ 4. Locations + dashboard
✅ 5. Work orders + tasks
✅ 6. Financials (placeholder)
✅ 7. Frontend UI shell

---

## Next Steps (Phase 2)

- [ ] Compliance module (SOPs + audits)
- [ ] AI reporting (Ava-lite integration)
- [ ] Luna integration (work orders sync)
- [ ] CommandDeck integration (AI orchestration)
- [ ] Role-based permissions (franchisor vs franchisee)
- [ ] Real-time alerts
- [ ] Mobile PWA

---

## Deployment (Render)

1. Push to GitHub
2. Connect repo to Render
3. Services auto-deploy from `render.yaml`:
   - Backend (Python)
   - Frontend (Node)
   - PostgreSQL (managed)
   - Redis (managed)

---

## Development Notes

- All mutations are logged to `audit_logs` table with hash-chain verification
- Multi-tenant isolation enforced at query level (always filter by `organization_id`)
- Auth middleware extracts user + org context from JWT
- No destructive migrations (Alembic forward-only)
- Health checks on all services ensure readiness

---

## License

Proprietary — Frantech Inc.
