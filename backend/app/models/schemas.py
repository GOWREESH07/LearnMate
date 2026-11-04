"""
Pydantic v2 models for the LearnMate FastAPI backend.
"""

from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any
from datetime import date, datetime
from enum import Enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class TopicStateEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    practicing  = "practicing"
    mastered    = "mastered"


class ResourceTypeEnum(str, Enum):
    video         = "video"
    article       = "article"
    pdf           = "pdf"
    external_link = "external_link"


class DifficultyEnum(str, Enum):
    beginner     = "beginner"
    intermediate = "intermediate"
    advanced     = "advanced"


class StudyPlanStatusEnum(str, Enum):
    draft     = "draft"
    active    = "active"
    completed = "completed"
    paused    = "paused"


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    provider: str = "google"


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OnboardingRequest(BaseModel):
    interests: list[str] = []
    study_pace: str = "moderate"
    target_career: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: str


# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    interests: Optional[list[str]] = None
    study_pace: Optional[str] = None
    target_career: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    name: str
    avatar_url: Optional[str] = None
    interests: list[str] = []
    study_pace: str = "moderate"
    target_career: Optional[str] = None
    streak_days: int = 0
    onboarding_done: bool = False
    created_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# COURSE + TOPIC
# ─────────────────────────────────────────────

class CourseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    subject: str
    difficulty_level: str = "beginner"
    thumbnail_url: Optional[str] = None
    total_topics: int = 0


class TopicResponse(BaseModel):
    id: str
    course_id: str
    title: str
    description: Optional[str] = None
    order_index: int = 0
    state: Optional[TopicStateEnum] = None   # joined from topic_progress


class TopicProgressUpdate(BaseModel):
    state: TopicStateEnum


# ─────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────

class ResourceCreate(BaseModel):
    topic_id: str
    resource_type: ResourceTypeEnum
    title: str
    url: str
    source: str = ""
    duration: Optional[int] = None
    metadata: dict[str, Any] = {}


class ResourceResponse(BaseModel):
    id: str
    topic_id: str
    type: str
    title: str
    url: str
    source: str = ""
    duration: Optional[int] = None
    metadata: dict[str, Any] = {}


# ─────────────────────────────────────────────
# QUIZZES
# ─────────────────────────────────────────────

class GenerateQuizRequest(BaseModel):
    topic_id: str
    topic_title: str
    difficulty: DifficultyEnum = DifficultyEnum.intermediate


class QuizQuestion(BaseModel):
    id: Optional[str] = None
    question_text: str
    options: list[str]
    correct_answer: str
    explanation: Optional[str] = None
    order_index: int = 0


class QuizResponse(BaseModel):
    id: str
    topic_id: str
    title: str
    difficulty: str
    generated_by: str
    questions: list[QuizQuestion] = []
    created_at: Optional[datetime] = None


class QuizAttemptRequest(BaseModel):
    quiz_id: str
    answers: dict[str, str]   # question_id → chosen_answer


class QuizAttemptResponse(BaseModel):
    id: str
    quiz_id: str
    user_id: str
    score: float
    answers: dict[str, Any]
    completed_at: datetime
    new_topic_state: Optional[str] = None   # if state changed


# ─────────────────────────────────────────────
# STUDY PLANS
# ─────────────────────────────────────────────

class StudyPlanCreate(BaseModel):
    title: str
    goal: Optional[str] = None
    start_date: date
    end_date: date
    duration_minutes: int = 45
    sessions_per_week: int = 3
    topics: list[dict] = []   # [{topic_id, topic_title}, ...]


class StudyPlanItemUpdate(BaseModel):
    completed: bool


class StudyPlanResponse(BaseModel):
    id: str
    user_id: str
    title: str
    goal: Optional[str] = None
    start_date: date
    end_date: date
    status: str
    items: list[dict] = []
    created_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    read: bool
    metadata: dict[str, Any] = {}
    created_at: datetime


# ─────────────────────────────────────────────
# GROUPS
# ─────────────────────────────────────────────

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime
    member_count: Optional[int] = None


# ─────────────────────────────────────────────
# PREDICTIONS
# ─────────────────────────────────────────────

class PredictionResponse(BaseModel):
    id: str
    user_id: str
    topic_id: str
    predicted_score: float
    confidence: float
    rationale: Optional[str] = None
    generated_at: datetime


# ─────────────────────────────────────────────
# RECOMMENDATIONS
# ─────────────────────────────────────────────

class RecommendationResponse(BaseModel):
    topic_id: Optional[str] = None
    topic_title: str
    course_title: str = ""
    reason: str
    strategy: str
    priority: int = 5


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

class DashboardResponse(BaseModel):
    profile: dict[str, Any] = {}
    state_counts: dict[str, int] = {}
    total_topics: int = 0
    mastery_percentage: float = 0.0
    quiz_attempts: list[dict] = []
    upcoming_items: list[dict] = []
    unread_notifications: int = 0
    achievements: list[dict] = []


# ─────────────────────────────────────────────
# GENERIC
# ─────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True
