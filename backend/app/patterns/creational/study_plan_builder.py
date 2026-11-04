"""
BUILDER PATTERN — Creational
==============================
Separates the construction of a complex StudyPlan object from its
representation, so the same construction process can create different plans.

Used by: /study-plans router when a user creates a new plan via the wizard.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
import uuid


# ──────────────────────────────────────────────
# PRODUCT: StudyPlan
# ──────────────────────────────────────────────

@dataclass
class StudyPlanItem:
    topic_id: str
    topic_title: str
    scheduled_date: date
    duration_minutes: int
    completed: bool = False
    notes: str = ""


@dataclass
class StudyPlan:
    id: str
    user_id: str
    title: str
    goal: str
    start_date: date
    end_date: date
    status: str
    items: list[StudyPlanItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "goal": self.goal,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
            "items": [
                {
                    "topic_id": item.topic_id,
                    "topic_title": item.topic_title,
                    "scheduled_date": item.scheduled_date.isoformat(),
                    "duration_minutes": item.duration_minutes,
                    "completed": item.completed,
                    "notes": item.notes,
                }
                for item in self.items
            ],
        }

    @property
    def total_study_time_minutes(self) -> int:
        return sum(i.duration_minutes for i in self.items)

    @property
    def completion_percentage(self) -> float:
        if not self.items:
            return 0.0
        completed = sum(1 for i in self.items if i.completed)
        return round(completed / len(self.items) * 100, 1)


# ──────────────────────────────────────────────
# BUILDER
# ──────────────────────────────────────────────

class StudyPlanBuilder:
    """
    Builder class with chainable setter methods.
    Call .build() at the end to get the final StudyPlan product.

    Usage:
        plan = (
            StudyPlanBuilder(user_id="abc", title="My Plan")
            .set_goal("Master calculus before exams")
            .set_schedule(start=date.today(), end=date.today() + timedelta(days=30))
            .set_duration(default_minutes=45)
            .add_topic("topic-uuid-1", "Derivatives", study_date=date.today() + timedelta(days=1))
            .add_topic("topic-uuid-2", "Integrals",   study_date=date.today() + timedelta(days=3))
            .build()
        )
    """

    def __init__(self, user_id: str, title: str):
        self._user_id: str = user_id
        self._title: str = title
        self._goal: str = ""
        self._start_date: date = date.today()
        self._end_date: date = date.today() + timedelta(days=30)
        self._status: str = "draft"
        self._default_duration: int = 30          # minutes
        self._items: list[StudyPlanItem] = []

    # ── Chainable setters ──────────────────────

    def set_goal(self, goal: str) -> "StudyPlanBuilder":
        self._goal = goal
        return self

    def set_schedule(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> "StudyPlanBuilder":
        if start:
            self._start_date = start
        if end:
            self._end_date = end
        return self

    def set_duration(self, default_minutes: int) -> "StudyPlanBuilder":
        """Set the default session duration (minutes) for auto-scheduled items."""
        self._default_duration = max(15, default_minutes)
        return self

    def set_status(self, status: str) -> "StudyPlanBuilder":
        allowed = {"draft", "active", "completed", "paused"}
        if status not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        self._status = status
        return self

    def add_topic(
        self,
        topic_id: str,
        topic_title: str,
        study_date: Optional[date] = None,
        duration_minutes: Optional[int] = None,
        notes: str = "",
    ) -> "StudyPlanBuilder":
        """Add a topic session to the plan."""
        scheduled = study_date or (self._start_date + timedelta(days=len(self._items) * 2))
        self._items.append(
            StudyPlanItem(
                topic_id=topic_id,
                topic_title=topic_title,
                scheduled_date=scheduled,
                duration_minutes=duration_minutes or self._default_duration,
                notes=notes,
            )
        )
        return self

    def add_topics_auto_scheduled(
        self,
        topics: list[dict],
        sessions_per_week: int = 3,
    ) -> "StudyPlanBuilder":
        """
        Auto-schedule a list of topics across the plan period.
        topics: list of {"topic_id": str, "topic_title": str}
        """
        total_days = (self._end_date - self._start_date).days or 1
        interval_days = max(1, 7 // sessions_per_week)
        for i, topic in enumerate(topics):
            offset = i * interval_days
            if offset > total_days:
                offset = total_days - 1
            self._items.append(
                StudyPlanItem(
                    topic_id=topic["topic_id"],
                    topic_title=topic.get("topic_title", ""),
                    scheduled_date=self._start_date + timedelta(days=offset),
                    duration_minutes=self._default_duration,
                )
            )
        return self

    # ── Build ──────────────────────────────────

    def build(self) -> StudyPlan:
        """
        Validate and assemble the final StudyPlan product.
        Raises ValueError if required fields are missing.
        """
        if not self._user_id:
            raise ValueError("StudyPlanBuilder: user_id is required")
        if not self._title:
            raise ValueError("StudyPlanBuilder: title is required")
        if self._end_date <= self._start_date:
            raise ValueError("StudyPlanBuilder: end_date must be after start_date")

        return StudyPlan(
            id=str(uuid.uuid4()),
            user_id=self._user_id,
            title=self._title,
            goal=self._goal,
            start_date=self._start_date,
            end_date=self._end_date,
            status=self._status,
            items=list(self._items),
        )

    # ── Director helpers (preset configurations) ──

    @classmethod
    def quick_plan(
        cls,
        user_id: str,
        title: str,
        topics: list[dict],
        days: int = 14,
    ) -> StudyPlan:
        """
        Director method: build a quick 2-week plan with daily sessions.
        """
        return (
            cls(user_id=user_id, title=title)
            .set_goal(f"Complete {len(topics)} topics in {days} days")
            .set_schedule(start=date.today(), end=date.today() + timedelta(days=days))
            .set_duration(default_minutes=45)
            .set_status("active")
            .add_topics_auto_scheduled(topics, sessions_per_week=5)
            .build()
        )

    @classmethod
    def exam_prep_plan(
        cls,
        user_id: str,
        title: str,
        topics: list[dict],
        exam_date: date,
    ) -> StudyPlan:
        """
        Director method: build an intensive exam-prep plan ending on exam_date.
        """
        return (
            cls(user_id=user_id, title=title)
            .set_goal("Mastery before the exam")
            .set_schedule(start=date.today(), end=exam_date)
            .set_duration(default_minutes=60)
            .set_status("active")
            .add_topics_auto_scheduled(topics, sessions_per_week=6)
            .build()
        )
