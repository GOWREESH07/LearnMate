"""Chat router — GeminiAIAdapter for grounded conversation."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ChatMessageRequest, ChatMessageResponse
from app.services.database import get_supabase, get_service_supabase
from app.patterns.structural.external_adapters import GeminiAIAdapter
import logging
import uuid
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.get("/history", response_model=list[ChatMessageResponse])
async def get_chat_history(user_id: str = Query(...), limit: int = 50):
    sb = get_service_supabase() or get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("chat_messages").select("*").eq("user_id", user_id).order("created_at").limit(limit).execute()
        return [ChatMessageResponse(**m) for m in (res.data or [])]
    except Exception as exc:
        logger.error(f"Chat history error: {exc}")
        return []


@router.post("/send", response_model=ChatMessageResponse)
async def send_message(req: ChatMessageRequest, user_id: str = Query(...)):
    """
    Store user message, fetch context, call Gemini via GeminiAIAdapter,
    store and return the assistant response.
    """
    sb = get_service_supabase() or get_supabase()
    ai = GeminiAIAdapter()
    now = datetime.utcnow()

    # Persist user message
    user_msg_id = str(uuid.uuid4())
    if sb:
        sb.table("chat_messages").insert({
            "id": user_msg_id,
            "user_id": user_id,
            "role": "user",
            "content": req.content,
            "created_at": now.isoformat(),
        }).execute()

    # Build context from user's actual data
    context = await _build_user_context(user_id, sb)

    # Fetch recent chat history
    messages = []
    if sb:
        hist = sb.table("chat_messages").select("role, content").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        messages = list(reversed(hist.data or []))

    # Generate AI response via adapter
    try:
        response_text = await ai.chat(messages, context)
    except Exception as exc:
        logger.error(f"AI chat error: {exc}")
        response_text = "I'm having trouble connecting to the AI right now. Please check that GEMINI_API_KEY is configured and try again."

    # Persist assistant response
    asst_id = str(uuid.uuid4())
    asst_time = datetime.utcnow()
    if sb:
        sb.table("chat_messages").insert({
            "id": asst_id,
            "user_id": user_id,
            "role": "assistant",
            "content": response_text,
            "created_at": asst_time.isoformat(),
        }).execute()

    return ChatMessageResponse(id=asst_id, role="assistant", content=response_text, created_at=asst_time)


@router.delete("/history", response_model=dict)
async def clear_chat_history(user_id: str = Query(...)):
    sb = get_service_supabase() or get_supabase()
    if sb:
        sb.table("chat_messages").delete().eq("user_id", user_id).execute()
    return {"message": "Chat history cleared"}


async def _build_user_context(user_id: str, sb) -> str:
    """Build a rich context string from the user's Supabase data for the AI prompt."""
    if not sb:
        return "No student data available."
    try:
        profile_res = sb.table("profiles").select("name, interests, study_pace, target_career, streak_days").eq("id", user_id).single().execute()
        profile = profile_res.data or {}

        prog_res = sb.table("topic_progress").select("state, topics(title, courses(title))").eq("user_id", user_id).execute()
        progress = prog_res.data or []

        attempts_res = sb.table("quiz_attempts").select("score, completed_at, quizzes(title, topics(title))").eq("user_id", user_id).order("completed_at", desc=True).limit(5).execute()
        attempts = attempts_res.data or []

        state_summary = {}
        for p in progress:
            state_summary[p["state"]] = state_summary.get(p["state"], 0) + 1

        lines = [
            f"Student: {profile.get('name', 'Unknown')}",
            f"Streak: {profile.get('streak_days', 0)} days",
            f"Study pace: {profile.get('study_pace', 'moderate')}",
            f"Target career: {profile.get('target_career', 'not set')}",
            f"Interests: {', '.join(profile.get('interests', []) or ['not specified'])}",
            f"Topic progress: {state_summary.get('mastered', 0)} mastered, {state_summary.get('practicing', 0)} practicing, {state_summary.get('in_progress', 0)} in progress, {state_summary.get('not_started', 0)} not started",
        ]
        if attempts:
            avg_score = sum(a["score"] for a in attempts) / len(attempts)
            lines.append(f"Recent quiz average: {avg_score:.1f}%")
        return "\n".join(lines)
    except Exception as exc:
        logger.warning(f"Context build error: {exc}")
        return "Limited student context available."
