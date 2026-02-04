"""
FastAPI webhook server for receiving Gong webhooks.
Lightweight server that returns 200 OK quickly (<500ms).
Heavy processing happens asynchronously via Prefect flows.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from gong.webhook import router as webhook_router

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Gong Call Coaching Webhook Server",
    description="Receives webhooks from Gong for call analysis",
    version="1.0.0",
)

# Add CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook router
app.include_router(webhook_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "service": "Gong Call Coaching Webhook Server",
        "status": "running",
        "version": "1.0.0",
    }


@app.on_event("startup")
async def startup_event():
    """Run on startup."""
    logger.info("Starting webhook server")
    logger.info(f"Webhook endpoint: http://{settings.webhook_host}:{settings.webhook_port}/webhooks/gong")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown."""
    logger.info("Shutting down webhook server")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "webhook_server:app",
        host=settings.webhook_host,
        port=settings.webhook_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
