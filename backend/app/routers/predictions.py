"""Predictions router — performance prediction via GeminiAIAdapter."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import PredictionResponse
from app.services.database import get_supabase
from app.patterns.structural.external_adapters import GeminiAIAdapter
import logging
import uuid
from datetime import datetime

router = APIRouter(prefix="/predictions", tags=["predictions"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[PredictionResponse])
async def get_predictions(user_id: str = Query(...)):
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("performance_predictions").select("*, topics(title)").eq("user_id", user_id).execute()
        return [PredictionResponse(**p) for p in (res.data or [])]
    except Exception as exc:
        logger.error(f"Get predictions error: {exc}")
        return []


@router.post("/generate/{topic_id}", response_model=PredictionResponse)
async def generate_prediction(topic_id: str, user_id: str = Query(...)):
    """
    Generate a performance prediction for a topic using GeminiAIAdapter.
    Uses the user's quiz history and progress as context.
    """
    sb = get_supabase()
    ai = GeminiAIAdapter()

    # Build user context
    user_context = "No data available."
    topic_title = "Unknown Topic"
    if sb:
        topic_res = sb.table("topics").select("title").eq("id", topic_id).single().execute()
        topic_title = topic_res.data.get("title", "Unknown") if topic_res.data else "Unknown"

        prog_res = sb.table("topic_progress").select("state, topics(title)").eq("user_id", user_id).execute()
        attempts_res = sb.table("quiz_attempts").select("score, quizzes(title)").eq("user_id", user_id).order("completed_at", desc=True).limit(10).execute()
        profile_res = sb.table("profiles").select("study_pace, target_career, streak_days").eq("id", user_id).single().execute()
        profile = profile_res.data or {}

        mastered = [p for p in (prog_res.data or []) if p["state"] == "mastered"]
        avg_score = sum(a["score"] for a in (attempts_res.data or [])) / max(len(attempts_res.data or []), 1)

        user_context = f"""
Study pace: {profile.get('study_pace', 'moderate')}
Streak: {profile.get('streak_days', 0)} days
Topics mastered: {len(mastered)}
Average quiz score: {avg_score:.1f}%
Recent quiz attempts: {len(attempts_res.data or [])}
"""

    prediction_data = await ai.predict_performance(topic=topic_title, user_context=user_context)

    # Upsert prediction
    pred_id = str(uuid.uuid4())
    now = datetime.utcnow()
    if sb:
        try:
            sb.table("performance_predictions").upsert({
                "id": pred_id,
                "user_id": user_id,
                "topic_id": topic_id,
                "predicted_score": prediction_data["predicted_score"],
                "confidence": prediction_data["confidence"],
                "rationale": prediction_data.get("rationale", ""),
                "generated_at": now.isoformat(),
            }).execute()
        except Exception as exc:
            logger.warning(f"Prediction upsert failed: {exc}")

    return PredictionResponse(
        id=pred_id,
        user_id=user_id,
        topic_id=topic_id,
        predicted_score=prediction_data["predicted_score"],
        confidence=prediction_data["confidence"],
        rationale=prediction_data.get("rationale", ""),
        generated_at=now,
    )
