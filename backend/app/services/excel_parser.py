import pandas as pd
from io import BytesIO
from typing import Dict, Any
from app.services.transaction_parser import detect_category

def parse_excel_csv(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    if filename.endswith('.csv'):
        df = pd.read_csv(BytesIO(file_bytes))
    else:
        df = pd.read_excel(BytesIO(file_bytes))
        
    df.columns = [c.lower().strip() for c in df.columns]
    
    required = ['date', 'description', 'amount', 'type']
    for req in required:
        if req not in df.columns:
            raise ValueError(f"Missing required column: {req}")

    monthly_income = 0.0
    monthly_expenses = 0.0
    monthly_sip = 0.0
    emi = 0.0
    rent = 0.0
    living = 0.0
    
    df['type'] = df['type'].astype(str).str.lower().str.strip()
    if 'category' not in df.columns:
        df['category'] = df['description'].apply(lambda x: detect_category(str(x)))
    else:
        df['category'] = df['category'].astype(str).str.lower().str.strip()

    summary_messages = []

    for _, row in df.iterrows():
        try:
            amount = float(row['amount'])
        except ValueError:
            continue
            
        t = row['type']
        cat = row['category']
        desc = str(row['description']).lower()
        
        # Determine category if not explicitly clear
        inferred_cat = detect_category(desc + " " + cat)

        if t == 'income' or inferred_cat == 'salary':
            monthly_income += amount
            summary_messages.append(f"Income detected: ₹{amount} ({row['description']})")
        elif t == 'investment' or inferred_cat == 'sip':
            monthly_sip += amount
            summary_messages.append(f"SIP detected: ₹{amount} ({row['description']})")
        elif t == 'expense':
            monthly_expenses += amount
            if inferred_cat == 'emi':
                emi += amount
                summary_messages.append(f"EMI detected: ₹{amount} ({row['description']})")
            elif inferred_cat == 'rent':
                rent += amount
                summary_messages.append(f"Rent detected: ₹{amount} ({row['description']})")
            elif inferred_cat == 'living':
                living += amount
                summary_messages.append(f"Living expense detected: ₹{amount} ({row['description']})")

    surplus = monthly_income - monthly_expenses - monthly_sip - emi

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
