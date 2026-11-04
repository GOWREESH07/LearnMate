"""Groups router — collaborative study groups."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import GroupCreate, GroupResponse, MessageResponse
from app.services.database import get_supabase
import logging
from datetime import datetime

router = APIRouter(prefix="/groups", tags=["groups"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[GroupResponse])
async def list_groups(user_id: str = Query(None)):
    sb = get_supabase()
    if not sb:
        return []
    try:
        if user_id:
            # Get groups the user is a member of
            res = sb.table("group_members").select("collaborative_groups(*)").eq("user_id", user_id).execute()
            groups = [r["collaborative_groups"] for r in (res.data or []) if r.get("collaborative_groups")]
        else:
            res = sb.table("collaborative_groups").select("*").order("created_at", desc=True).execute()
            groups = res.data or []
        return [GroupResponse(**g, member_count=None) for g in groups]
    except Exception as exc:
        logger.error(f"List groups error: {exc}")
        return []


@router.post("", response_model=GroupResponse)
async def create_group(req: GroupCreate, user_id: str = Query(...)):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        res = sb.table("collaborative_groups").insert({
            "name": req.name,
            "description": req.description,
            "created_by": user_id,
        }).execute()
        group = res.data[0]
        # Auto-add creator as member
        sb.table("group_members").insert({"group_id": group["id"], "user_id": user_id}).execute()
        return GroupResponse(**group)
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.post("/{group_id}/join", response_model=MessageResponse)
async def join_group(group_id: str, user_id: str = Query(...)):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        sb.table("group_members").insert({"group_id": group_id, "user_id": user_id}).execute()
        return MessageResponse(message="Joined group successfully")
    except Exception as exc:
        raise HTTPException(400, "Already a member or group not found")


@router.delete("/{group_id}/leave", response_model=MessageResponse)
async def leave_group(group_id: str, user_id: str = Query(...)):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        sb.table("group_members").delete().eq("group_id", group_id).eq("user_id", user_id).execute()
        return MessageResponse(message="Left group")
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.get("/{group_id}/members")
async def get_group_members(group_id: str):
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("group_members").select("user_id, joined_at, profiles(name, avatar_url, streak_days)").eq("group_id", group_id).execute()
        return res.data or []
    except Exception as exc:
        logger.error(f"Get members error: {exc}")
        return []


@router.get("/{group_id}/leaderboard")
async def get_group_leaderboard(group_id: str):
    """Return member quiz score leaderboard for this group."""
    sb = get_supabase()
    if not sb:
        return []
    try:
        members = sb.table("group_members").select("user_id, profiles(name, avatar_url)").eq("group_id", group_id).execute()
        leaderboard = []
        for m in (members.data or []):
            uid = m["user_id"]
            attempts = sb.table("quiz_attempts").select("score").eq("user_id", uid).execute()
            scores = [a["score"] for a in (attempts.data or [])]
            avg = sum(scores) / len(scores) if scores else 0
            leaderboard.append({
                "user_id": uid,
                "name": m.get("profiles", {}).get("name", "Unknown"),
                "avatar_url": m.get("profiles", {}).get("avatar_url"),
                "avg_score": round(avg, 1),
                "quiz_count": len(scores),
            })
        leaderboard.sort(key=lambda x: x["avg_score"], reverse=True)
        return leaderboard
    except Exception as exc:
        logger.error(f"Leaderboard error: {exc}")
        return []
