"""Auth router — Google OAuth authentication & onboarding."""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    GoogleAuthRequest,
    OnboardingRequest,
    AuthResponse,
    MessageResponse,
)
from app.services.database import get_supabase
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/google", response_model=AuthResponse)
async def authenticate_google(req: GoogleAuthRequest):
    """
    Authenticate user session with Google OAuth token via Supabase.
    """
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        user_res = sb.auth.get_user(req.access_token)
        if not user_res or not user_res.user:
            raise HTTPException(401, "Invalid Google OAuth session")

        user = user_res.user
        # Fetch profile
        profile = sb.table("profiles").select("name").eq("id", user.id).single().execute()
        name = profile.data.get("name", "") if profile.data else (user.user_metadata.get("full_name") or user.user_metadata.get("name") or "")

        return AuthResponse(
            access_token=req.access_token,
            user_id=user.id,
            email=user.email or "",
            name=name,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Google auth error: {exc}")
        raise HTTPException(401, "Google authentication failed")


@router.post("/logout", response_model=MessageResponse)
async def logout():
    sb = get_supabase()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass
    return MessageResponse(message="Logged out successfully")


@router.post("/onboarding", response_model=MessageResponse)
async def complete_onboarding(req: OnboardingRequest, user_id: str):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        sb.table("profiles").update({
            "interests": req.interests,
            "study_pace": req.study_pace,
            "target_career": req.target_career,
            "onboarding_done": True,
        }).eq("id", user_id).execute()
        return MessageResponse(message="Onboarding complete!")
    except Exception as exc:
        raise HTTPException(400, str(exc))
