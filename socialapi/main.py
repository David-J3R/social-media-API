import logging
from contextlib import asynccontextmanager

# asgi_correlation_id is used to add correlation IDs to requests for better traceability
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from socialapi.database import database
from socialapi.logging_conf import configure_logging
from socialapi.routers.post import router as post_router

# test logging
logger = logging.getLogger(__name__)


# Turn on and shut down database connection with our app
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting up connection...")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
# Add Correlation ID Middleware
app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router)


# Global exception handler to log HTTPExceptions
# For example, if a route raises HTTPException, it will be logged here
@app.exception_handler(HTTPException)
async def http_exception_handler_logger(request, exc):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)
