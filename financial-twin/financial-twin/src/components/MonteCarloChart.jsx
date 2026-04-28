import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
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
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 shadow-xl">
      <p className="text-slate-300 font-body text-xs mb-2 font-semibold">{label}</p>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center gap-2 text-xs font-body">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-400">{p.name}:</span>
          <span className="text-slate-100 font-medium">
            {formatCurrency(p.value, true)}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function MonteCarloChart({ data }) {
  if (!data?.length) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 font-body text-sm">
        No simulation data available
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-4 text-xs font-body">
        <LegendItem color="#6ee7b7" label="Optimistic (P95)" />
        <LegendItem color="#2dd4bf" label="Median (P50)" />
        <LegendItem color="#7c3aed" label="Conservative (P5)" />
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="p95Grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6ee7b7" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#6ee7b7" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="p50Grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="p5Grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="year"
            tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={axisFormatter}
            tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }}
            axisLine={false}
            tickLine={false}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="p95"
            name="Optimistic (P95)"
            stroke="#6ee7b7"
            strokeWidth={1.5}
            fill="url(#p95Grad)"
            strokeDasharray="5 3"
          />
          <Area
            type="monotone"
            dataKey="p50"
            name="Median (P50)"
            stroke="#2dd4bf"
            strokeWidth={2.5}
            fill="url(#p50Grad)"
          />
          <Area
            type="monotone"
            dataKey="p5"
            name="Conservative (P5)"
            stroke="#7c3aed"
            strokeWidth={1.5}
            fill="url(#p5Grad)"
            strokeDasharray="5 3"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

function LegendItem({ color, label }) {
  return (
    <div className="flex items-center gap-1.5 text-slate-400">
      <span className="w-6 h-0.5 inline-block rounded" style={{ background: color }} />
      {label}
    </div>
  );
}
