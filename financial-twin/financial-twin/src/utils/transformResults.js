/**
 * transformResults.js
 *
 * Normalize the backend response into chart-ready data structures.
 * If your backend uses a different schema, update the mapping here ONLY.
 * The rest of the app consumes the normalized shape.
 */

/**
 * Normalize raw API results into the shape the UI expects.
 * @param {Object} raw - raw API response
 * @returns {Object} - normalized results
 */
export function transformResults(raw) {
  if (!raw) return null;

  return {
    metrics: transformMetrics(raw.metrics || raw),
    projections: transformProjections(raw.net_worth_projection || raw.projections || []),
    cashFlow: transformCashFlow(raw.cash_flow || raw.cashFlow || []),
    monteCarlo: transformMonteCarlo(raw.monte_carlo || raw.monteCarlo || {}),
    scenarios: transformScenarios(raw.scenarios || []),
    recommendations: raw.recommendations || [],
  };
}

function transformMetrics(m) {
  return {
    netWorth: m.net_worth ?? m.netWorth ?? 0,
    totalAssets: m.total_assets ?? m.totalAssets ?? 0,
    totalLiabilities: m.total_liabilities ?? m.totalLiabilities ?? 0,
    savingsRate: m.savings_rate ?? m.savingsRate ?? 0,
    healthScore: m.financial_health_score ?? m.healthScore ?? 0,
    goalSuccessProbability: m.success_probability ?? m.goal_success_probability ?? m.goalSuccessProbability ?? 0,
    projectedCorpus: m.projected_corpus ?? m.projectedCorpus ?? 0,
    emergencyFundMonths: m.emergency_fund_months ?? m.emergencyFundMonths ?? 0,
    monthlySurplus: m.monthly_surplus ?? m.monthlySurplus ?? 0,
    
    // Missing fields
    targetCorpus: m.target_corpus ?? m.targetCorpus ?? 0,
    projectedRealCorpus: m.projected_real_corpus ?? m.projectedRealCorpus ?? 0,
    successProbabilityNominal: m.success_probability_nominal ?? m.successProbabilityNominal ?? 0,
    successProbabilityReal: m.success_probability_real ?? m.successProbabilityReal ?? 0,
    corpusAdequacyRatio: m.corpus_adequacy_ratio ?? m.corpusAdequacyRatio ?? 0,
    inflationAssumption: m.inflation_assumption ?? m.inflationAssumption ?? 0,
    incomeGrowthAssumption: m.income_growth_assumption ?? m.incomeGrowthAssumption ?? 0,
    portfolioExpectedReturn: m.portfolio_expected_return ?? m.portfolioExpectedReturn ?? 0,
    portfolioVolatility: m.portfolio_volatility ?? m.portfolioVolatility ?? 0,
  };
}

function transformProjections(arr) {
  // Expected: [{ year, net_worth, corpus }]
  return arr.map((d) => ({
    year: d.year,
    netWorth: d.net_worth ?? d.netWorth ?? d.value ?? 0,
    corpus: d.corpus ?? d.value ?? 0,
  }));
}

function transformCashFlow(arr) {
  // Expected: [{ month, income, expenses, surplus }]
  return arr.map((d) => ({
    label: d.month ?? d.label ?? d.period ?? "",
    income: d.income ?? 0,
    expenses: d.expenses ?? 0,
    surplus: d.surplus ?? (d.income - d.expenses) ?? 0,
  }));
}

function transformMonteCarlo(mc) {
  if (Array.isArray(mc)) {
    return mc.map((d) => ({
      year: d.year,
      p5: d.p5 ?? 0,
      p50: d.p50 ?? 0,
      p95: d.p95 ?? 0,
    }));
  }

  // Expected: { years: [], p5: [], p50: [], p95: [] }
  const years = mc.years ?? [];
  const p5 = mc.p5 ?? mc.low ?? [];
  const p50 = mc.p50 ?? mc.median ?? mc.base ?? [];
  const p95 = mc.p95 ?? mc.high ?? [];

  if (!years.length && p50.length) {
    // Build year array if missing
    const currentYear = new Date().getFullYear();
    return p50.map((v, i) => ({
      year: currentYear + i,
      p5: p5[i] ?? 0,
      p50: v ?? 0,
      p95: p95[i] ?? 0,
    }));
  }

  return years.map((y, i) => ({
    year: y,
    p5: p5[i] ?? 0,
    p50: p50[i] ?? 0,
    p95: p95[i] ?? 0,
  }));
}

function transformScenarios(arr) {
  // Expected: [{ name, corpus, success_prob }]
  return arr.map((s) => ({
    name: s.name ?? s.scenario ?? "Scenario",
    corpus: s.corpus ?? s.projected_corpus ?? 0,
    realCorpus: s.projected_real_corpus ?? s.projectedRealCorpus ?? 0,
    successProb: s.success_probability ?? s.success_prob ?? s.successProb ?? s.probability ?? 0,
    changeVsBase: s.change_vs_base ?? s.changeVsBase ?? 0,
  }));
}

/**
 * Generate fallback scenario data from metrics when backend doesn't return scenarios.
 * Uses simple heuristic extrapolation — clearly labelled as estimated.
 */
export function generateFallbackScenarios(metrics, preferences) {
  const base = metrics.projectedCorpus || 0;
  const baseProb = metrics.goalSuccessProbability || 50;
  const sip = Number(preferences?.sipAmount) || 0;

  return [
    { name: "Current Plan", corpus: base, successProb: baseProb },
    {
      name: "SIP +10%",
      corpus: Math.round(base * 1.08),
      successProb: Math.min(baseProb + 6, 98),
    },
    {
      name: "SIP +20%",
      corpus: Math.round(base * 1.17),
      successProb: Math.min(baseProb + 12, 98),
    },
    {
      name: "Retire 5yr Later",
      corpus: Math.round(base * 1.35),
      successProb: Math.min(baseProb + 18, 98),
    },
    {
      name: "Reduce Expenses 10%",
      corpus: Math.round(base * 1.1),
      successProb: Math.min(baseProb + 8, 98),
    },
    {
      name: "Aggressive (80% Eq)",
      corpus: Math.round(base * 1.15),
      successProb: Math.min(baseProb + 10, 98),
    },
  ];
}
