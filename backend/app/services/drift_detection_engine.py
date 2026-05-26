"""
drift_detection_engine.py - Compares planned vs actual financial metrics.
========================================================================
Calculates monthly variances for expenses, SIPs, EMIs, surplus, and emergency
reserves, identifying deviations from budget plans.
"""

from typing import List
from datetime import datetime
from app.models.schemas import UserProfile, TransactionEvent, DriftReport, DriftItem


class DriftDetectionEngine:
    @staticmethod
    def calculate_drift(
        baseline_profile: UserProfile,
        updated_profile: UserProfile,
        transactions: List[TransactionEvent]
    ) -> DriftReport:
        # 1. Filter transactions for the current calendar month
        now = datetime.utcnow()
        current_year_month = f"{now.year:04d}-{now.month:02d}"
        
        current_month_txs = [
            tx for tx in transactions
            if tx.timestamp.startswith(current_year_month) or tx.timestamp[:7] == current_year_month
        ]
        
        # If no transactions in current month, fallback to all transactions to show comparison
        if not current_month_txs:
            current_month_txs = transactions
 
        # 2. Sum up actual figures
        actual_income = 0.0
        actual_expenses = 0.0
        actual_sip = 0.0
        actual_emi = 0.0
        
        # Category expense breakdown
        actual_categories = {
            "living": 0.0,
            "emi": 0.0,
            "insurance": 0.0,
            "education": 0.0,
            "discretionary": 0.0,
            "other": 0.0,
        }
 
        for tx in current_month_txs:
            t_type = tx.transaction_type
            amt = tx.amount
            cat = tx.category.lower().strip()
 
            if t_type == "income":
                actual_income += amt
            elif t_type in ("expense", "emergency"):
                actual_expenses += amt
                # Map category
                if "living" in cat:
                    actual_categories["living"] += amt
                elif "emi" in cat:
                    actual_categories["emi"] += amt
                elif "insurance" in cat:
                    actual_categories["insurance"] += amt
                elif "education" in cat:
                    actual_categories["education"] += amt
                elif "discretionary" in cat or "spend" in cat:
                    actual_categories["discretionary"] += amt
                else:
                    actual_categories["other"] += amt
            elif t_type == "investment":
                actual_sip += amt
            elif t_type == "debt_payment":
                actual_emi += amt
 
        # 3. Get planned monthly values from baseline_profile
        planned_income = (
            baseline_profile.income.monthly_salary
            + baseline_profile.income.bonus / 12
            + baseline_profile.income.side_income
            + baseline_profile.income.rental_income
            + baseline_profile.income.other_income
        )
        
        planned_expenses = (
            baseline_profile.expenses.living_expenses
            + baseline_profile.expenses.emi_payments
            + baseline_profile.expenses.insurance
            + baseline_profile.expenses.education_expenses
            + baseline_profile.expenses.discretionary_spending
            + baseline_profile.expenses.other_expenses
        )
        
        planned_sip = baseline_profile.investments.sip_amount
        planned_emi = baseline_profile.expenses.emi_payments
        planned_surplus = max(0.0, planned_income - planned_expenses - planned_sip)
        
        actual_surplus = actual_income - actual_expenses - actual_sip - actual_emi
        
        planned_ef_months = (
            baseline_profile.assets.emergency_fund / baseline_profile.expenses.essential_expenses
            if baseline_profile.expenses.essential_expenses > 0
            else 0.0
        )
        actual_ef_months = (
            updated_profile.assets.emergency_fund / baseline_profile.expenses.essential_expenses
            if baseline_profile.expenses.essential_expenses > 0
            else planned_ef_months
        )
 
        items: List[DriftItem] = []
        overall_warnings = 0
        overall_criticals = 0
 
        # Helper to append drift items
        def add_drift_item(metric: str, planned: float, actual: float, is_cost: bool):
            nonlocal overall_warnings, overall_criticals
            variance = actual - planned
            variance_pct = (variance / max(1.0, planned)) * 100
 
            status = "on_track"
            description = ""
 
            if is_cost:
                # For costs, higher is worse
                if actual > planned * 1.50:
                    status = "critical"
                    overall_criticals += 1
                    description = f"Critical: Overspent by {variance_pct:.1f}% vs budget."
                elif actual > planned * 1.15:
                    status = "warning"
                    overall_warnings += 1
                    description = f"Warning: Overspent by {variance_pct:.1f}% vs budget."
                else:
                    description = "On track. Under budget limits."
            else:
                # For savings/surplus/SIP, lower is worse
                if actual < planned * 0.50:
                    status = "critical"
                    overall_criticals += 1
                    description = f"Critical: Deficit of {abs(variance_pct):.1f}% vs planned goal."
                elif actual < planned * 0.85:
                    status = "warning"
                    overall_warnings += 1
                    description = f"Warning: Deficit of {abs(variance_pct):.1f}% vs planned goal."
                else:
                    description = "On track. Met or exceeded targets."
 
            items.append(
                DriftItem(
                    metric=metric,
                    planned=round(planned, 2),
                    actual=round(actual, 2),
                    variance=round(variance, 2),
                    status=status,
                    description=description,
                )
            )
 
        # 4. Add key high-level drift items
        add_drift_item("Monthly Expense", planned_expenses, actual_expenses, is_cost=True)
        add_drift_item("SIP (Investments)", planned_sip, actual_sip, is_cost=False)
        add_drift_item("EMI & Debt Service", planned_emi, actual_emi + actual_categories["emi"], is_cost=True)
        add_drift_item("Cash Surplus", planned_surplus, actual_surplus, is_cost=False)
        add_drift_item("Emergency Coverage (Months)", planned_ef_months, actual_ef_months, is_cost=False)
 
        # 5. Add Category-wise expense drift items
        category_mapping = [
            ("Living Expenses", baseline_profile.expenses.living_expenses, actual_categories["living"]),
            ("Insurance Payments", baseline_profile.expenses.insurance, actual_categories["insurance"]),
            ("Education Expenses", baseline_profile.expenses.education_expenses, actual_categories["education"]),
            ("Discretionary Expenses", baseline_profile.expenses.discretionary_spending, actual_categories["discretionary"]),
            ("Other Expenses", baseline_profile.expenses.other_expenses, actual_categories["other"]),
        ]
 
        for label, planned_val, actual_val in category_mapping:
            if planned_val > 0 or actual_val > 0:
                add_drift_item(f"Category: {label}", planned_val, actual_val, is_cost=True)
 
        # Calculate overall status
        if overall_criticals > 0:
            overall_status = "critical"
        elif overall_warnings > 0:
            overall_status = "warning"
        else:
            overall_status = "on_track"
 
        return DriftReport(items=items, overall_status=overall_status)
