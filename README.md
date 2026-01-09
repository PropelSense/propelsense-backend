# PropelSense Backend API

FastAPI backend for PropelSense propulsion data analysis dashboard.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Python 3.9+** - Programming language

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   └── config.py        # Configuration settings
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py  # API router
│   │       └── endpoints/   # API endpoints
│   │           ├── health.py
│   │           └── propulsion.py
│   ├── schemas/             # Pydantic models
│   │   └── propulsion.py
│   └── services/            # Business logic
│       └── propulsion_service.py
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
├── .env.example            # Example environment variables
└── run.py                  # Development server runner
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

### 3. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

### 4. Run Development Server

```bash
python run.py

# Or with uvicorn directly
uvicorn app.main:app --reload
```

Server will start at: http://localhost:8000

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/health` - Detailed health check

### Propulsion Data
- `GET /api/v1/propulsion/data` - Get sensor data
- `GET /api/v1/propulsion/stats` - Get statistics
- `GET /api/v1/propulsion/predict` - Predict power output

## Example Requests

### Get Propulsion Data
```bash
curl http://localhost:8000/api/v1/propulsion/data?limit=10
```

### Get Statistics
```bash
curl http://localhost:8000/api/v1/propulsion/stats
```

### Predict Power
```bash
curl "http://localhost:8000/api/v1/propulsion/predict?rpm=2500&torque=150&temperature=85"
```

## Development

### Code Structure Explanation

**app/main.py**: FastAPI application setup, CORS, middleware

**app/core/config.py**: Environment variables and settings

**app/api/v1/endpoints/**: API route handlers (controllers)

**app/schemas/**: Pydantic models for request/response validation

**app/services/**: Business logic layer (separate from routes)

### Adding New Endpoints

1. Create schema in `app/schemas/`
2. Create service in `app/services/`
3. Create endpoint in `app/api/v1/endpoints/`
4. Register router in `app/api/v1/__init__.py`

## Testing

```bash
pytest
```

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)