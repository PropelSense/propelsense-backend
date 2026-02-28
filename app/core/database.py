"""
Database Connection Setup
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Disable SQL query logging
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for future models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Test connection
def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            print(f"[INFO] Database Connected")
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


# Initialize database tables
def init_db():
    """Create all database tables"""
    # print("[INFO] Creating database tables...")
    
    # Import all models to register them with Base
    from app.models.vessel import Vessel
    from app.models.prediction_history import PredictionHistory
    from app.models.ml_model import MLModel
    from app.models.propulsion_reading import PropulsionReading
    from app.models.weather_data import WeatherData
    from app.models.ocean_data import OceanData
    from app.models.report import Report
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # print("[INFO] Database tables created successfully")