"""Study Plans router — Builder pattern + Command pattern."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import StudyPlanCreate, StudyPlanResponse, StudyPlanItemUpdate, MessageResponse
from app.services.database import get_supabase, get_service_supabase
from app.patterns.behavioral.commands import CreateStudyPlanCommand, command_invoker
import logging

router = APIRouter(prefix="/study-plans", tags=["study-plans"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[StudyPlanResponse])
async def list_study_plans(user_id: str = Query(...)):
    sb = get_service_supabase() or get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        res = sb.table("study_plans").select("*, study_plan_items(*)").eq("user_id", user_id).order("created_at", desc=True).execute()
        plans = []
        for p in (res.data or []):
            items = p.pop("study_plan_items", []) or []
            plans.append(StudyPlanResponse(**p, items=items))
        return plans
    except Exception as exc:
        logger.error(f"List study plans error: {exc}")
        raise HTTPException(500, str(exc))


@router.post("", response_model=StudyPlanResponse)
async def create_study_plan(req: StudyPlanCreate, user_id: str = Query(...)):
    """Build study plan via CreateStudyPlanCommand → StudyPlanBuilder."""
    sb = get_service_supabase() or get_supabase()
    cmd = CreateStudyPlanCommand(
        plan_data=req.model_dump(),
        user_id=user_id,
        supabase=sb,
    )
    try:
        result = await command_invoker.execute_command(cmd)
        return StudyPlanResponse(
            id=result["id"],
            user_id=result["user_id"],
            title=result["title"],
            goal=result.get("goal"),
            start_date=result["start_date"],
            end_date=result["end_date"],
            status=result["status"],
            items=result.get("items", []),
        )
    except Exception as exc:
        logger.error(f"Create study plan error: {exc}")
        raise HTTPException(500, str(exc))


@router.get("/{plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(plan_id: str, user_id: str = Query(...)):
    sb = get_service_supabase() or get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        res = sb.table("study_plans").select("*, study_plan_items(*, topics(title, course_id))").eq("id", plan_id).eq("user_id", user_id).single().execute()
        if not res.data:
            raise HTTPException(404, "Study plan not found")
        data = res.data
        items = data.pop("study_plan_items", []) or []
        return StudyPlanResponse(**data, items=items)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.patch("/items/{item_id}", response_model=MessageResponse)
async def update_plan_item(item_id: str, req: StudyPlanItemUpdate):
    sb = get_service_supabase() or get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        sb.table("study_plan_items").update({"completed": req.completed}).eq("id", item_id).execute()
        return MessageResponse(message="Item updated")
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_study_plan(plan_id: str, user_id: str = Query(...)):
    sb = get_service_supabase() or get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        sb.table("study_plan_items").delete().eq("study_plan_id", plan_id).execute()
        sb.table("study_plans").delete().eq("id", plan_id).eq("user_id", user_id).execute()
        return MessageResponse(message="Study plan deleted")
    except Exception as exc:
        raise HTTPException(500, str(exc))
