import uuid
from typing import Dict
from app.models.schemas import UserProfile, SimulationResult

users_db: Dict[str, UserProfile] = {}
simulations_db: Dict[str, SimulationResult] = {}

def create_user(profile: UserProfile) -> str:
    user_id = str(uuid.uuid4())
    users_db[user_id] = profile
    return user_id

def get_user(user_id: str) -> UserProfile:
    return users_db.get(user_id)

def save_simulation(result: SimulationResult) -> str:
    sim_id = result.simulation_id
    simulations_db[sim_id] = result
    return sim_id

def get_simulation(sim_id: str) -> SimulationResult:
    return simulations_db.get(sim_id)
