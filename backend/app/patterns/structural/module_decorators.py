"""
DECORATOR PATTERN — Structural
================================
Adds behaviour to LearningModule objects dynamically without altering
the base class. Decorators wrap modules and add:
  - VoiceAssistanceDecorator: TTS narration metadata
  - PremiumContentDecorator: extra premium resources
  - GamificationDecorator: points, badges, and XP tracking

Used by: topic/resource service when serving enhanced content.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ──────────────────────────────────────────────
# COMPONENT INTERFACE
# ──────────────────────────────────────────────

class LearningModule(ABC):
    """Base component interface that all modules and decorators implement."""

    @abstractmethod
    def get_content(self) -> dict:
        """Return the module's content dict."""
        ...

    @abstractmethod
    def get_features(self) -> list[str]:
        """Return a list of active feature names."""
        ...

    @abstractmethod
    def get_title(self) -> str:
        ...


# ──────────────────────────────────────────────
# CONCRETE COMPONENT
# ──────────────────────────────────────────────

@dataclass
class BasicLearningModule(LearningModule):
    """The base learning module without any enhancements."""
    topic_id: str
    title: str
    description: str
    resources: list[dict] = field(default_factory=list)

    def get_content(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "description": self.description,
            "resources": self.resources,
            "features": self.get_features(),
        }

    def get_features(self) -> list[str]:
        return ["basic"]

    def get_title(self) -> str:
        return self.title


# ──────────────────────────────────────────────
# BASE DECORATOR
# ──────────────────────────────────────────────

class LearningModuleDecorator(LearningModule):
    """
    Abstract decorator. Wraps a LearningModule and delegates to it,
    while subclasses add their own behaviour.
    """

    def __init__(self, wrapped: LearningModule):
        self._wrapped = wrapped

    def get_content(self) -> dict:
        return self._wrapped.get_content()

    def get_features(self) -> list[str]:
        return self._wrapped.get_features()

    def get_title(self) -> str:
        return self._wrapped.get_title()


# ──────────────────────────────────────────────
# CONCRETE DECORATORS
# ──────────────────────────────────────────────

class VoiceAssistanceDecorator(LearningModuleDecorator):
    """
    Adds text-to-speech (TTS) narration metadata to the module content.
    The frontend can use this to show a "Listen" button.
    """

    def __init__(self, wrapped: LearningModule, voice: str = "en-US-Neural2-F"):
        super().__init__(wrapped)
        self._voice = voice

    def get_content(self) -> dict:
        content = self._wrapped.get_content()
        content["voice_assistance"] = {
            "enabled": True,
            "voice": self._voice,
            "tts_text": f"Welcome to {self.get_title()}. {content.get('description', '')}",
            "auto_play": False,
        }
        content["features"] = self.get_features()
        return content

    def get_features(self) -> list[str]:
        return self._wrapped.get_features() + ["voice_assistance"]


class PremiumContentDecorator(LearningModuleDecorator):
    """
    Adds premium resources (extra videos, practice problems, expert notes)
    to the module. In a real system this would gate on subscription tier.
    """

    def __init__(
        self,
        wrapped: LearningModule,
        premium_resources: list[dict] | None = None,
    ):
        super().__init__(wrapped)
        self._premium_resources = premium_resources or []

    def get_content(self) -> dict:
        content = self._wrapped.get_content()
        base_resources = content.get("resources", [])
        content["resources"] = base_resources + self._premium_resources
        content["premium"] = {
            "enabled": True,
            "extra_resource_count": len(self._premium_resources),
            "badge": "⭐ Premium",
        }
        content["features"] = self.get_features()
        return content

    def get_features(self) -> list[str]:
        return self._wrapped.get_features() + ["premium_content"]


class GamificationDecorator(LearningModuleDecorator):
    """
    Adds gamification layer: XP points, badges, and progress milestones.
    Tied into the AchievementObserver — reaching milestones fires achievements.
    """

    XP_PER_RESOURCE_VIEWED = 10
    XP_PER_QUIZ_PASSED = 50
    XP_TOPIC_MASTERED = 100

    def __init__(
        self,
        wrapped: LearningModule,
        user_xp: int = 0,
        resources_completed: int = 0,
    ):
        super().__init__(wrapped)
        self._user_xp = user_xp
        self._resources_completed = resources_completed

    def get_content(self) -> dict:
        content = self._wrapped.get_content()
        total_resources = len(content.get("resources", []))
        progress_pct = (
            round(self._resources_completed / total_resources * 100)
            if total_resources > 0 else 0
        )

        content["gamification"] = {
            "user_xp": self._user_xp,
            "resources_completed": self._resources_completed,
            "total_resources": total_resources,
            "progress_percentage": progress_pct,
            "xp_rewards": {
                "per_resource": self.XP_PER_RESOURCE_VIEWED,
                "per_quiz": self.XP_PER_QUIZ_PASSED,
                "topic_mastery": self.XP_TOPIC_MASTERED,
            },
            "badges": self._compute_badges(),
            "next_milestone": self._next_milestone(progress_pct),
        }
        content["features"] = self.get_features()
        return content

    def get_features(self) -> list[str]:
        return self._wrapped.get_features() + ["gamification"]

    def _compute_badges(self) -> list[dict]:
        badges = []
        if self._resources_completed >= 1:
            badges.append({"id": "first_step", "label": "First Step", "icon": "👣"})
        if self._user_xp >= 100:
            badges.append({"id": "century_club", "label": "Century Club", "icon": "💯"})
        if self._user_xp >= 500:
            badges.append({"id": "knowledge_seeker", "label": "Knowledge Seeker", "icon": "📚"})
        return badges

    def _next_milestone(self, progress_pct: int) -> dict:
        if progress_pct < 25:
            return {"at": 25, "label": "Quarter way there!", "xp_bonus": 20}
        if progress_pct < 50:
            return {"at": 50, "label": "Halfway point!", "xp_bonus": 30}
        if progress_pct < 75:
            return {"at": 75, "label": "Almost there!", "xp_bonus": 40}
        if progress_pct < 100:
            return {"at": 100, "label": "Topic complete!", "xp_bonus": self.XP_TOPIC_MASTERED}
        return {"at": 100, "label": "Fully completed!", "xp_bonus": 0}


# ──────────────────────────────────────────────
# CONVENIENCE BUILDER
# ──────────────────────────────────────────────

def build_enhanced_module(
    topic: dict,
    resources: list[dict],
    user_xp: int = 0,
    resources_completed: int = 0,
    enable_voice: bool = False,
    is_premium: bool = False,
    premium_resources: list[dict] | None = None,
) -> LearningModule:
    """
    Convenience function: wrap a BasicLearningModule with the appropriate
    decorators based on user/content flags.
    """
    module: LearningModule = BasicLearningModule(
        topic_id=topic.get("id", ""),
        title=topic.get("title", ""),
        description=topic.get("description", ""),
        resources=resources,
    )
    # Always apply gamification
    module = GamificationDecorator(module, user_xp=user_xp, resources_completed=resources_completed)
    if enable_voice:
        module = VoiceAssistanceDecorator(module)
    if is_premium:
        module = PremiumContentDecorator(module, premium_resources=premium_resources or [])
    return module
