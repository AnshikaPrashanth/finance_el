# Personal Financial Digital Twin

A fintech dashboard for personal financial planning, simulation, and PDF report generation.

---

## Project Structure

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

---

## Completed Features

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

---

## How to Run

From `financial-twin/financial-twin`:

```bash
npm install
npm start
```

Open the app in your browser at `http://localhost:3000`.

> Optionally set `REACT_APP_API_BASE_URL` in a `.env` file to point to a different backend host.

Ensure the FastAPI backend is running at `http://localhost:8000` or the URL configured in `REACT_APP_API_BASE_URL`.

---

## API Contract

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

### Payload shape

The frontend builds a payload with:
- `personal`
- `income`
- `expenses`
- `assets`
- `liabilities`
- `investments`

These values are normalized in `src/services/api.js` before sending to the backend.

---

## Notes

- `src/utils/transformResults.js` converts backend response payloads into chart-friendly data.
- `src/services/api.js` centralizes backend communication and retry behavior.
- Charts and results components depend on the backend response shape, so update the backend contract if the schema changes.
- The app uses Tailwind classes in `src` and requires standard Create React App tooling from `package.json`.
