"""
OBSERVER PATTERN — Behavioral
================================
Defines a one-to-many dependency between objects so that when one
object (the Subject) changes state, all its dependents (Observers) are
notified and updated automatically.

NotificationSubject fires events; QuizGeneratedObserver,
StudyReminderObserver, AchievementObserver, RecommendationObserver each
react by writing rows to the `notifications` table.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# OBSERVER INTERFACE
# ──────────────────────────────────────────────

class Observer(ABC):
    """All observers must implement this interface."""

    @abstractmethod
    async def update(self, event_type: str, data: dict) -> None:
        """
        Called by the Subject when an event occurs.
        event_type: a string like 'quiz_generated', 'topic_mastered', etc.
        data: a dict containing event-specific payload.
        """
        ...


# ──────────────────────────────────────────────
# SUBJECT INTERFACE
# ──────────────────────────────────────────────

class Subject(ABC):
    """All subjects must support attach, detach, notify."""

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        ...

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        ...

    @abstractmethod
    async def notify(self, event_type: str, data: dict) -> None:
        ...


# ──────────────────────────────────────────────
# CONCRETE SUBJECT
# ──────────────────────────────────────────────

class NotificationSubject(Subject):
    """
    The concrete subject. Maintains a list of observers and broadcasts
    events to all of them when user actions occur.
    """

    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observer attached: {type(observer).__name__}")

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
        logger.debug(f"Observer detached: {type(observer).__name__}")

    async def notify(self, event_type: str, data: dict) -> None:
        """Broadcast the event to every attached observer."""
        logger.info(f"NotificationSubject broadcasting: {event_type!r} to {len(self._observers)} observers")
        for observer in self._observers:
            try:
                await observer.update(event_type, data)
            except Exception as exc:
                logger.error(f"Observer {type(observer).__name__} error: {exc}")


# ──────────────────────────────────────────────
# CONCRETE OBSERVERS
# ──────────────────────────────────────────────

class QuizGeneratedObserver(Observer):
    """
    Fires when a new AI quiz is generated for a topic.
    Writes a 'quiz_generated' notification row.
    """

    async def update(self, event_type: str, data: dict) -> None:
        if event_type != "quiz_generated":
            return

        user_id = data.get("user_id")
        topic_title = data.get("topic_title", "your topic")
        quiz_id = data.get("quiz_id", "")

        if not user_id:
            return

        from app.patterns.creational.singletons import NotificationServiceSingleton
        svc = NotificationServiceSingleton()
        await svc.push_notification(
            user_id=user_id,
            notification_type="quiz_generated",
            title="🎯 New Quiz Ready",
            message=f"A personalised quiz on {topic_title!r} has been generated for you. Time to test your knowledge!",
            metadata={"quiz_id": quiz_id, "topic_title": topic_title},
        )
        logger.info(f"QuizGeneratedObserver: notification sent to user {user_id}")


class StudyReminderObserver(Observer):
    """
    Fires when a study plan item is due.
    Writes a 'study_reminder' notification row.
    """

    async def update(self, event_type: str, data: dict) -> None:
        if event_type != "study_reminder":
            return

        user_id = data.get("user_id")
        topic_title = data.get("topic_title", "your scheduled topic")
        duration = data.get("duration_minutes", 30)

        if not user_id:
            return

        from app.patterns.creational.singletons import NotificationServiceSingleton
        svc = NotificationServiceSingleton()
        await svc.push_notification(
            user_id=user_id,
            notification_type="study_reminder",
            title="📚 Study Session Today",
            message=f"You have {topic_title!r} scheduled today. {duration} minutes — let's go!",
            metadata={"topic_title": topic_title, "duration_minutes": duration},
        )
        logger.info(f"StudyReminderObserver: reminder sent to user {user_id}")


class AchievementObserver(Observer):
    """
    Fires when a user masters a topic or earns a badge.
    Writes an 'achievement_unlocked' notification AND an achievements row.
    """

    MILESTONE_MAP = {
        "topic_mastered":   ("🏆 Topic Mastered!", "You've fully mastered {topic}! Great work."),
        "first_quiz":       ("⭐ First Quiz Complete!", "You completed your first quiz. Keep it up!"),
        "streak_5":         ("🔥 5-Day Streak!", "5 consecutive days of study — you're on fire!"),
        "streak_10":        ("💎 10-Day Streak!", "10 days in a row — incredible dedication!"),
        "perfect_score":    ("💯 Perfect Score!", "100% on a quiz — flawless!"),
    }

    async def update(self, event_type: str, data: dict) -> None:
        mapping = self.MILESTONE_MAP.get(event_type)
        if not mapping:
            return

        user_id = data.get("user_id")
        if not user_id:
            return

        title, message_template = mapping
        topic = data.get("topic_title", "this topic")
        message = message_template.format(topic=topic)

        from app.patterns.creational.singletons import NotificationServiceSingleton
        svc = NotificationServiceSingleton()
        client = svc.get_service_client()

        # Write achievement row
        if client:
            try:
                client.table("achievements").insert({
                    "user_id": user_id,
                    "title": title,
                    "description": message,
                    "badge_icon": "trophy",
                }).execute()
            except Exception as exc:
                logger.warning(f"Achievement insert failed: {exc}")

        # Write notification
        await svc.push_notification(
            user_id=user_id,
            notification_type="achievement_unlocked",
            title=title,
            message=message,
            metadata={"event_type": event_type},
        )
        logger.info(f"AchievementObserver: achievement {event_type!r} for user {user_id}")


class RecommendationObserver(Observer):
    """
    Fires when a new personalized recommendation is generated.
    Writes a 'recommendation' notification row.
    """

    async def update(self, event_type: str, data: dict) -> None:
        if event_type != "new_recommendation":
            return

        user_id = data.get("user_id")
        topic_title = data.get("topic_title", "a new topic")
        reason = data.get("reason", "based on your progress")

        if not user_id:
            return

        from app.patterns.creational.singletons import NotificationServiceSingleton
        svc = NotificationServiceSingleton()
        await svc.push_notification(
            user_id=user_id,
            notification_type="recommendation",
            title="✨ Recommended for You",
            message=f"Try {topic_title!r} — {reason}",
            metadata={"topic_title": topic_title, "reason": reason},
        )
        logger.info(f"RecommendationObserver: recommendation notification sent to user {user_id}")
