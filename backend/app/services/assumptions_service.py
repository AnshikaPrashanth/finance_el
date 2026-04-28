import math
from typing import Dict, Tuple
from app.models.schemas import UserProfile
from app.services import market_assumptions

ASSET_CLASS_ASSUMPTIONS = {
    "equity": {"return": 0.115, "volatility": 0.15},
    "debt": {"return": 0.065, "volatility": 0.04},
    "liquid": {"return": 0.035, "volatility": 0.01},
    "gold": {"return": 0.08, "volatility": 0.10},
}

def get_inflation_assumption(profile: UserProfile) -> float:
    return profile.investments.inflation_rate / 100.0

def get_income_growth_assumption() -> float:
    return 0.07 # 7% nominal income growth

def get_market_adjusted_assumptions(use_live: bool = False) -> Dict[str, float]:
    """
    Get market-adjusted assumptions from market_assumptions service.
    
    Args:
        use_live: Whether to use live market data
    
    Returns:
        Dictionary with market assumptions
    """
    if use_live:
        return market_assumptions.get_live_market_assumptions()
    else:
        return market_assumptions.get_fallback_market_assumptions()

def calculate_portfolio_metrics(allocation: Dict[str, float], market_data: Dict[str, float] = None) -> Tuple[float, float]:
    """
    Returns (expected_return, volatility) based on weighted sum.
    allocation is a dict with percentages, e.g., {'equity': 60, 'debt': 40}
    
    Args:
        allocation: Asset allocation percentages
        market_data: Optional market assumptions data
    """
    total_weight = sum(allocation.values())
    if total_weight == 0:
        return 0.0, 0.0

    # Use market data if provided, otherwise use defaults
    if market_data:
        ASSET_CLASS_ASSUMPTIONS["equity"]["return"] = market_data.get("equity_return", 0.115) / 100.0
        ASSET_CLASS_ASSUMPTIONS["debt"]["return"] = market_data.get("debt_return", 0.065) / 100.0
        ASSET_CLASS_ASSUMPTIONS["gold"]["return"] = market_data.get("gold_return", 0.08) / 100.0

    exp_return = 0.0
    var_sum = 0.0
    
    for asset, weight_pct in allocation.items():
        w = weight_pct / 100.0
        assumptions = ASSET_CLASS_ASSUMPTIONS.get(asset, {"return": 0.06, "volatility": 0.05})
        r = assumptions["return"]
        vol = assumptions["volatility"]
        
        exp_return += w * r
        # simplified volatility formula assuming zero correlation for placeholder
        var_sum += (w**2) * (vol**2)
        
    return exp_return, math.sqrt(var_sum)
