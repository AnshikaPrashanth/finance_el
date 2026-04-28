# Personal Financial Digital Twin

A production-ready fintech dashboard for personal financial planning, simulation, and PDF report generation.

---

## Project Structure

```
src/
├── components/
│   ├── InputForm.jsx          # Multi-step financial input form
│   ├── Dashboard.jsx          # Main results dashboard
│   ├── MonteCarloChart.jsx    # Monte Carlo simulation chart (P5/P50/P95)
│   ├── CashFlowChart.jsx      # Income vs Expenses timeline
│   ├── ScenarioComparison.jsx # Strategy comparison bar chart
│   ├── MetricsCards.jsx       # KPI summary cards
│   ├── LoadingSpinner.jsx     # Animated loader
│   ├── ErrorState.jsx         # Error display with retry
│   └── ReportDownload.jsx     # PDF download button + logic
├── pages/
│   └── Home.jsx               # Main page orchestrator
├── services/
│   └── api.js                 # All API calls (createUser, simulate, getResults)
├── utils/
│   ├── formatters.js          # Currency, %, number formatters
│   ├── validators.js          # Form validation helpers
│   └── transformResults.js    # Backend → chart data transformers
├── App.js
└── index.js
```

---

## Completed Features

- ✅ Multi-step input form with all personal/income/expense/asset/liability fields
- ✅ Form validation (required, numeric, allocation must = 100%)
- ✅ API service layer (createUser → simulate → getResults with polling)
- ✅ Dashboard with KPI cards (net worth, health score, savings rate, etc.)
- ✅ Net Worth / Wealth Projection line chart
- ✅ Cash Flow chart (income vs expenses)
- ✅ Monte Carlo simulation chart (percentile bands)
- ✅ Scenario Comparison chart
- ✅ Insights / Recommendations section
- ✅ PDF report download (html2canvas + jsPDF)
- ✅ Loading states, error states, retry logic
- ✅ Local form persistence (localStorage)
- ✅ Reset form
- ✅ Responsive layout

---

## Pending / Future Improvements

- Backend-driven PDF with proper chart images (requires canvas serialization)
- Authentication / multi-user support
- Comparison of saved simulations
- Dark mode toggle
- Export to CSV

---

## How to Run

```bash
# 1. Install dependencies
npm install

# 2. Copy env file
cp .env.example .env

# 3. Start dev server
npm start
```

Ensure your FastAPI backend is running at `http://localhost:8000`.

---

## API Contract

### POST /api/v1/create-user
**Request:**
```json
{
  "name": "string",
  "age": 30,
  "city": "string",
  "marital_status": "single|married",
  "dependents": 0
}
```
**Response:**
```json
{ "user_id": "uuid-string" }
```

### POST /api/v1/simulate
**Request:**
```json
{
  "user_id": "uuid",
  "income": { "salary": 100000, "bonus": 0, "side": 0, "rental": 0, "other": 0 },
  "expenses": { "living": 40000, "emi": 0, "insurance": 0, "education": 0, "discretionary": 0, "other": 0 },
  "assets": { "savings": 500000, "emergency_fund": 200000, "fd": 0, "stocks": 0, "mutual_funds": 0, "epf_ppf": 0, "gold": 0, "real_estate": 0, "business": 0, "other": 0 },
  "liabilities": { "home_loan": 0, "personal_loan": 0, "credit_card": 0, "vehicle_loan": 0, "education_loan": 0, "other": 0 },
  "preferences": {
    "sip_amount": 10000,
    "expected_return": 12,
    "inflation": 6,
    "risk_appetite": "moderate",
    "investment_horizon": 20,
    "target_corpus": 10000000,
    "goal_type": "retirement",
    "retirement_age": 60,
    "equity_pct": 60,
    "debt_pct": 30,
    "gold_pct": 10
  }
}
```
**Response:**
```json
{ "simulation_id": "uuid-string", "status": "processing|complete" }
```

### GET /api/v1/results/{simulation_id}
**Response (assumed schema):**
```json
{
  "status": "complete",
  "metrics": {
    "net_worth": 1500000,
    "total_assets": 2000000,
    "total_liabilities": 500000,
    "savings_rate": 35.5,
    "financial_health_score": 72,
    "goal_success_probability": 68,
    "projected_corpus": 25000000,
    "emergency_fund_months": 5,
    "monthly_surplus": 15000
  },
  "projections": [
    { "year": 2024, "net_worth": 1500000, "corpus": 1500000 },
    ...
  ],
  "cash_flow": [
    { "month": "Jan 2024", "income": 100000, "expenses": 60000, "surplus": 40000 },
    ...
  ],
  "monte_carlo": {
    "p5": [...],
    "p50": [...],
    "p95": [...],
    "years": [2024, 2025, ...]
  },
  "scenarios": [
    { "name": "Current Plan", "corpus": 25000000, "success_prob": 68 },
    { "name": "SIP +10%", "corpus": 28000000, "success_prob": 75 },
    ...
  ],
  "recommendations": [
    "Increase SIP by ₹2,000/month to stay on retirement track.",
    "Emergency fund covers only 5 months; target 6+.",
    ...
  ]
}
```

> **NOTE**: If your backend returns a different schema, update `src/utils/transformResults.js` — all data normalization happens there.

---

## PDF Generation

Uses `jspdf` + `html2canvas`. The `ReportDownload` component:
1. Captures the `#report-content` div with html2canvas
2. Splits into A4 pages
3. Saves as `financial-report.pdf`

To improve chart quality in PDF, set `scale: 2` in html2canvas options.

---

## Assumptions

- Backend returns `simulation_id` immediately; results may be polled up to 30s
- All monetary values are in INR (₹)
- `financial_health_score` is 0–100
- Monte Carlo returns arrays indexed by year
- If backend doesn't return `scenarios`, `ScenarioComparison` renders empty state
