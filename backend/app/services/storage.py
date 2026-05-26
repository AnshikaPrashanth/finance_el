import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.schemas import FinancialHistoryEntry, SimulationResult, UserProfile, TransactionEvent


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DB_PATH = DATA_DIR / "storage.json"


def _default_db() -> Dict[str, Any]:
    return {
        "users": {},
        "simulations": {},
        "history": {},
        "latest_simulation_by_user": {},
        "transactions": {},
    }


def _load_db() -> Dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        return _default_db()
    try:
        return json.loads(DB_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _default_db()


def _save_db(db: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(db, indent=2), encoding="utf-8")


def create_user(profile: UserProfile) -> str:
    user_id = str(uuid.uuid4())
    save_user_profile(user_id, profile)
    return user_id


def save_user_profile(user_id: str, profile: UserProfile) -> str:
    db = _load_db()
    db["users"][user_id] = profile.model_dump()
    _save_db(db)
    return user_id


def get_user(user_id: str) -> Optional[UserProfile]:
    db = _load_db()
    payload = db["users"].get(user_id)
    return UserProfile.model_validate(payload) if payload else None


def save_simulation(result: SimulationResult, user_id: Optional[str] = None) -> str:
    db = _load_db()
    sim_id = result.simulation_id
    result_payload = result.model_dump()
    if user_id:
        result_payload["user_id"] = user_id
        db["latest_simulation_by_user"][user_id] = sim_id
    db["simulations"][sim_id] = result_payload
    _save_db(db)
    return sim_id


def get_simulation(sim_id: str) -> Optional[SimulationResult]:
    db = _load_db()
    payload = db["simulations"].get(sim_id)
    return SimulationResult.model_validate(payload) if payload else None


def get_latest_simulation_id(user_id: str) -> Optional[str]:
    db = _load_db()
    return db["latest_simulation_by_user"].get(user_id)


def get_latest_simulation(user_id: str) -> Optional[SimulationResult]:
    sim_id = get_latest_simulation_id(user_id)
    return get_simulation(sim_id) if sim_id else None


def append_history_entry(
    user_id: str,
    profile: UserProfile,
    simulation: SimulationResult,
) -> FinancialHistoryEntry:
    db = _load_db()
    entry = FinancialHistoryEntry(
        record_id=str(uuid.uuid4()),
        user_id=user_id,
        timestamp=simulation.debug_info.get("generated_at", "") if simulation.debug_info else "",
        simulation_id=simulation.simulation_id,
        profile=profile,
        metrics=simulation.metrics.model_dump(),
    )
    db["history"].setdefault(user_id, []).append(entry.model_dump())
    _save_db(db)
    return entry


def get_history(user_id: str) -> List[FinancialHistoryEntry]:
    db = _load_db()
    entries = db["history"].get(user_id, [])
    return [FinancialHistoryEntry.model_validate(item) for item in entries]


def save_transaction(user_id: str, transaction: TransactionEvent) -> None:
    db = _load_db()
    db.setdefault("transactions", {}).setdefault(user_id, []).append(transaction.model_dump())
    _save_db(db)


def get_transactions(user_id: str) -> List[TransactionEvent]:
    db = _load_db()
    payloads = db.get("transactions", {}).get(user_id, [])
    return [TransactionEvent.model_validate(p) for p in payloads]
