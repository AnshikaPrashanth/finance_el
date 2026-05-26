"""
live_transaction_simulator.py - Simulates realistic financial transaction events.
================================================================================
Generates random or scenario-based transactions (salary, expenses, SIPs, debt,
emergencies) for live digital twin updates.
"""

import random
import uuid
from datetime import datetime
from app.models.schemas import TransactionEvent


class LiveTransactionSimulator:
    EVENTS = [
        {
            "description": "Monthly Salary Credit",
            "category": "Salary",
            "transaction_type": "income",
            "source": "live_simulator",
            "base_amount": 95000.0,
            "amount_variation": 5000.0,
            "is_recurring": True,
            "metadata": {"update_baseline": False},
        },
        {
            "description": "Premium Dining Out & Lounge",
            "category": "Discretionary",
            "transaction_type": "expense",
            "source": "live_simulator",
            "base_amount": 4200.0,
            "amount_variation": 1800.0,
            "is_recurring": False,
            "metadata": {},
        },
        {
            "description": "Supermarket Weekly Groceries",
            "category": "Living",
            "transaction_type": "expense",
            "source": "live_simulator",
            "base_amount": 3500.0,
            "amount_variation": 1000.0,
            "is_recurring": False,
            "metadata": {},
        },
        {
            "description": "Mutual Fund SIP Installment",
            "category": "SIP",
            "transaction_type": "investment",
            "source": "live_simulator",
            "base_amount": 15000.0,
            "amount_variation": 0.0,
            "is_recurring": True,
            "metadata": {"update_baseline": False, "asset_type": "mutual_funds"},
        },
        {
            "description": "Emergency Root Canal Medical Bill",
            "category": "Emergency",
            "transaction_type": "emergency",
            "source": "live_simulator",
            "base_amount": 18000.0,
            "amount_variation": 4000.0,
            "is_recurring": False,
            "metadata": {},
        },
        {
            "description": "Extra Credit Card Debt Prepayment",
            "category": "EMI",
            "transaction_type": "debt_payment",
            "source": "live_simulator",
            "base_amount": 25000.0,
            "amount_variation": 5000.0,
            "is_recurring": False,
            "metadata": {"debt_type": "credit_card_debt", "loan_closed": True},
        },
        {
            "description": "Broadband Internet Monthly Bill",
            "category": "Living",
            "transaction_type": "expense",
            "source": "live_simulator",
            "base_amount": 1200.0,
            "amount_variation": 100.0,
            "is_recurring": True,
            "metadata": {},
        },
        {
            "description": "Purchase of Digital Gold Portfolio",
            "category": "Gold",
            "transaction_type": "asset_update",
            "source": "live_simulator",
            "base_amount": 8000.0,
            "amount_variation": 2000.0,
            "is_recurring": False,
            "metadata": {"asset_type": "gold", "delta": 8000.0},
        },
        {
            "description": "Freelance Project Milestone Bonus",
            "category": "Salary",
            "transaction_type": "income",
            "source": "live_simulator",
            "base_amount": 35000.0,
            "amount_variation": 10000.0,
            "is_recurring": False,
            "metadata": {},
        },
    ]

    @classmethod
    def generate_random_event(cls, user_id: str) -> TransactionEvent:
        event_template = random.choice(cls.EVENTS)
        
        # Calculate amount with random variation
        base_amt = event_template["base_amount"]
        variation = event_template["amount_variation"]
        amount = base_amt + random.uniform(-variation, variation) if variation > 0 else base_amt
        amount = round(amount, 2)
        
        return TransactionEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            description=event_template["description"],
            amount=amount,
            category=event_template["category"],
            transaction_type=event_template["transaction_type"],
            source=event_template["source"],
            is_recurring=event_template["is_recurring"],
            metadata=event_template["metadata"],
        )
