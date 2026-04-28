import re

def detect_category(text: str, default_type: str = "expense") -> str:
    text = text.lower()
    if any(kw in text for kw in ['salary', 'sal', 'payroll']):
        return "salary"
    if any(kw in text for kw in ['sip', 'mutual fund', 'mf', 'zerodha', 'groww', 'investment']):
        return "sip"
    if any(kw in text for kw in ['rent', 'owner']):
        return "rent"
    if any(kw in text for kw in ['emi', 'loan', 'mortgage', 'bajaj']):
        return "emi"
    if any(kw in text for kw in ['grocery', 'supermarket', 'mart', 'swiggy', 'zomato', 'living']):
        return "living"
    if any(kw in text for kw in ['insurance', 'lic', 'premium']):
        return "insurance"
    if any(kw in text for kw in ['amazon', 'flipkart', 'myntra', 'zara', 'shopping', 'movie', 'pvr']):
        return "discretionary"
    return "other"
