from fastapi import APIRouter, HTTPException
from app.models.schemas import UserProfile, UserCreateResponse
from app.services.storage import create_user

router = APIRouter()

@router.post("/create-user", response_model=UserCreateResponse)
def create_new_user(profile: UserProfile):
    try:
        user_id = create_user(profile)
        return UserCreateResponse(user_id=user_id, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
