"""
transaction_event_engine.py - Mutates UserProfile based on transaction events.
=============================================================================
Updates liquid assets, liabilities, or recurring baseline settings based on
strict rule definitions and user-specific corrections.
"""

from typing import List, Tuple, Dict, Any
from app.models.schemas import UserProfile, TransactionEvent
from app.services.financial_metrics import calculate_metrics


class TransactionEventEngine:
    @staticmethod
    def apply_transaction(
        profile: UserProfile, transaction: TransactionEvent
    ) -> Tuple[UserProfile, List[str], str]:
        # Create a deep copy of the profile to avoid mutating the baseline in-place before save
        updated_profile = UserProfile.model_validate(profile.model_dump())
        alerts: List[str] = []
        narrative = ""
        amount = transaction.amount
        is_recurring = transaction.is_recurring
        metadata = transaction.metadata or {}

        # 1. Process mutations by type
        if transaction.transaction_type == "income":
            # Income updates cash/savings
            updated_profile.assets.savings += amount
            narrative = f"Income of ₹{amount:,.2f} added to liquid savings."

            # Only update baseline monthly income if recurring and update_baseline is true
            if is_recurring and metadata.get("update_baseline"):
                # We can add it to other_income or monthly_salary
                updated_profile.income.other_income += amount
                narrative += f" Baseline monthly other income increased by ₹{amount:,.2f}."

        elif transaction.transaction_type == "expense":
            # Expense updates cash/savings
            updated_profile.assets.savings = max(0.0, updated_profile.assets.savings - amount)
            narrative = f"Expense of ₹{amount:,.2f} deducted from liquid savings."

        elif transaction.transaction_type == "investment":
            # Investment decreases savings, increases mutual_funds/stocks
            updated_profile.assets.savings = max(0.0, updated_profile.assets.savings - amount)
            
            # Default to mutual funds unless metadata specifies stocks
            if metadata.get("asset_type") == "stocks":
                updated_profile.assets.stocks += amount
                narrative = f"Investment of ₹{amount:,.2f} transferred from savings to stocks."
            else:
                updated_profile.assets.mutual_funds += amount
                narrative = f"Investment of ₹{amount:,.2f} transferred from savings to mutual funds."

            # Update baseline monthly SIP only if recurring and update_baseline is true
            if is_recurring and metadata.get("update_baseline"):
                updated_profile.investments.sip_amount += amount
                narrative += f" Baseline monthly SIP amount increased by ₹{amount:,.2f}."

        elif transaction.transaction_type == "debt_payment":
            # Debt payment updates cash/savings
            updated_profile.assets.savings = max(0.0, updated_profile.assets.savings - amount)

            # Determine which liability to pay down
            liab_type = metadata.get("debt_type")
            valid_liabs = [
                "credit_card_debt",
                "personal_loan",
                "vehicle_loan",
                "education_loan",
                "home_loan",
                "other_liabilities",
            ]

            # If not specified or invalid, pick the highest interest liability that is currently > 0
            if liab_type not in valid_liabs:
                # Find highest interest rate debt currently > 0
                liab_type = None
                for candidate in valid_liabs:
                    current_val = getattr(updated_profile.liabilities, candidate)
                    if current_val > 0:
                        liab_type = candidate
                        break
                # Fallback to credit_card_debt if all are 0
                if not liab_type:
                    liab_type = "credit_card_debt"

            # Get outstanding principal before payment
            old_principal = getattr(updated_profile.liabilities, liab_type)
            
            # Calculate total liabilities before payment for proportional EMI reduction
            total_liabs_before = sum(
                getattr(updated_profile.liabilities, k) for k in valid_liabs
            )

            # Apply reduction
            paid_amount = min(old_principal, amount)
            new_principal = max(0.0, old_principal - paid_amount)
            setattr(updated_profile.liabilities, liab_type, new_principal)
            
            narrative = f"Debt payment of ₹{amount:,.2f} applied to {liab_type.replace('_', ' ').title()}."
            if paid_amount < amount:
                # Refund remaining amount to savings
                refund = amount - paid_amount
                updated_profile.assets.savings += refund
                narrative += f" Remaining ₹{refund:,.2f} returned to savings (debt fully cleared)."

            # Only reduce EMI if metadata.loan_closed is true or liability becomes zero
            loan_closed_val = metadata.get("loan_closed")
            if isinstance(loan_closed_val, str):
                loan_closed_triggered = loan_closed_val.lower() == "true"
            else:
                loan_closed_triggered = bool(loan_closed_val)
            loan_closed_triggered = loan_closed_triggered or new_principal == 0
            if loan_closed_triggered:
                # Check for explicit EMI reduction in metadata
                explicit_emi_reduction = metadata.get("emi_reduction")
                if explicit_emi_reduction is not None:
                    emi_freed = float(explicit_emi_reduction)
                else:
                    # Estimate freed EMI proportionally
                    if total_liabs_before > 0:
                        emi_freed = updated_profile.expenses.emi_payments * (
                            paid_amount / total_liabs_before
                        )
                    else:
                        emi_freed = 0.0

                updated_profile.expenses.emi_payments = max(
                    0.0, updated_profile.expenses.emi_payments - emi_freed
                )
                narrative += f" Loan closed/cleared! Monthly EMI payments reduced by ₹{emi_freed:,.2f}."

        elif transaction.transaction_type == "emergency":
            # Deducts from emergency fund first, then savings
            ef = updated_profile.assets.emergency_fund
            if ef >= amount:
                updated_profile.assets.emergency_fund -= amount
                narrative = f"Emergency of ₹{amount:,.2f} covered fully from Emergency Fund."
            else:
                updated_profile.assets.emergency_fund = 0.0
                remaining = amount - ef
                updated_profile.assets.savings = max(
                    0.0, updated_profile.assets.savings - remaining
                )
                narrative = (
                    f"Emergency of ₹{amount:,.2f} processed. Emergency Fund fully drained "
                    f"(₹{ef:,.2f}); remaining ₹{remaining:,.2f} deducted from savings."
                )

            alerts.append(f"Emergency event triggered: {transaction.description}. Liquid buffers reduced.")

        elif transaction.transaction_type == "asset_update":
            asset_type = metadata.get("asset_type")
            valid_assets = [
                "savings",
                "emergency_fund",
                "fixed_deposits",
                "stocks",
                "mutual_funds",
                "epf",
                "ppf",
                "nps",
                "gold",
                "real_estate",
                "business_assets",
                "other_assets",
            ]

            if asset_type in valid_assets:
                current_val = getattr(updated_profile.assets, asset_type)
                
                # Check metadata for new_value or delta
                if "new_value" in metadata:
                    new_val = float(metadata["new_value"])
                    setattr(updated_profile.assets, asset_type, new_val)
                    narrative = f"Asset {asset_type.replace('_', ' ').title()} updated to ₹{new_val:,.2f}."
                elif "delta" in metadata:
                    delta = float(metadata["delta"])
                    new_val = max(0.0, current_val + delta)
                    setattr(updated_profile.assets, asset_type, new_val)
                    narrative = f"Asset {asset_type.replace('_', ' ').title()} changed by ₹{delta:,.2f} to ₹{new_val:,.2f}."
                else:
                    # Default: set to transaction.amount
                    setattr(updated_profile.assets, asset_type, amount)
                    narrative = f"Asset {asset_type.replace('_', ' ').title()} updated to ₹{amount:,.2f}."
            else:
                narrative = "Asset update skipped: invalid or missing 'asset_type' in metadata."

        # 2. Recalculate metrics to generate dynamic alerts
        new_metrics = calculate_metrics(updated_profile)

        if new_metrics.emergency_fund_months < 3.0:
            alerts.append(
                f"Your emergency buffer currently covers about {new_metrics.emergency_fund_months:.1f} "
                "months of essential expenses. Strengthening it toward 6 months would improve resilience."
            )
        
        if new_metrics.debt_to_income_ratio > 0.40:
            alerts.append(
                f"EMI payments are using roughly {new_metrics.debt_to_income_ratio*100:.1f}% "
                "of monthly income. Easing this burden over time would free up flexibility."
            )

        if new_metrics.success_probability < 0.50:
            alerts.append(
                "Your current retirement path may need a few adjustments to feel more comfortable. "
                "Increasing SIP or extending the horizon can improve the outlook."
            )

        return updated_profile, alerts, narrative
