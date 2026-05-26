# Personal Financial Digital Twin - Backend

This repository contains the FastAPI backend for the Personal Financial Digital Twin application. It supports:
- user profile storage,
- financial simulation and Monte Carlo projections,
- scenario results retrieval,
- data sync from CSV/Excel upload and SMS payloads,
- market assumption lookup.

## Backend Structure

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

## Setup

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

## Run the Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
OpenAPI docs are available at `http://localhost:8000/api/v1/openapi.json` and Swagger UI at `http://localhost:8000/docs`.

## API Endpoints

### General
- `GET /` — basic health check/welcome message

### User Management
- `POST /api/v1/create-user` — create and persist a user profile

### Simulation
- `POST /api/v1/simulate` — run a financial simulation
  - Accepts either `user_id` or full `profile`
  - Returns `simulation_id` and `status`
- `GET /api/v1/results/{simulation_id}` — fetch completed simulation results

### Sync / Data Import
- `POST /api/v1/sync/upload` — upload CSV/Excel financial data
- `POST /api/v1/sync/sms` — sync financial data from SMS payloads
- `GET /api/v1/sync/status/{sync_id}` — fetch sync status

### Market Assumptions
- `GET /api/v1/market/assumptions` — fallback/default assumptions
- `POST /api/v1/market/assumptions` — request live or fallback assumptions

## Testing

A simple connectivity test is available at the repository root:

```bash
python test_api.py
```

This script submits a sample simulation payload to `http://localhost:8000/api/v1/simulate` and prints the response.

## Notes

- The backend uses CORS middleware to allow requests from the frontend.
- The service layer is split across `app/services` for simulation, storage, parsing, and market assumptions.
- `app/models/schemas.py` defines input/output validation for the API.
- `scripts/generate_synthetic_eval.py` generates synthetic profiles and evaluates the simulation engine for batch testing.
