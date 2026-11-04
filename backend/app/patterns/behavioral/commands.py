"""
COMMAND PATTERN — Behavioral
==============================
Encapsulates user actions as command objects with execute() and (where
applicable) undo(). A CommandInvoker logs all executed commands for
audit trails and makes the system easy to extend with new actions.

Used by: routers call CommandInvoker.execute_command(cmd) instead of
inline logic.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# COMMAND INTERFACE
# ──────────────────────────────────────────────

class Command(ABC):
    """All command objects must implement execute (and optionally undo)."""

    @property
    def command_id(self) -> str:
        return str(uuid.uuid4())

    @abstractmethod
    async def execute(self) -> dict:
        """Execute the command and return a result dict."""
        ...

    async def undo(self) -> dict:
        """Undo the command (default: not supported)."""
        return {"undone": False, "message": f"{type(self).__name__} does not support undo."}

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description for audit log."""
        ...


# ──────────────────────────────────────────────
# CONCRETE COMMANDS
# ──────────────────────────────────────────────

class GenerateQuizCommand(Command):
    """
    Command to generate an AI quiz for a topic.
    execute() → calls LearningPlatformFacade.generate_quiz()
    undo()    → deletes the generated quiz (if still unattempted)
    """

    def __init__(
        self,
        topic_id: str,
        topic_title: str,
        difficulty: str,
        user_id: str,
        supabase=None,
    ):
        self._topic_id = topic_id
        self._topic_title = topic_title
        self._difficulty = difficulty
        self._user_id = user_id
        self._supabase = supabase
        self._generated_quiz_id: Optional[str] = None

    @property
    def description(self) -> str:
        return f"Generate AI quiz for topic '{self._topic_title}' (difficulty: {self._difficulty})"

    async def execute(self) -> dict:
        from app.patterns.structural.learning_facade import LearningPlatformFacade
        facade = LearningPlatformFacade(supabase_client=self._supabase)
        result = await facade.generate_quiz(
            topic_id=self._topic_id,
            topic_title=self._topic_title,
            difficulty=self._difficulty,
            user_id=self._user_id,
        )
        self._generated_quiz_id = result.get("id")
        return result

    async def undo(self) -> dict:
        """Delete the generated quiz if no attempts have been made yet."""
        if not self._generated_quiz_id or not self._supabase:
            return {"undone": False, "message": "No quiz to undo."}
        try:
            # Check for attempts first
            attempts = (
                self._supabase.table("quiz_attempts")
                .select("id")
                .eq("quiz_id", self._generated_quiz_id)
                .execute()
            )
            if attempts.data:
                return {"undone": False, "message": "Quiz has attempts — cannot undo."}
            # Delete questions then quiz
            self._supabase.table("quiz_questions").delete().eq("quiz_id", self._generated_quiz_id).execute()
            self._supabase.table("quizzes").delete().eq("id", self._generated_quiz_id).execute()
            return {"undone": True, "quiz_id": self._generated_quiz_id}
        except Exception as exc:
            return {"undone": False, "message": str(exc)}


class CreateStudyPlanCommand(Command):
    """
    Command to create a study plan using StudyPlanBuilder.
    execute() → builds the plan, persists to Supabase
    undo()    → deletes the plan (if no items are marked complete)
    """

    def __init__(self, plan_data: dict, user_id: str, supabase=None):
        self._plan_data = plan_data
        self._user_id = user_id
        self._supabase = supabase
        self._created_plan_id: Optional[str] = None

    @property
    def description(self) -> str:
        return f"Create study plan '{self._plan_data.get('title', 'Untitled')}' for user {self._user_id}"

    async def execute(self) -> dict:
        from app.patterns.creational.study_plan_builder import StudyPlanBuilder
        from datetime import date

        data = self._plan_data
        builder = StudyPlanBuilder(user_id=self._user_id, title=data.get("title", "My Study Plan"))
        builder.set_goal(data.get("goal", ""))

        start = data.get("start_date")
        end = data.get("end_date")
        if start and end:
            start_val = date.fromisoformat(start) if isinstance(start, str) else start
            end_val = date.fromisoformat(end) if isinstance(end, str) else end
            builder.set_schedule(
                start=start_val,
                end=end_val,
            )
        builder.set_duration(data.get("duration_minutes", 45))

        topics = data.get("topics", [])
        if topics:
            builder.add_topics_auto_scheduled(topics, sessions_per_week=data.get("sessions_per_week", 3))

        plan = builder.build()
        self._created_plan_id = plan.id

        # Persist to Supabase
        sb = self._supabase
        if not sb:
            from app.services.database import get_service_supabase, get_supabase
            sb = get_service_supabase() or get_supabase()

        if sb:
            sb.table("study_plans").insert({
                "id": plan.id,
                "user_id": plan.user_id,
                "title": plan.title,
                "goal": plan.goal,
                "start_date": plan.start_date.isoformat(),
                "end_date": plan.end_date.isoformat(),
                "status": plan.status,
            }).execute()

            for item in plan.items:
                sb.table("study_plan_items").insert({
                    "study_plan_id": plan.id,
                    "topic_id": item.topic_id,
                    "scheduled_date": item.scheduled_date.isoformat(),
                    "duration_minutes": item.duration_minutes,
                    "completed": item.completed,
                }).execute()

        return plan.to_dict()

    async def undo(self) -> dict:
        if not self._created_plan_id or not self._supabase:
            return {"undone": False, "message": "No plan to undo."}
        try:
            completed = (
                self._supabase.table("study_plan_items")
                .select("id")
                .eq("study_plan_id", self._created_plan_id)
                .eq("completed", True)
                .execute()
            )
            if completed.data:
                return {"undone": False, "message": "Plan has completed items — cannot undo."}
            self._supabase.table("study_plan_items").delete().eq("study_plan_id", self._created_plan_id).execute()
            self._supabase.table("study_plans").delete().eq("id", self._created_plan_id).execute()
            return {"undone": True, "plan_id": self._created_plan_id}
        except Exception as exc:
            return {"undone": False, "message": str(exc)}


class UpdateProgressCommand(Command):
    """
    Command to update a topic's progress state.
    execute() → calls LearningPlatformFacade.update_topic_state()
    undo()    → reverts to the previous state
    """

    def __init__(
        self,
        user_id: str,
        topic_id: str,
        new_state: str,
        supabase=None,
    ):
        self._user_id = user_id
        self._topic_id = topic_id
        self._new_state = new_state
        self._supabase = supabase
        self._previous_state: Optional[str] = None

    @property
    def description(self) -> str:
        return f"Update topic {self._topic_id} to state '{self._new_state}' for user {self._user_id}"

    async def execute(self) -> dict:
        # Capture current state for undo
        if self._supabase:
            result = (
                self._supabase.table("topic_progress")
                .select("state")
                .eq("user_id", self._user_id)
                .eq("topic_id", self._topic_id)
                .execute()
            )
            self._previous_state = result.data[0]["state"] if result.data else "not_started"

        from app.patterns.structural.learning_facade import LearningPlatformFacade
        facade = LearningPlatformFacade(supabase_client=self._supabase)
        return await facade.update_topic_state(
            user_id=self._user_id,
            topic_id=self._topic_id,
            new_state=self._new_state,
        )

    async def undo(self) -> dict:
        if not self._previous_state or not self._supabase:
            return {"undone": False, "message": "No previous state to revert to."}
        self._supabase.table("topic_progress").upsert({
            "user_id": self._user_id,
            "topic_id": self._topic_id,
            "state": self._previous_state,
        }).execute()
        return {
            "undone": True,
            "topic_id": self._topic_id,
            "reverted_to": self._previous_state,
        }


# ──────────────────────────────────────────────
# AUDIT LOG ENTRY
# ──────────────────────────────────────────────

@dataclass
class AuditLogEntry:
    command_type: str
    description: str
    executed_at: datetime = field(default_factory=datetime.utcnow)
    result: dict = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


# ──────────────────────────────────────────────
# COMMAND INVOKER
# ──────────────────────────────────────────────

class CommandInvoker:
    """
    Receives and executes commands. Maintains an in-process audit log.
    Routers call execute_command() to run any command.
    """

    def __init__(self):
        self._history: list[AuditLogEntry] = []
        self._last_command: Optional[Command] = None

    async def execute_command(self, command: Command) -> dict:
        """Execute a command and log it."""
        self._last_command = command
        logger.info(f"CommandInvoker executing: {command.description}")
        try:
            result = await command.execute()
            self._history.append(
                AuditLogEntry(
                    command_type=type(command).__name__,
                    description=command.description,
                    result=result,
                    success=True,
                )
            )
            return result
        except Exception as exc:
            self._history.append(
                AuditLogEntry(
                    command_type=type(command).__name__,
                    description=command.description,
                    success=False,
                    error=str(exc),
                )
            )
            raise

    async def undo_last(self) -> dict:
        """Undo the last executed command (if supported)."""
        if not self._last_command:
            return {"undone": False, "message": "No command to undo."}
        return await self._last_command.undo()

    def get_audit_log(self, limit: int = 50) -> list[dict]:
        """Return the most recent audit log entries."""
        return [
            {
                "command": entry.command_type,
                "description": entry.description,
                "executed_at": entry.executed_at.isoformat(),
                "success": entry.success,
                "error": entry.error,
            }
            for entry in self._history[-limit:]
        ]


# ── Shared invoker instance (imported by routers) ──
command_invoker = CommandInvoker()
