import React, { useState } from "react";
import { Download, FileText } from "lucide-react";
import { formatCurrency, formatPercent, formatMonths } from "../utils/formatters";

export default function ReportDownload({ results, userName }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDownload = async () => {
    setLoading(true);
    setError(null);
    try {
      const jsPDF = (await import("jspdf")).default;
      const html2canvas = (await import("html2canvas")).default;

      const element = document.getElementById("report-content");
      if (!element) throw new Error("Report content not found");

      const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 15;

      const addBg = () => {
        pdf.setFillColor(2, 6, 23); // slate-950
        pdf.rect(0, 0, pageWidth, pageHeight, "F");
      };

      const writeTitle = (text, y) => {
        pdf.setTextColor(45, 212, 191); // brand-400
        pdf.setFontSize(16);
        pdf.setFont("helvetica", "bold");
        pdf.text(text, margin, y);
      };

      const writeNormal = (text, y, align="left") => {
        pdf.setFontSize(10);
        pdf.setTextColor(226, 232, 240);
        pdf.setFont("helvetica", "normal");
        pdf.text(text, align === "right" ? pageWidth - margin : margin, y, { align });
      };

      // --- PAGE 1: Summary ---
      addBg();
      pdf.setTextColor(45, 212, 191);
      pdf.setFontSize(24);
      pdf.setFont("helvetica", "bold");
      pdf.text("Personal Financial Digital Twin", margin, 40);

      const u = results?.user_summary || {};
      const projYears = (u.retirement_age || 60) - (u.age || 30);

      pdf.setTextColor(148, 163, 184);
      pdf.setFontSize(11);
      pdf.setFont("helvetica", "normal");
      pdf.text(`Prepared for: ${userName || u.name || "User"}`, margin, 55);
      pdf.text(`Date: ${new Date().toLocaleDateString("en-IN")}`, margin, 62);

      const m = results?.metrics || {};
      const a = results?.assumptions || {};
      const d = results?.debug_info || {};
      const e = results?.explainability || {};

      let y = 75;
      
      const summarySentence = e.goal_analysis && e.debt_analysis 
        ? `${e.goal_analysis} ${e.debt_analysis}`
        : "Your current financial position requires structured planning to ensure long-term stability.";
        
      const summaryLinesText = pdf.splitTextToSize(summarySentence, pageWidth - margin * 2);
      pdf.setFontSize(10);
      pdf.setTextColor(226, 232, 240);
      pdf.setFont("helvetica", "italic");
      pdf.text(summaryLinesText, margin, y);
      y += summaryLinesText.length * 5 + 10;

      writeTitle("Financial Summary", y);
      y += 10;

      const summaryLines = [
        ["Net Worth", formatCurrency(m.netWorth ?? 0, true)],
        ["Total Assets", formatCurrency(m.totalAssets ?? 0, true)],
        ["Total Liabilities", formatCurrency(m.totalLiabilities ?? 0, true)],
        ["Monthly Surplus", formatCurrency(m.monthlySurplus ?? 0, true)],
        ["Savings Rate", formatPercent(m.savingsRate ?? 0)],
        ["Target Corpus", formatCurrency(m.targetCorpus ?? 0, true)],
        ["Projected Nominal Corpus", formatCurrency(m.projectedCorpus ?? 0, true)],
        ["Projected Real Corpus", formatCurrency(m.projectedRealCorpus ?? 0, true)],
        ["Success Probability (REAL)", formatPercent(m.successProbabilityReal ?? 0, 1, true)],
        ["Emergency Fund", formatMonths(m.emergencyFundMonths ?? 0)],
        ["Financial Health Score", `${formatPercent(m.healthScore ?? 0).replace("%", "")} / 100`],
      ];

      summaryLines.forEach(([label, value]) => {
        pdf.setTextColor(100, 116, 139);
        pdf.text(label, margin, y);
        writeNormal(value, y, "right");
        y += 8;
      });

      // --- PAGE 2: Assumptions & Limitations ---
      pdf.addPage();
      addBg();
      y = 30;

      writeTitle("Assumptions Used", y);
      y += 10;
      const assumptionsLines = [
        ["Projection Horizon", `${projYears} years (Age ${u.age || 30} to ${u.retirement_age || 60})`],
        ["Inflation Rate", formatPercent(m.inflationAssumption ?? 0)],
        ["Income Growth Assumption", formatPercent(m.incomeGrowthAssumption ?? 0)],
        ["Expected Portfolio Return", formatPercent(m.portfolioExpectedReturn ?? 0)],
        ["Portfolio Volatility", formatPercent(m.portfolioVolatility ?? 0)],
        ["Tax Assumption", "Effective tax rate assumption applied over time"],
        ["Monte Carlo Simulations", "1,000 trials"],
      ];
      assumptionsLines.forEach(([label, value]) => {
        pdf.setTextColor(100, 116, 139);
        pdf.text(label, margin, y);
        writeNormal(value, y, "right");
        y += 8;
      });

      y += 15;
      writeTitle("Real vs Nominal Clarity", y);
      y += 8;
      writeNormal("• Nominal corpus = future face value", y); y += 6;
      writeNormal("• Real corpus = today's purchasing-power equivalent", y); y += 6;
      writeNormal("Formula: real = nominal / (1 + inflation)^years", y); y += 10;

      writeTitle("Target Corpus Method", y);
      y += 8;
      writeNormal("Target = Annual Expenses × 25", y); y += 6;
      writeNormal("This follows a simplified retirement adequacy heuristic assuming constant real consumption.", y); y += 10;

      writeTitle("Model Limitations", y);
      y += 10;
      const limitations = [
        "• Simplified tax modeling",
        "• Assumption-based returns (historical proxies)",
        "• No behavioral modeling (assumes perfect discipline)",
        "• No macroeconomic shocks included in base projections",
        "• Scenario results depend entirely on current inputs and stated assumptions."
      ];
      limitations.forEach((line) => {
        writeNormal(line, y);
        y += 6;
      });

      // --- PAGE 3: Charts & Risk Explanation ---
      const canvas = await html2canvas(element, {
        scale: 1.5,
        backgroundColor: "#020617",
        useCORS: true,
        logging: false,
      });
      const imgData = canvas.toDataURL("image/jpeg", 0.85);
      const imgWidth = pageWidth - margin * 2;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      pdf.addPage();
      addBg();
      y = 30;
      
      writeTitle("Risk Explanation (Monte Carlo Analysis)", y);
      y += 10;
      if (d.final_real_p5) {
        const riskLines = [
          `In adverse scenarios (5th percentile), corpus may fall to ${formatCurrency(d.final_real_p5, true)}.`,
          `Median expected outcome is ${formatCurrency(d.final_real_p50, true)}.`,
          `In favorable scenarios (95th percentile), corpus may reach ${formatCurrency(d.final_real_p95, true)}.`,
        ];
        riskLines.forEach(line => {
          writeNormal(line, y);
          y += 7;
        });
      } else {
        writeNormal("Run a stochastic simulation to see risk percentiles.", y);
        y += 7;
      }

      y += 10;
      // Fit chart image
      const maxImgH = pageHeight - y - margin;
      const renderH = Math.min(imgHeight, maxImgH);
      pdf.addImage(imgData, "JPEG", margin, y, imgWidth, renderH, undefined, "FAST", 0);

      // --- PAGE 4: Scenarios & Recommendations ---
      pdf.addPage();
      addBg();
      y = 30;

      writeTitle("Scenario Comparison", y);
      y += 10;
      
      // Target Context
      writeNormal(`Target Corpus to Achieve: ${formatCurrency(m.targetCorpus ?? 0, true)}`, y);
      y += 8;

      let scenarios = results?.scenarios || [];
      // Sort worst to best by real success probability
      scenarios.sort((a, b) => (a.successProb || 0) - (b.successProb || 0));
      
      const bestGrowth = [...scenarios].sort((a, b) => (b.realCorpus || b.corpus || 0) - (a.realCorpus || a.corpus || 0))[0];
      const bestRisk = [...scenarios].sort((a, b) => (b.successProb || 0) - (a.successProb || 0))[0];

      if (scenarios.length) {
        scenarios.forEach(s => {
          let flags = [];
          if (s.name === bestGrowth?.name) flags.push("Best Growth");
          if (s.name === bestRisk?.name) flags.push("Best Risk-Balanced");
          
          const flagStr = flags.length ? ` [${flags.join(", ")}]` : "";
          
          writeNormal(`• ${s.name}${flagStr}`, y);
          y += 6;
          
          pdf.setTextColor(148, 163, 184);
          const detail = `  Nominal: ${formatCurrency(s.corpus, true)} | Real: ${formatCurrency(s.realCorpus, true)} | Success: ${formatPercent(s.successProb, 1, true)} | Change vs Base: ${formatCurrency(s.changeVsBase, true)}`;
          writeNormal(detail, y);
          y += 8;
        });
      }

      y += 5;
      const recs = results?.recommendations || [];
      writeTitle("Recommendations & Action Plan", y);
      y += 10;
      if (recs.length) {
        recs.forEach((rec, i) => {
          const textLines = pdf.splitTextToSize(`${i + 1}. ${rec}`, pageWidth - margin * 2);
          pdf.setFontSize(10);
          pdf.setTextColor(226, 232, 240);
          pdf.setFont("helvetica", "normal");
          pdf.text(textLines, margin, y);
          y += textLines.length * 6 + 4;
        });
      }

      // Footer
      const totalPages = pdf.internal.getNumberOfPages();
      for (let p = 1; p <= totalPages; p++) {
        pdf.setPage(p);
        pdf.setFontSize(8);
        pdf.setTextColor(71, 85, 105);
        pdf.text(
          "All outputs are model-based estimates under stated assumptions.",
          pageWidth / 2,
          pageHeight - 12,
          { align: "center" }
        );
        pdf.text(
          "Real outcomes depend on returns, inflation, taxation, income stability, and behavioral factors.",
          pageWidth / 2,
          pageHeight - 8,
          { align: "center" }
        );
      }

      pdf.save(`financial-advisory-report-${Date.now()}.pdf`);
    } catch (err) {
      console.error("PDF generation failed:", err);
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
            Generating Advisory Report…
          </>
        ) : (
          <>
            <Download className="w-4 h-4" />
            Download Advisory Report
          </>
        )}
      </button>
      {error && (
        <p className="text-rose-400 font-body text-xs">{error}</p>
      )}
      {!results && (
        <p className="text-slate-500 font-body text-xs flex items-center gap-1">
          <FileText className="w-3 h-3" /> Run simulation first to enable report
        </p>
      )}
    </div>
  );
}
