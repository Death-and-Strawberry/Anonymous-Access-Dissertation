from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
STATIC_DIR = PROJECT_ROOT / "public"

from contextlib import asynccontextmanager
import logging
from .utils import render_template
from .config import settings
from .routers import api, auth, dashboard  # your separate routers


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Tor Hidden Service API")
    # Create database tables on startup
    from .database import engine
    from .models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    logger.info("Shutting down Tor Hidden Service API")

# Initialize FastAPI app
app = FastAPI(
    title="Anonymous Therapy Platform",
    description="A Therapy application running as a Tor hidden service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # More permissive CSP to allow navigation
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(dashboard.router, prefix="/dashboard")

# Home page
@app.get("/", response_class=HTMLResponse)
async def root():
    return render_template("home.html")