"""
FACADE PATTERN — Structural
==============================
LearningPlatformFacade provides a unified, simplified interface over
the complex subsystem of AI services, analytics, recommendation engines,
and assessment modules.

Routers call this facade instead of coordinating subsystems directly.
"""

from __future__ import annotations
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LearningPlatformFacade:
    """
    Facade class. Exposes simple, high-level operations that internally
    coordinate multiple backend subsystems:
      - GeminiAIAdapter (AI generation)
      - RecommendationContext (strategy selection)
      - TopicStateContext (state transitions)
      - NotificationSubject (observer notifications)
      - AnalyticsService (progress aggregation)
    """

    def __init__(self, supabase_client=None):
        self._supabase = supabase_client
        self._ai_adapter: Optional[Any] = None
        self._recommendation_context: Optional[Any] = None
        self._notification_subject: Optional[Any] = None

    def _get_ai_adapter(self):
        if self._ai_adapter is None:
            from app.patterns.structural.external_adapters import GeminiAIAdapter
            self._ai_adapter = GeminiAIAdapter()
        return self._ai_adapter

    def _get_recommendation_context(self):
        if self._recommendation_context is None:
            from app.patterns.behavioral.recommendation_strategy import RecommendationContext
            self._recommendation_context = RecommendationContext()
        return self._recommendation_context

    def _get_notification_subject(self):
        if self._notification_subject is None:
            from app.patterns.behavioral.notification_observer import NotificationSubject
            subj = NotificationSubject()
            # Auto-attach all default observers
            from app.patterns.behavioral.notification_observer import (
                QuizGeneratedObserver,
                StudyReminderObserver,
                AchievementObserver,
                RecommendationObserver,
            )
            subj.attach(QuizGeneratedObserver())
            subj.attach(StudyReminderObserver())
            subj.attach(AchievementObserver())
            subj.attach(RecommendationObserver())
            self._notification_subject = subj
        return self._notification_subject

    # ─────────────────────────────────────────────
    # PUBLIC FACADE METHODS
    # ─────────────────────────────────────────────

    async def get_dashboard_data(self, user_id: str) -> dict:
        """
        Aggregate all data needed for the dashboard in one call:
        - Topic progress summary
        - Recent quiz attempts
        - Upcoming study plan items
        - Unread notifications count
        - Recent achievements
        - Performance predictions
        """
        if not self._supabase:
            return self._mock_dashboard_data(user_id)

        try:
            # 1. Topic progress
            progress_res = (
                self._supabase.table("topic_progress")
                .select("state, topic_id, topics(title, course_id, courses(title, subject))")
                .eq("user_id", user_id)
                .execute()
            )
            progress = progress_res.data or []

            # 2. State counts
            state_counts = {"not_started": 0, "in_progress": 0, "practicing": 0, "mastered": 0}
            for p in progress:
                state_counts[p["state"]] = state_counts.get(p["state"], 0) + 1

            # 3. Recent quiz attempts (last 10)
            quiz_res = (
                self._supabase.table("quiz_attempts")
                .select("score, completed_at, quizzes(title, topic_id, topics(title))")
                .eq("user_id", user_id)
                .order("completed_at", desc=True)
                .limit(10)
                .execute()
            )
            quiz_attempts = quiz_res.data or []

            # 4. Upcoming study plan items (next 7 days)
            from datetime import date, timedelta
            today = date.today().isoformat()
            next_week = (date.today() + timedelta(days=7)).isoformat()
            plan_res = (
                self._supabase.table("study_plan_items")
                .select("*, topics(title), study_plans!inner(user_id, title)")
                .eq("study_plans.user_id", user_id)
                .gte("scheduled_date", today)
                .lte("scheduled_date", next_week)
                .eq("completed", False)
                .order("scheduled_date")
                .limit(10)
                .execute()
            )
            upcoming = plan_res.data or []

            # 5. Unread notifications
            notif_res = (
                self._supabase.table("notifications")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("read", False)
                .execute()
            )
            unread_count = notif_res.count or 0

            # 6. Recent achievements
            ach_res = (
                self._supabase.table("achievements")
                .select("*")
                .eq("user_id", user_id)
                .order("earned_at", desc=True)
                .limit(5)
                .execute()
            )
            achievements = ach_res.data or []

            # 7. Profile (streak)
            profile_res = (
                self._supabase.table("profiles")
                .select("name, streak_days, study_pace, target_career")
                .eq("id", user_id)
                .execute()
            )
            profile = (
                profile_res.data[0]
                if (profile_res.data and len(profile_res.data) > 0)
                else {"name": "Student", "streak_days": 0, "study_pace": "moderate", "target_career": None}
            )

            return {
                "profile": profile,
                "state_counts": state_counts,
                "total_topics": len(progress),
                "mastery_percentage": round(
                    state_counts["mastered"] / len(progress) * 100 if progress else 0, 1
                ),
                "quiz_attempts": quiz_attempts,
                "upcoming_items": upcoming,
                "unread_notifications": unread_count,
                "achievements": achievements,
            }
        except Exception as exc:
            logger.error(f"Dashboard data fetch error: {exc}")
            return {"error": str(exc)}

    async def generate_quiz(
        self,
        topic_id: str,
        topic_title: str,
        difficulty: str,
        user_id: str,
    ) -> dict:
        """
        Use GeminiAIAdapter to generate quiz questions, then:
        1. Save quiz + questions to Supabase
        2. Notify observers (QuizGeneratedObserver fires)
        Return the quiz dict.
        """
        ai_adapter = self._get_ai_adapter()

        # Generate questions via AI
        questions = await ai_adapter.generate_quiz_questions(
            topic_title=topic_title,
            difficulty=difficulty,
            num_questions=5,
        )

        if not questions:
            raise RuntimeError("AI quiz generation returned no questions")

        # Create quiz via QuizFactory
        from app.patterns.creational.resource_factory import QuizFactory
        quiz_obj = QuizFactory.create_ai_quiz(
            topic_id=topic_id,
            title=f"{topic_title} — AI Quiz ({difficulty})",
            difficulty=difficulty,
            questions=questions,
        )

        # Persist to Supabase
        if self._supabase:
            quiz_row = self._supabase.table("quizzes").insert({
                "id": quiz_obj.id,
                "topic_id": quiz_obj.topic_id,
                "title": quiz_obj.title,
                "difficulty": quiz_obj.difficulty,
                "generated_by": "ai",
            }).execute()

            for i, q in enumerate(questions):
                self._supabase.table("quiz_questions").insert({
                    "quiz_id": quiz_obj.id,
                    "question_text": q.get("question_text", ""),
                    "options": q.get("options", []),
                    "correct_answer": q.get("correct_answer", ""),
                    "explanation": q.get("explanation", ""),
                    "order_index": i,
                }).execute()

        # Fire notification via observer
        try:
            subject = self._get_notification_subject()
            await subject.notify("quiz_generated", {
                "user_id": user_id,
                "quiz_id": quiz_obj.id,
                "topic_title": topic_title,
            })
        except Exception as exc:
            logger.warning(f"Observer notification failed: {exc}")

        return quiz_obj.to_dict()

    async def get_recommendations(
        self,
        user_id: str,
        user_profile: dict,
        progress_data: list[dict],
    ) -> list[dict]:
        """
        Use RecommendationContext (Strategy pattern) to select the best
        strategy for this user and generate personalized recommendations.
        """
        context = self._get_recommendation_context()
        context.select_strategy(user_profile, progress_data)
        return await context.get_recommendations(
            user_id=user_id,
            user_profile=user_profile,
            progress_data=progress_data,
            supabase=self._supabase,
        )

    async def update_topic_state(
        self,
        user_id: str,
        topic_id: str,
        new_state: str,
    ) -> dict:
        """
        Transition topic state using the State pattern, then persist,
        then fire observer notifications.
        """
        from app.patterns.behavioral.topic_state import TopicStateContext
        ctx = TopicStateContext(current_state=new_state)

        if self._supabase:
            existing = (
                self._supabase.table("topic_progress")
                .select("state")
                .eq("user_id", user_id)
                .eq("topic_id", topic_id)
                .execute()
            )
            current_state = "not_started"
            if existing.data:
                current_state = existing.data[0]["state"]

            ctx = TopicStateContext(current_state=current_state)

            # Validate transition
            if not ctx.can_transition_to(new_state):
                raise ValueError(
                    f"Invalid transition: {current_state} → {new_state}"
                )

            # Upsert progress row
            self._supabase.table("topic_progress").upsert({
                "user_id": user_id,
                "topic_id": topic_id,
                "state": new_state,
            }).execute()

            # Fire achievement observer if mastered
            if new_state == "mastered":
                try:
                    subject = self._get_notification_subject()
                    await subject.notify("topic_mastered", {
                        "user_id": user_id,
                        "topic_id": topic_id,
                    })
                except Exception as exc:
                    logger.warning(f"Achievement observer error: {exc}")

        return {"user_id": user_id, "topic_id": topic_id, "state": new_state}

    def _mock_dashboard_data(self, user_id: str) -> dict:
        """Return realistic mock data when Supabase is not configured."""
        return {
            "profile": {"name": "Demo User", "streak_days": 7, "study_pace": "moderate"},
            "state_counts": {"not_started": 12, "in_progress": 8, "practicing": 6, "mastered": 9},
            "total_topics": 35,
            "mastery_percentage": 25.7,
            "quiz_attempts": [],
            "upcoming_items": [],
            "unread_notifications": 2,
            "achievements": [],
        }
