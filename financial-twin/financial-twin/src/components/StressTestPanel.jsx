import React from "react";
import { ShieldAlert } from "lucide-react";
import { formatCurrency, formatMonths, formatPercent, formatScore, formatActionLabel } from "../utils/formatters";

function SeverityBadge({ severity }) {
  const tone =
    severity === "high"
      ? "bg-rose-950/60 text-rose-300 border-rose-800/60"
      : "bg-amber-950/60 text-amber-300 border-amber-800/60";
  return (
    <span className={`px-2 py-1 rounded-full border text-xs uppercase tracking-wide ${tone}`}>
      {severity}
    </span>
  );
}

export default function StressTestPanel({ stressTest }) {
  if (!stressTest) return null;

  return (
    <div className="space-y-4">
      <div className="grid md:grid-cols-4 gap-3">
        <SummaryTile
          label="Resilience Score"
          value={formatScore(stressTest.summary?.resilience_score || 0)}
        />
        <SummaryTile
          label="Risk Level"
          value={stressTest.summary?.overall_risk_level || "N/A"}
        />
        <SummaryTile
          label="Worst Case"
          value={stressTest.summary?.worst_case_scenario || "N/A"}
        />
        <SummaryTile
          label="Worst Probability Drop"
          value={formatPercent(Math.abs(stressTest.summary?.worst_case_rsp_drop || 0), 1, true)}
        />
      </div>

      <div className="grid xl:grid-cols-2 gap-4">
        {(stressTest.scenarios || []).map((scenario) => (
          <div key={scenario.scenario_id} className="rounded-xl border border-slate-700/40 bg-slate-800/40 p-4">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <h4 className="text-slate-100 font-semibold">{scenario.label}</h4>
                <p className="text-slate-400 text-sm mt-1">{scenario.narrative}</p>
              </div>
              <SeverityBadge severity={scenario.severity} />
            </div>

            <div className="grid sm:grid-cols-2 gap-3 text-sm">
              <Metric label="Net Worth Change" value={formatCurrency(scenario.impact?.net_worth_change)} />
              <Metric label="Emergency Fund After" value={formatMonths(scenario.impact?.emergency_fund_months_after)} />
              <Metric label="Success Probability" value={formatPercent(scenario.impact?.real_success_probability_after || 0, 1, true)} />
              <Metric label="Resilience After" value={formatScore(scenario.impact?.resilience_score_after || 0)} />
            </div>

            <div className="mt-4 rounded-xl bg-slate-900/60 border border-slate-700/40 p-3">
              <div className="flex items-center gap-2 text-slate-200 text-sm font-medium">
                <ShieldAlert className="w-4 h-4 text-brand-300" />
                Recommended response: {formatActionLabel(scenario.recommended_recovery_action)}
              </div>
              <p className="text-slate-400 text-sm mt-1">{scenario.recovery_rationale}</p>
            </div>

            {scenario.ranked_recovery_actions?.length > 0 && (
              <div className="mt-3 space-y-2">
                {scenario.ranked_recovery_actions.map((action) => (
                  <div key={action.rank + action.action} className="flex items-start justify-between gap-3 rounded-lg bg-slate-900/40 px-3 py-2">
                    <div>
                      <p className="text-slate-200 text-sm font-medium">
                        {action.rank}. {formatActionLabel(action.action)}
                      </p>
                      <p className="text-slate-500 text-xs mt-0.5">{action.rationale}</p>
                    </div>
                    <span className="text-brand-300 text-xs font-semibold">
                      {action.composite_score}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function SummaryTile({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-700/40 bg-slate-800/40 p-4">
      <p className="text-slate-500 text-xs uppercase tracking-wide">{label}</p>
      <p className="text-slate-100 font-semibold mt-2">{value}</p>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-900/40 px-3 py-2">
      <p className="text-slate-500 text-xs uppercase tracking-wide">{label}</p>
      <p className="text-slate-100 mt-1">{value}</p>
    </div>
  );
}
