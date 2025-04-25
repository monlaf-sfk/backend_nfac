from fastapi import APIRouter

from src.init import coin_gecko_client

router = APIRouter(
    prefix="/cryptocurrencies"
)

@router.get("/cryptocurrency")
async def get_cryptocurrency():
    return await coin_gecko_client.get()

@router.get("/cryptocurrency/{currency_id}")
async def get_currency(currency_id: str):
    return await coin_gecko_client.get_currency(currency_id)