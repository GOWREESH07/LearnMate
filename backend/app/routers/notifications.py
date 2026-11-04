"""Notifications router — Observer pattern backing."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import NotificationResponse, MessageResponse
from app.services.database import get_supabase
import logging
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[NotificationResponse])
async def get_notifications(user_id: str = Query(...), unread_only: bool = False):
    sb = get_supabase()
    if not sb:
        return _mock_notifications(user_id)
    try:
        q = sb.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(50)
        if unread_only:
            q = q.eq("read", False)
        res = q.execute()
        return [NotificationResponse(**n) for n in (res.data or [])]
    except Exception as exc:
        logger.error(f"Get notifications error: {exc}")
        return []


@router.get("/unread-count")
async def get_unread_count(user_id: str = Query(...)):
    from app.patterns.creational.singletons import NotificationServiceSingleton
    svc = NotificationServiceSingleton()
    count = svc.get_unread_count(user_id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(notification_id: str):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        sb.table("notifications").update({"read": True}).eq("id", notification_id).execute()
        return MessageResponse(message="Notification marked as read")
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.patch("/mark-all-read", response_model=MessageResponse)
async def mark_all_read(user_id: str = Query(...)):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        sb.table("notifications").update({"read": True}).eq("user_id", user_id).eq("read", False).execute()
        return MessageResponse(message="All notifications marked as read")
    except Exception as exc:
        raise HTTPException(500, str(exc))


def _mock_notifications(user_id: str) -> list[NotificationResponse]:
    return [
        NotificationResponse(id="n1", type="achievement_unlocked", title="🏆 Achievement Unlocked!", message="You've earned 'Linear Algebra Legend' — 100% on your first quiz!", read=False, metadata={}, created_at=datetime.utcnow()),
        NotificationResponse(id="n2", type="study_reminder", title="📚 Study Session Today", message="You have 'Computer Networks' scheduled today. 45 minutes — let's go!", read=False, metadata={}, created_at=datetime.utcnow()),
    ]
