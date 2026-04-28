import React from "react";
import {
  TrendingUp, Shield, Target, Wallet,
  AlertCircle, CheckCircle, Activity, DollarSign,
} from "lucide-react";
import { formatCurrency, formatPercent, formatHealthScore } from "../utils/formatters";

const CARD_CONFIG = [
  {
    key: "netWorth",
    label: "Net Worth",
    icon: Wallet,
    format: (v) => formatCurrency(v, true),
    colorClass: "text-brand-400",
    bgClass: "bg-brand-900/30 border-brand-700/40",
    hint: "Total assets minus liabilities",
  },
  {
    key: "totalAssets",
    label: "Total Assets",
    icon: TrendingUp,
    format: (v) => formatCurrency(v, true),
    colorClass: "text-emerald-400",
    bgClass: "bg-emerald-900/20 border-emerald-700/30",
    hint: null,
  },
  {
    key: "totalLiabilities",
    label: "Total Liabilities",
    icon: AlertCircle,
    format: (v) => formatCurrency(v, true),
    colorClass: "text-rose-400",
    bgClass: "bg-rose-900/20 border-rose-700/30",
    hint: null,
  },
  {
    key: "savingsRate",
    label: "Savings Rate",
    icon: Activity,
    format: (v) => formatPercent(v),
    colorClass: "text-sky-400",
    bgClass: "bg-sky-900/20 border-sky-700/30",
    hint: "% of income saved monthly",
  },
  {
    key: "goalSuccessProbability",
    label: "Goal Success",
    icon: Target,
    format: (v) => formatPercent(v),
    colorClass: "text-violet-400",
    bgClass: "bg-violet-900/20 border-violet-700/30",
    hint: "Probability of reaching target corpus",
  },
  {
    key: "projectedCorpus",
    label: "Projected Corpus",
    icon: DollarSign,
    format: (v) => formatCurrency(v, true),
    colorClass: "text-amber-400",
    bgClass: "bg-amber-900/20 border-amber-700/30",
    hint: "At end of investment horizon",
  },
  {
    key: "emergencyFundMonths",
    label: "Emergency Fund",
    icon: Shield,
    format: (v) => `${v} months`,
    colorClass: (v) => (v >= 6 ? "text-emerald-400" : "text-amber-400"),
    bgClass: "bg-slate-800/60 border-slate-700/40",
    hint: "Recommended: 6+ months",
  },
  {
    key: "monthlySurplus",
    label: "Monthly Surplus",
    icon: CheckCircle,
    format: (v) => formatCurrency(v, true),
    colorClass: (v) => (v >= 0 ? "text-emerald-400" : "text-rose-400"),
    bgClass: "bg-slate-800/60 border-slate-700/40",
    hint: "Income minus all expenses",
  },
];

export default function MetricsCards({ metrics }) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {CARD_CONFIG.map(({ key, label, icon: Icon, format, colorClass, bgClass, hint }) => {
        const value = metrics?.[key];
        const color =
          typeof colorClass === "function" ? colorClass(value) : colorClass;

        return (
          <div
            key={key}
            className={`rounded-2xl border p-5 transition-transform hover:-translate-y-0.5 ${bgClass}`}
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-slate-400 font-body text-xs uppercase tracking-wider">
                {label}
              </span>
              <div className="w-8 h-8 rounded-lg bg-slate-700/50 flex items-center justify-center shrink-0">
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
            </div>

            <div className={`font-display text-2xl font-semibold ${color} mb-1`}>
              {value !== undefined && value !== null ? format(value) : "—"}
            </div>

            {hint && (
              <p className="text-slate-500 font-body text-xs">{hint}</p>
            )}
          </div>
        );
      })}

      {/* Health Score — special wide card */}
      <HealthScoreCard score={metrics?.healthScore} />
    </div>
  );
}

function HealthScoreCard({ score }) {
  const { value, label } = formatHealthScore(score);
  const pct = typeof value === "number" ? value : 0;
  const color =
    pct >= 80
      ? "text-emerald-400"
      : pct >= 60
      ? "text-brand-400"
      : pct >= 40
      ? "text-amber-400"
      : "text-rose-400";
  const strokeColor =
    pct >= 80 ? "#34d399" : pct >= 60 ? "#2dd4bf" : pct >= 40 ? "#fbbf24" : "#f87171";

  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (pct / 100) * circumference;

  return (
    <div className="col-span-2 lg:col-span-4 rounded-2xl border border-slate-700/40 bg-slate-800/40 p-6 flex items-center gap-8">
      {/* SVG ring */}
      <div className="relative shrink-0">
        <svg width="88" height="88" viewBox="0 0 88 88">
          <circle cx="44" cy="44" r={radius} fill="none" stroke="#1e293b" strokeWidth="8" />
          <circle
            cx="44"
            cy="44"
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            transform="rotate(-90 44 44)"
            style={{ transition: "stroke-dashoffset 0.8s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-display text-2xl font-bold ${color}`}>{pct}</span>
          <span className="text-slate-500 text-[10px] font-body">/100</span>
        </div>
      </div>

      <div>
        <p className="text-slate-400 font-body text-xs uppercase tracking-wider mb-1">
          Financial Health Score
        </p>
        <p className={`font-display text-2xl font-semibold ${color}`}>{label}</p>
        <p className="text-slate-500 font-body text-sm mt-1">
          Based on savings rate, debt ratio, emergency fund, and goal progress.
        </p>
      </div>
    </div>
  );
}
