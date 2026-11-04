"""Dashboard router — Facade pattern."""
from fastapi import APIRouter, HTTPException, Query
from app.patterns.structural.learning_facade import LearningPlatformFacade
from app.services.database import get_supabase

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(user_id: str = Query(...)):
    sb = get_supabase()
    facade = LearningPlatformFacade(supabase_client=sb)
    return await facade.get_dashboard_data(user_id)
