from app.models.schemas import UserProfile

def get_tax_version() -> str:
    return "India_FY25_Estimator"

def calculate_estimated_taxes(income: float, mode: str = "current") -> float:
    """
    Calculates estimated tax drag based on mode.
    Modes: 'current', 'past', 'future_optimistic', 'future_conservative'
    """
    if mode == "future_conservative":
        return income * 0.25 if income > 1500000 else income * 0.15
        
    if mode == "future_optimistic":
        return income * 0.10 if income > 1500000 else income * 0.05

    # Default to current India New Tax Regime estimation
    if income <= 700000:
        return 0 
        
    tax = 0
    if income > 300000:
        tax += min(300000, income - 300000) * 0.05
    if income > 600000:
        tax += min(300000, income - 600000) * 0.10
    if income > 900000:
        tax += min(300000, income - 900000) * 0.15
    if income > 1200000:
        tax += min(300000, income - 1200000) * 0.20
    if income > 1500000:
        tax += (income - 1500000) * 0.30
        
    return tax

def calculate_capital_gains_tax_drag(wealth: float, realized_gains_pct: float = 0.1) -> float:
    """Placeholder hook for capital gains."""
    # Assuming 10% LTCG on realized portion
    return wealth * realized_gains_pct * 0.10
