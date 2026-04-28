import uuid
from typing import Dict, Any
from datetime import datetime

def create_sync_response(source: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the parsed data into the expected response payload.
    """
    return {
        "sync_id": str(uuid.uuid4()),
        "source": source,
        "last_synced": datetime.now().isoformat(),
        "detected": {
            "monthly_income": parsed_data.get("monthly_income", 0),
            "monthly_expenses": parsed_data.get("monthly_expenses", 0),
            "monthly_sip": parsed_data.get("monthly_sip", 0),
            "emi": parsed_data.get("emi", 0),
            "rent": parsed_data.get("rent", 0),
            "living_expenses": parsed_data.get("living_expenses", 0),
            "surplus": parsed_data.get("surplus", 0)
        },
        "prefill_payload": {
            "income": {
                "salary": str(parsed_data.get("monthly_income", 0))
            },
            "expenses": {
                "living": str(parsed_data.get("living_expenses", 0) + parsed_data.get("rent", 0) or parsed_data.get("monthly_expenses", 0)),
                "emi": str(parsed_data.get("emi", 0))
            },
            "preferences": {
                "sipAmount": str(parsed_data.get("monthly_sip", 0))
            }
        },
        "summary": parsed_data.get("summary", [])
    }
