"""
FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analytics, health, orders, products
from app.config import settings
from app.database.seed import seed_products
from app.database.session import SessionLocal, init_db
from app.telemetry.otel import setup_telemetry

logger = logging.getLogger("ecommerce.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    db = SessionLocal()
    try:
        seed_products(db)
    finally:
        db.close()
    logger.info("Startup complete: database ready and seeded.")
    yield


app = FastAPI(
    title="E-Commerce Data & Observability Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# OpenTelemetry must be wired up right after the app is constructed so it
# can wrap route handling from the very first request.
setup_telemetry(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(health.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(analytics.router)
