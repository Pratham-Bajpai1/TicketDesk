from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.db import engine, Base, get_db
from app.routers import tickets, comments, attachments, dashboard
from app.schemas import HealthResponse

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ticketdesk")

# Ensure database tables exist at startup
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Error initializing database tables on module load: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan handler.
    Ensures DB tables exist on application startup.
    """
    logger.info("Starting TicketDesk Application...")
    logger.info(f"Database Target URI: {settings.database_uri.split('@')[-1]}")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified and initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema on startup: {e}")
    yield
    logger.info("Shutting down TicketDesk Application...")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Production-grade IT Support Ticket Tracking System Backend",
    lifespan=lifespan
)

# Configure CORS Middleware for AWS CloudFront / S3 static frontend cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Domain Routers
app.include_router(tickets.router)
app.include_router(comments.router)
app.include_router(attachments.router)
app.include_router(dashboard.router)


@app.get("/health", response_model=HealthResponse, tags=["Operations"])
@app.get("/api/health", response_model=HealthResponse, tags=["Operations"])
def health_check(db: Session = Depends(get_db)):
    """
    AWS ALB Health Check Probe.
    Executes 'SELECT 1' against the DB to verify connectivity.
    Returns HTTP 200 when healthy, or HTTP 500 when database connection fails.
    """
    try:
        db.execute(text("SELECT 1"))
        return HealthResponse(status="healthy", database="connected")
    except Exception as e:
        logger.error(f"Health check failed - Database connectivity error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


# Serve Static Frontend Single-Page Application (SPA)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "TicketDesk API is running. Frontend index.html not found."}
