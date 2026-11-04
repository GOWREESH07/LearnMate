"""Courses router."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import CourseResponse, ProfileUpdate, ProfileResponse, MessageResponse
from app.services.database import get_supabase
import logging

router = APIRouter(prefix="/courses", tags=["courses"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[CourseResponse])
async def list_courses():
    sb = get_supabase()
    if not sb:
        return _mock_courses()
    try:
        res = sb.table("courses").select("*").order("subject").execute()
        return [CourseResponse(**c) for c in (res.data or [])]
    except Exception as exc:
        logger.error(f"List courses error: {exc}")
        return _mock_courses()


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        res = sb.table("courses").select("*").eq("id", course_id).single().execute()
        if not res.data:
            raise HTTPException(404, "Course not found")
        return CourseResponse(**res.data)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, str(exc))


def _mock_courses():
    return [
        CourseResponse(id="mock-1", title="Advanced Mathematics", description="From algebra to graph theory", subject="Mathematics", difficulty_level="intermediate", total_topics=9),
        CourseResponse(id="mock-2", title="Computer Science Fundamentals", description="Algorithms, data structures, OS", subject="Computer Science", difficulty_level="intermediate", total_topics=9),
        CourseResponse(id="mock-3", title="Modern Biology", description="Cell biology through ecology", subject="Biology", difficulty_level="beginner", total_topics=9),
        CourseResponse(id="mock-4", title="Physics Mastery", description="Classical mechanics to quantum physics", subject="Physics", difficulty_level="advanced", total_topics=9),
        CourseResponse(id="mock-5", title="Data Science in Practice", description="Pandas to deep learning", subject="Data Science", difficulty_level="intermediate", total_topics=9),
    ]
