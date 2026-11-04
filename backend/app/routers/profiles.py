"""Profile router."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ProfileResponse, ProfileUpdate, MessageResponse
from app.services.database import get_supabase
import logging

router = APIRouter(prefix="/profiles", tags=["profiles"])
logger = logging.getLogger(__name__)


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        res = sb.table("profiles").select("*").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            return ProfileResponse(**res.data[0])
        # Default fallback profile if row does not exist yet
        return ProfileResponse(
            id=user_id,
            name="Student",
            interests=[],
            study_pace="moderate",
            target_career="",
            streak_days=0,
            onboarding_done=False,
        )
    except Exception as exc:
        logger.error(f"Get profile error: {exc}")
        return ProfileResponse(
            id=user_id,
            name="Student",
            interests=[],
            study_pace="moderate",
            target_career="",
            streak_days=0,
            onboarding_done=False,
        )


@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(user_id: str, req: ProfileUpdate):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        update_data = req.model_dump(exclude_none=True)
        sb.table("profiles").update(update_data).eq("id", user_id).execute()
        res = sb.table("profiles").select("*").eq("id", user_id).single().execute()
        return ProfileResponse(**res.data)
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.get("/{user_id}/achievements")
async def get_achievements(user_id: str):
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("achievements").select("*").eq("user_id", user_id).order("earned_at", desc=True).execute()
        return res.data or []
    except Exception as exc:
        logger.error(f"Get achievements error: {exc}")
        return []
