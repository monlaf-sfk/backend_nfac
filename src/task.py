import asyncio
import logging
from src.init import coin_gecko_client, market_data_cache

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = ["usd"]
UPDATE_INTERVAL_SECONDS = 60

async def update_market_data_task():
    """
    Periodically fetches market data for supported currencies and updates the cache.
    """
    while True:
        logger.info("Starting market data update cycle...")
        for currency in SUPPORTED_CURRENCIES:
            try:
                logger.debug(f"Fetching market data for {currency.upper()}...")
                data = await coin_gecko_client.get_markets(vs_currency=currency)

                market_data_cache[currency] = data
                logger.debug(f"Cache updated successfully for {currency.upper()}. {len(data)} items.")

            except Exception as e:
                logger.error(f"Failed to update market data for {currency.upper()}: {e}")

            await asyncio.sleep(2)

        logger.info(f"Market data update cycle finished. Waiting {UPDATE_INTERVAL_SECONDS} seconds.")
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)