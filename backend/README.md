# Personal Financial Digital Twin - Backend

This is the FastAPI backend for the academically rigorous Personal Financial Digital Twin application. It handles user profiles, complex financial metrics calculation, stochastic Monte Carlo simulations, and deterministic scenario generation.

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
      venv\Scripts\activate
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

## Financial Model and Assumptions

This engine employs several robust academic formulas to provide highly realistic long-term planning trajectories rather than simple geometric compounding:

- **Net Worth**: `TotalAssets - TotalLiabilities`
- **Future Value of SIP**: `SIP * [((1 + i)^n - 1) / i] * (1 + i)` where `i` is the monthly expected return and `n` is months.
- **Real Returns & Inflation Drag**: The nominal projected corpus is discounted back to present value using the formula `real_corpus = nominal_corpus / (1 + inflation_rate)^years` to understand true purchasing power.
- **Portfolio Math**: Expected portfolio return and volatility are computed via a weighted sum of underlying asset class assumptions (`w_i * r_i`), avoiding flat arbitrary estimates.
- **Retirement Target Estimation**: If a user does not provide a target corpus, it is automatically computed using the "25x Rule" based on their essential expenses (`essential_expenses * 12 * 25`).

## Tax Handling Strategy

The system features a decoupled `tax_engine.py` that can operate in multiple modes:
- **Current Tax Mode**: Evaluates income against current active tax slabs (e.g., India New Tax Regime FY25 estimator).
- **Future Tax Mode**: Since future tax law is unknown, future simulations apply a simplified conservative or optimistic drag percentage, treating future taxes as assumptions rather than absolute truth.

## Real-time Data Strategy

Live market data integration is handled via `market_data_service.py`.
- To avoid faking precision, live spot prices are **not** used to project 30-year returns.
- Live data is intended for calibrating current benchmarks, while long-term simulations rely on configured actuarial/economic assumptions managed in `assumptions_service.py`.
- Every simulation payload tracks assumption versions (e.g., `market_version`, `tax_version`) to guarantee reproducibility.

## Nominal vs Real Outputs

The system strictly differentiates between:
- **Nominal Corpus**: The raw face value of wealth in the future.
- **Real Corpus**: The inflation-adjusted purchasing power of that wealth today.
Success probabilities and goal evaluations prioritize the **Real Corpus** to prevent "money illusion" (believing a large future nominal number is adequate when inflation has eroded its value).

## Monte Carlo Methodology

The stochastic simulation engine abandons simplistic terminal-wealth multipliers for a **step-by-step Markov-style projection**:
- Uses **1000 trials** sampling returns via a log-normal/normal distribution: `sampled_return_t ~ Normal(mean_portfolio_return, portfolio_volatility^2)`.
- Tracks both **real and nominal paths** independently inside the loop.
- Outputs `p5`, `p50`, and `p95` percentile paths, as well as a strict `shortfall_probability` metric.

## Limitations and Production Roadmap

- **Covariance**: Currently, portfolio volatility assumes zero correlation across asset classes for simplicity. Adding a full covariance matrix is slated for v2.
- **Tax Precision**: The current tax engine is an estimator, not compliance-grade accounting software. It ignores complex surcharges and cesses.
- **Dynamic Rebalancing**: The simulation assumes a constant asset allocation and does not currently model dynamic glide paths (e.g., moving from 80% equity to 40% equity near retirement).

## Synthetic Evaluation Tool

For academic analysis or mass-testing, use the included evaluation script:
```bash
python scripts/generate_synthetic_eval.py
```
This will generate 20 randomized synthetic user profiles, process them through the simulation engine, and output a CSV (`evaluation_results.csv`) comparing the efficacy of the "Base" scenario versus dynamically improved scenarios.
