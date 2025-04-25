from pydantic import BaseModel, Field
from typing import List, Optional

class PortfolioItemInput(BaseModel):
    coin_id: str = Field(..., description="CoinGecko ID of the coin (e.g., 'bitcoin')")
    quantity: float = Field(..., gt=0, description="Amount of the coin owned")
    entry_price: float = Field(..., ge=0, description="Price per coin at time of purchase (in USD)")
class PortfolioItemOutput(PortfolioItemInput):
    id: str = Field(..., description="Unique identifier for this portfolio entry")
    current_price: Optional[float] = Field(None, description="Current price per coin (in USD)")
    current_value: Optional[float] = Field(None, description="Total current value (quantity * current_price)")
    profit_loss: Optional[float] = Field(None, description="Profit or loss for this holding")
    profit_loss_percent: Optional[float] = Field(None, description="% Profit or loss for this holding")

class PortfolioSummary(BaseModel):
    total_entry_value: float = Field(0.0, description="Total value of all assets at purchase time")
    total_current_value: float = Field(0.0, description="Total current value of all assets")
    total_profit_loss: float = Field(0.0, description="Total profit or loss across the portfolio")
    total_profit_loss_percent: float = Field(0.0, description="% Profit or loss across the portfolio")
    items: List[PortfolioItemOutput] = Field([], description="List of assets in the portfolio")


portfolio_storage = {}