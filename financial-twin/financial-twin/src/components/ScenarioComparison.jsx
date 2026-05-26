import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import { formatCurrency, formatPercent } from "../utils/formatters";

const COLORS = ["#2dd4bf", "#34d399", "#60a5fa", "#a78bfa", "#fb923c", "#f472b6"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 shadow-xl">
      <p className="text-slate-300 font-body text-xs mb-2 font-semibold">{label}</p>
      <div className="text-xs font-body space-y-1">
        <div className="flex gap-3">
          <span className="text-slate-400">Projected Corpus:</span>
          <span className="text-slate-100 font-medium">{formatCurrency(d?.corpus, true)}</span>
        </div>
        <div className="flex gap-3">
          <span className="text-slate-400">Success Probability:</span>
          <span className="text-brand-300 font-medium">{formatPercent(d?.successProb, 1, true)}</span>
        </div>
      </div>
    </div>
  );
};

export default function ScenarioComparison({ scenarios }) {
  if (!scenarios?.length) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 font-body text-sm">
        No scenario data returned by backend
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
        {scenarios.map((s, i) => (
          <div
            key={i}
            className="rounded-xl bg-slate-800/60 border border-slate-700/40 p-3"
          >
            <p className="text-slate-400 font-body text-xs mb-1 truncate">{s.name}</p>
            <p
              className="font-display text-lg font-semibold"
              style={{ color: COLORS[i % COLORS.length] }}
            >
              {formatCurrency(s.corpus, true)}
            </p>
            <p className="text-slate-500 font-body text-xs">
              {formatPercent(s.successProb, 1, true)} success probability
            </p>
          </div>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={scenarios} margin={{ top: 5, right: 10, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="name"
            tick={{ fill: "#64748b", fontSize: 10, fontFamily: "DM Sans" }}
            axisLine={false}
            tickLine={false}
            angle={-20}
            textAnchor="end"
            interval={0}
          />
          <YAxis
            tickFormatter={(v) =>
              v >= 1e7 ? `${(v / 1e7).toFixed(0)}Cr` : `${(v / 1e5).toFixed(0)}L`
            }
            tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }}
            axisLine={false}
            tickLine={false}
            width={50}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="corpus" name="Corpus" radius={[4, 4, 0, 0]} maxBarSize={40}>
            {scenarios.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
