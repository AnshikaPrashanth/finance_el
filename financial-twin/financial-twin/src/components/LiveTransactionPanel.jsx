import React, { useState, useEffect } from "react";
import {
  Play,
  Plus,
  TrendingUp,
  Shield,
  Target,
  Wallet,
  AlertTriangle,
  CheckCircle,
  Activity,
  Info,
  RefreshCw,
  ArrowDownLeft,
  ArrowUpRight,
  ChevronRight,
  Layers
} from "lucide-react";
import {
  postTransaction,
  getLatestTwinState,
  simulateLiveEvent
} from "../services/api";
import {
  formatCurrency,
  formatPercent,
  formatHealthScore,
  formatMonths,
  formatScore,
  formatActionLabel,
} from "../utils/formatters";

export default function LiveTransactionPanel({ userId, onTwinUpdate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState("drift"); // "drift" | "manual" | "recent"
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Manual Transaction form state
  const [txType, setTxType] = useState("expense");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [isRecurring, setIsRecurring] = useState(false);
  
  // Metadata fields
  const [updateBaseline, setUpdateBaseline] = useState(false);
  const [debtType, setDebtType] = useState("credit_card_debt");
  const [loanClosed, setLoanClosed] = useState(false);
  const [emiReduction, setEmiReduction] = useState("");
  const [assetType, setAssetType] = useState("savings");
  const [assetUpdateMode, setAssetUpdateMode] = useState("new_value"); // "new_value" | "delta"
  const [assetDelta, setAssetDelta] = useState("");
  const [assetNewValue, setAssetNewValue] = useState("");

  const loadLatestState = async (showLoading = true) => {
    if (showLoading) setLoading(true);
    setError(null);
    try {
      const res = await getLatestTwinState(userId);
      setData(res);
      if (res.simulation_result && onTwinUpdate) {
        onTwinUpdate(res.simulation_result);
      }
    } catch (err) {
      setError(err.message || "Failed to load digital twin state.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      loadLatestState(true);
    }
  }, [userId]);

  const handleSimulate = async () => {
    setSubmitting(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const res = await simulateLiveEvent(userId);
      setData(res);
      setSuccessMsg(`Simulated event: "${res.transaction.description}" for ${formatCurrency(res.transaction.amount)}`);
      if (res.simulation_result && onTwinUpdate) {
        onTwinUpdate(res.simulation_result);
      }
    } catch (err) {
      setError(err.message || "Failed to run simulation event.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    if (!description || !amount) {
      setError("Please fill in description and amount.");
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccessMsg(null);

    // Prepare metadata
    const metadata = {};
    if (txType === "income" || txType === "expense" || txType === "investment") {
      metadata.update_baseline = updateBaseline;
    }
    if (txType === "investment") {
      metadata.asset_type = assetType;
    }
    if (txType === "debt_payment") {
      metadata.debt_type = debtType;
      metadata.loan_closed = loanClosed;
      if (emiReduction) {
        metadata.emi_reduction = Number(emiReduction);
      }
    }
    if (txType === "asset_update") {
      metadata.asset_type = assetType;
      if (assetUpdateMode === "new_value" && assetNewValue) {
        metadata.new_value = Number(assetNewValue);
      } else if (assetUpdateMode === "delta" && assetDelta) {
        metadata.delta = Number(assetDelta);
      }
    }

    const payload = {
      description,
      amount: Number(amount),
      category: category || (txType.charAt(0).toUpperCase() + txType.slice(1)),
      transaction_type: txType,
      source: "manual",
      is_recurring: isRecurring,
      metadata: Object.keys(metadata).length > 0 ? metadata : null
    };

    try {
      const res = await postTransaction(userId, payload);
      setData(res);
      setSuccessMsg(`Transaction applied: "${res.transaction.description}"`);
      
      // Reset form
      setDescription("");
      setAmount("");
      setCategory("");
      setIsRecurring(false);
      setUpdateBaseline(false);
      setEmiReduction("");
      setAssetDelta("");
      setAssetNewValue("");

      if (res.simulation_result && onTwinUpdate) {
        onTwinUpdate(res.simulation_result);
      }
    } catch (err) {
      setError(err.message || "Failed to apply transaction.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <RefreshCw className="w-8 h-8 text-brand-400 animate-spin" />
        <p className="text-slate-400 font-body text-sm">Loading live digital twin state...</p>
      </div>
    );
  }

  const metrics = data?.updated_metrics;
  const recentTxs = data?.recent_transactions || [];
  const driftReport = data?.drift_report;
  const alerts = data?.alerts || [];

  return (
    <div className="space-y-6">
      {/* Live Metrics Header Grid */}
      {metrics && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm">
            <div className="flex items-start justify-between mb-2">
              <span className="text-slate-400 font-body text-xs uppercase tracking-wider">Live Net Worth</span>
              <Wallet className="w-4 h-4 text-brand-400" />
            </div>
            <div className="font-display text-2xl font-semibold text-brand-300">
              {formatCurrency(metrics.netWorth || metrics.net_worth)}
            </div>
            <p className="text-slate-500 font-body text-xs mt-1">Real-time assets minus liabilities</p>
          </div>

          <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm">
            <div className="flex items-start justify-between mb-2">
              <span className="text-slate-400 font-body text-xs uppercase tracking-wider">Goal Success</span>
              <Target className="w-4 h-4 text-violet-400" />
            </div>
            <div className="font-display text-2xl font-semibold text-violet-400">
              {formatPercent(metrics.goalSuccessProbability || metrics.success_probability, 1, true)}
            </div>
            <p className="text-slate-500 font-body text-xs mt-1">Monte Carlo success probability</p>
          </div>

          <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm">
            <div className="flex items-start justify-between mb-2">
              <span className="text-slate-400 font-body text-xs uppercase tracking-wider">Health Score</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="font-display text-2xl font-semibold text-emerald-400">
              {formatScore(metrics.healthScore || metrics.financial_health_score)}
            </div>
            <p className="text-slate-500 font-body text-xs mt-1">
              {formatHealthScore(metrics.healthScore || metrics.financial_health_score).label}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm">
            <div className="flex items-start justify-between mb-2">
              <span className="text-slate-400 font-body text-xs uppercase tracking-wider">Emergency Buffer</span>
              <Shield className="w-4 h-4 text-amber-400" />
            </div>
            <div className="font-display text-2xl font-semibold text-amber-400">
              {formatMonths(metrics.emergencyFundMonths || metrics.emergency_fund_months)}
            </div>
            <p className="text-slate-500 font-body text-xs mt-1">Months of essential expenses</p>
          </div>
        </div>
      )}

      {/* Main Panel Content */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Side: Simulation Controls & Navigation */}
        <div className="lg:col-span-5 space-y-6">
          <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-6 backdrop-blur-sm space-y-4">
            <div>
              <h3 className="text-slate-100 font-display text-lg">Digital Twin Events</h3>
              <p className="text-slate-400 font-body text-xs mt-1">
                Simulate real-time events or log manual transactions to see how your financial twin evolves.
              </p>
            </div>

            {/* Quick Simulator Button */}
            <button
              onClick={handleSimulate}
              disabled={submitting}
              className="w-full relative py-4 px-6 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold flex items-center justify-center gap-2 shadow-lg hover:shadow-indigo-500/20 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Processing Event...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current animate-pulse" />
                  <span>Simulate Live Event</span>
                </>
              )}
            </button>

            {/* Sub-tab navigation */}
            <div className="grid grid-cols-3 gap-1 p-1 bg-slate-950 rounded-xl border border-slate-800">
              <button
                onClick={() => setActiveSubTab("drift")}
                className={`py-2 px-3 text-xs font-medium rounded-lg transition-colors ${
                  activeSubTab === "drift"
                    ? "bg-slate-800 text-slate-100"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Drift Report
              </button>
              <button
                onClick={() => setActiveSubTab("manual")}
                className={`py-2 px-3 text-xs font-medium rounded-lg transition-colors ${
                  activeSubTab === "manual"
                    ? "bg-slate-800 text-slate-100"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Log Transaction
              </button>
              <button
                onClick={() => setActiveSubTab("recent")}
                className={`py-2 px-3 text-xs font-medium rounded-lg transition-colors ${
                  activeSubTab === "recent"
                    ? "bg-slate-800 text-slate-100"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Recent
              </button>
            </div>

            {/* Messages */}
            {error && (
              <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-400 text-xs flex gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            {successMsg && (
              <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 text-xs flex gap-2">
                <CheckCircle className="w-4 h-4 shrink-0" />
                <span>{successMsg}</span>
              </div>
            )}
          </div>

          {/* Form tab Content */}
          {activeSubTab === "manual" && (
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-6 backdrop-blur-sm">
              <h4 className="text-slate-100 font-display text-base mb-4">Log Manual Transaction</h4>
              <form onSubmit={handleManualSubmit} className="space-y-4">
                {/* Transaction Type */}
                <div>
                  <label className="block text-slate-400 text-xs font-medium mb-1.5">Type</label>
                  <select
                    value={txType}
                    onChange={(e) => setTxType(e.target.value)}
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-brand-500"
                  >
                    <option value="expense">Expense (Outflow)</option>
                    <option value="income">Income (Inflow)</option>
                    <option value="investment">Investment (Asset Allocation)</option>
                    <option value="debt_payment">Debt Payment (Liabilities Reduction)</option>
                    <option value="emergency">Emergency (Drawdown)</option>
                    <option value="asset_update">Asset Revaluation</option>
                  </select>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-slate-400 text-xs font-medium mb-1.5">Description</label>
                  <input
                    type="text"
                    required
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="e.g. Swiggy Food Delivery, Salary, CC Payment"
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-brand-500 placeholder-slate-600"
                  />
                </div>

                {/* Amount & Category */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-slate-400 text-xs font-medium mb-1.5">Amount (₹)</label>
                    <input
                      type="number"
                      required
                      min="1"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder="Amount"
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-brand-500 placeholder-slate-600"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 text-xs font-medium mb-1.5">Category</label>
                    <input
                      type="text"
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      placeholder="e.g. Living, Food, EMI"
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-brand-500 placeholder-slate-600"
                    />
                  </div>
                </div>

                {/* Recurring switch */}
                {txType !== "asset_update" && (
                  <div className="flex items-center justify-between p-3 bg-slate-950 rounded-xl border border-slate-800">
                    <div>
                      <span className="block text-slate-200 text-xs font-medium">Recurring Monthly</span>
                      <span className="block text-slate-500 text-[10px]">Happens automatically every month</span>
                    </div>
                    <input
                      type="checkbox"
                      checked={isRecurring}
                      onChange={(e) => setIsRecurring(e.target.checked)}
                      className="w-4 h-4 rounded border-slate-800 text-brand-600 focus:ring-brand-500 bg-slate-950"
                    />
                  </div>
                )}

                {/* Conditional Metadata: Income / Investment / Expense (update baseline) */}
                {isRecurring && (txType === "income" || txType === "investment") && (
                  <div className="flex items-center justify-between p-3 bg-indigo-950/20 border border-indigo-900/40 rounded-xl">
                    <div>
                      <span className="block text-indigo-300 text-xs font-medium">Update Plan Baseline</span>
                      <span className="block text-slate-500 text-[10px]">Recalculate budget baseline in profile</span>
                    </div>
                    <input
                      type="checkbox"
                      checked={updateBaseline}
                      onChange={(e) => setUpdateBaseline(e.target.checked)}
                      className="w-4 h-4 rounded border-indigo-800 text-indigo-600 focus:ring-indigo-500 bg-slate-950"
                    />
                  </div>
                )}

                {/* Conditional Metadata: Debt Payment */}
                {txType === "debt_payment" && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                    <div>
                      <label className="block text-slate-400 text-[11px] font-medium mb-1">Target Debt Type</label>
                      <select
                        value={debtType}
                        onChange={(e) => setDebtType(e.target.value)}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1.5 text-slate-200 text-xs focus:outline-none"
                      >
                        <option value="credit_card_debt">Credit Card Debt (High Interest)</option>
                        <option value="personal_loan">Personal Loan (High Interest)</option>
                        <option value="vehicle_loan">Vehicle Loan</option>
                        <option value="education_loan">Education Loan</option>
                        <option value="home_loan">Home Loan</option>
                        <option value="other_liabilities">Other Liabilities</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between py-1 border-t border-slate-800/60 pt-2">
                      <div>
                        <span className="block text-slate-200 text-[11px] font-medium">Loan Fully Closed?</span>
                        <span className="block text-slate-500 text-[9px]">Will recalculate/reduce EMI payments</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={loanClosed}
                        onChange={(e) => setLoanClosed(e.target.checked)}
                        className="w-4 h-4 rounded border-slate-800 text-brand-600 focus:ring-brand-500 bg-slate-950"
                      />
                    </div>

                    {loanClosed && (
                      <div>
                        <label className="block text-slate-400 text-[11px] font-medium mb-1">Explicit EMI Saved (₹)</label>
                        <input
                          type="number"
                          value={emiReduction}
                          onChange={(e) => setEmiReduction(e.target.value)}
                          placeholder="Optional: Freed EMI"
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1.5 text-slate-200 text-xs focus:outline-none"
                        />
                      </div>
                    )}
                  </div>
                )}

                {/* Conditional Metadata: Asset Update */}
                {txType === "asset_update" && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                    <div>
                      <label className="block text-slate-400 text-[11px] font-medium mb-1">Target Asset</label>
                      <select
                        value={assetType}
                        onChange={(e) => setAssetType(e.target.value)}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1.5 text-slate-200 text-xs focus:outline-none"
                      >
                        <option value="savings">Savings Cash</option>
                        <option value="emergency_fund">Emergency Fund</option>
                        <option value="fixed_deposits">Fixed Deposits</option>
                        <option value="stocks">Stocks</option>
                        <option value="mutual_funds">Mutual Funds</option>
                        <option value="gold">Gold</option>
                        <option value="real_estate">Real Estate</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-slate-400 text-[11px] font-medium mb-1">Update Mode</label>
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          type="button"
                          onClick={() => setAssetUpdateMode("new_value")}
                          className={`py-1 px-2 text-[10px] font-medium rounded border ${
                            assetUpdateMode === "new_value"
                              ? "bg-brand-600/20 border-brand-500/50 text-slate-200"
                              : "border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          Absolute New Value
                        </button>
                        <button
                          type="button"
                          onClick={() => setAssetUpdateMode("delta")}
                          className={`py-1 px-2 text-[10px] font-medium rounded border ${
                            assetUpdateMode === "delta"
                              ? "bg-brand-600/20 border-brand-500/50 text-slate-200"
                              : "border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          Delta (+/-)
                        </button>
                      </div>
                    </div>

                    {assetUpdateMode === "new_value" ? (
                      <div>
                        <label className="block text-slate-400 text-[11px] font-medium mb-1">Absolute Value (₹)</label>
                        <input
                          type="number"
                          value={assetNewValue}
                          onChange={(e) => setAssetNewValue(e.target.value)}
                          placeholder="e.g. 500000"
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1.5 text-slate-200 text-xs focus:outline-none"
                        />
                      </div>
                    ) : (
                      <div>
                        <label className="block text-slate-400 text-[11px] font-medium mb-1">Delta Amount (+/- ₹)</label>
                        <input
                          type="number"
                          value={assetDelta}
                          onChange={(e) => setAssetDelta(e.target.value)}
                          placeholder="e.g. -20000 or 50000"
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1.5 text-slate-200 text-xs focus:outline-none"
                        />
                      </div>
                    )}
                  </div>
                )}

                {/* Submit button */}
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50 text-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>Log Transaction</span>
                </button>
              </form>
            </div>
          )}
        </div>

        {/* Right Side: Drift report / Alerts / Recent transactions list */}
        <div className="lg:col-span-7 space-y-6">
          {/* Active Alerts */}
          {alerts.length > 0 && (
            <div className="rounded-2xl bg-amber-950/20 border border-amber-800/40 p-6 backdrop-blur-sm">
              <h4 className="text-amber-400 font-display text-sm font-semibold flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4" />
                <span>Live Digital Twin Alerts</span>
              </h4>
              <div className="space-y-2">
                {alerts.map((alert, i) => (
                  <div key={i} className="flex gap-2.5 p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                    <Info className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                    <p className="text-slate-300 font-body text-xs leading-relaxed">{alert}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab Selection panels */}
          {activeSubTab === "drift" && (
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-6 backdrop-blur-sm space-y-5">
              <div>
                <h3 className="text-slate-100 font-display text-base">Plan vs Actual Drift Analysis</h3>
                <p className="text-slate-500 font-body text-xs mt-0.5">
                  Compares your initial twin plan metrics against actual transactions.
                </p>
              </div>

              {driftReport?.items?.length > 0 ? (
                <div className="space-y-4">
                  {driftReport.items.map((item, idx) => {
                    const isCost =
                      item.metric.includes("Expense") ||
                      item.metric.includes("EMI") ||
                      item.metric.includes("Category");
                    const varianceSign = item.variance > 0 ? "+" : "";
                    
                    // Colors based on status
                    let statusColor = "text-emerald-400 bg-emerald-950/40 border-emerald-800/40";
                    let barColor = "bg-emerald-500";
                    if (item.status === "warning") {
                      statusColor = "text-amber-400 bg-amber-950/40 border-amber-800/40";
                      barColor = "bg-amber-500";
                    } else if (item.status === "critical") {
                      statusColor = "text-rose-400 bg-rose-950/40 border-rose-800/40";
                      barColor = "bg-rose-500";
                    }

                    // Progress bar ratio
                    let ratio = 0;
                    if (item.planned > 0) {
                      ratio = Math.min((item.actual / item.planned) * 100, 100);
                    } else if (item.actual > 0) {
                      ratio = 100;
                    }

                    const isMonths = item.metric.includes("Months") || item.metric.includes("Coverage");

                    return (
                      <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="text-slate-200 text-xs font-semibold block">{item.metric}</span>
                            <span className="text-slate-500 text-[10px] block mt-0.5">{item.description}</span>
                          </div>
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${statusColor}`}>
                            {item.status.replace("_", " ").toUpperCase()}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 py-1 border-t border-b border-slate-800/60">
                          <div>
                            <span className="text-[10px] text-slate-500 block">Planned</span>
                            <span className="text-xs font-semibold text-slate-300 block">
                              {isMonths ? formatMonths(item.planned) : formatCurrency(item.planned, true)}
                            </span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 block">Actual</span>
                            <span className="text-xs font-semibold text-slate-300 block">
                              {isMonths ? formatMonths(item.actual) : formatCurrency(item.actual, true)}
                            </span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 block">Variance</span>
                            <span className={`text-xs font-semibold block ${item.variance > 0 ? (isCost ? "text-rose-400" : "text-emerald-400") : (isCost ? "text-emerald-400" : "text-rose-400")}`}>
                              {varianceSign}
                              {isMonths ? formatMonths(item.variance) : formatCurrency(item.variance, true)}
                            </span>
                          </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${barColor}`}
                            style={{ width: `${ratio}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-600 text-xs">No drift metrics available. Run a live transaction simulation.</div>
              )}
            </div>
          )}

          {activeSubTab === "recent" && (
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-6 backdrop-blur-sm space-y-4">
              <h3 className="text-slate-100 font-display text-base">Recent Transactions</h3>
              {recentTxs.length > 0 ? (
                <div className="flow-root">
                  <ul className="-mb-8">
                    {recentTxs.map((tx, idx) => {
                      const date = new Date(tx.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + " " + new Date(tx.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' });
                      const isInflow = tx.transaction_type === "income";
                      const Icon = isInflow ? ArrowDownLeft : ArrowUpRight;
                      
                      return (
                        <li key={tx.id || idx}>
                          <div className="relative pb-8">
                            {idx !== recentTxs.length - 1 && (
                              <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-slate-800" aria-hidden="true" />
                            )}
                            <div className="relative flex space-x-3">
                              <div>
                                <span className={`h-8 w-8 rounded-lg flex items-center justify-center ring-4 ring-slate-900 ${isInflow ? "bg-emerald-950/80 text-emerald-400" : "bg-slate-800 text-slate-300"}`}>
                                  <Icon className="w-4 h-4" />
                                </span>
                              </div>
                              <div className="flex-1 min-w-0 pt-0.5 flex justify-between gap-4">
                                <div>
                                  <p className="text-xs text-slate-200 font-semibold">{tx.description}</p>
                                  <p className="text-[10px] text-slate-500 mt-0.5">
                                    {tx.category} • <span>{formatActionLabel(tx.transaction_type)}</span>
                                    {tx.is_recurring && " • Recurring"}
                                  </p>
                                </div>
                                <div className="text-right whitespace-nowrap">
                                  <span className={`text-xs font-bold block ${isInflow ? "text-emerald-400" : "text-slate-200"}`}>
                                    {isInflow ? "+" : "-"} {formatCurrency(tx.amount)}
                                  </span>
                                  <span className="text-[9px] text-slate-600 block mt-0.5">{date}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : (
                <div className="text-center py-8 text-slate-600 text-xs">No transactions logged yet.</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
