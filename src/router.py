import uuid

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional

from src.init import coin_gecko_client, market_data_cache
from src.models import portfolio_storage, PortfolioSummary, PortfolioItemOutput, PortfolioItemInput

router = APIRouter(
    prefix="/api/v1"
)

ALLOWED_CURRENCIES = ["usd"]

@router.get("/cryptocurrencies")
async def get_cryptocurrencies(
    vs_currency: Optional[str] = Query("usd", enum=ALLOWED_CURRENCIES)
):
    """
    Get cached list of top cryptocurrencies market data.
    Data is updated periodically in the background.
    """
    cached_data = market_data_cache.get(vs_currency.lower())

    if not cached_data:
        raise HTTPException(
            status_code=503,
            detail=f"Market data for {vs_currency.upper()} is currently unavailable. Please try again shortly."
        )

    return cached_data

@router.get("/cryptocurrency/{currency_id}")
async def get_currency_details(currency_id: str):
    """
    Get detailed information for a specific cryptocurrency.
    Uses caching for individual coin details.
    """
    try:
        return await coin_gecko_client.get_coin_details(currency_id=currency_id)
    except Exception as e:
         raise HTTPException(
             status_code=500,
             detail=f"Could not fetch details for {currency_id}: {e}"
         )

@router.post("/portfolio", response_model=PortfolioItemOutput, status_code=201)
async def add_portfolio_item(item: PortfolioItemInput):
    """
    Add a new cryptocurrency holding to the portfolio.
    Assumes entry price is in USD.
    """
    item_id = str(uuid.uuid4())
    stored_item = PortfolioItemOutput(
        id=item_id,
        coin_id=item.coin_id,
        quantity=item.quantity,
        entry_price=item.entry_price
    )
    portfolio_storage[item_id] = stored_item
    return stored_item

@router.get("/portfolio", response_model=PortfolioSummary)
async def get_portfolio():
    """
    Retrieve the current portfolio summary, including calculated profit/loss.
    Calculations are based on the latest cached USD market data.
    """
    summary = PortfolioSummary()
    usd_market_data = market_data_cache.get("usd", [])

    if not usd_market_data:
         raise HTTPException(
            status_code=503,
            detail="Market data (USD) is currently unavailable for portfolio calculation. Please try again shortly."
         )

    current_prices = {coin['id']: coin.get('current_price') for coin in usd_market_data if coin.get('current_price') is not None}

    processed_items = []
    for item_id, item in portfolio_storage.items():
        output_item = item.copy(deep=True)

        entry_value = item.quantity * item.entry_price
        summary.total_entry_value += entry_value

        current_price = current_prices.get(item.coin_id)
        output_item.current_price = current_price

        if current_price is not None:
            current_value = item.quantity * current_price
            profit_loss = current_value - entry_value
            profit_loss_percent = (profit_loss / entry_value * 100) if entry_value > 0 else 0

            output_item.current_value = current_value
            output_item.profit_loss = profit_loss
            output_item.profit_loss_percent = profit_loss_percent

            summary.total_current_value += current_value
        else:
            output_item.current_value = None
            output_item.profit_loss = None
            output_item.profit_loss_percent = None

        processed_items.append(output_item)

    summary.items = processed_items
    summary.total_profit_loss = summary.total_current_value - summary.total_entry_value
    if summary.total_entry_value > 0:
         summary.total_profit_loss_percent = (summary.total_profit_loss / summary.total_entry_value) * 100
    else:
         summary.total_profit_loss_percent = 0.0

    return summary

@router.delete("/portfolio/{item_id}", status_code=204)
async def delete_portfolio_item(item_id: str):
    """
    Delete a specific item from the portfolio by its ID.
    """
    if item_id not in portfolio_storage:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    del portfolio_storage[item_id]
    return None