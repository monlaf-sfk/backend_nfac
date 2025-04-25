from aiohttp import ClientSession

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
#api.coingecko.com/api
class CoingeckoClient(HTTPClient):
    async def get(self):
        async with self._session.get("v3/coins/list") as response:
            if response.status != 200:
                raise Exception(f"Error: {response.status}")
            return await response.json()
    async def get_currency(self, currency_id: str):
        async with self._session.get(f"v3/coins/{currency_id}") as response:
            if response.status != 200:
                raise Exception(f"Error: {response.status}")
            return await response.json()

