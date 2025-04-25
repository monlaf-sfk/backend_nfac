from aiohttp import ClientSession
from async_lru import alru_cache
import logging

logger = logging.getLogger(__name__)

class HTTPClient:

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self._session = ClientSession(
            base_url=base_url,
            headers={
                "Accept": "application/json",
                "x-cg-pro-api-key": api_key
            },
        )

    async def initialize_session(self):
        """Creates the ClientSession. Call this during app startup."""
        if self._session is None:
            logger.info(f"Initializing ClientSession for {self.base_url}")
            self._session = ClientSession(
                base_url=self.base_url,
                headers={
                    "Accept": "application/json",
                    "x-cg-pro-api-key": self.api_key
                },
            )
        else:
            logger.info(f"ClientSession for {self.base_url} already initialized.")

    async def close_session(self):
        """Closes the ClientSession. Call this during app shutdown."""
        if self._session:
            logger.info(f"Closing ClientSession for {self.base_url}")
            await self._session.close()
            self._session = None
        else:
            logger.info(f"ClientSession for {self.base_url} was not initialized or already closed.")

    async def _get_session(self) -> ClientSession:
        """Helper to get the session, ensuring it's initialized."""

        if self._session is None:
            raise RuntimeError("ClientSession not initialized via lifespan event.")
        return self._session

    async def close(self):
        await self.close_session()


class CoingeckoClient(HTTPClient):
    async def get_markets(self, vs_currency: str = 'usd'):
        session = await self._get_session()
        include_sparkline = False
        allowed_currencies = ['usd']
        if vs_currency.lower() not in allowed_currencies:
            logger.warning(f"Unsupported currency '{vs_currency}' requested. Defaulting to 'usd'.")
            vs_currency = 'usd'

        params = {
            'vs_currency': vs_currency.lower(),
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1,
            'sparkline': str(include_sparkline).lower(),
            'price_change_percentage': '24h'
        }
        try:
            async with session.get("v3/coins/markets", params=params) as response:
                response.raise_for_status()
                logger.debug(f"Markets fetch status: {response.status}")
                return await response.json()

        except Exception as e:
            logger.error(f"Error fetching markets for {vs_currency}: {e}")

            raise Exception(f"Error fetching market data: {e}") from e

    @alru_cache
    async def get_coin_details(self, currency_id: str):
        session = await self._get_session()  # Use helper
        try:
            async with session.get(f"v3/coins/{currency_id}") as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching details for {currency_id}: {e}")
            raise Exception(f"Error fetching coin details: {e}") from e
