import React from "react";
import { Clock3 } from "lucide-react";
import { formatCurrency, formatMonthYear, formatPercent } from "../utils/formatters";

export default function HistoryPanel({ history }) {
  if (!history?.length) return null;

  const items = [...history].slice(-5).reverse();

  return (
    <div className="space-y-3">
      {items.map((entry, index) => (
        <div key={entry.recordId || index} className="rounded-xl border border-slate-700/40 bg-slate-800/40 p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Clock3 className="w-4 h-4 text-brand-300" />
              <p className="text-slate-100 font-medium">
                {entry.timestamp ? formatMonthYear(entry.timestamp) : "Recent snapshot"}
              </p>
            </div>
            <span className="text-slate-500 text-xs">{entry.simulationId}</span>
          </div>
          <div className="grid sm:grid-cols-3 gap-3 mt-3">
            <HistoryMetric label="Net Worth" value={formatCurrency(entry.metrics?.net_worth)} />
            <HistoryMetric label="Corpus" value={formatCurrency(entry.metrics?.projected_corpus)} />
            <HistoryMetric label="Success" value={formatPercent(entry.metrics?.success_probability_real || 0, 1, true)} />
          </div>
        </div>
      ))}
    </div>
  );
}

function HistoryMetric({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-900/40 px-3 py-2">
      <p className="text-slate-500 text-xs uppercase tracking-wide">{label}</p>
      <p className="text-slate-100 mt-1">{value}</p>
    </div>
  );
}
