import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, text

from app.core import init_db, get_db_session, tasks
from app.api import dns
from app.core.settings import settings
from app.core.exceptions import (
    setup_exception_handlers,
    DNSBaseError,
    ValidationError,
    NotFoundError,
    ConflictError,
    DNSError,
    CNAMELoopError,
    RecordValidationError,
    HostnameValidationError,
    RecordConflictError
)

# Lifespan function for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    
    # Start background tasks
    await tasks.task_scheduler.start()
    
    yield
    
    # Clean up on shutdown
    await tasks.task_scheduler.stop()

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A simple DNS-like API for managing hostname records",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup exception handlers
setup_exception_handlers(app)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Include routers
app.include_router(dns.router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Root endpoint with API information
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "environment": settings.ENVIRONMENT
    }

# Example of a protected endpoint that uses the database
@app.get("/status")
async def get_status(session: Session = Depends(get_db_session)):
    """Get application status with database connectivity check."""
    try:
        # Simple query to check database connectivity
        result = session.execute(text("SELECT 1"))
        db_status = "connected" if result.scalar() == 1 else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "running",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }
