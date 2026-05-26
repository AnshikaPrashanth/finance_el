import urllib.request
import json
import time
import subprocess
import os

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

def make_request(url, method='GET', body=None):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))
    except Exception as e:
        return 500, {'error': str(e)}

def run_tests():
    print("Step 1: Running user twin simulation and setup")
    status, raw_res = make_request('http://localhost:8000/api/v1/twin/run', 'POST', payload)
    if status != 200:
        print("FAIL: Setup failed", status, raw_res)
        return False
    user_id = raw_res.get('user_id')
    print("SUCCESS: User twin created. User ID:", user_id)

    # 1. Post expense transaction
    print("\nStep 2: Log manual expense transaction (Verify assets update but planned expenses do not)")
    tx_body = {
        'description': 'Premium Coffee & Dessert',
        'amount': 2500.0,
        'category': 'Discretionary',
        'transaction_type': 'expense',
        'source': 'manual',
        'is_recurring': False,
        'metadata': {}
    }
    status, res = make_request(f'http://localhost:8000/api/v1/twin/{user_id}/transaction', 'POST', tx_body)
    if status != 200:
        print("FAIL: Log transaction failed", status, res)
        return False
    
    # Check that updated savings is less than original 150000
    orig_savings = payload['profile']['assets']['savings']
    new_savings = res['updated_profile']['assets']['savings']
    expected_savings = orig_savings - 2500.0
    if new_savings != expected_savings:
        print(f"FAIL: Savings mismatch. Expected {expected_savings}, got {new_savings}")
        return False
    
    # Check that planned expenses (discretionary spending or other) did not change
    orig_discretionary = payload['profile']['expenses']['discretionary_spending']
    new_discretionary = res['updated_profile']['expenses']['discretionary_spending']
    if orig_discretionary != new_discretionary:
        print(f"FAIL: Planned discretionary expenses modified! Expected {orig_discretionary}, got {new_discretionary}")
        return False
    print("SUCCESS: Expense updated cash assets without corrupting planned expenses.")

    # 2. Simulate live event
    print("\nStep 3: Simulate live event")
    status, res = make_request(f'http://localhost:8000/api/v1/twin/{user_id}/simulate-live-event', 'POST')
    if status != 200:
        print("FAIL: Simulate live event failed", status, res)
        return False
    print("SUCCESS: Live event simulated. Event type:", res['transaction']['transaction_type'], "Description:", res['transaction']['description'])
    print("Recent transactions count:", len(res['recent_transactions']))
    print("Drift report items count:", len(res['drift_report']['items']))

    # 3. Get transactions list
    print("\nStep 4: Get list of transactions")
    status, res = make_request(f'http://localhost:8000/api/v1/twin/{user_id}/transactions')
    if status != 200:
        print("FAIL: Get transactions failed", status, res)
        return False
    print("SUCCESS: Listed transactions. Total count:", len(res))

    # 4. Get latest twin state
    print("\nStep 5: Get latest state")
    status, res = make_request(f'http://localhost:8000/api/v1/twin/{user_id}/latest-state')
    if status != 200:
        print("FAIL: Get latest state failed", status, res)
        return False
    print("SUCCESS: Retrieved latest state.")
    print("Overall drift status:", res['drift_report']['overall_status'])
    print("Live alerts generated:", res['alerts'])
    return True

if __name__ == '__main__':
    try:
        success = run_tests()
        if success:
            print("\nALL API TESTS PASSED SUCCESSFULLY!")
        else:
            print("\nSOME API TESTS FAILED!")
    except Exception as e:
        print("Error during tests:", str(e))
