/**
 * Format a number as Indian Rupee currency.
 * e.g. 1500000 → "₹15,00,000"
 */
export function formatCurrency(value, compact = false) {
  if (value === null || value === undefined || isNaN(value)) return "—";
  const num = Number(value);
  if (compact) {
    if (num >= 1_00_00_000) return `₹${Number((num / 1_00_00_000).toFixed(2))}Cr`;
    if (num >= 1_00_000) return `₹${Number((num / 1_00_000).toFixed(2))}L`;
    if (num >= 1_000) return `₹${Number((num / 1_000).toFixed(1))}K`;
    return `₹${Math.round(num).toLocaleString("en-IN")}`;
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Math.round(num));
}

/**
 * Format a number as percentage.
 * e.g. 35.5 → "35.5%"
 */
export function formatPercent(value, decimals = 1, isProbability = false) {
  if (value === null || value === undefined || isNaN(value)) return "—";
  let num = Number(value);
  // Backend returns success probability as a float 0.0 to 1.0
  if (num <= 1 && num >= 0 && value !== 0 && value !== "0") {
    num = num * 100;
  }
  if (isProbability && num >= 95) {
    return "Very High (≈98%)";
  }
  return `${Number(num.toFixed(decimals))}%`;
}

/**
 * Format months string.
 */
export function formatMonths(value) {
  if (value === null || value === undefined || isNaN(value)) return "—";
  return `${Number(Number(value).toFixed(1))} months`;
}

/**
 * Format plain number with locale separators.
 */
export function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return "—";
  return Number(value).toLocaleString("en-IN");
}

/**
 * Format a score out of 100 with label.
 */
export function formatHealthScore(score) {
  if (score === null || score === undefined) return { value: "—", label: "" };
  const s = Number(score);
  if (s >= 80) return { value: s, label: "Excellent" };
  if (s >= 60) return { value: s, label: "Good" };
  if (s >= 40) return { value: s, label: "Fair" };
  return { value: s, label: "Needs Attention" };
}

/**
 * Short month-year label from ISO date string or Date.
 */
export function formatMonthYear(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { month: "short", year: "numeric" });
}

/**
 * Compact currency for chart axis ticks.
 */
export function axisFormatter(value) {
  if (value >= 1_00_00_000) return `₹${(value / 1_00_00_000).toFixed(1)}Cr`;
  if (value >= 1_00_000) return `₹${(value / 1_00_000).toFixed(0)}L`;
  if (value >= 1_000) return `₹${(value / 1_000).toFixed(0)}K`;
  return `₹${value}`;
}
