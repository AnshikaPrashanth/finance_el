import os

base_dir = r"d:\finance el\backend"

structure = {
    "requirements.txt": """fastapi>=0.104.1
uvicorn>=0.24.0
pydantic>=2.5.2
pydantic-settings>=2.1.0
numpy>=1.26.2""",
    
    "app/__init__.py": "",
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import users, simulation, results

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(simulation.router, prefix=settings.API_V1_STR, tags=["simulation"])
app.include_router(results.router, prefix=settings.API_V1_STR, tags=["results"])

@app.get("/")
def root():
    return {"message": "Welcome to the Personal Financial Digital Twin API"}
""",

    "app/api/__init__.py": "",
    "app/api/routes/__init__.py": "",
    
    "app/api/routes/users.py": """from fastapi import APIRouter, HTTPException
from app.models.schemas import UserProfile, UserCreateResponse
from app.services.storage import create_user

router = APIRouter()

@router.post("/create-user", response_model=UserCreateResponse)
def create_new_user(profile: UserProfile):
    try:
        user_id = create_user(profile)
        return UserCreateResponse(user_id=user_id, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
""",

    "app/api/routes/simulation.py": """from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.schemas import SimulationRequest, UserProfile
from app.services.storage import get_user, save_simulation
from app.services.simulation_engine import run_simulation

router = APIRouter()

class SimulateResponse(BaseModel):
    simulation_id: str
    status: str

@router.post("/simulate", response_model=SimulateResponse)
def simulate(request: SimulationRequest):
    profile = None
    if request.user_id:
        profile = get_user(request.user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
    elif request.profile:
        profile = request.profile
    else:
        raise HTTPException(status_code=400, detail="Must provide user_id or profile")
        
    try:
        result = run_simulation(profile)
        save_simulation(result)
        return SimulateResponse(simulation_id=result.simulation_id, status=result.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
""",

    "app/api/routes/results.py": """from fastapi import APIRouter, HTTPException
from app.models.schemas import SimulationResult
from app.services.storage import get_simulation

router = APIRouter()

@router.get("/results/{simulation_id}", response_model=SimulationResult)
def get_results(simulation_id: str):
    result = get_simulation(simulation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return result
""",

    "app/core/__init__.py": "",
    "app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal Financial Digital Twin"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    class Config:
        case_sensitive = True

settings = Settings()
""",

    "app/models/__init__.py": "",
    "app/models/schemas.py": """from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PersonalInfo(BaseModel):
    name: str
    age: int
    retirement_age: int
    city: str
    marital_status: str
    dependents: int

class IncomeInfo(BaseModel):
    monthly_salary: float = 0
    bonus: float = 0
    side_income: float = 0
    rental_income: float = 0
    other_income: float = 0

class ExpenseInfo(BaseModel):
    living_expenses: float = 0
    emi_payments: float = 0
    insurance: float = 0
    education_expenses: float = 0
    discretionary_spending: float = 0
    other_expenses: float = 0

class AssetInfo(BaseModel):
    savings: float = 0
    emergency_fund: float = 0
    fixed_deposits: float = 0
    stocks: float = 0
    mutual_funds: float = 0
    epf: float = 0
    ppf: float = 0
    nps: float = 0
    gold: float = 0
    real_estate: float = 0
    business_assets: float = 0
    other_assets: float = 0

class LiabilityInfo(BaseModel):
    home_loan: float = 0
    personal_loan: float = 0
    vehicle_loan: float = 0
    education_loan: float = 0
    credit_card_debt: float = 0
    other_liabilities: float = 0

class InvestmentGoals(BaseModel):
    sip_amount: float = 0
    expected_annual_return: float = 10.0
    inflation_rate: float = 6.0
    target_corpus: float = 0
    risk_appetite: str = "moderate"
    asset_allocation: Dict[str, float] = {"equity": 60, "debt": 40}
    investment_horizon: int = 10
    goals: List[str] = []

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

class Metrics(BaseModel):
    net_worth: float
    total_assets: float
    total_liabilities: float
    monthly_surplus: float
    savings_rate: float
    financial_health_score: int
    target_corpus: float
    projected_corpus: float
    success_probability: float
    emergency_fund_months: float

class ProjectionPoint(BaseModel):
    year: int
    value: float

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

class ScenarioPoint(BaseModel):
    name: str
    projected_corpus: float
    success_probability: float
    summary: str

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
    recommendations: List[str]
    explainability: Explainability
""",

    "app/services/__init__.py": "",
    "app/services/storage.py": """import uuid
from typing import Dict
from app.models.schemas import UserProfile, SimulationResult

users_db: Dict[str, UserProfile] = {}
simulations_db: Dict[str, SimulationResult] = {}

def create_user(profile: UserProfile) -> str:
    user_id = str(uuid.uuid4())
    users_db[user_id] = profile
    return user_id

def get_user(user_id: str) -> UserProfile:
    return users_db.get(user_id)

def save_simulation(result: SimulationResult) -> str:
    sim_id = result.simulation_id
    simulations_db[sim_id] = result
    return sim_id

def get_simulation(sim_id: str) -> SimulationResult:
    return simulations_db.get(sim_id)
""",

    "app/services/financial_metrics.py": """from app.models.schemas import UserProfile, Metrics

def calculate_metrics(profile: UserProfile) -> Metrics:
    assets = profile.assets
    liabilities = profile.liabilities
    income = profile.income
    expenses = profile.expenses
    investments = profile.investments

    total_assets = sum([
        assets.savings, assets.emergency_fund, assets.fixed_deposits,
        assets.stocks, assets.mutual_funds, assets.epf, assets.ppf,
        assets.nps, assets.gold, assets.real_estate,
        assets.business_assets, assets.other_assets
    ])

    total_liabilities = sum([
        liabilities.home_loan, liabilities.personal_loan, liabilities.vehicle_loan,
        liabilities.education_loan, liabilities.credit_card_debt, liabilities.other_liabilities
    ])

    net_worth = total_assets - total_liabilities

    monthly_income = sum([
        income.monthly_salary, income.bonus / 12, income.side_income,
        income.rental_income, income.other_income
    ])

    monthly_expenses = sum([
        expenses.living_expenses, expenses.emi_payments, expenses.insurance / 12,
        expenses.education_expenses, expenses.discretionary_spending, expenses.other_expenses
    ])

    monthly_surplus = monthly_income - monthly_expenses
    savings_rate = monthly_surplus / monthly_income if monthly_income > 0 else 0

    emergency_fund_months = assets.emergency_fund / monthly_expenses if monthly_expenses > 0 else 0

    health_score = 50
    if savings_rate > 0.2: health_score += 10
    if savings_rate > 0.3: health_score += 10
    if emergency_fund_months >= 3: health_score += 10
    if emergency_fund_months >= 6: health_score += 10
    if total_assets > total_liabilities * 2: health_score += 10
    
    years_to_retire = profile.personal.retirement_age - profile.personal.age
    r = investments.expected_annual_return / 100
    monthly_r = r / 12
    n = years_to_retire * 12
    
    future_assets = total_assets * ((1 + r) ** years_to_retire)
    sip_future = investments.sip_amount * (((1 + monthly_r) ** n - 1) / monthly_r) * (1 + monthly_r) if monthly_r > 0 else investments.sip_amount * n
    
    projected_corpus = future_assets + sip_future
    target = investments.target_corpus or (monthly_expenses * 12 * 25)
    
    success_prob = min(projected_corpus / target if target > 0 else 1.0, 1.0) * 0.9

    return Metrics(
        net_worth=net_worth,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        monthly_surplus=monthly_surplus,
        savings_rate=savings_rate,
        financial_health_score=min(100, health_score),
        target_corpus=target,
        projected_corpus=projected_corpus,
        success_probability=success_prob,
        emergency_fund_months=emergency_fund_months
    )
""",

    "app/services/monte_carlo.py": """import numpy as np
from typing import List
from app.models.schemas import UserProfile, MonteCarloPoint
import datetime

def run_monte_carlo(profile: UserProfile, years: int = None) -> List[MonteCarloPoint]:
    years = years or (profile.personal.retirement_age - profile.personal.age)
    if years <= 0:
        return []

    initial_portfolio = profile.assets.stocks + profile.assets.mutual_funds + profile.assets.savings + profile.assets.fixed_deposits + profile.assets.epf + profile.assets.ppf + profile.assets.nps
    annual_addition = profile.investments.sip_amount * 12
    
    mean_return = profile.investments.expected_annual_return / 100
    volatility = 0.12

    num_simulations = 1000
    
    results = []
    current_year = datetime.datetime.now().year
    
    for year in range(1, years + 1):
        random_returns = np.random.normal(mean_return, volatility, num_simulations)
        
        if year == 1:
            portfolios = initial_portfolio * (1 + random_returns) + annual_addition
        else:
            portfolios = portfolios * (1 + random_returns) + annual_addition
            
        p5 = float(np.percentile(portfolios, 5))
        p50 = float(np.percentile(portfolios, 50))
        p95 = float(np.percentile(portfolios, 95))
        
        results.append(MonteCarloPoint(
            year=current_year + year,
            p5=p5,
            p50=p50,
            p95=p95
        ))
        
    return results
""",

    "app/services/scenario_engine.py": """from typing import List
from app.models.schemas import UserProfile, ScenarioPoint
from app.services.financial_metrics import calculate_metrics

def generate_scenarios(profile: UserProfile) -> List[ScenarioPoint]:
    scenarios = []
    
    base_metrics = calculate_metrics(profile)
    scenarios.append(ScenarioPoint(
        name="Base",
        projected_corpus=base_metrics.projected_corpus,
        success_probability=base_metrics.success_probability,
        summary="Current plan projection based on existing inputs."
    ))
    
    def clone_profile(p: UserProfile) -> UserProfile:
        return UserProfile.model_validate(p.model_dump())

    p_sip_10 = clone_profile(profile)
    p_sip_10.investments.sip_amount *= 1.10
    m_sip_10 = calculate_metrics(p_sip_10)
    scenarios.append(ScenarioPoint(
        name="SIP +10%",
        projected_corpus=m_sip_10.projected_corpus,
        success_probability=m_sip_10.success_probability,
        summary="Increasing SIP by 10% boosts long-term corpus."
    ))

    p_sip_20 = clone_profile(profile)
    p_sip_20.investments.sip_amount *= 1.20
    m_sip_20 = calculate_metrics(p_sip_20)
    scenarios.append(ScenarioPoint(
        name="SIP +20%",
        projected_corpus=m_sip_20.projected_corpus,
        success_probability=m_sip_20.success_probability,
        summary="Increasing SIP by 20% significantly improves chances."
    ))

    p_exp = clone_profile(profile)
    saved = p_exp.expenses.discretionary_spending * 0.2
    p_exp.expenses.discretionary_spending *= 0.8
    p_exp.investments.sip_amount += saved
    m_exp = calculate_metrics(p_exp)
    scenarios.append(ScenarioPoint(
        name="Reduce expenses",
        projected_corpus=m_exp.projected_corpus,
        success_probability=m_exp.success_probability,
        summary="Cutting discretionary spend by 20% and investing it."
    ))

    p_retire = clone_profile(profile)
    p_retire.personal.retirement_age += 2
    m_retire = calculate_metrics(p_retire)
    scenarios.append(ScenarioPoint(
        name="Retire later",
        projected_corpus=m_retire.projected_corpus,
        success_probability=m_retire.success_probability,
        summary="Working 2 more years allows compound interest more time."
    ))

    scenarios.append(ScenarioPoint(
        name="Emergency-fund-first",
        projected_corpus=base_metrics.projected_corpus * 0.98,
        success_probability=base_metrics.success_probability * 0.95,
        summary="Prioritizes safety but slightly delays market investments."
    ))

    scenarios.append(ScenarioPoint(
        name="Debt-prepayment-first",
        projected_corpus=base_metrics.projected_corpus * 1.05,
        success_probability=min(base_metrics.success_probability * 1.1, 1.0),
        summary="Clearing high-interest debt improves overall net worth trajectory."
    ))

    return scenarios
""",

    "app/services/explainability.py": """from typing import List
from app.models.schemas import UserProfile, Metrics, Explainability

def generate_explainability(profile: UserProfile, metrics: Metrics) -> Explainability:
    if metrics.success_probability < 0.6:
        goal_analysis = "Target corpus is unlikely under current contribution levels. Consider increasing your SIP."
    elif metrics.success_probability < 0.8:
        goal_analysis = "You are on track, but there is some risk. Small increases in savings could secure your target."
    else:
        goal_analysis = "Your current plan looks solid. You have a high probability of reaching your target corpus."

    if metrics.total_liabilities > profile.income.monthly_salary * 12 * 3:
        debt_analysis = "Debt burden is high relative to income. Consider prioritizing high-interest debt prepayment."
    elif profile.expenses.emi_payments > (profile.income.monthly_salary + profile.income.side_income) * 0.4:
        debt_analysis = "EMI payments consume a large portion of your monthly income, reducing investable surplus."
    else:
        debt_analysis = "Your debt levels appear manageable and do not overly constrain your cash flow."

    if metrics.emergency_fund_months < 3:
        liquidity_analysis = "Emergency reserves are critically low. Prioritize building at least 3-6 months of living expenses."
    elif metrics.emergency_fund_months < 6:
        liquidity_analysis = "Emergency fund is adequate but could be stronger. Aim for 6 months for better security."
    else:
        liquidity_analysis = "You have excellent liquidity and a strong emergency buffer."

    return Explainability(
        goal_analysis=goal_analysis,
        debt_analysis=debt_analysis,
        liquidity_analysis=liquidity_analysis
    )

def generate_recommendations(profile: UserProfile, metrics: Metrics) -> List[str]:
    recs = []
    if metrics.success_probability < 0.8:
        recs.append("Increase SIP by 10-20% to improve retirement success probability.")
    if metrics.emergency_fund_months < 6:
        recs.append("Build emergency fund to at least 6 months of expenses.")
    if profile.expenses.emi_payments > profile.income.monthly_salary * 0.4:
        recs.append("Focus on prepaying high-interest debt to free up cash flow.")
    if metrics.savings_rate < 0.2:
        recs.append("Try to reduce discretionary spending to increase your savings rate above 20%.")
    
    if not recs:
        recs.append("Maintain your current financial discipline.")
        
    return recs
""",

    "app/services/simulation_engine.py": """import uuid
import datetime
from app.models.schemas import UserProfile, SimulationResult, ProjectionPoint, CashFlowPoint
from app.services.financial_metrics import calculate_metrics
from app.services.monte_carlo import run_monte_carlo
from app.services.scenario_engine import generate_scenarios
from app.services.explainability import generate_explainability, generate_recommendations

def run_simulation(profile: UserProfile) -> SimulationResult:
    sim_id = str(uuid.uuid4())
    
    metrics = calculate_metrics(profile)
    monte_carlo = run_monte_carlo(profile)
    scenarios = generate_scenarios(profile)
    explainability = generate_explainability(profile, metrics)
    recommendations = generate_recommendations(profile, metrics)
    
    nw_proj = []
    current_year = datetime.datetime.now().year
    current_nw = metrics.net_worth
    annual_savings = metrics.monthly_surplus * 12
    r = profile.investments.expected_annual_return / 100
    
    for i in range(11):
        nw_proj.append(ProjectionPoint(year=current_year + i, value=current_nw))
        current_nw = current_nw * (1 + r) + annual_savings
        
    total_income_annual = sum([profile.income.monthly_salary, profile.income.bonus/12, profile.income.side_income, profile.income.rental_income, profile.income.other_income]) * 12
    total_expenses_annual = sum([profile.expenses.living_expenses, profile.expenses.emi_payments, profile.expenses.insurance/12, profile.expenses.education_expenses, profile.expenses.discretionary_spending, profile.expenses.other_expenses]) * 12
    
    cf = [
        CashFlowPoint(
            period=str(current_year),
            income=total_income_annual,
            expenses=total_expenses_annual,
            surplus=total_income_annual - total_expenses_annual
        )
    ]

    result = SimulationResult(
        simulation_id=sim_id,
        status="completed",
        user_summary={
            "name": profile.personal.name,
            "age": profile.personal.age,
            "retirement_age": profile.personal.retirement_age
        },
        metrics=metrics,
        net_worth_projection=nw_proj,
        cash_flow=cf,
        monte_carlo=monte_carlo,
        scenarios=scenarios,
        recommendations=recommendations,
        explainability=explainability
    )
    
    return result
""",

    "app/utils/__init__.py": "",
    "app/utils/helpers.py": """def format_currency(value: float) -> str:
    return f"₹{value:,.2f}"
"""
}

readme_content = """# Personal Financial Digital Twin - Backend

This is the FastAPI backend for the Personal Financial Digital Twin application. It handles user profiles, financial metrics calculation, Monte Carlo simulations, and scenario generation.

## Setup Instructions

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    - On Windows:
      ```bash
      venv\\Scripts\\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the application locally:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

The backend will run on `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

## API Endpoints

- `POST /api/v1/create-user`: Creates a user profile in memory.
- `POST /api/v1/simulate`: Runs the financial simulation for a user profile.
- `GET /api/v1/results/{simulation_id}`: Retrieves the results of a simulation.

## Sample Request Payload for /api/v1/create-user

```json
{
  "personal": {
    "name": "Sahil",
    "age": 30,
    "retirement_age": 60,
    "city": "Mumbai",
    "marital_status": "Single",
    "dependents": 0
  },
  "income": {
    "monthly_salary": 100000,
    "bonus": 100000,
    "side_income": 0,
    "rental_income": 0,
    "other_income": 0
  },
  "expenses": {
    "living_expenses": 30000,
    "emi_payments": 10000,
    "insurance": 12000,
    "education_expenses": 0,
    "discretionary_spending": 10000,
    "other_expenses": 0
  },
  "assets": {
    "savings": 200000,
    "emergency_fund": 100000,
    "fixed_deposits": 0,
    "stocks": 500000,
    "mutual_funds": 300000,
    "epf": 200000,
    "ppf": 100000,
    "nps": 0,
    "gold": 50000,
    "real_estate": 0,
    "business_assets": 0,
    "other_assets": 0
  },
  "liabilities": {
    "home_loan": 0,
    "personal_loan": 100000,
    "vehicle_loan": 0,
    "education_loan": 0,
    "credit_card_debt": 0,
    "other_liabilities": 0
  },
  "investments": {
    "sip_amount": 20000,
    "expected_annual_return": 12.0,
    "inflation_rate": 6.0,
    "target_corpus": 50000000,
    "risk_appetite": "High",
    "asset_allocation": {
      "equity": 80,
      "debt": 20
    },
    "investment_horizon": 30,
    "goals": ["Retirement", "House"]
  }
}
```
"""

structure["README.md"] = readme_content

for path, content in structure.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Backend generation complete.")
