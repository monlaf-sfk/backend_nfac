
import asyncio
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.router import router as router_crypto
from src.init import coin_gecko_client
from src.task import update_market_data_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CryptoWatcher API",
    description="API for fetching cryptocurrency data.",
    version="1.0.0"
)

app.include_router(router_crypto)


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

background_task = None

@app.on_event("startup")
async def startup_event():
    global background_task
    logger.info("Application startup...")
    logger.info("Starting background market data update task...")
    loop = asyncio.get_event_loop()
    background_task = loop.create_task(update_market_data_task())
    logger.info("Background task scheduled.")

@app.on_event("shutdown")
async def shutdown_event():
    global background_task
    logger.info("Application shutdown...")

    if background_task:
        logger.info("Cancelling background task...")
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            logger.info("Background task successfully cancelled.")
        except Exception as e:
            logger.error(f"Error during background task shutdown: {e}")


    await coin_gecko_client.close()
    logger.info("HTTP Client closed.")

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An internal server error occurred."},
    )