# PropelSense — Backend API

REST API backend for PropelSense, a ship propulsion intelligence platform. Built with FastAPI and Python 3.11.

## Tech Stack

| Technology                       | Purpose                               |
| -------------------------------- | ------------------------------------- |
| **FastAPI**                      | REST API framework                    |
| **SQLAlchemy**                   | ORM and database layer                |
| **Pydantic / Pydantic Settings** | Data validation and config management |
| **Uvicorn**                      | ASGI server                           |
| **XGBoost**                      | Shaft power prediction ML model       |
| **scikit-learn**                 | Feature engineering and preprocessing |
| **Hugging Face Hub**             | Remote model hosting and download     |
| **fpdf2**                        | PDF report generation                 |
| **python-jose**                  | JWT authentication                    |
| **PostgreSQL**                   | Production database (via psycopg2)    |

## Project Structure

```
backend/
├── app/
│   ├── main.py                   # FastAPI application entry point
│   ├── core/
│   │   ├── config.py             # Environment config (Pydantic Settings)
│   │   ├── database.py           # SQLAlchemy session and engine
│   │   └── auth.py               # JWT authentication utilities
│   ├── api/
│   │   └── v1/
│   │       ├── routes.py         # API router registration
│   │       └── endpoints/
│   │           ├── health.py
│   │           ├── propulsion.py
│   │           ├── auth.py
│   │           ├── sea_trial.py
│   │           ├── ml_prediction.py
│   │           └── reports.py
│   ├── models/                   # SQLAlchemy ORM models
│   ├── schemas/                  # Pydantic request/response schemas
│   └── services/                 # Business logic
│       └── propulsion_service.py
├── requirements.txt
├── render.yaml                   # Render deployment config
└── run.py                        # Local development server runner
```

## Getting Started

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/propelsense
SECRET_KEY=your_secret_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
CORS_ORIGINS=http://localhost:3000
EXTRA_CORS_ORIGINS=https://your-production-frontend.vercel.app
```

### 4. Run Development Server

```bash
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload
```

Server starts at: [http://localhost:8000](http://localhost:8000)

## API Documentation

Once running, visit:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Health

- `GET /api/v1/health` — Health check

### Authentication

- `POST /api/v1/auth/verify` — Verify Supabase JWT token

### ML Prediction

- `POST /api/v1/ml/predict` — Predict shaft power from vessel and environmental parameters
- `GET /api/v1/ml/history` — Retrieve prediction history for the authenticated user

### Sea Trials

- `GET /api/v1/sea-trials` — List all sea trials
- `POST /api/v1/sea-trials` — Create a new sea trial
- `GET /api/v1/sea-trials/{id}` — Get a specific sea trial
- `PUT /api/v1/sea-trials/{id}` — Update a sea trial
- `DELETE /api/v1/sea-trials/{id}` — Delete a sea trial
- `POST /api/v1/sea-trials/{id}/ml-predict` — Run ML prediction on a completed trial

### Propulsion

- `GET /api/v1/propulsion/data` — Get propulsion sensor readings
- `GET /api/v1/propulsion/stats` — Get propulsion statistics

### Reports

- `GET /api/v1/reports/sea-trials/pdf` — Generate PDF report for sea trials
- `GET /api/v1/reports/predictions/pdf` — Generate PDF report for prediction history

## ML Model

The shaft power prediction model is an XGBoost regressor hosted on Hugging Face Hub. It is downloaded and cached locally on first startup — no manual setup required.

**Input features (10 base):** speed through water, aft draft, fore draft, apparent wind U/V components, ocean current U/V components, combined wave height, days since dry dock, speed difference (STW − SOG).

**Performance:** R² = 0.978 · MAE = 866 kW · Inference < 10ms · Model size = 993 KB

## Deployment

Deployed on **Render** using `render.yaml`. Python version is pinned to `3.11` in `render.yaml` to ensure compatible binary wheels for all dependencies.

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Adding New Endpoints

1. Define schema in `app/schemas/`
2. Implement logic in `app/services/`
3. Create route handler in `app/api/v1/endpoints/`
4. Register in `app/api/v1/routes.py`

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
