from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging

from app.config import settings
from app.controllers import router as api_router
from app.database import engine
from app.utils.observability import setup_observability

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise HSE (Health, Safety, Environment) Platform API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# =============================================
# MIDDLEWARE
# =============================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response


# Rate limiting middleware (simple in-memory, use Redis for production)
if settings.RATE_LIMIT_ENABLED:
    from collections import defaultdict
    from fastapi import HTTPException

    request_counts = defaultdict(list)

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW_SECONDS

        # Clean old requests
        request_counts[client_ip] = [
            t for t in request_counts[client_ip] if now - t < window
        ]

        if len(request_counts[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        request_counts[client_ip].append(now)
        return await call_next(request)


# =============================================
# ERROR HANDLERS
# =============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if settings.DEBUG else None},
    )


# =============================================
# ROUTES
# =============================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs",
    }


# Include API routes
app.include_router(api_router)


# =============================================
# LIFECYCLE EVENTS
# =============================================

@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")

    # Initialize observability stack
    try:
        celery_app = None
        try:
            from app.utils.celery_app import celery_app as ca
            celery_app = ca
        except Exception:
            logger.info("Celery not available - skipping Celery instrumentation")

        setup_observability(app=app, celery_app=celery_app, db_engine=engine)
    except Exception as e:
        logger.warning(f"Observability initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
