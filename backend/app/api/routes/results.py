from fastapi import APIRouter, HTTPException
from app.models.schemas import SimulationResult
from app.services.storage import get_simulation

router = APIRouter()

@router.get("/results/{simulation_id}", response_model=SimulationResult)
def get_results(simulation_id: str):
    result = get_simulation(simulation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return result
