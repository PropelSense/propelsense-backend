"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import test_connection, init_db
from app.api.v1.routes import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # Startup
    print("[INFO] Starting PropelSense API...")
    test_connection()
    init_db()
    
    # Pre-load ML service and XGBoost model
    print("[INFO] Initializing ML service...")
    from app.services.ml_service import get_ml_service
    ml_service = get_ml_service()
    try:
        ml_service.load_model()
        print("[INFO] XGBoost model loaded successfully (993 KB)")
    except Exception as e:
        print(f"[WARNING] Failed to pre-load XGBoost model: {e}")
    
    yield
    # Shutdown
    print("[INFO] Shutting down PropelSense API...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for PropelSense Dashboard",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to PropelSense API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.API_VERSION}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )