"""Topics router — includes State pattern and Decorator pattern usage."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import TopicResponse, TopicProgressUpdate, MessageResponse
from app.services.database import get_supabase
from app.patterns.behavioral.commands import UpdateProgressCommand, command_invoker
from app.patterns.behavioral.topic_state import TopicStateContext, get_state
from app.patterns.structural.module_decorators import build_enhanced_module
import logging

router = APIRouter(prefix="/topics", tags=["topics"])
logger = logging.getLogger(__name__)


@router.get("/course/{course_id}", response_model=list[TopicResponse])
async def get_topics_for_course(course_id: str, user_id: str = Query(None)):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        # Fetch topics
        topics_res = sb.table("topics").select("*").eq("course_id", course_id).order("order_index").execute()
        topics = topics_res.data or []

        # Fetch user's progress for these topics
        progress_map = {}
        if user_id:
            topic_ids = [t["id"] for t in topics]
            if topic_ids:
                prog_res = sb.table("topic_progress").select("topic_id, state").eq("user_id", user_id).in_("topic_id", topic_ids).execute()
                progress_map = {p["topic_id"]: p["state"] for p in (prog_res.data or [])}

        return [
            TopicResponse(
                **{k: v for k, v in t.items() if k in TopicResponse.model_fields},
                state=progress_map.get(t["id"], "not_started"),
            )
            for t in topics
        ]
    except Exception as exc:
        logger.error(f"Get topics error: {exc}")
        raise HTTPException(500, str(exc))


@router.get("/{topic_id}/detail")
async def get_topic_detail(topic_id: str, user_id: str = Query(None)):
    """
    Returns topic info + resources + gamification layer (Decorator pattern).
    Also marks the topic as 'in_progress' if it was 'not_started'.
    """
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        # Fetch topic
        topic_res = sb.table("topics").select("*, courses(id, title, subject)").eq("id", topic_id).single().execute()
        if not topic_res.data:
            raise HTTPException(404, "Topic not found")
        topic = topic_res.data

        # Fetch resources
        res_res = sb.table("learning_resources").select("*").eq("topic_id", topic_id).execute()
        resources = res_res.data or []

        # Fetch user progress & XP proxy
        user_xp = 0
        resources_completed = 0
        current_state = "not_started"
        if user_id:
            prog = sb.table("topic_progress").select("state").eq("user_id", user_id).eq("topic_id", topic_id).execute()
            if prog.data:
                current_state = prog.data[0]["state"]
            # Proxy XP from quiz attempts
            attempts = sb.table("quiz_attempts").select("score").eq("user_id", user_id).execute()
            user_xp = int(sum(a["score"] for a in (attempts.data or [])))
            resources_completed = min(len(resources), user_xp // 10)

            # Auto-advance to in_progress on first view
            if current_state == "not_started" and user_id:
                try:
                    cmd = UpdateProgressCommand(user_id=user_id, topic_id=topic_id, new_state="in_progress", supabase=sb)
                    await command_invoker.execute_command(cmd)
                    current_state = "in_progress"
                except Exception:
                    pass

        # Apply Decorator pattern
        module = build_enhanced_module(
            topic=topic,
            resources=resources,
            user_xp=user_xp,
            resources_completed=resources_completed,
            enable_voice=False,
            is_premium=False,
        )
        content = module.get_content()
        content["current_state"] = current_state
        content["state_info"] = get_state(current_state).to_dict()
        content["course"] = topic.get("courses", {})
        return content
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Topic detail error: {exc}")
        raise HTTPException(500, str(exc))


@router.put("/{topic_id}/progress")
async def update_topic_progress(topic_id: str, req: TopicProgressUpdate, user_id: str = Query(...)):
    """
    Update topic state via Command pattern + State pattern validation.
    """
    sb = get_supabase()
    cmd = UpdateProgressCommand(
        user_id=user_id,
        topic_id=topic_id,
        new_state=req.state.value,
        supabase=sb,
    )
    try:
        result = await command_invoker.execute_command(cmd)
        return result
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.get("/states/all")
async def get_all_states():
    """Return state definitions for the frontend progress trail legend."""
    return TopicStateContext.all_states()
