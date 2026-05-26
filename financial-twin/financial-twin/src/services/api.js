import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";
const POLL_INTERVAL_MS = 2000;
const POLL_MAX_ATTEMPTS = 15;

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// Centralized error normalizer
function normalizeError(err) {
  if (err.response) {
    const msg =
      err.response.data?.detail ||
      err.response.data?.message ||
      `Server error (${err.response.status})`;
    return new Error(msg);
  }
  if (err.request) {
    return new Error(
      "Cannot reach the server. Make sure the backend is running at " + BASE_URL
    );
  }
  return err;
}

/**
 * Create a user profile on the backend.
 * @param {Object} personalDetails - name, age, city, marital_status, dependents
 * @returns {Promise<{ user_id: string }>}
 */
export async function createUser(personalDetails) {
  try {
    const { data } = await client.post("/api/v1/create-user", personalDetails);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

/**
 * Submit simulation payload.
 * @param {Object} payload - full financial payload including user_id
 * @returns {Promise<{ simulation_id: string, status: string }>}
 */
export async function runSimulation(payload) {
  try {
    const { data } = await client.post("/api/v1/simulate", payload);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

/**
 * Fetch simulation results by ID.
 * @param {string} simulationId
 * @returns {Promise<Object>} - full results object
 */
export async function getSimulationResults(simulationId) {
  try {
    const { data } = await client.get(`/api/v1/results/${simulationId}`);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

/**
 * Poll until results are ready (status === "complete") or max attempts reached.
 * @param {string} simulationId
 * @param {Function} onProgress - called with attempt count
 * @returns {Promise<Object>}
 */
export async function pollUntilComplete(simulationId, onProgress) {
  for (let attempt = 1; attempt <= POLL_MAX_ATTEMPTS; attempt++) {
    if (onProgress) onProgress(attempt);
    const data = await getSimulationResults(simulationId);
    if (data.status === "completed" || !data.status) {
      return data;
    }
    if (data.status === "failed") {
      throw new Error("Simulation failed on the server. Please try again.");
    }
    await new Promise((res) => setTimeout(res, POLL_INTERVAL_MS));
  }
  throw new Error("Simulation timed out. Please check your backend or retry.");
}

/**
 * Full orchestrated flow: createUser → simulate → poll results
 * @param {Object} formData - complete form values
 * @param {Function} onStepChange - callback(stepName: string)
 * @returns {Promise<Object>} - final results
 */
export async function runFullSimulation(formData, onStepChange) {
  // Step 1: Create user
  onStepChange("Creating your profile…");
  const userProfile = buildUserProfile(formData);
  const { user_id } = await createUser(userProfile);

  // Step 2: Run simulation
  onStepChange("Running financial simulation…");
  const { simulation_id } = await runSimulation({ user_id });

  // Step 3: Poll for results
  onStepChange("Processing results…");
  const results = await pollUntilComplete(simulation_id, (attempt) => {
    onStepChange(`Processing results… (attempt ${attempt})`);
  });

  return results;
}

export async function runTwinAnalysis(formData, existingUserId, onStepChange) {
  onStepChange("Saving your financial twin...");
  const profile = buildUserProfile(formData);
  const payload = existingUserId ? { user_id: existingUserId, profile } : { profile };
  try {
    const { data } = await client.post("/api/v1/twin/run", payload);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

export async function getLatestTwin(userId) {
  try {
    const { data } = await client.get(`/api/v1/twin/${userId}/latest`);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

export async function getFinancialHistory(userId) {
  try {
    const { data } = await client.get(`/api/v1/twin/${userId}/history`);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

export async function postTransaction(userId, transaction) {
  try {
    const { data } = await client.post(`/api/v1/twin/${userId}/transaction`, transaction);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

export async function getTransactions(userId) {
  try {
    const { data } = await client.get(`/api/v1/twin/${userId}/transactions`);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

export async function getLatestTwinState(userId) {
  try {
    const { data } = await client.get(`/api/v1/twin/${userId}/latest-state`);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

export async function simulateLiveEvent(userId) {
  try {
    const { data } = await client.post(`/api/v1/twin/${userId}/simulate-live-event`);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

/** Build the complete UserProfile request body from form data to match backend schema */
function buildUserProfile(formData) {
  const { personal, income, expenses, assets, liabilities, preferences } = formData;
  return {
    personal: {
      name: personal.fullName || "User",
      age: num(personal.age),
      retirement_age: num(personal.retirementAge) || 60,
      city: personal.city || "Unknown",
      marital_status: personal.maritalStatus || "Single",
      dependents: num(personal.dependents),
    },
    income: {
      monthly_salary: num(income.salary),
      bonus: num(income.bonus),
      side_income: num(income.sideIncome),
      rental_income: num(income.rentalIncome),
      other_income: num(income.otherIncome),
    },
    expenses: {
      living_expenses: num(expenses.living),
      emi_payments: num(expenses.emi),
      insurance: num(expenses.insurance),
      education_expenses: num(expenses.education),
      discretionary_spending: num(expenses.discretionary),
      other_expenses: num(expenses.other),
    },
    assets: {
      savings: num(assets.savings),
      emergency_fund: num(assets.emergencyFund),
      fixed_deposits: num(assets.fd),
      stocks: num(assets.stocks),
      mutual_funds: num(assets.mutualFunds),
      epf: num(assets.epfPpf),
      ppf: 0,
      nps: 0,
      gold: num(assets.gold),
      real_estate: num(assets.realEstate),
      business_assets: num(assets.business),
      other_assets: num(assets.otherAssets),
    },
    liabilities: {
      home_loan: num(liabilities.homeLoan),
      personal_loan: num(liabilities.personalLoan),
      vehicle_loan: num(liabilities.vehicleLoan),
      education_loan: num(liabilities.educationLoan),
      credit_card_debt: num(liabilities.creditCard),
      other_liabilities: num(liabilities.otherLiabilities),
    },
    investments: {
      sip_amount: num(preferences.sipAmount),
      expected_annual_return: num(preferences.expectedReturn) || 12.0,
      inflation_rate: num(preferences.inflation) || 6.0,
      target_corpus: num(preferences.targetCorpus),
      risk_appetite: preferences.riskAppetite || "Moderate",
      asset_allocation: {
        equity: preferences.equityPct !== "" && preferences.equityPct !== undefined ? num(preferences.equityPct) : 60,
        debt: preferences.debtPct !== "" && preferences.debtPct !== undefined ? num(preferences.debtPct) : 30,
        gold: preferences.goldPct !== "" && preferences.goldPct !== undefined ? num(preferences.goldPct) : 10,
      },
      investment_horizon: num(preferences.investmentHorizon) || Math.max(1, num(personal.retirementAge) - num(personal.age)),
      goals: preferences.goalType ? [preferences.goalType] : [],
    },
  };
}

const num = (v) => Number(v) || 0;

/**
 * Upload a file for data synchronization.
 * @param {File} file - CSV or Excel file
 * @returns {Promise<Object>} - sync response with detected data
 */
export async function uploadDataFile(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', file.name.endsWith('.csv') ? 'csv' : 'excel');

    const { data } = await client.post("/api/v1/sync/upload", formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

/**
 * Sync financial data from SMS messages.
 * @param {Array<string>} messages - SMS message strings
 * @returns {Promise<Object>} - sync response with detected data
 */
export async function syncSmsData(messages) {
  try {
    const { data } = await client.post("/api/v1/sync/sms", messages);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

/**
 * Get market assumptions.
 * @param {boolean} useLive - whether to use live market data
 * @returns {Promise<Object>} - market assumptions
 */
export async function getMarketAssumptions(useLive = false) {
  try {
    const { data } = await client.post("/api/v1/market/assumptions", { 
      use_live: useLive 
    });
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

/**
 * Get default market assumptions (fallback).
 * @returns {Promise<Object>} - market assumptions
 */
export async function getDefaultMarketAssumptions() {
  try {
    const { data } = await client.get("/api/v1/market/assumptions");
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}
