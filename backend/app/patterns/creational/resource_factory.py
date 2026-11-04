"""
FACTORY METHOD PATTERN — Creational
====================================
Defines an interface for creating learning resource objects, but lets
concrete factory classes decide which class to instantiate.

Used by: /resources router, quiz generation service
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import uuid


# ──────────────────────────────────────────────
# PRODUCT: LearningResource
# ──────────────────────────────────────────────

@dataclass
class LearningResource:
    id: str
    topic_id: str
    resource_type: str      # video | article | pdf | external_link
    title: str
    url: str
    source: str = ""
    duration: int | None = None   # seconds, for videos
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "type": self.resource_type,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "duration": self.duration,
            "metadata": self.metadata,
        }


@dataclass
class QuizObject:
    id: str
    topic_id: str
    title: str
    difficulty: str
    generated_by: str
    questions: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "title": self.title,
            "difficulty": self.difficulty,
            "generated_by": self.generated_by,
            "questions": self.questions,
        }


@dataclass
class UserProfile:
    id: str
    name: str
    interests: list[str] = field(default_factory=list)
    study_pace: str = "moderate"
    target_career: str = ""
    onboarding_done: bool = False


# ──────────────────────────────────────────────
# ABSTRACT CREATOR
# ──────────────────────────────────────────────

class ResourceCreator(ABC):
    """
    Abstract factory class. Subclasses override `factory_method()` to
    create a specific type of LearningResource.
    """

    @abstractmethod
    def factory_method(
        self,
        topic_id: str,
        title: str,
        url: str,
        source: str = "",
        duration: int | None = None,
        metadata: dict | None = None,
    ) -> LearningResource:
        ...

    def create_resource(
        self,
        topic_id: str,
        title: str,
        url: str,
        source: str = "",
        duration: int | None = None,
        metadata: dict | None = None,
    ) -> LearningResource:
        """Template method: calls factory_method and returns the product."""
        resource = self.factory_method(
            topic_id=topic_id,
            title=title,
            url=url,
            source=source,
            duration=duration,
            metadata=metadata or {},
        )
        return resource


# ──────────────────────────────────────────────
# CONCRETE CREATORS
# ──────────────────────────────────────────────

class VideoResourceFactory(ResourceCreator):
    """Creates video-type learning resources (YouTube, Coursera, etc.)."""

    def factory_method(self, topic_id, title, url, source="", duration=None, metadata=None) -> LearningResource:
        meta = metadata or {}
        meta.setdefault("embeddable", "youtube.com" in url or "vimeo.com" in url)
        return LearningResource(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            resource_type="video",
            title=title,
            url=url,
            source=source,
            duration=duration,
            metadata=meta,
        )


class ArticleResourceFactory(ResourceCreator):
    """Creates article/web-page learning resources."""

    def factory_method(self, topic_id, title, url, source="", duration=None, metadata=None) -> LearningResource:
        meta = metadata or {}
        meta.setdefault("reading_time_min", None)
        return LearningResource(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            resource_type="article",
            title=title,
            url=url,
            source=source,
            duration=None,      # articles don't have duration
            metadata=meta,
        )


class PDFResourceFactory(ResourceCreator):
    """Creates PDF/document learning resources."""

    def factory_method(self, topic_id, title, url, source="", duration=None, metadata=None) -> LearningResource:
        meta = metadata or {}
        meta.setdefault("pages", None)
        return LearningResource(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            resource_type="pdf",
            title=title,
            url=url,
            source=source,
            duration=None,
            metadata=meta,
        )


class ExternalLinkResourceFactory(ResourceCreator):
    """Creates external link resources (interactive tools, playgrounds, etc.)."""

    def factory_method(self, topic_id, title, url, source="", duration=None, metadata=None) -> LearningResource:
        meta = metadata or {}
        meta.setdefault("interactive", True)
        return LearningResource(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            resource_type="external_link",
            title=title,
            url=url,
            source=source,
            duration=None,
            metadata=meta,
        )


# ──────────────────────────────────────────────
# QUIZ FACTORY
# ──────────────────────────────────────────────

class QuizFactory:
    """
    Factory for creating quiz objects. Differentiates between AI-generated
    and manually created quizzes.
    """

    @staticmethod
    def create_ai_quiz(topic_id: str, title: str, difficulty: str, questions: list[dict]) -> QuizObject:
        return QuizObject(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            title=title,
            difficulty=difficulty,
            generated_by="ai",
            questions=questions,
        )

    @staticmethod
    def create_manual_quiz(topic_id: str, title: str, difficulty: str, questions: list[dict]) -> QuizObject:
        return QuizObject(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            title=title,
            difficulty=difficulty,
            generated_by="manual",
            questions=questions,
        )


# ──────────────────────────────────────────────
# USER PROFILE FACTORY
# ──────────────────────────────────────────────

class UserProfileFactory:
    """Factory for creating typed user profile objects from raw Supabase data."""

    @staticmethod
    def create_from_dict(data: dict) -> UserProfile:
        return UserProfile(
            id=data.get("id", ""),
            name=data.get("name", ""),
            interests=data.get("interests", []),
            study_pace=data.get("study_pace", "moderate"),
            target_career=data.get("target_career", ""),
            onboarding_done=data.get("onboarding_done", False),
        )

    @staticmethod
    def create_new(user_id: str, name: str) -> UserProfile:
        return UserProfile(
            id=user_id,
            name=name,
            interests=[],
            study_pace="moderate",
            target_career="",
            onboarding_done=False,
        )


# ──────────────────────────────────────────────
# FACTORY REGISTRY (convenience lookup by type string)
# ──────────────────────────────────────────────

RESOURCE_FACTORY_MAP: dict[str, ResourceCreator] = {
    "video":         VideoResourceFactory(),
    "article":       ArticleResourceFactory(),
    "pdf":           PDFResourceFactory(),
    "external_link": ExternalLinkResourceFactory(),
}


def get_resource_factory(resource_type: str) -> ResourceCreator:
    """Return the appropriate factory for the given resource type string."""
    factory = RESOURCE_FACTORY_MAP.get(resource_type)
    if factory is None:
        raise ValueError(f"Unknown resource type: {resource_type!r}. Must be one of {list(RESOURCE_FACTORY_MAP)}")
    return factory
