import re
from typing import Dict, Any, List
from app.services.transaction_parser import detect_category

def parse_sms_messages(messages: List[str]) -> Dict[str, Any]:
    monthly_income = 0.0
    monthly_expenses = 0.0
    monthly_sip = 0.0
    emi = 0.0
    rent = 0.0
    living = 0.0
    summary_messages = []

    # Simple regex to find INR/Rs amounts
    amount_pattern = re.compile(r'(?:inr|rs\.?|₹)\s*([\d,]+(?:\.\d{1,2})?)', re.IGNORECASE)

    for msg in messages:
        amount_match = amount_pattern.search(msg)
        if not amount_match:
            # Fallback for plain numbers before/after credited/debited
            amount_match = re.search(r'(?:credited|debited).+?([\d,]+(?:\.\d{1,2})?)', msg, re.IGNORECASE)
            if not amount_match:
                amount_match = re.search(r'([\d,]+(?:\.\d{1,2})?).+?(?:credited|debited)', msg, re.IGNORECASE)
                
        if amount_match:
            amt_str = amount_match.group(1).replace(',', '')
            try:
                amount = float(amt_str)
            except ValueError:
                continue
                
            inferred_cat = detect_category(msg)
            
            if 'credit' in msg.lower() or inferred_cat == 'salary':
                monthly_income += amount
                summary_messages.append(f"SMS parsed - Income detected: ₹{amount}")
            elif 'debit' in msg.lower() or 'spent' in msg.lower():
                monthly_expenses += amount
                if inferred_cat == 'sip':
                    monthly_sip += amount
                    summary_messages.append(f"SMS parsed - SIP detected: ₹{amount}")
                elif inferred_cat == 'emi':
                    emi += amount
                    summary_messages.append(f"SMS parsed - EMI detected: ₹{amount}")
                elif inferred_cat == 'rent':
                    rent += amount
                    summary_messages.append(f"SMS parsed - Rent detected: ₹{amount}")
                elif inferred_cat == 'living':
                    living += amount
                    summary_messages.append(f"SMS parsed - Living expense detected: ₹{amount}")
                else:
                    summary_messages.append(f"SMS parsed - General expense detected: ₹{amount}")

    surplus = monthly_income - monthly_expenses

    return {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "monthly_sip": monthly_sip,
        "emi": emi,
        "rent": rent,
        "living_expenses": living,
        "surplus": surplus,
        "summary": summary_messages
    }
