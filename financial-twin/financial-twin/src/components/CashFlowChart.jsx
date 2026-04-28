import React, { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { axisFormatter, formatCurrency } from "../utils/formatters";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 shadow-xl min-w-[160px]">
      <p className="text-slate-300 font-body text-xs mb-2 font-semibold">{label}</p>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center gap-2 text-xs font-body mb-1">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-400">{p.name}:</span>
          <span className={`font-medium ${p.value >= 0 ? "text-slate-100" : "text-rose-400"}`}>
            {formatCurrency(p.value, true)}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function CashFlowChart({ data }) {
  const [view, setView] = useState("monthly");

  if (!data?.length) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 font-body text-sm">
        No cash flow data available
      </div>
    );
  }

  // Aggregate to yearly if selected
  const chartData =
    view === "yearly" ? aggregateYearly(data) : data.slice(0, 24);

  return (
    <div>
      {/* View toggle */}
      <div className="flex gap-2 mb-4">
        {["monthly", "yearly"].map((v) => (
          <button
            key={v}
            onClick={() => setView(v)}
            className={`px-3 py-1.5 rounded-lg text-xs font-body font-medium capitalize transition-colors ${
              view === v
                ? "bg-brand-700 text-white"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            {v}
          </button>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0.4} />
            </linearGradient>
            <linearGradient id="expGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f87171" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#f87171" stopOpacity={0.4} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="label"
            tick={{ fill: "#64748b", fontSize: 10, fontFamily: "DM Sans" }}
            axisLine={false}
            tickLine={false}
            interval={view === "monthly" ? 2 : 0}
          />
          <YAxis
            tickFormatter={axisFormatter}
            tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }}
            axisLine={false}
            tickLine={false}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="income" name="Income" fill="url(#incomeGrad)" radius={[3, 3, 0, 0]} maxBarSize={24} />
          <Bar dataKey="expenses" name="Expenses" fill="url(#expGrad)" radius={[3, 3, 0, 0]} maxBarSize={24} />
          <Line
            type="monotone"
            dataKey="surplus"
            name="Surplus"
            stroke="#fb923c"
            strokeWidth={2}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function aggregateYearly(monthlyData) {
  const map = {};
  monthlyData.forEach(({ label, income, expenses, surplus }) => {
    // Extract year from label like "Jan 2024"
    const parts = label.split(" ");
    const year = parts[1] || parts[0];
    if (!map[year]) map[year] = { label: year, income: 0, expenses: 0, surplus: 0 };
    map[year].income += income;
    map[year].expenses += expenses;
    map[year].surplus += surplus;
  });
  return Object.values(map);
}
