from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.schemas import SimulationRequest, UserProfile
from app.services.storage import get_user, save_simulation
from app.services.simulation_engine import run_simulation

router = APIRouter()

class SimulateResponse(BaseModel):
    simulation_id: str
    status: str

@router.post("/simulate", response_model=SimulateResponse)
def simulate(request: SimulationRequest):
    profile = None
    if request.user_id:
        profile = get_user(request.user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
    elif request.profile:
        profile = request.profile
    else:
        raise HTTPException(status_code=400, detail="Must provide user_id or profile")
        
    try:
        result = run_simulation(profile)
        save_simulation(result)
        return SimulateResponse(simulation_id=result.simulation_id, status=result.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
