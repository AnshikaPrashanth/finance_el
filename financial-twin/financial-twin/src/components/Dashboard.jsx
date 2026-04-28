import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import MetricsCards from "./MetricsCards";
import MonteCarloChart from "./MonteCarloChart";
import CashFlowChart from "./CashFlowChart";
import ScenarioComparison from "./ScenarioComparison";
import ReportDownload from "./ReportDownload";
import { formatCurrency, axisFormatter } from "../utils/formatters";
import { CheckCircle, TrendingUp, AlertTriangle, Info } from "lucide-react";

const SectionCard = ({ title, subtitle, children }) => (
  <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-6 backdrop-blur-sm">
    <div className="mb-5">
      <h3 className="text-slate-100 font-display text-lg">{title}</h3>
      {subtitle && <p className="text-slate-500 font-body text-sm mt-0.5">{subtitle}</p>}
    </div>
    {children}
  </div>
);

const NetWorthTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 shadow-xl">
      <p className="text-slate-400 font-body text-xs mb-1">{label}</p>
      {payload.map((p) => (
        <div key={p.dataKey} className="text-xs font-body">
          <span className="text-slate-400">{p.name}: </span>
          <span className="text-slate-100 font-medium">{formatCurrency(p.value, true)}</span>
        </div>
      ))}
    </div>
  );
};

export default function Dashboard({ results, userName, formData }) {
  const { metrics, projections, cashFlow, monteCarlo, scenarios, recommendations } = results;

  return (
    <div className="space-y-6 animate-fade-in" id="report-content">
      {/* Hero banner */}
      <div className="rounded-2xl bg-mesh-pattern border border-brand-800/30 p-7 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950/80 to-transparent" />
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <p className="text-brand-300 font-body text-sm font-medium mb-1">
              Financial Simulation Complete
            </p>
            <h2 className="font-display text-3xl text-white">
              {userName ? `Welcome, ${userName.split(" ")[0]}` : "Your Financial Twin"}
            </h2>
            <p className="text-slate-400 font-body text-sm mt-2">
              Based on your inputs, here is your complete financial projection and analysis.
            </p>
          </div>
          <ReportDownload results={results} userName={userName} />
        </div>
      </div>

      {/* Metrics grid */}
      <MetricsCards metrics={metrics} />

      {/* Net Worth Projection */}
      <SectionCard
        title="Wealth Projection Over Time"
        subtitle="Projected net worth and investment corpus growth"
      >
        {projections?.length ? (
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={projections} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="nwGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="corpusGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#60a5fa" stopOpacity={0} />
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
              <Tooltip content={<NetWorthTooltip />} />
              <Area
                type="monotone"
                dataKey="netWorth"
                name="Net Worth"
                stroke="#2dd4bf"
                strokeWidth={2.5}
                fill="url(#nwGrad)"
              />
              <Area
                type="monotone"
                dataKey="corpus"
                name="Corpus"
                stroke="#60a5fa"
                strokeWidth={2}
                fill="url(#corpusGrad)"
                strokeDasharray="5 3"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <EmptyChart />
        )}
      </SectionCard>

      {/* Cash Flow + Monte Carlo side-by-side on large screens */}
      <div className="grid lg:grid-cols-2 gap-6">
        <SectionCard
          title="Cash Flow Analysis"
          subtitle="Monthly income, expenses, and surplus"
        >
          <CashFlowChart data={cashFlow} />
        </SectionCard>

        <SectionCard
          title="Monte Carlo Simulation"
          subtitle="Wealth range across 1,000 market scenarios"
        >
          <MonteCarloChart data={monteCarlo} />
        </SectionCard>
      </div>

      {/* Scenario Comparison */}
      <SectionCard
        title="Strategy Comparison"
        subtitle="How different approaches affect your retirement corpus"
      >
        <ScenarioComparison scenarios={scenarios} />
      </SectionCard>

      {/* Recommendations */}
      {recommendations?.length > 0 && (
        <SectionCard
          title="Insights & Recommendations"
          subtitle="Actionable steps based on your simulation"
        >
          <div className="space-y-3">
            {recommendations.map((rec, i) => (
              typeof rec === 'string' ? (
                <RecommendationItem key={i} text={rec} index={i} />
              ) : (
                <EnhancedRecommendationItem key={i} recommendation={rec} />
              )
            ))}
          </div>
        </SectionCard>
      )}

      {/* Transparency & Explainability Section */}
      {results.explainability && (
        <SectionCard
          title="Transparency & Analysis"
          subtitle="Understanding your financial situation"
        >
          <div className="grid md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
              <p className="text-slate-400 font-body text-xs uppercase tracking-wider mb-2">Goal Analysis</p>
              <p className="text-slate-200 font-body text-sm leading-relaxed">{results.explainability.goal_analysis}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
              <p className="text-slate-400 font-body text-xs uppercase tracking-wider mb-2">Debt Analysis</p>
              <p className="text-slate-200 font-body text-sm leading-relaxed">{results.explainability.debt_analysis}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
              <p className="text-slate-400 font-body text-xs uppercase tracking-wider mb-2">Liquidity Analysis</p>
              <p className="text-slate-200 font-body text-sm leading-relaxed">{results.explainability.liquidity_analysis}</p>
            </div>
          </div>
        </SectionCard>
      )}
    </div>
  );
}

function RecommendationItem({ text, index }) {
  const icon =
    index === 0 ? CheckCircle
    : text.toLowerCase().includes("warning") || text.toLowerCase().includes("risk")
    ? AlertTriangle
    : index % 2 === 0
    ? TrendingUp
    : Info;
  const Icon = icon;
  const color =
    icon === AlertTriangle ? "text-amber-400" : icon === CheckCircle ? "text-emerald-400" : "text-brand-400";

  return (
    <div className="flex gap-3 p-4 rounded-xl bg-slate-800/50 border border-slate-700/30">
      <div className={`shrink-0 mt-0.5 ${color}`}>
        <Icon className="w-4 h-4" />
      </div>
      <p className="text-slate-300 font-body text-sm leading-relaxed">{text}</p>
    </div>
  );
}

function EnhancedRecommendationItem({ recommendation }) {
  const getImpactColor = (impact) => {
    switch(impact?.toLowerCase()) {
      case 'high':
        return 'bg-red-900/20 border-red-800/40 text-red-300';
      case 'medium':
        return 'bg-amber-900/20 border-amber-800/40 text-amber-300';
      case 'low':
        return 'bg-blue-900/20 border-blue-800/40 text-blue-300';
      default:
        return 'bg-slate-800/50 border-slate-700/30 text-slate-300';
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'debt': '💳',
      'liquidity': '🏦',
      'investment': '📈',
      'taxes': '📋',
      'insurance': '🛡️'
    };
    return icons[category?.toLowerCase()] || '💡';
  };

  return (
    <div className={`p-4 rounded-xl border ${getImpactColor(recommendation.impact)}`}>
      <div className="flex items-start gap-3">
        <span className="text-lg shrink-0">{getCategoryIcon(recommendation.category)}</span>
        <div className="flex-1">
          <h4 className="font-semibold text-slate-100 mb-1">{recommendation.title}</h4>
          <p className="text-sm text-slate-300 mb-2">{recommendation.description}</p>
          {recommendation.action && (
            <p className="text-xs font-medium text-slate-400 bg-slate-900/40 px-3 py-1.5 rounded-lg inline-block">
              ✓ {recommendation.action}
            </p>
          )}
        </div>
        {recommendation.impact && (
          <span className={`text-xs font-semibold px-2 py-1 rounded shrink-0 ${getImpactColor(recommendation.impact)}`}>
            {recommendation.impact.toUpperCase()}
          </span>
        )}
      </div>
    </div>
  );
}

function EmptyChart() {
  return (
    <div className="flex items-center justify-center h-40 text-slate-500 font-body text-sm">
      No projection data available
    </div>
  );
}
