import React, { useState, useEffect } from "react";
import { ChevronRight, ChevronLeft, RotateCcw, Play } from "lucide-react";
import { validateForm, isStepValid } from "../utils/validators";

// ─── Default form state ──────────────────────────────────────────────────────
const DEFAULT_FORM = {
  personal: {
    fullName: "Rahul Kumar",
    age: "29",
    retirementAge: "60",
    city: "Chennai",
    country: "India",
    maritalStatus: "married",
    dependents: "2",
  },

  income: {
    salary: "55000",
    bonus: "50000",
    sideIncome: "3000",
    rentalIncome: "0",
    otherIncome: "0",
  },

  expenses: {
    living: "25000",
    emi: "10000",
    insurance: "2500",
    education: "3000",
    discretionary: "5000",
    other: "2000",
  },

  assets: {
    savings: "80000",
    emergencyFund: "150000",
    fd: "100000",
    stocks: "50000",
    mutualFunds: "200000",
    epfPpf: "250000",
    gold: "75000",
    realEstate: "0",
    business: "0",
    otherAssets: "0",
  },

  liabilities: {
    homeLoan: "0",
    personalLoan: "50000",
    creditCard: "10000",
    vehicleLoan: "250000",
    educationLoan: "0",
    otherLiabilities: "0",
  },

  preferences: {
    sipAmount: "8000",
    expectedReturn: "11",
    inflation: "6",
    riskAppetite: "moderate",
    investmentHorizon: "25",
    targetCorpus: "25000000",
    goalType: "retirement",

    equityPct: "50",
    debtPct: "40",
    goldPct: "10",

    insuranceCoverage: "5000000",
  },
};
const STEPS = [
  { id: "personal", label: "Personal", icon: "👤" },
  { id: "income", label: "Income", icon: "💰" },
  { id: "expenses", label: "Expenses", icon: "🧾" },
  { id: "assets", label: "Assets", icon: "📈" },
  { id: "liabilities", label: "Liabilities", icon: "🏦" },
  { id: "preferences", label: "Preferences", icon: "⚙️" },
];

// ─── Field component ──────────────────────────────────────────────────────────
function Field({ label, name, type = "number", value, onChange, error, min, placeholder, hint, prefix }) {
  return (
    <div>
      <label className="block text-slate-400 font-body text-xs uppercase tracking-wider mb-1.5">
        {label}
      </label>
      <div className="relative">
        {prefix && (
          <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 font-body text-sm">
            {prefix}
          </span>
        )}
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          min={min}
          placeholder={placeholder}
          className={`w-full rounded-xl bg-slate-800/80 border ${
            error ? "border-rose-500" : "border-slate-700/60"
          } ${prefix ? "pl-8" : "px-4"} px-4 py-2.5 text-slate-100 font-body text-sm placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 transition-colors`}
        />
      </div>
      {error && <p className="text-rose-400 font-body text-xs mt-1">{error}</p>}
      {hint && !error && <p className="text-slate-600 font-body text-xs mt-1">{hint}</p>}
    </div>
  );
}

function SelectField({ label, name, value, onChange, options, error }) {
  return (
    <div>
      <label className="block text-slate-400 font-body text-xs uppercase tracking-wider mb-1.5">
        {label}
      </label>
      <select
        name={name}
        value={value}
        onChange={onChange}
        className={`w-full rounded-xl bg-slate-800/80 border ${
          error ? "border-rose-500" : "border-slate-700/60"
        } px-4 py-2.5 text-slate-100 font-body text-sm focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 transition-colors appearance-none`}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value} className="bg-slate-900">
            {o.label}
          </option>
        ))}
      </select>
      {error && <p className="text-rose-400 font-body text-xs mt-1">{error}</p>}
    </div>
  );
}

// ─── Step subforms ────────────────────────────────────────────────────────────
function PersonalStep({ data, onChange, errors }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <div className="sm:col-span-2">
        <Field label="Full Name" name="fullName" type="text" value={data.fullName}
          onChange={onChange} error={errors["personal.fullName"]} placeholder="e.g. Priya Sharma" />
      </div>
      <Field label="Current Age" name="age" value={data.age} onChange={onChange}
        error={errors["personal.age"]} min={18} placeholder="30" />
      <Field label="Retirement Age" name="retirementAge" value={data.retirementAge}
        onChange={onChange} error={errors["personal.retirementAge"]} min={40} placeholder="60" />
      <Field label="City" name="city" type="text" value={data.city} onChange={onChange}
        error={errors["personal.city"]} placeholder="Chennai" />
      <Field label="Country" name="country" type="text" value={data.country}
        onChange={onChange} placeholder="India" />
      <SelectField label="Marital Status" name="maritalStatus" value={data.maritalStatus}
        onChange={onChange} options={[
          { value: "single", label: "Single" },
          { value: "married", label: "Married" },
          { value: "divorced", label: "Divorced" },
        ]} />
      <SelectField label="Dependents" name="dependents" value={data.dependents}
        onChange={onChange} options={[0,1,2,3,4,5].map(n => ({ value: String(n), label: String(n) }))} />
    </div>
  );
}

function IncomeStep({ data, onChange, errors }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <Field label="Monthly Salary (₹)" name="salary" value={data.salary} onChange={onChange}
        error={errors["income.salary"]} min={0} placeholder="75000" prefix="₹" />
      <Field label="Annual Bonus (₹)" name="bonus" value={data.bonus} onChange={onChange}
        error={errors["income.bonus"]} min={0} placeholder="0" prefix="₹" />
      <Field label="Side Income / Month (₹)" name="sideIncome" value={data.sideIncome}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Rental Income / Month (₹)" name="rentalIncome" value={data.rentalIncome}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Other Income / Month (₹)" name="otherIncome" value={data.otherIncome}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
    </div>
  );
}

function ExpensesStep({ data, onChange, errors }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <Field label="Monthly Living Expenses (₹)" name="living" value={data.living}
        onChange={onChange} error={errors["expenses.living"]} min={0} placeholder="35000" prefix="₹" />
      <Field label="EMI / Debt Payments (₹)" name="emi" value={data.emi} onChange={onChange}
        min={0} placeholder="0" prefix="₹" />
      <Field label="Insurance Premiums / Month (₹)" name="insurance" value={data.insurance}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Education Expenses / Month (₹)" name="education" value={data.education}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Discretionary Spending (₹)" name="discretionary" value={data.discretionary}
        onChange={onChange} min={0} placeholder="5000" prefix="₹" />
      <Field label="Other Expenses (₹)" name="other" value={data.other} onChange={onChange}
        min={0} placeholder="0" prefix="₹" />
    </div>
  );
}

function AssetsStep({ data, onChange }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <Field label="Savings Account (₹)" name="savings" value={data.savings} onChange={onChange}
        min={0} placeholder="200000" prefix="₹" />
      <Field label="Emergency Fund (₹)" name="emergencyFund" value={data.emergencyFund}
        onChange={onChange} min={0} placeholder="150000" prefix="₹" />
      <Field label="Fixed Deposits (₹)" name="fd" value={data.fd} onChange={onChange}
        min={0} placeholder="0" prefix="₹" />
      <Field label="Stocks (₹)" name="stocks" value={data.stocks} onChange={onChange}
        min={0} placeholder="0" prefix="₹" />
      <Field label="Mutual Funds (₹)" name="mutualFunds" value={data.mutualFunds}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="EPF / PPF / NPS (₹)" name="epfPpf" value={data.epfPpf} onChange={onChange}
        min={0} placeholder="0" prefix="₹" />
      <Field label="Gold (₹)" name="gold" value={data.gold} onChange={onChange}
        min={0} placeholder="0" prefix="₹" />
      <Field label="Real Estate (₹)" name="realEstate" value={data.realEstate}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Business Assets (₹)" name="business" value={data.business}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Other Assets (₹)" name="otherAssets" value={data.otherAssets}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
    </div>
  );
}

function LiabilitiesStep({ data, onChange }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <Field label="Home Loan Outstanding (₹)" name="homeLoan" value={data.homeLoan}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Personal Loan (₹)" name="personalLoan" value={data.personalLoan}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Credit Card Debt (₹)" name="creditCard" value={data.creditCard}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Vehicle Loan (₹)" name="vehicleLoan" value={data.vehicleLoan}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Education Loan (₹)" name="educationLoan" value={data.educationLoan}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
      <Field label="Other Liabilities (₹)" name="otherLiabilities" value={data.otherLiabilities}
        onChange={onChange} min={0} placeholder="0" prefix="₹" />
    </div>
  );
}

function PreferencesStep({ data, onChange, errors }) {
  const eq = Number(data.equityPct) || 0;
  const debt = Number(data.debtPct) || 0;
  const gold = Number(data.goldPct) || 0;
  const total = eq + debt + gold;
  const allocationOk = total === 100;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <Field label="Monthly SIP (₹)" name="sipAmount" value={data.sipAmount}
        onChange={onChange} error={errors["preferences.sipAmount"]} min={0} placeholder="10000" prefix="₹" />
      <Field label="Expected Annual Return (%)" name="expectedReturn" value={data.expectedReturn}
        onChange={onChange} error={errors["preferences.expectedReturn"]} min={1} max={30} placeholder="12" />
      <Field label="Inflation Assumption (%)" name="inflation" value={data.inflation}
        onChange={onChange} error={errors["preferences.inflation"]} min={1} max={20} placeholder="6" />
      <Field label="Investment Horizon (years)" name="investmentHorizon" value={data.investmentHorizon}
        onChange={onChange} error={errors["preferences.investmentHorizon"]} min={1} placeholder="20" />
      <Field label="Target Corpus (₹)" name="targetCorpus" value={data.targetCorpus}
        onChange={onChange} error={errors["preferences.targetCorpus"]} min={0} placeholder="10000000" prefix="₹" />
      <Field label="Insurance Coverage (₹)" name="insuranceCoverage" value={data.insuranceCoverage}
        onChange={onChange} min={0} placeholder="5000000" prefix="₹" />
      <SelectField label="Risk Appetite" name="riskAppetite" value={data.riskAppetite}
        onChange={onChange} options={[
          { value: "conservative", label: "Conservative" },
          { value: "moderate", label: "Moderate" },
          { value: "aggressive", label: "Aggressive" },
        ]} />
      <SelectField label="Goal Type" name="goalType" value={data.goalType}
        onChange={onChange} options={[
          { value: "retirement", label: "Retirement" },
          { value: "education", label: "Child Education" },
          { value: "house", label: "Buy a House" },
          { value: "wealth", label: "Wealth Creation" },
          { value: "other", label: "Other" },
        ]} />

      {/* Allocation inputs */}
      <div className="sm:col-span-2">
        <p className="text-slate-400 font-body text-xs uppercase tracking-wider mb-3">
          Asset Allocation (must total 100%)
        </p>
        <div className="grid grid-cols-3 gap-4">
          <Field label="Equity (%)" name="equityPct" value={data.equityPct}
            onChange={onChange} min={0} max={100} placeholder="60" />
          <Field label="Debt (%)" name="debtPct" value={data.debtPct}
            onChange={onChange} min={0} max={100} placeholder="30" />
          <Field label="Gold (%)" name="goldPct" value={data.goldPct}
            onChange={onChange} min={0} max={100} placeholder="10" />
        </div>
        <div className={`mt-2 flex items-center gap-2 text-xs font-body ${allocationOk ? "text-emerald-400" : "text-amber-400"}`}>
          <div className={`w-2 h-2 rounded-full ${allocationOk ? "bg-emerald-400" : "bg-amber-400"}`} />
          Total: {total}% {allocationOk ? "✓" : "(must be 100%)"}
        </div>
        {errors["preferences.allocation"] && (
          <p className="text-rose-400 text-xs mt-1">{errors["preferences.allocation"]}</p>
        )}
      </div>
    </div>
  );
}

/**
 * Merge initial data (from API sync) with form structure
 */
function mergeInitialData(defaultForm, syncData) {
  if (!syncData || !syncData.prefill_payload) return defaultForm;
  
  const { prefill_payload } = syncData;
  
  return {
    ...defaultForm,
    income: {
      ...defaultForm.income,
      salary: String(prefill_payload.income?.salary || defaultForm.income.salary),
    },
    expenses: {
      ...defaultForm.expenses,
      living: String(prefill_payload.expenses?.living || defaultForm.expenses.living),
      emi: String(prefill_payload.expenses?.emi || defaultForm.expenses.emi),
    },
    preferences: {
      ...defaultForm.preferences,
      sipAmount: String(prefill_payload.preferences?.sipAmount || defaultForm.preferences.sipAmount),
    },
  };
}

// ─── Main component ───────────────────────────────────────────────────────────
export default function InputForm({ onSubmit, isSubmitting, submitLabel = "Run Simulation", initialData = null }) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState(() => {
    return initialData ? mergeInitialData(DEFAULT_FORM, initialData) : DEFAULT_FORM;
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState(false);

  // Persist form to localStorage
  useEffect(() => {
    localStorage.setItem("fin_twin_form", JSON.stringify(form));
  }, [form]);

  const currentStepId = STEPS[step].id;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [currentStepId]: { ...prev[currentStepId], [name]: value },
    }));
  };

  const handleNext = () => {
    const allErrors = validateForm(form);
    const stepErrors = Object.fromEntries(
      Object.entries(allErrors).filter(([k]) => k.startsWith(currentStepId))
    );
    if (Object.keys(stepErrors).length > 0) {
      setErrors(allErrors);
      return;
    }
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };

  const handleBack = () => setStep((s) => Math.max(s - 1, 0));

  const handleReset = () => {
    if (window.confirm("Reset all form data?")) {
      setForm(DEFAULT_FORM);
      setStep(0);
      setErrors({});
      localStorage.removeItem("fin_twin_form");
    }
  };

  const handleSubmit = () => {
    const allErrors = validateForm(form);
    if (Object.keys(allErrors).length > 0) {
      setErrors(allErrors);
      // Jump to first errored step
      const firstErrStep = STEPS.findIndex((s) =>
        Object.keys(allErrors).some((k) => k.startsWith(s.id))
      );
      if (firstErrStep !== -1) setStep(firstErrStep);
      return;
    }
    setErrors({});
    onSubmit(form);
  };

  const stepData = form[currentStepId];
  const isLastStep = step === STEPS.length - 1;

  return (
    <div className="rounded-2xl bg-slate-900/70 border border-slate-800/80 backdrop-blur-sm overflow-hidden">
      {/* Step tabs */}
      <div className="border-b border-slate-800/80 px-6 pt-5 pb-0">
        <div className="flex gap-1 overflow-x-auto pb-0 scrollbar-hide">
          {STEPS.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setStep(i)}
              className={`flex items-center gap-1.5 px-4 py-2.5 rounded-t-xl text-xs font-body font-medium whitespace-nowrap transition-all border-b-2 ${
                i === step
                  ? "bg-slate-800/70 text-brand-300 border-brand-500"
                  : "text-slate-500 border-transparent hover:text-slate-300"
              }`}
            >
              <span>{s.icon}</span>
              {s.label}
              {Object.keys(errors).some((k) => k.startsWith(s.id)) && (
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Form content */}
      <div className="p-6 min-h-[340px]">
        <div className="animate-slide-up" key={currentStepId}>
          {currentStepId === "personal" && (
            <PersonalStep data={stepData} onChange={handleChange} errors={errors} />
          )}
          {currentStepId === "income" && (
            <IncomeStep data={stepData} onChange={handleChange} errors={errors} />
          )}
          {currentStepId === "expenses" && (
            <ExpensesStep data={stepData} onChange={handleChange} errors={errors} />
          )}
          {currentStepId === "assets" && (
            <AssetsStep data={stepData} onChange={handleChange} />
          )}
          {currentStepId === "liabilities" && (
            <LiabilitiesStep data={stepData} onChange={handleChange} />
          )}
          {currentStepId === "preferences" && (
            <PreferencesStep data={stepData} onChange={handleChange} errors={errors} />
          )}
        </div>
      </div>

      {/* Navigation footer */}
      <div className="border-t border-slate-800/80 px-6 py-4 flex items-center justify-between">
        <div className="flex gap-2">
          {step > 0 && (
            <button
              onClick={handleBack}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white font-body text-sm font-medium transition-colors"
            >
              <ChevronLeft className="w-4 h-4" /> Back
            </button>
          )}
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-slate-500 hover:text-slate-300 font-body text-sm transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-slate-600 font-body text-xs">
            Step {step + 1} of {STEPS.length}
          </span>
          {isLastStep ? (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-60 disabled:cursor-not-allowed text-white font-body text-sm font-semibold transition-all shadow-lg shadow-brand-900/40"
            >
              {isSubmitting ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {isSubmitting ? "Running…" : submitLabel}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-white font-body text-sm font-medium transition-colors"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
