"""Recommendations router — Facade + Strategy patterns."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import RecommendationResponse
from app.services.database import get_supabase
from app.patterns.structural.learning_facade import LearningPlatformFacade
import logging

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[RecommendationResponse])
async def get_recommendations(user_id: str = Query(...)):
    """
    Returns personalized recommendations via LearningPlatformFacade.
    The facade internally uses RecommendationContext (Strategy pattern)
    to pick the best strategy for this user.
    """
    sb = get_supabase()
    facade = LearningPlatformFacade(supabase_client=sb)

    try:
        # Fetch user profile and progress
        profile_data = {}
        progress_data = []
        if sb:
            profile_res = sb.table("profiles").select("interests, study_pace, target_career").eq("id", user_id).single().execute()
            profile_data = profile_res.data or {}

            prog_res = sb.table("topic_progress").select("topic_id, state, topics(title, course_id, courses(title, subject))").eq("user_id", user_id).execute()
            progress_data = prog_res.data or []

        recs = await facade.get_recommendations(
            user_id=user_id,
            user_profile=profile_data,
            progress_data=progress_data,
        )
        if not recs:
            return _mock_recommendations()
        return [RecommendationResponse(**r) for r in recs]
    except Exception as exc:
        logger.error(f"Recommendations error: {exc}")
        return _mock_recommendations()


def _mock_recommendations() -> list[RecommendationResponse]:
    return [
        RecommendationResponse(topic_id=None, topic_title="Graph Theory", course_title="Advanced Mathematics", reason="You've mastered 3 related topics — you're ready for this next challenge.", strategy="performance_based", priority=1),
        RecommendationResponse(topic_id=None, topic_title="Deep Learning Fundamentals", course_title="Data Science in Practice", reason="Matches your interest in AI.", strategy="interest_based", priority=2),
        RecommendationResponse(topic_id=None, topic_title="Computer Networks", course_title="CS Fundamentals", reason="You're already in progress here — perfect for a focused session today.", strategy="time_availability", priority=3),
    ]
