from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Optional, Dict, Any

class PersonalInfo(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)
    retirement_age: int = Field(ge=0, le=120)
    city: str
    marital_status: str
    dependents: int = Field(ge=0)

    @model_validator(mode='after')
    def check_retirement_age(self):
        if self.retirement_age < self.age:
            raise ValueError("Retirement age cannot be less than current age")
        return self

class IncomeInfo(BaseModel):
    monthly_salary: float = Field(default=0, ge=0)
    bonus: float = Field(default=0, ge=0)
    side_income: float = Field(default=0, ge=0)
    rental_income: float = Field(default=0, ge=0)
    other_income: float = Field(default=0, ge=0)

class ExpenseInfo(BaseModel):
    living_expenses: float = Field(default=0, ge=0)
    emi_payments: float = Field(default=0, ge=0)
    insurance: float = Field(default=0, ge=0)
    education_expenses: float = Field(default=0, ge=0)
    discretionary_spending: float = Field(default=0, ge=0)
    other_expenses: float = Field(default=0, ge=0)

    @property
    def essential_expenses(self) -> float:
        return self.living_expenses + self.emi_payments + self.insurance + self.education_expenses

    @property
    def discretionary_expenses(self) -> float:
        return self.discretionary_spending + self.other_expenses

class AssetInfo(BaseModel):
    savings: float = Field(default=0, ge=0)
    emergency_fund: float = Field(default=0, ge=0)
    fixed_deposits: float = Field(default=0, ge=0)
    stocks: float = Field(default=0, ge=0)
    mutual_funds: float = Field(default=0, ge=0)
    epf: float = Field(default=0, ge=0)
    ppf: float = Field(default=0, ge=0)
    nps: float = Field(default=0, ge=0)
    gold: float = Field(default=0, ge=0)
    real_estate: float = Field(default=0, ge=0)
    business_assets: float = Field(default=0, ge=0)
    other_assets: float = Field(default=0, ge=0)

class LiabilityInfo(BaseModel):
    home_loan: float = Field(default=0, ge=0)
    personal_loan: float = Field(default=0, ge=0) # Unsecured / high interest
    vehicle_loan: float = Field(default=0, ge=0)
    education_loan: float = Field(default=0, ge=0)
    credit_card_debt: float = Field(default=0, ge=0) # Unsecured / high interest
    other_liabilities: float = Field(default=0, ge=0)

    @property
    def high_interest_debt(self) -> float:
        return self.personal_loan + self.credit_card_debt

class InvestmentGoals(BaseModel):
    sip_amount: float = Field(default=0, ge=0)
    expected_annual_return: float = Field(default=11.0, ge=-100, le=100)
    inflation_rate: float = Field(default=5.5, ge=-10, le=50)
    target_corpus: float = Field(default=0, ge=0)
    risk_appetite: str = "moderate"
    asset_allocation: Dict[str, float] = {"equity": 60, "debt": 40}
    investment_horizon: int = Field(default=10, ge=1, le=100)
    goals: List[str] = []

    @field_validator("asset_allocation")
    @classmethod
    def check_allocation_sum(cls, v):
        total = sum(v.values())
        if total == 0:
            return {"equity": 60, "debt": 40}
        if not (99.0 <= total <= 101.0): # allow slight float precision issues
            raise ValueError(f"Asset allocation must sum to 100, got {total}")
        return v

class UserProfile(BaseModel):
    personal: PersonalInfo
    income: IncomeInfo
    expenses: ExpenseInfo
    assets: AssetInfo
    liabilities: LiabilityInfo
    investments: InvestmentGoals

class UserCreateResponse(BaseModel):
    user_id: str
    status: str

class SimulationRequest(BaseModel):
    user_id: Optional[str] = None
    profile: Optional[UserProfile] = None

class AssumptionVersions(BaseModel):
    tax_version: str
    market_version: str
    inflation_assumption: float
    income_growth_assumption: float

class Metrics(BaseModel):
    net_worth: float
    total_assets: float
    total_liabilities: float
    monthly_surplus: float
    savings_rate: float
    financial_health_score: float
    target_corpus: float
    projected_corpus: float # nominal
    projected_real_corpus: float
    success_probability: float # nominal
    success_probability_nominal: float
    success_probability_real: float
    shortfall_probability: float
    corpus_adequacy_ratio: float
    emergency_fund_months: float
    debt_to_income_ratio: float
    expense_ratio: float
    portfolio_expected_return: float
    portfolio_volatility: float
    inflation_assumption: float
    income_growth_assumption: float

class ProjectionPoint(BaseModel):
    year: int
    value: float
    real_value: float = 0

class CashFlowPoint(BaseModel):
    period: str
    income: float
    expenses: float
    surplus: float

class MonteCarloPoint(BaseModel):
    year: int
    p5: float
    p50: float
    p95: float
    p5_real: float = 0
    p50_real: float = 0
    p95_real: float = 0

class ScenarioPoint(BaseModel):
    name: str
    projected_corpus: float
    projected_real_corpus: float = 0
    success_probability: float
    corpus_adequacy_ratio: float = 0
    change_vs_base: float = 0
    summary: str
    changed_inputs: Dict[str, Any] = {}
    path: List[ProjectionPoint] = []

class Explainability(BaseModel):
    goal_analysis: str
    debt_analysis: str
    liquidity_analysis: str

class SimulationResult(BaseModel):
    simulation_id: str
    status: str
    user_summary: Dict[str, Any]
    metrics: Metrics
    net_worth_projection: List[ProjectionPoint]
    cash_flow: List[CashFlowPoint]
    monte_carlo: List[MonteCarloPoint]
    scenarios: List[ScenarioPoint]
    recommendations: List[Dict[str, Any]]
    explainability: Explainability
    assumptions: AssumptionVersions
    debug_info: Optional[Dict[str, Any]] = None

# Data Sync Related Schemas
class SyncDetected(BaseModel):
    """Parsed/detected financial data from sync source"""
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    monthly_sip: float = 0.0
    emi: float = 0.0
    rent: float = 0.0
    living_expenses: float = 0.0
    surplus: float = 0.0

class PrefillPayload(BaseModel):
    """Auto-prefill data for user profile form"""
    income: Dict[str, Any] = {}
    expenses: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}

class DataSyncResponse(BaseModel):
    """Response from data sync operation"""
    sync_id: str
    source: str  # 'csv', 'sms', 'excel'
    last_synced: str
    detected: SyncDetected
    prefill_payload: PrefillPayload
    summary: List[str]

class MarketAssumptions(BaseModel):
    """Market assumptions for simulations"""
    repo_rate: float
    debt_return: float
    equity_return: float
    gold_return: float
    inflation: float
    source: str  # 'live' or 'fallback'
    last_updated: str

class MarketAssumptionsRequest(BaseModel):
    """Request for market assumptions"""
    use_live: bool = False

class TransactionData(BaseModel):
    """Single transaction data point"""
    date: str
    amount: float
    category: str
    description: str
    type: str  # 'income', 'expense', 'investment', 'transfer'

class RecommendationItem(BaseModel):
    """Recommendation with explanation"""
    title: str
    description: str
    impact: str  # 'high', 'medium', 'low'
    category: str  # 'debt', 'emergency_fund', 'investment', 'taxes', 'liquidity'
    action: str
