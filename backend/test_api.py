import urllib.request
import json

payload = {
    'profile': {
        'personal': {
            'name': 'Test User',
            'age': 32,
            'retirement_age': 60,
            'city': 'Bangalore',
            'marital_status': 'married',
            'dependents': 1
        },
        'income': {
            'monthly_salary': 120000,
            'bonus': 100000,
            'side_income': 0,
            'rental_income': 0,
            'other_income': 0
        },
        'expenses': {
            'living_expenses': 45000,
            'emi_payments': 15000,
            'insurance': 3000,
            'education_expenses': 5000,
            'discretionary_spending': 10000,
            'other_expenses': 0
        },
        'assets': {
            'savings': 150000,
            'emergency_fund': 300000,
            'fixed_deposits': 200000,
            'stocks': 400000,
            'mutual_funds': 750000,
            'epf': 600000,
            'ppf': 0,
            'nps': 0,
            'gold': 100000,
            'real_estate': 0,
            'business_assets': 0,
            'other_assets': 0
        },
        'liabilities': {
            'home_loan': 0,
            'personal_loan': 0,
            'vehicle_loan': 400000,
            'education_loan': 0,
            'credit_card_debt': 15000,
            'other_liabilities': 0
        },
        'investments': {
            'sip_amount': 25000,
            'expected_annual_return': 12.0,
            'inflation_rate': 6.0,
            'target_corpus': 40000000,
            'risk_appetite': 'moderate',
            'asset_allocation': {'equity': 60, 'debt': 30, 'gold': 10},
            'investment_horizon': 28,
            'goals': ['retirement']
        }
    }
}

try:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/api/v1/simulate', data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print('Status:', response.status)
        print('Response:', response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('Status:', e.code)
    print('Error:', e.read().decode('utf-8'))
except Exception as e:
    print('Error:', str(e))
