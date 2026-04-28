"""API routes for market assumptions."""
from fastapi import APIRouter
from app.services import market_assumptions
from app.models.schemas import MarketAssumptions, MarketAssumptionsRequest

router = APIRouter()

@router.post("/market/assumptions", response_model=MarketAssumptions, tags=["market"])
async def get_market_assumptions(request: MarketAssumptionsRequest):
    """
    Get market assumptions for simulations.
    
    Args:
        request: MarketAssumptionsRequest with use_live flag
    
    Returns:
        MarketAssumptions with current market data
    """
    if request.use_live:
        assumptions = market_assumptions.get_live_market_assumptions()
    else:
        assumptions = market_assumptions.get_fallback_market_assumptions()
    
    return MarketAssumptions(
        repo_rate=assumptions["repo_rate"],
        debt_return=assumptions["debt_return"],
        equity_return=assumptions["equity_return"],
        gold_return=assumptions["gold_return"],
        inflation=assumptions["inflation"],
        source=assumptions["source"],
        last_updated=assumptions["last_updated"]
    )

@router.get("/market/assumptions", response_model=MarketAssumptions, tags=["market"])
async def get_market_assumptions_default():
    """
    Get default market assumptions (fallback).
    
    Returns:
        MarketAssumptions with fallback data
    """
    assumptions = market_assumptions.get_fallback_market_assumptions()
    
    return MarketAssumptions(
        repo_rate=assumptions["repo_rate"],
        debt_return=assumptions["debt_return"],
        equity_return=assumptions["equity_return"],
        gold_return=assumptions["gold_return"],
        inflation=assumptions["inflation"],
        source=assumptions["source"],
        last_updated=assumptions["last_updated"]
    )
