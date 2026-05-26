const RUPEE = "\u20B9";
const EMPTY = "-";

function toFiniteNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function trimFixed(value, decimals = 1) {
  const num = toFiniteNumber(value);
  if (num === null) return EMPTY;
  return Number(num.toFixed(decimals)).toString();
}

function compactRupees(value) {
  const num = toFiniteNumber(value);
  if (num === null) return EMPTY;

  const sign = num < 0 ? "-" : "";
  const abs = Math.abs(num);

  if (abs >= 1_00_00_000) return `${sign}${RUPEE}${trimFixed(abs / 1_00_00_000, 2)}Cr`;
  if (abs >= 1_00_000) return `${sign}${RUPEE}${trimFixed(abs / 1_00_000, 2)}L`;
  if (abs >= 1_000) return `${sign}${RUPEE}${trimFixed(abs / 1_000, 1)}K`;
  return `${sign}${RUPEE}${Math.round(abs).toLocaleString("en-IN")}`;
}

/**
 * Format a number as Indian Rupee currency.
 */
export function formatCurrency(value, compact = false) {
  const num = toFiniteNumber(value);
  if (num === null) return EMPTY;
  if (compact) return compactRupees(num);

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Math.round(num));
}

/**
 * Format a number as percentage.
 * Supports probabilities returned as ratios between 0 and 1.
 */
export function formatPercent(value, decimals = 1, isProbability = false) {
  const num = toFiniteNumber(value);
  if (num === null) return EMPTY;

  const percent = num >= 0 && num <= 1 ? num * 100 : num;
  if (isProbability && percent <= 0) return "<1%";
  if (isProbability && percent > 0 && percent < 1) return "<1%";
  if (isProbability && percent >= 95) return "Very High (~98%)";
  return `${trimFixed(percent, decimals)}%`;
}

/**
 * Format month coverage with at most one decimal.
 */
export function formatMonths(value) {
  const num = toFiniteNumber(value);
  if (num === null) return EMPTY;
  return `${trimFixed(num, 1)} months`;
}

/**
 * Format a plain number using Indian locale separators.
 */
export function formatNumber(value, decimals = 0) {
  const num = toFiniteNumber(value);
  if (num === null) return EMPTY;
  return Number(num.toFixed(decimals)).toLocaleString("en-IN");
}

/**
 * Format a score out of 100.
 */
export function formatScore(value, decimals = 0) {
  const num = toFiniteNumber(value);
  if (num === null) return EMPTY;
  return `${trimFixed(num, decimals)}/100`;
}

/**
 * Label health score bands.
 */
export function formatHealthScore(score) {
  const num = toFiniteNumber(score);
  if (num === null) return { value: EMPTY, label: "" };
  if (num >= 80) return { value: Math.round(num), label: "Excellent" };
  if (num >= 65) return { value: Math.round(num), label: "Good" };
  if (num >= 45) return { value: Math.round(num), label: "Stable" };
  if (num >= 30) return { value: Math.round(num), label: "Needs Attention" };
  return { value: Math.round(num), label: "High Risk" };
}

/**
 * Format a transaction or action label from snake_case.
 */
export function formatActionLabel(value) {
  if (!value) return "Review Plan";
  return value
    .split("_")
    .map((part) => {
      if (part.toLowerCase() === "sip") return "SIP";
      return part.charAt(0).toUpperCase() + part.slice(1);
    })
    .join(" ");
}

/**
 * Short month-year label from ISO date string or Date.
 */
export function formatMonthYear(dateStr) {
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return EMPTY;
  return d.toLocaleDateString("en-IN", { month: "short", year: "numeric" });
}

/**
 * Compact currency for chart axis ticks.
 */
export function axisFormatter(value) {
  return compactRupees(value);
}
