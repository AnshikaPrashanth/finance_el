# Personal Financial Digital Twin

A fintech dashboard for personal financial planning, simulation, and PDF report generation.

## Repository Contents

- `backend/`: FastAPI backend services, simulation logic, and storage
- `financial-twin/financial-twin/`: React frontend application
- `screenshots/`: Screenshot documentation and image assets

---

## Backend Overview

This repository contains the FastAPI backend for the Personal Financial Digital Twin application. It supports:

- user profile storage
- financial simulation and Monte Carlo projections
- scenario results retrieval
- data sync from CSV/Excel upload and SMS payloads
- market assumption lookup

### Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── market.py
│   │   │   ├── results.py
│   │   │   ├── simulation.py
│   │   │   ├── sync.py
│   │   │   └── users.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── assumptions_service.py
│   │   ├── digital_twin_sync.py
│   │   ├── excel_parser.py
│   │   ├── explainability.py
│   │   ├── financial_metrics.py
│   │   ├── market_assumptions.py
│   │   ├── market_data_service.py
│   │   ├── monte_carlo.py
│   │   ├── scenario_engine.py
│   │   ├── simulation_engine.py
│   │   ├── sms_parser.py
│   │   ├── storage.py
│   │   ├── tax_engine.py
│   │   └── transaction_parser.py
│   └── utils/
│       └── helpers.py
├── scripts/
│   └── generate_synthetic_eval.py
├── requirements.txt
└── test_api.py
```

### Backend Setup

1. Open a terminal in the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate it:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Run the Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
OpenAPI docs are available at `http://localhost:8000/api/v1/openapi.json` and Swagger UI at `http://localhost:8000/docs`.

### API Endpoints

#### General
- `GET /` — basic health check/welcome message

#### User Management
- `POST /api/v1/create-user` — create and persist a user profile

#### Simulation
- `POST /api/v1/simulate` — run a financial simulation
  - Accepts either `user_id` or full `profile`
  - Returns `simulation_id` and `status`
- `GET /api/v1/results/{simulation_id}` — fetch completed simulation results

#### Sync / Data Import
- `POST /api/v1/sync/upload` — upload CSV/Excel financial data
- `POST /api/v1/sync/sms` — sync financial data from SMS payloads
- `GET /api/v1/sync/status/{sync_id}` — fetch sync status

#### Market Assumptions
- `GET /api/v1/market/assumptions` — fallback/default assumptions
- `POST /api/v1/market/assumptions` — request live or fallback assumptions

### Testing

A simple connectivity test is available at the repository root:

```bash
python test_api.py
```

This script submits a sample simulation payload to `http://localhost:8000/api/v1/simulate` and prints the response.

### Backend Notes

- The backend uses CORS middleware to allow frontend requests.
- The service layer is split across `app/services` for simulation, storage, parsing, and market assumptions.
- `app/models/schemas.py` defines input/output validation for the API.
- `scripts/generate_synthetic_eval.py` generates synthetic profiles and evaluates the simulation engine for batch testing.

---

## Frontend Overview

A fintech dashboard for personal financial planning, simulation, and PDF report generation.

### Frontend Structure

```
financial-twin/financial-twin/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── CashFlowChart.jsx
│   │   ├── Dashboard.jsx
│   │   ├── DataSyncPanel.jsx
│   │   ├── ErrorState.jsx
│   │   ├── InputForm.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── MetricsCards.jsx
│   │   ├── MonteCarloChart.jsx
│   │   ├── ReportDownload.jsx
│   │   └── ScenarioComparison.jsx
│   ├── pages/
│   │   └── Home.jsx
│   ├── services/
│   │   └── api.js
│   ├── utils/
│   │   ├── formatters.js
│   │   ├── transformResults.js
│   │   └── validators.js
│   ├── App.js
│   └── index.js
├── package.json
├── postcss.config.js
├── tailwind.config.js
└── README.md
```

### Completed Features

- ✅ Multi-step financial input form with personal, income, expense, asset, liability, and preference fields
- ✅ Form validation and allocation checks
- ✅ Frontend service layer for `createUser`, `simulate`, and `getResults`
- ✅ Dashboard summary cards and financial metrics
- ✅ Wealth projection and Monte Carlo percentile charts
- ✅ Cash flow timeline
- ✅ Scenario comparison chart
- ✅ PDF report generation using `jspdf` + `html2canvas`
- ✅ Loading and error states with retry support
- ✅ Local form persistence
- ✅ Responsive UI

### How to Run

From `financial-twin/financial-twin`:

```bash
npm install
npm start
```

Open the app in your browser at `http://localhost:3000`.

> Optionally set `REACT_APP_API_BASE_URL` in a `.env` file to point to a different backend host.

Ensure the FastAPI backend is running at `http://localhost:8000` or the URL configured in `REACT_APP_API_BASE_URL`.

### Frontend API Contract

The frontend uses these backend endpoints:

- `POST /api/v1/create-user` — create a new user profile
- `POST /api/v1/simulate` — submit a simulation request
- `GET /api/v1/results/{simulation_id}` — fetch simulation results
- `POST /api/v1/sync/upload` — upload CSV/Excel financial data
- `POST /api/v1/sync/sms` — sync SMS-derived financial data
- `GET /api/v1/sync/status/{sync_id}` — query sync status
- `GET /api/v1/market/assumptions` — retrieve default market assumptions
- `POST /api/v1/market/assumptions` — request market assumptions with `use_live`

### Simulation Flow

The UI follows this sequence:
1. `createUser(personalDetails)`
2. `runSimulation({ user_id })`
3. `pollUntilComplete(simulation_id)`

### Payload Shape

The frontend builds a payload with:

- `personal`
- `income`
- `expenses`
- `assets`
- `liabilities`
- `investments`

These values are normalized in `src/services/api.js` before sending to the backend.

### Frontend Notes

- `src/utils/transformResults.js` converts backend response payloads into chart-friendly data.
- `src/services/api.js` centralizes backend communication and retry behavior.
- Charts and results components depend on the backend response shape, so update the backend contract if the schema changes.
- The app uses Tailwind classes in `src` and requires standard Create React App tooling from `package.json`.

---

## Screenshots

The full screenshot gallery is available in `screenshots/README.md`.

## Notes

- Runtime logs and environment files are intentionally excluded from commits.
- Use `backend/README.md` and `financial-twin/financial-twin/README.md` for subsystem-specific setup details.
