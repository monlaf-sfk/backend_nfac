from src.config import settings
from src.http_client import CoingeckoClient

coin_gecko_client = CoingeckoClient(
    base_url="https://api.coingecko.com/api/",
    api_key=settings.API_COINGECKO,
)
market_data_cache = {
    "usd": [],

}
