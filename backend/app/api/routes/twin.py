from typing import List
from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    FinancialHistoryResponse,
    SimulationResult,
    TwinRunRequest,
    TransactionEvent,
    TransactionEventCreate,
    TransactionResponse,
    UserProfile,
    DriftReport
)
from app.services.simulation_engine import run_simulation
from app.services.storage import (
    append_history_entry,
    get_history,
    get_latest_simulation,
    get_user,
    save_simulation,
    save_user_profile,
    save_transaction,
    get_transactions,
)
from app.services.stress_test_engine import StressTestEngine, build_state_from_profile
from app.services.transaction_event_engine import TransactionEventEngine
from app.services.drift_detection_engine import DriftDetectionEngine
from app.services.live_transaction_simulator import LiveTransactionSimulator


router = APIRouter()


@router.post("/twin/run", response_model=SimulationResult)
def save_and_run_twin(request: TwinRunRequest):
    try:
        user_id = request.user_id
        if user_id:
            existing = get_user(user_id)
            if existing is None:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            from uuid import uuid4

            user_id = str(uuid4())

        save_user_profile(user_id, request.profile)
        result = run_simulation(request.profile)
        result.user_id = user_id
        result.stress_test = StressTestEngine().run_all(
            build_state_from_profile(request.profile, user_id=user_id),
            baseline_probability=result.metrics.success_probability_real,
        )
        save_simulation(result, user_id=user_id)
        append_history_entry(user_id, request.profile, result)
        result.history = [entry.model_dump() for entry in get_history(user_id)]
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/twin/{user_id}/history", response_model=FinancialHistoryResponse)
def get_twin_history(user_id: str):
    if not get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return FinancialHistoryResponse(
        user_id=user_id,
        entries=get_history(user_id),
    )


@router.get("/twin/{user_id}/latest", response_model=SimulationResult)
def get_latest_twin(user_id: str):
    result = get_latest_simulation(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No simulation found for user")
    result.history = [entry.model_dump() for entry in get_history(user_id)]
    return result


@router.post("/twin/{user_id}/transaction", response_model=TransactionResponse)
def post_transaction(user_id: str, request: TransactionEventCreate):
    profile = get_user(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    transaction = TransactionEvent(
        id=str(uuid.uuid4()),
        user_id=user_id,
        timestamp=datetime.utcnow().isoformat(),
        description=request.description,
        amount=request.amount,
        category=request.category,
        transaction_type=request.transaction_type,
        source=request.source,
        is_recurring=request.is_recurring,
        metadata=request.metadata,
    )
    
    save_transaction(user_id, transaction)
    all_transactions = get_transactions(user_id)
    history = get_history(user_id)
    baseline_profile = history[0].profile if history else profile

    updated_profile, alerts, narrative = TransactionEventEngine.apply_transaction(profile, transaction)
    save_user_profile(user_id, updated_profile)
    
    sim_result = run_simulation(updated_profile)
    sim_result.user_id = user_id
    sim_result.stress_test = StressTestEngine().run_all(
        build_state_from_profile(updated_profile, user_id=user_id),
        baseline_probability=sim_result.metrics.success_probability_real,
    )
    save_simulation(sim_result, user_id=user_id)
    append_history_entry(user_id, updated_profile, sim_result)
    
    updated_metrics = sim_result.metrics
    drift_report = DriftDetectionEngine.calculate_drift(baseline_profile, updated_profile, all_transactions)
    
    return TransactionResponse(
        transaction=transaction,
        updated_profile=updated_profile,
        updated_metrics=updated_metrics,
        simulation_result=sim_result,
        drift_report=drift_report,
        alerts=alerts,
        recommendations=sim_result.recommendations,
        recent_transactions=all_transactions[-10:]
    )


@router.post("/twin/{user_id}/simulate-live-event", response_model=TransactionResponse)
def simulate_live_event(user_id: str):
    profile = get_user(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    transaction = LiveTransactionSimulator.generate_random_event(user_id)
    
    save_transaction(user_id, transaction)
    all_transactions = get_transactions(user_id)
    history = get_history(user_id)
    baseline_profile = history[0].profile if history else profile

    updated_profile, alerts, narrative = TransactionEventEngine.apply_transaction(profile, transaction)
    save_user_profile(user_id, updated_profile)
    
    sim_result = run_simulation(updated_profile)
    sim_result.user_id = user_id
    sim_result.stress_test = StressTestEngine().run_all(
        build_state_from_profile(updated_profile, user_id=user_id),
        baseline_probability=sim_result.metrics.success_probability_real,
    )
    save_simulation(sim_result, user_id=user_id)
    append_history_entry(user_id, updated_profile, sim_result)
    
    updated_metrics = sim_result.metrics
    drift_report = DriftDetectionEngine.calculate_drift(baseline_profile, updated_profile, all_transactions)
    
    return TransactionResponse(
        transaction=transaction,
        updated_profile=updated_profile,
        updated_metrics=updated_metrics,
        simulation_result=sim_result,
        drift_report=drift_report,
        alerts=alerts,
        recommendations=sim_result.recommendations,
        recent_transactions=all_transactions[-10:]
    )


@router.get("/twin/{user_id}/transactions", response_model=List[TransactionEvent])
def get_user_transactions(user_id: str):
    if not get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return get_transactions(user_id)


@router.get("/twin/{user_id}/latest-state", response_model=TransactionResponse)
def get_latest_twin_state(user_id: str):
    profile = get_user(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    sim_result = get_latest_simulation(user_id)
    if not sim_result:
        sim_result = run_simulation(profile)
        sim_result.user_id = user_id
        sim_result.stress_test = StressTestEngine().run_all(
            build_state_from_profile(profile, user_id=user_id),
            baseline_probability=sim_result.metrics.success_probability_real,
        )
        save_simulation(sim_result, user_id=user_id)
        append_history_entry(user_id, profile, sim_result)
        
    all_transactions = get_transactions(user_id)
    history = get_history(user_id)
    baseline_profile = history[0].profile if history else profile
    
    drift_report = DriftDetectionEngine.calculate_drift(baseline_profile, profile, all_transactions)
    
    alerts = []
    if sim_result.metrics.emergency_fund_months < 3.0:
        alerts.append(
            f"Your emergency buffer currently covers about {sim_result.metrics.emergency_fund_months:.1f} "
            "months of essential expenses. Strengthening it toward 6 months would improve resilience."
        )
    if sim_result.metrics.debt_to_income_ratio > 0.40:
        alerts.append(
            f"EMI payments are using roughly {sim_result.metrics.debt_to_income_ratio*100:.1f}% "
            "of monthly income. Easing this burden over time would free up flexibility."
        )
    if sim_result.metrics.success_probability < 0.50:
        alerts.append(
            "Your current retirement path may need a few adjustments to feel more comfortable. "
            "Increasing SIP or extending the horizon can improve the outlook."
        )
        
    last_tx = all_transactions[-1] if all_transactions else TransactionEvent(
        id="",
        user_id=user_id,
        timestamp=datetime.utcnow().isoformat(),
        description="Initial State",
        amount=0.0,
        category="System",
        transaction_type="income",
        source="system",
        is_recurring=False,
        metadata={}
    )
    
    return TransactionResponse(
        transaction=last_tx,
        updated_profile=profile,
        updated_metrics=sim_result.metrics,
        simulation_result=sim_result,
        drift_report=drift_report,
        alerts=alerts,
        recommendations=sim_result.recommendations,
        recent_transactions=all_transactions[-10:]
    )
