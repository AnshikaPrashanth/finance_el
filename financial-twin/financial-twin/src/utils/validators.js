/**
 * Validate the entire multi-step form.
 * Returns an errors object: { fieldPath: "error message" }
 */
export function validateForm(formData) {
  const errors = {};

  // --- Personal ---
  const p = formData.personal || {};
  if (!p.fullName?.trim()) errors["personal.fullName"] = "Full name is required";
  if (!p.age || p.age < 18 || p.age > 80)
    errors["personal.age"] = "Age must be between 18 and 80";
  if (!p.retirementAge || Number(p.retirementAge) <= Number(p.age))
    errors["personal.retirementAge"] = "Retirement age must be greater than current age";
  if (!p.city?.trim()) errors["personal.city"] = "City is required";

  // --- Income ---
  const i = formData.income || {};
  if (!i.salary || Number(i.salary) <= 0)
    errors["income.salary"] = "Monthly salary must be greater than 0";
  if (i.bonus && Number(i.bonus) < 0)
    errors["income.bonus"] = "Cannot be negative";

  // --- Expenses ---
  const e = formData.expenses || {};
  if (!e.living || Number(e.living) <= 0)
    errors["expenses.living"] = "Monthly living expenses required";

  // --- Preferences ---
  const pr = formData.preferences || {};
  if (!pr.sipAmount || Number(pr.sipAmount) < 0)
    errors["preferences.sipAmount"] = "SIP amount cannot be negative";
  if (!pr.expectedReturn || Number(pr.expectedReturn) < 1 || Number(pr.expectedReturn) > 30)
    errors["preferences.expectedReturn"] = "Expected return must be between 1% and 30%";
  if (!pr.inflation || Number(pr.inflation) < 1 || Number(pr.inflation) > 20)
    errors["preferences.inflation"] = "Inflation must be between 1% and 20%";
  if (!pr.investmentHorizon || Number(pr.investmentHorizon) < 1)
    errors["preferences.investmentHorizon"] = "Investment horizon is required";
  if (!pr.targetCorpus || Number(pr.targetCorpus) <= 0)
    errors["preferences.targetCorpus"] = "Target corpus is required";

  // --- Asset allocation must sum to 100 ---
  const eq = Number(pr.equityPct) || 0;
  const debt = Number(pr.debtPct) || 0;
  const gold = Number(pr.goldPct) || 0;
  const total = eq + debt + gold;
  if (total !== 100) {
    errors["preferences.allocation"] = `Allocation must sum to 100% (currently ${total}%)`;
  }

  return errors;
}

/**
 * Check if a value is a valid positive number.
 */
export function isPositiveNumber(value) {
  return !isNaN(value) && Number(value) >= 0;
}

/**
 * Check if form step is valid (returns true if no errors for that step).
 */
export function isStepValid(errors, stepPrefix) {
  return !Object.keys(errors).some((k) => k.startsWith(stepPrefix));
}
