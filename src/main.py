import asyncio
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from src.config import settings
from src.router import router as router_crypto
from src.init import coin_gecko_client
from src.task import update_market_data_task


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

background_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global background_task
    logger.info("Application startup...")
    await coin_gecko_client.initialize_session()
    logger.info("HTTP Client Initialized.")

    logger.info("Starting background market data update task...")
    loop = asyncio.get_running_loop()
    background_task = loop.create_task(update_market_data_task())
    logger.info("Background task scheduled.")

    yield

    logger.info("Application shutdown...")
    if background_task and not background_task.done():
        logger.info("Cancelling background task...")
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            logger.info("Background task successfully cancelled.")
        except Exception as e:
            logger.error(f"Exception during background task cancellation: {e}", exc_info=True)
    else:
         logger.info("Background task already done or never started.")

    await coin_gecko_client.close_session()
    logger.info("HTTP Client closed.")


app = FastAPI(
    title="CryptoWatcher API",
    description="API for fetching cryptocurrency data.",
    version="1.0.0",
    lifespan=lifespan #
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    settings.FRONTEND_URL,
]
logger.info(f"Allowed CORS origins: {origins}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_crypto)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during request to {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An internal server error occurred."},
    )

