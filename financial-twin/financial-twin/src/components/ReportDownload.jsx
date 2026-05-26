import React, { useState } from "react";
import { Download, FileText } from "lucide-react";
import {
  formatCurrency,
  formatPercent,
  formatMonths,
  formatScore,
  formatHealthScore,
} from "../utils/formatters";

const COLORS = {
  bg: [248, 250, 252],
  ink: [15, 23, 42],
  muted: [100, 116, 139],
  border: [226, 232, 240],
  brand: [15, 118, 110],
  brandSoft: [240, 253, 250],
  good: [22, 163, 74],
  goodSoft: [240, 253, 244],
  warn: [217, 119, 6],
  warnSoft: [255, 251, 235],
  risk: [220, 38, 38],
  riskSoft: [254, 242, 242],
  info: [37, 99, 235],
  infoSoft: [239, 246, 255],
};

const PAGE = {
  width: 210,
  height: 297,
  marginX: 16,
  top: 18,
  bottom: 16,
  headerGap: 12,
};

function setFill(pdf, color) {
  pdf.setFillColor(...color);
}

function setText(pdf, color) {
  pdf.setTextColor(...color);
}

function setDraw(pdf, color) {
  pdf.setDrawColor(...color);
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

function getHealthBadge(score) {
  const label = formatHealthScore(score).label || "Stable";
  if (score >= 80) return { label, fill: COLORS.goodSoft, text: COLORS.good };
  if (score >= 65) return { label, fill: COLORS.brandSoft, text: COLORS.brand };
  if (score >= 45) return { label, fill: COLORS.warnSoft, text: COLORS.warn };
  return { label, fill: COLORS.riskSoft, text: COLORS.risk };
}

function getRiskBadge(level) {
  if (level === "LOW") return { fill: COLORS.goodSoft, text: COLORS.good };
  if (level === "MEDIUM") return { fill: COLORS.warnSoft, text: COLORS.warn };
  return { fill: COLORS.riskSoft, text: COLORS.risk };
}

function getPriorityBadge(impact) {
  if ((impact || "").toLowerCase() === "high") {
    return { label: "Immediate", fill: COLORS.riskSoft, text: COLORS.risk };
  }
  if ((impact || "").toLowerCase() === "medium") {
    return { label: "Medium-Term", fill: COLORS.warnSoft, text: COLORS.warn };
  }
  return { label: "Long-Term", fill: COLORS.infoSoft, text: COLORS.info };
}

function asLines(pdf, text, width, fontSize = 10) {
  pdf.setFontSize(fontSize);
  return pdf.splitTextToSize(text || "", width);
}

function addPageBase(pdf) {
  pdf.addPage();
  setFill(pdf, COLORS.bg);
  pdf.rect(0, 0, PAGE.width, PAGE.height, "F");
}

function addHeader(pdf, title, subtitle, pageNumber) {
  setText(pdf, COLORS.brand);
  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(19);
  pdf.text(title, PAGE.marginX, PAGE.top);

  setText(pdf, COLORS.muted);
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(10);
  if (subtitle) {
    pdf.text(subtitle, PAGE.marginX, PAGE.top + 7);
  }
  pdf.text(`Page ${pageNumber}`, PAGE.width - PAGE.marginX, PAGE.top, { align: "right" });

  setDraw(pdf, COLORS.border);
  pdf.setLineWidth(0.4);
  pdf.line(PAGE.marginX, PAGE.top + 12, PAGE.width - PAGE.marginX, PAGE.top + 12);
  return PAGE.top + PAGE.headerGap + 8;
}

function addFooter(pdf) {
  setDraw(pdf, COLORS.border);
  pdf.setLineWidth(0.3);
  pdf.line(PAGE.marginX, PAGE.height - PAGE.bottom - 7, PAGE.width - PAGE.marginX, PAGE.height - PAGE.bottom - 7);

  setText(pdf, COLORS.muted);
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(8);
  pdf.text(
    "FinTwin advisory output is educational and assumption-based. It should support, not replace, personal financial judgment.",
    PAGE.width / 2,
    PAGE.height - PAGE.bottom + 1,
    { align: "center" }
  );
}

function ensureSpace(pdf, y, needed, addPage, title = "Continued", subtitle = "Advisory report continuation.") {
  if (y + needed <= PAGE.height - PAGE.bottom - 10) return y;
  addPage(title, subtitle);
  return addPage.currentY;
}

function drawSectionTitle(pdf, title, y) {
  setText(pdf, COLORS.ink);
  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(13);
  pdf.text(title, PAGE.marginX, y);
  setDraw(pdf, COLORS.border);
  pdf.setLineWidth(0.25);
  pdf.line(PAGE.marginX, y + 2, PAGE.width - PAGE.marginX, y + 2);
  return y + 8;
}

function drawParagraph(pdf, text, y, options = {}) {
  const width = options.width || PAGE.width - PAGE.marginX * 2;
  const x = options.x || PAGE.marginX;
  const fontSize = options.fontSize || 10;
  const color = options.color || COLORS.ink;
  const lineGap = options.lineGap || 4.6;
  const lines = asLines(pdf, text, width, fontSize);
  setText(pdf, color);
  pdf.setFont("helvetica", options.bold ? "bold" : "normal");
  pdf.setFontSize(fontSize);
  pdf.text(lines, x, y);
  return y + lines.length * lineGap;
}

function drawBadge(pdf, text, x, y, fill, textColor) {
  const width = pdf.getTextWidth(text) + 8;
  setFill(pdf, fill);
  pdf.roundedRect(x, y - 4, width, 7, 2, 2, "F");
  setText(pdf, textColor);
  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(8);
  pdf.text(text, x + 4, y);
}

function drawMetricCard(pdf, x, y, w, h, label, value, subtext, tone = "brand") {
  const toneMap = {
    brand: { fill: COLORS.brandSoft, value: COLORS.brand },
    good: { fill: COLORS.goodSoft, value: COLORS.good },
    warn: { fill: COLORS.warnSoft, value: COLORS.warn },
    risk: { fill: COLORS.riskSoft, value: COLORS.risk },
    info: { fill: COLORS.infoSoft, value: COLORS.info },
  };
  const selected = toneMap[tone] || toneMap.brand;

  setFill(pdf, [255, 255, 255]);
  setDraw(pdf, COLORS.border);
  pdf.roundedRect(x, y, w, h, 3, 3, "FD");
  setFill(pdf, selected.fill);
  pdf.roundedRect(x, y, w, 8, 3, 3, "F");

  setText(pdf, COLORS.muted);
  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(8);
  pdf.text(label.toUpperCase(), x + 4, y + 5);

  setText(pdf, selected.value);
  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(15);
  pdf.text(value, x + 4, y + 16);

  if (subtext) {
    setText(pdf, COLORS.muted);
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(8.5);
    const lines = pdf.splitTextToSize(subtext, w - 8);
    pdf.text(lines, x + 4, y + 23);
  }
}

function drawKeyValueRows(pdf, rows, y, valueAlign = "right") {
  let currentY = y;
  rows.forEach(([label, value]) => {
    setText(pdf, COLORS.muted);
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(9.5);
    pdf.text(label, PAGE.marginX, currentY);

    setText(pdf, COLORS.ink);
    pdf.setFont("helvetica", "bold");
    pdf.text(String(value), valueAlign === "right" ? PAGE.width - PAGE.marginX : PAGE.marginX + 70, currentY, {
      align: valueAlign,
    });

    setDraw(pdf, COLORS.border);
    pdf.setLineWidth(0.2);
    pdf.line(PAGE.marginX, currentY + 2, PAGE.width - PAGE.marginX, currentY + 2);
    currentY += 8;
  });
  return currentY;
}

function deriveStrengths(metrics) {
  const items = [];
  if ((metrics.healthScore || 0) >= 65) items.push("overall financial discipline is above average");
  if ((metrics.emergencyFundMonths || 0) >= 3) items.push("emergency reserves already provide a useful first line of protection");
  if ((metrics.savingsRate || 0) >= 0.15) items.push("monthly savings behavior is supporting long-term wealth creation");
  if ((metrics.monthlySurplus || 0) > 0) items.push("cash flow remains positive after regular commitments");
  return items.slice(0, 3);
}

function deriveImprovementAreas(metrics) {
  const items = [];
  if ((metrics.goalSuccessProbability || metrics.successProbabilityReal || 0) < 0.35) items.push("retirement readiness still needs stronger compounding support");
  if ((metrics.emergencyFundMonths || 0) < 6) items.push("liquidity can be strengthened toward a full 6-month reserve");
  if ((metrics.totalLiabilities || 0) > 0 && (metrics.savingsRate || 0) < 0.25) items.push("debt servicing is reducing flexibility that could go toward investments");
  if ((metrics.monthlySurplus || 0) < 0) items.push("cash flow needs rebalancing before long-term goals can accelerate");
  return items.slice(0, 3);
}

function deriveKeyRisks(results) {
  const metrics = results?.metrics || {};
  const stress = results?.stress_test || {};
  const risks = [];
  if ((metrics.goalSuccessProbability || metrics.successProbabilityReal || 0) < 0.20) {
    risks.push("Retirement corpus adequacy remains the primary long-term planning risk under current contribution levels.");
  }
  if ((metrics.emergencyFundMonths || 0) < 3) {
    risks.push("Liquidity is still thin for a multi-month income shock, which increases the chance of dipping into debt or investments.");
  }
  if ((stress.summary?.overall_risk_level || "") === "HIGH") {
    risks.push("Stress scenarios indicate that job interruption or large health expenses could materially weaken plan stability.");
  }
  if ((metrics.totalLiabilities || 0) > 0 && (metrics.monthlySurplus || 0) < 15000) {
    risks.push("Debt repayments are reducing the amount of surplus available for higher-value long-term compounding.");
  }
  return risks.slice(0, 4);
}

function buildRoadmap(recommendations) {
  const roadmap = {
    immediate: [],
    medium: [],
    long: [],
  };

  (recommendations || []).forEach((rec) => {
    const category = (rec.category || "").toLowerCase();
    const impact = (rec.impact || "").toLowerCase();
    if (impact === "high" || category === "debt" || category === "liquidity" || category === "protection") {
      roadmap.immediate.push(rec);
      return;
    }
    if (impact === "medium" || category === "investment" || category === "planning") {
      roadmap.medium.push(rec);
      return;
    }
    roadmap.long.push(rec);
  });

  return roadmap;
}

function addCanvasSlicesToPdf(pdf, canvas, addPage) {
  const usableWidth = PAGE.width - PAGE.marginX * 2;
  const usableHeight = PAGE.height - PAGE.top - PAGE.bottom - 28;
  const scale = usableWidth / canvas.width;
  const sliceHeightPx = Math.floor(usableHeight / scale);

  let offsetY = 0;
  let firstPage = true;
  while (offsetY < canvas.height) {
    if (!firstPage) {
      addPage("Visual Appendix", "High-resolution dashboard capture for charts and panel context.");
    }

    const remaining = canvas.height - offsetY;
    const currentSliceHeight = Math.min(sliceHeightPx, remaining);
    const slice = document.createElement("canvas");
    slice.width = canvas.width;
    slice.height = currentSliceHeight;
    const ctx = slice.getContext("2d");
    ctx.drawImage(
      canvas,
      0,
      offsetY,
      canvas.width,
      currentSliceHeight,
      0,
      0,
      canvas.width,
      currentSliceHeight
    );

    const imgData = slice.toDataURL("image/jpeg", 0.92);
    const renderedHeight = currentSliceHeight * scale;
    pdf.addImage(imgData, "JPEG", PAGE.marginX, addPage.currentY, usableWidth, renderedHeight, undefined, "FAST");

    offsetY += currentSliceHeight;
    firstPage = false;
  }
}

export default function ReportDownload({ results, userName }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState("");

  const handleDownload = async () => {
    setLoading(true);
    setError(null);
    setSuccess("");

    try {
      const jsPDF = (await import("jspdf")).default;
      const html2canvas = (await import("html2canvas")).default;

      const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
      const m = results?.metrics || {};
      const e = results?.explainability || {};
      const stress = results?.stress_test || {};
      const recommendations = results?.recommendations || [];
      const latestProfile =
        results?.history?.[results.history.length - 1]?.profile ||
        results?.history?.[0]?.profile ||
        null;
      const u = results?.user_summary || {};
      const preparedFor = userName || u.name || "Client";
      const goalProbability = m.goalSuccessProbability ?? m.successProbabilityReal ?? 0;
      const roadmap = buildRoadmap(recommendations);
      const strengths = deriveStrengths(m);
      const improvementAreas = deriveImprovementAreas(m);
      const keyRisks = deriveKeyRisks(results);
      const healthBadge = getHealthBadge(m.healthScore || 0);
      const resilienceBadge = getRiskBadge(stress.summary?.overall_risk_level || "MEDIUM");
      const essentialExpenses =
        latestProfile?.expenses
          ? (latestProfile.expenses.living_expenses || 0) +
            (latestProfile.expenses.emi_payments || 0) +
            (latestProfile.expenses.insurance || 0) +
            (latestProfile.expenses.education_expenses || 0)
          : 0;
      const currentEmergencyFund = latestProfile?.assets?.emergency_fund || 0;
      const emergencyReserveGap =
        essentialExpenses > 0
          ? Math.max(0, essentialExpenses * 6 - currentEmergencyFund)
          : null;

      let pageNo = 1;
      const addPage = (title, subtitle) => {
        addPageBase(pdf);
        addPage.currentY = addHeader(pdf, title, subtitle, pageNo);
        addFooter(pdf);
        pageNo += 1;
      };

      setFill(pdf, COLORS.bg);
      pdf.rect(0, 0, PAGE.width, PAGE.height, "F");
      addPage.currentY = addHeader(
        pdf,
        "FinTwin Advisory Report",
        `Prepared for ${preparedFor} on ${new Date().toLocaleDateString("en-IN")} at ${new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}`,
        pageNo
      );
      addFooter(pdf);
      pageNo += 1;

      let y = addPage.currentY;

      setFill(pdf, [255, 255, 255]);
      setDraw(pdf, COLORS.border);
      pdf.roundedRect(PAGE.marginX, y, PAGE.width - PAGE.marginX * 2, 33, 4, 4, "FD");
      setFill(pdf, COLORS.brandSoft);
      pdf.roundedRect(PAGE.marginX, y, PAGE.width - PAGE.marginX * 2, 10, 4, 4, "F");
      setText(pdf, COLORS.brand);
      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(10);
      pdf.text("1. Executive Summary", PAGE.marginX + 4, y + 6.5);

      drawBadge(pdf, healthBadge.label, PAGE.width - PAGE.marginX - 28, y + 6.5, healthBadge.fill, healthBadge.text);

      const executiveSummary =
        `${e.goal_analysis || "Your plan is moving in the right direction, with room to strengthen long-term reliability."} ` +
        `${e.liquidity_analysis || ""}`.trim();
      y = drawParagraph(pdf, executiveSummary, y + 16, {
        x: PAGE.marginX + 4,
        width: PAGE.width - PAGE.marginX * 2 - 8,
        color: COLORS.ink,
        fontSize: 10,
      });

      y += 8;
      drawMetricCard(pdf, PAGE.marginX, y, 42, 26, "Financial Health", formatScore(m.healthScore ?? 0), healthBadge.label, "brand");
      drawMetricCard(pdf, PAGE.marginX + 46, y, 42, 26, "Goal Success", formatPercent(goalProbability, 1, true), "Retirement readiness", goalProbability >= 0.6 ? "good" : goalProbability >= 0.3 ? "warn" : "risk");
      drawMetricCard(pdf, PAGE.marginX + 92, y, 42, 26, "Emergency Buffer", formatMonths(m.emergencyFundMonths ?? 0), "Target: 6 months", (m.emergencyFundMonths || 0) >= 6 ? "good" : "warn");
      drawMetricCard(pdf, PAGE.marginX + 138, y, 56, 26, "Debt & Resilience", `${stress.summary?.overall_risk_level || "MEDIUM"} / ${formatScore(stress.summary?.resilience_score || 0)}`, "Stress-test stability", resilienceBadge.text === COLORS.good ? "good" : resilienceBadge.text === COLORS.warn ? "warn" : "risk");

      y += 34;
      y = drawSectionTitle(pdf, "Strengths and Improvement Areas", y);

      setFill(pdf, [255, 255, 255]);
      setDraw(pdf, COLORS.border);
      pdf.roundedRect(PAGE.marginX, y, 86, 44, 3, 3, "FD");
      pdf.roundedRect(PAGE.marginX + 92, y, 102, 44, 3, 3, "FD");

      y = drawParagraph(pdf, "Major Strengths", y + 7, { x: PAGE.marginX + 4, bold: true, fontSize: 10 });
      let leftY = y + 2;
      strengths.forEach((item, index) => {
        leftY = drawParagraph(pdf, `${index + 1}. ${item}`, leftY, { x: PAGE.marginX + 4, width: 78, fontSize: 9, color: COLORS.muted });
        leftY += 1;
      });

      let rightY = y - 5;
      rightY = drawParagraph(pdf, "Improvement Areas", rightY + 12, { x: PAGE.marginX + 96, bold: true, fontSize: 10 });
      improvementAreas.forEach((item, index) => {
        rightY = drawParagraph(pdf, `${index + 1}. ${item}`, rightY + 2, {
          x: PAGE.marginX + 96,
          width: 94,
          fontSize: 9,
          color: COLORS.muted,
        });
      });

      addPage("Financial Snapshot", "Core personal finance position, cash flow health, and long-term retirement outlook.");
      y = addPage.currentY;

      y = drawSectionTitle(pdf, "2. Financial Snapshot", y);
      y = drawKeyValueRows(
        pdf,
        [
          ["Net Worth", formatCurrency(m.netWorth ?? 0)],
          ["Total Assets", formatCurrency(m.totalAssets ?? 0)],
          ["Total Liabilities", formatCurrency(m.totalLiabilities ?? 0)],
          ["Monthly Surplus", formatCurrency(m.monthlySurplus ?? 0)],
          ["Savings Rate", formatPercent(m.savingsRate ?? 0)],
          ["Financial Health Score", formatScore(m.healthScore ?? 0)],
        ],
        y
      );

      y += 4;
      y = drawSectionTitle(pdf, "3. Cash Flow Analysis", y);
      y = drawParagraph(
        pdf,
        `Your current monthly surplus stands at ${formatCurrency(m.monthlySurplus ?? 0)} with a savings rate of ${formatPercent(m.savingsRate ?? 0)}. ` +
          "This surplus is the main engine for emergency reserve strengthening, debt reduction, and SIP growth.",
        y
      );

      y += 3;
      drawMetricCard(pdf, PAGE.marginX, y, 56, 24, "Monthly Surplus", formatCurrency(m.monthlySurplus ?? 0, true), "Free cash after taxes and regular outflows", "good");
      drawMetricCard(pdf, PAGE.marginX + 60, y, 56, 24, "Savings Rate", formatPercent(m.savingsRate ?? 0), "Healthy middle-class target: 15-25%", (m.savingsRate || 0) >= 0.20 ? "good" : "warn");
      drawMetricCard(
        pdf,
        PAGE.marginX + 120,
        y,
        74,
        24,
        "Emergency Reserve Gap",
        emergencyReserveGap === null ? "See Note" : formatCurrency(emergencyReserveGap, true),
        emergencyReserveGap === null
          ? "Calculated when dedicated EF inputs are available"
          : emergencyReserveGap > 0
          ? "Additional emergency reserve still recommended"
          : "Emergency reserve target already funded",
        emergencyReserveGap > 0 ? "info" : "good"
      );

      y += 32;
      y = drawSectionTitle(pdf, "4. Net Worth Breakdown", y);
      y = drawKeyValueRows(
        pdf,
        [
          ["Asset Base", formatCurrency(m.totalAssets ?? 0)],
          ["Liability Base", formatCurrency(m.totalLiabilities ?? 0)],
          ["Debt-to-Income Ratio", formatPercent(m.debtToIncomeRatio ?? m.debt_to_income_ratio ?? 0)],
          ["Emergency Coverage", formatMonths(m.emergencyFundMonths ?? 0)],
        ],
        y
      );

      y += 4;
      y = drawSectionTitle(pdf, "5. Retirement Outlook", y);
      y = drawParagraph(
        pdf,
        `Projected nominal corpus is ${formatCurrency(m.projectedCorpus ?? 0)} and inflation-adjusted corpus is ${formatCurrency(m.projectedRealCorpus ?? 0)}. ` +
          `Current goal success is ${formatPercent(goalProbability, 1, true)} against a target corpus of ${formatCurrency(m.targetCorpus ?? 0)}.`,
        y
      );
      y = drawParagraph(pdf, e.goal_analysis || "", y + 3, { color: COLORS.muted });

      addPage("Stress Test Insights", "Shock resilience, consistency checks, and major planning risks.");
      y = addPage.currentY;

      y = drawSectionTitle(pdf, "6. Stress Test Insights", y);
      drawMetricCard(pdf, PAGE.marginX, y, 46, 24, "Baseline Resilience", formatScore(stress.baseline?.resilience_score || stress.summary?.resilience_score || 0), "0-100 stability score", "brand");
      drawMetricCard(pdf, PAGE.marginX + 50, y, 46, 24, "Risk Level", stress.summary?.overall_risk_level || "MEDIUM", "Across modeled shocks", stress.summary?.overall_risk_level === "LOW" ? "good" : stress.summary?.overall_risk_level === "MEDIUM" ? "warn" : "risk");
      drawMetricCard(pdf, PAGE.marginX + 100, y, 46, 24, "Worst Shock", stress.summary?.worst_case_scenario || "N/A", "Most challenging scenario", "warn");
      drawMetricCard(pdf, PAGE.marginX + 150, y, 44, 24, "Worst Prob. Drop", formatPercent(Math.abs(stress.summary?.worst_case_rsp_drop || 0), 1, true), "Controlled downside", "risk");

      y += 32;
      const stressRows = (stress.scenarios || []).slice(0, 4).map((scenario) => [
        scenario.label,
        `${formatPercent(scenario.impact?.real_success_probability_after || 0, 1, true)} success | ${formatScore(scenario.impact?.resilience_score_after || 0)} resilience`,
      ]);
      y = drawKeyValueRows(pdf, stressRows, y, "right");

      y += 4;
      y = drawSectionTitle(pdf, "7. Key Risks", y);
      keyRisks.forEach((risk, index) => {
        y = drawParagraph(pdf, `${index + 1}. ${risk}`, y, {
          color: COLORS.muted,
          fontSize: 9.5,
          width: PAGE.width - PAGE.marginX * 2,
        });
        y += 1;
      });

      addPage("Action Roadmap", "Prioritized action guidance with immediate, medium-term, and long-term focus areas.");
      y = addPage.currentY;

      y = drawSectionTitle(pdf, "8. Recommended Actions", y);
      recommendations.slice(0, 5).forEach((rec, index) => {
        y = ensureSpace(pdf, y, 25, addPage);
        const badge = getPriorityBadge(rec.impact);

        setFill(pdf, [255, 255, 255]);
        setDraw(pdf, COLORS.border);
        pdf.roundedRect(PAGE.marginX, y, PAGE.width - PAGE.marginX * 2, 20, 3, 3, "FD");
        drawBadge(pdf, badge.label, PAGE.width - PAGE.marginX - 28, y + 6, badge.fill, badge.text);

        setText(pdf, COLORS.ink);
        pdf.setFont("helvetica", "bold");
        pdf.setFontSize(10);
        pdf.text(`${index + 1}. ${rec.title}`, PAGE.marginX + 4, y + 6);

        y = drawParagraph(pdf, rec.description, y + 11, {
          x: PAGE.marginX + 4,
          width: PAGE.width - PAGE.marginX * 2 - 8,
          fontSize: 9,
          color: COLORS.muted,
        });

        if (rec.action) {
          y = drawParagraph(pdf, `Suggested next step: ${rec.action}`, y + 1, {
            x: PAGE.marginX + 4,
            width: PAGE.width - PAGE.marginX * 2 - 8,
            fontSize: 8.7,
            color: COLORS.brand,
            bold: true,
          });
        }
        y += 4;
      });

      y = ensureSpace(pdf, y, 70, addPage);
      y = drawSectionTitle(pdf, "9. Long-Term Improvement Strategy", y);

      const roadmapSections = [
        ["Immediate Priorities", roadmap.immediate],
        ["Medium-Term Priorities", roadmap.medium],
        ["Long-Term Priorities", roadmap.long],
      ];

      roadmapSections.forEach(([title, items]) => {
        y = ensureSpace(pdf, y, 24, addPage);
        setFill(pdf, COLORS.brandSoft);
        pdf.roundedRect(PAGE.marginX, y, PAGE.width - PAGE.marginX * 2, 8, 2, 2, "F");
        setText(pdf, COLORS.brand);
        pdf.setFont("helvetica", "bold");
        pdf.setFontSize(9.5);
        pdf.text(title, PAGE.marginX + 4, y + 5.5);
        y += 12;

        if (!items.length) {
          y = drawParagraph(pdf, "Maintain current momentum and review this area during the next scheduled plan update.", y, {
            color: COLORS.muted,
            fontSize: 9,
          });
          y += 2;
          return;
        }

        items.slice(0, 3).forEach((item, index) => {
          y = drawParagraph(pdf, `${index + 1}. ${item.title}: ${item.action || item.description}`, y, {
            color: COLORS.muted,
            fontSize: 9,
            width: PAGE.width - PAGE.marginX * 2,
          });
          y += 2;
        });
      });

      const visualSource = document.getElementById("report-content");
      if (visualSource) {
        const canvas = await html2canvas(visualSource, {
          scale: clamp(window.devicePixelRatio || 1.5, 1.5, 2.2),
          backgroundColor: "#ffffff",
          useCORS: true,
          logging: false,
          windowWidth: visualSource.scrollWidth,
          windowHeight: visualSource.scrollHeight,
        });
        addPage("Visual Appendix", "High-resolution dashboard capture for charts and panel context.");
        addCanvasSlicesToPdf(pdf, canvas, addPage);
      }

      addPage("10. Disclaimer", "Important context for interpretation and use.");
      y = addPage.currentY;
      y = drawParagraph(
        pdf,
        "This advisory report is designed for educational and planning support purposes. It is based on user-provided inputs, model assumptions, and scenario estimates rather than guaranteed outcomes.",
        y,
        { fontSize: 10 }
      );
      y += 4;
      [
        "Projected returns, inflation, taxes, and income stability may differ materially from actual future experience.",
        "Stress scenarios are illustrative planning tools intended to show relative sensitivity rather than forecast exact outcomes.",
        "This report should be used as a structured planning aid alongside personal judgment and, where needed, professional advice.",
      ].forEach((item, index) => {
        y = drawParagraph(pdf, `${index + 1}. ${item}`, y, { color: COLORS.muted, fontSize: 9.5 });
        y += 2;
      });

      pdf.save(`fintwin-advisory-report-${Date.now()}.pdf`);
      setSuccess("Advisory report downloaded successfully.");
    } catch (err) {
      setError("PDF generation failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        onClick={handleDownload}
        disabled={loading || !results}
        className="flex items-center gap-2.5 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-body text-sm font-semibold transition-all shadow-lg shadow-brand-900/30"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Generating Advisory Report...
          </>
        ) : (
          <>
            <Download className="w-4 h-4" />
            Download Advisory Report
          </>
        )}
      </button>
      {success && <p className="text-emerald-400 font-body text-xs">{success}</p>}
      {error && <p className="text-rose-400 font-body text-xs">{error}</p>}
      {!results && (
        <p className="text-slate-500 font-body text-xs flex items-center gap-1">
          <FileText className="w-3 h-3" /> Run simulation first to enable report
        </p>
      )}
    </div>
  );
}
