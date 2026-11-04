"""
STRATEGY PATTERN — Behavioral
================================
Defines a family of recommendation algorithms, encapsulates each one,
and makes them interchangeable. RecommendationContext picks the best
strategy at runtime based on available user data.

Used by: /recommendations router via LearningPlatformFacade.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# STRATEGY INTERFACE
# ──────────────────────────────────────────────

class RecommendationStrategy(ABC):
    """All recommendation strategies must implement this interface."""

    @abstractmethod
    async def recommend(
        self,
        user_id: str,
        user_profile: dict,
        progress_data: list[dict],
        supabase=None,
    ) -> list[dict]:
        """
        Return a list of recommendation dicts, each with:
          - topic_id, topic_title, course_title
          - reason: explanation in student's voice
          - strategy: name of this strategy (for UI display)
          - priority: int (lower = higher priority)
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


# ──────────────────────────────────────────────
# CONCRETE STRATEGIES
# ──────────────────────────────────────────────

class PerformanceBasedStrategy(RecommendationStrategy):
    """
    Recommends topics where the user has shown strength or gap.
    Logic: find mastered topics → surface related unstarted ones.
    """

    @property
    def name(self) -> str:
        return "performance_based"

    async def recommend(self, user_id, user_profile, progress_data, supabase=None) -> list[dict]:
        recs = []
        mastered = [p for p in progress_data if p.get("state") == "mastered"]
        not_started = [p for p in progress_data if p.get("state") == "not_started"]

        for topic in not_started[:3]:
            topic_info = topic.get("topics", {}) or {}
            course_info = (topic_info.get("courses") or {}) if isinstance(topic_info, dict) else {}
            recs.append({
                "topic_id": topic.get("topic_id"),
                "topic_title": topic_info.get("title", "Unknown Topic"),
                "course_title": course_info.get("title", ""),
                "reason": f"You've mastered {len(mastered)} topics — you're ready for this next challenge.",
                "strategy": self.name,
                "priority": 1,
            })
        return recs


class InterestBasedStrategy(RecommendationStrategy):
    """
    Recommends topics from courses that match the user's declared interests.
    """

    @property
    def name(self) -> str:
        return "interest_based"

    async def recommend(self, user_id, user_profile, progress_data, supabase=None) -> list[dict]:
        recs = []
        interests = user_profile.get("interests", [])
        if not interests or not supabase:
            return recs

        try:
            # Find courses matching interests
            result = (
                supabase.table("courses")
                .select("id, title, subject")
                .execute()
            )
            matching_courses = [
                c for c in (result.data or [])
                if any(interest.lower() in c.get("subject", "").lower() for interest in interests)
            ]

            # Find unstarted topics in matching courses
            started_ids = {p.get("topic_id") for p in progress_data if p.get("state") != "not_started"}
            for course in matching_courses[:2]:
                topics_res = (
                    supabase.table("topics")
                    .select("id, title")
                    .eq("course_id", course["id"])
                    .limit(3)
                    .execute()
                )
                for t in (topics_res.data or []):
                    if t["id"] not in started_ids:
                        interest_match = next(
                            (i for i in interests if i.lower() in course.get("subject", "").lower()),
                            interests[0] if interests else "your interests"
                        )
                        recs.append({
                            "topic_id": t["id"],
                            "topic_title": t["title"],
                            "course_title": course["title"],
                            "reason": f"Matches your interest in {interest_match}.",
                            "strategy": self.name,
                            "priority": 2,
                        })
                        if len(recs) >= 3:
                            return recs
        except Exception as exc:
            logger.warning(f"InterestBasedStrategy error: {exc}")
        return recs


class TimeAvailabilityStrategy(RecommendationStrategy):
    """
    Recommends short, quick-win topics based on the user's study pace.
    Slower pace → recommend shorter sessions; fast pace → deeper dives.
    """

    @property
    def name(self) -> str:
        return "time_availability"

    async def recommend(self, user_id, user_profile, progress_data, supabase=None) -> list[dict]:
        recs = []
        pace = user_profile.get("study_pace", "moderate")
        in_progress = [p for p in progress_data if p.get("state") == "in_progress"]

        label = {
            "slow": "a short, focused session",
            "moderate": "a steady study session",
            "fast": "an intensive deep-dive",
        }.get(pace, "a study session")

        for topic in in_progress[:3]:
            topic_info = topic.get("topics", {}) or {}
            course_info = (topic_info.get("courses") or {}) if isinstance(topic_info, dict) else {}
            recs.append({
                "topic_id": topic.get("topic_id"),
                "topic_title": topic_info.get("title", "Unknown"),
                "course_title": course_info.get("title", ""),
                "reason": f"You're already in progress here — perfect for {label} today.",
                "strategy": self.name,
                "priority": 3,
            })
        return recs


class CareerGoalStrategy(RecommendationStrategy):
    """
    Recommends topics most relevant to the user's declared target career.
    """

    CAREER_TOPIC_MAP = {
        "machine learning engineer": ["machine learning", "deep learning", "algorithms", "linear algebra"],
        "data scientist": ["statistics", "pandas", "regression", "visualization", "nlp"],
        "research physicist": ["quantum mechanics", "classical mechanics", "electromagnetism", "thermodynamics"],
        "software engineer": ["algorithms", "data structures", "databases", "operating systems"],
        "bioinformatician": ["genetics", "statistics", "pandas", "nlp"],
    }

    @property
    def name(self) -> str:
        return "career_goal"

    async def recommend(self, user_id, user_profile, progress_data, supabase=None) -> list[dict]:
        recs = []
        career = (user_profile.get("target_career") or "").lower()
        if not career:
            return recs

        # Find relevant keywords for this career
        relevant_keywords: list[str] = []
        for key, keywords in self.CAREER_TOPIC_MAP.items():
            if any(word in career for word in key.split()):
                relevant_keywords.extend(keywords)
                break
        if not relevant_keywords:
            return recs

        not_started = [p for p in progress_data if p.get("state") == "not_started"]
        for topic in not_started:
            topic_info = topic.get("topics", {}) or {}
            title_lower = topic_info.get("title", "").lower()
            if any(kw in title_lower for kw in relevant_keywords):
                course_info = (topic_info.get("courses") or {}) if isinstance(topic_info, dict) else {}
                recs.append({
                    "topic_id": topic.get("topic_id"),
                    "topic_title": topic_info.get("title", ""),
                    "course_title": course_info.get("title", ""),
                    "reason": f"Directly relevant to your goal of becoming a {career.title()}.",
                    "strategy": self.name,
                    "priority": 1,
                })
            if len(recs) >= 3:
                break
        return recs


# ──────────────────────────────────────────────
# CONTEXT
# ──────────────────────────────────────────────

class RecommendationContext:
    """
    Picks and switches between recommendation strategies at runtime
    based on the available user data.
    """

    def __init__(self):
        self._strategy: RecommendationStrategy = PerformanceBasedStrategy()

    def select_strategy(self, user_profile: dict, progress_data: list[dict]) -> None:
        """
        Automatically choose the best strategy based on data availability:
        1. Career goal strategy if target_career is set
        2. Interest-based if interests are set
        3. Time-availability if topics are in_progress
        4. Performance-based as default
        """
        career = user_profile.get("target_career", "")
        interests = user_profile.get("interests", [])
        in_progress = [p for p in progress_data if p.get("state") == "in_progress"]

        if career:
            self._strategy = CareerGoalStrategy()
        elif interests:
            self._strategy = InterestBasedStrategy()
        elif in_progress:
            self._strategy = TimeAvailabilityStrategy()
        else:
            self._strategy = PerformanceBasedStrategy()

        logger.info(f"RecommendationContext selected strategy: {self._strategy.name}")

    def set_strategy(self, strategy: RecommendationStrategy) -> None:
        """Manually override the strategy (for testing or explicit selection)."""
        self._strategy = strategy
        logger.info(f"RecommendationContext strategy set to: {strategy.name}")

    @property
    def current_strategy_name(self) -> str:
        return self._strategy.name

    async def get_recommendations(
        self,
        user_id: str,
        user_profile: dict,
        progress_data: list[dict],
        supabase=None,
    ) -> list[dict]:
        recs = await self._strategy.recommend(
            user_id=user_id,
            user_profile=user_profile,
            progress_data=progress_data,
            supabase=supabase,
        )
        if not recs and not isinstance(self._strategy, PerformanceBasedStrategy):
            # Fallback to PerformanceBasedStrategy
            fallback = PerformanceBasedStrategy()
            recs = await fallback.recommend(
                user_id=user_id,
                user_profile=user_profile,
                progress_data=progress_data,
                supabase=supabase,
            )
        if not recs and not isinstance(self._strategy, TimeAvailabilityStrategy):
            # Fallback to TimeAvailabilityStrategy
            fallback = TimeAvailabilityStrategy()
            recs = await fallback.recommend(
                user_id=user_id,
                user_profile=user_profile,
                progress_data=progress_data,
                supabase=supabase,
            )
        return recs
