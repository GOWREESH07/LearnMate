"""
STATE PATTERN — Behavioral
============================
Allows a topic's behaviour to change when its internal state changes.
Each state object defines valid transitions (so illegal jumps are rejected)
and what actions are available in that state.

Backs the `topic_progress.state` column and the progress trail UI.

Valid transition graph:
  not_started → in_progress     (on first resource view)
  in_progress → practicing      (on first quiz attempt)
  practicing  → mastered        (on quiz score ≥ 80%)
  Any state   → not_started     (reset — optional)
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ──────────────────────────────────────────────
# STATE INTERFACE
# ──────────────────────────────────────────────

class TopicState(ABC):
    """
    Abstract state. Each concrete state knows what transitions are allowed
    from it and what the state label/colour should be for the UI.
    """

    @property
    @abstractmethod
    def state_name(self) -> str:
        ...

    @property
    @abstractmethod
    def display_label(self) -> str:
        ...

    @property
    @abstractmethod
    def display_color(self) -> str:
        """CSS color token or hex for the progress badge."""
        ...

    @property
    @abstractmethod
    def marker_icon(self) -> str:
        """Icon for the progress trail notebook marker."""
        ...

    @abstractmethod
    def allowed_transitions(self) -> list[str]:
        """Return list of state names this state can transition to."""
        ...

    def can_transition_to(self, target: str) -> bool:
        return target in self.allowed_transitions()

    @abstractmethod
    def on_enter(self, context: "TopicStateContext") -> dict:
        """Return a dict describing any side-effects when entering this state."""
        ...

    def to_dict(self) -> dict:
        return {
            "state": self.state_name,
            "label": self.display_label,
            "color": self.display_color,
            "icon": self.marker_icon,
            "allowed_transitions": self.allowed_transitions(),
        }


# ──────────────────────────────────────────────
# CONCRETE STATES
# ──────────────────────────────────────────────

class NotStartedState(TopicState):
    """Topic has not been opened yet."""

    @property
    def state_name(self) -> str: return "not_started"

    @property
    def display_label(self) -> str: return "Not Started"

    @property
    def display_color(self) -> str: return "#9CA3AF"   # neutral gray

    @property
    def marker_icon(self) -> str: return "○"           # empty circle

    def allowed_transitions(self) -> list[str]:
        return ["in_progress"]

    def on_enter(self, context: "TopicStateContext") -> dict:
        return {"action": "reset", "message": "Topic reset to Not Started."}


class InProgressState(TopicState):
    """User has opened the topic and is consuming resources."""

    @property
    def state_name(self) -> str: return "in_progress"

    @property
    def display_label(self) -> str: return "In Progress"

    @property
    def display_color(self) -> str: return "#3B82F6"   # blue

    @property
    def marker_icon(self) -> str: return "◑"           # half-filled circle

    def allowed_transitions(self) -> list[str]:
        return ["practicing", "not_started"]

    def on_enter(self, context: "TopicStateContext") -> dict:
        return {
            "action": "start_studying",
            "message": "You've started this topic. Work through the resources and take a quiz to advance.",
        }


class PracticingState(TopicState):
    """User has attempted at least one quiz — now actively practicing."""

    @property
    def state_name(self) -> str: return "practicing"

    @property
    def display_label(self) -> str: return "Practicing"

    @property
    def display_color(self) -> str: return "#F59E0B"   # amber

    @property
    def marker_icon(self) -> str: return "◕"           # mostly-filled circle

    def allowed_transitions(self) -> list[str]:
        return ["mastered", "in_progress"]

    def on_enter(self, context: "TopicStateContext") -> dict:
        return {
            "action": "practice_mode",
            "message": "Great — you're practicing! Score 80%+ on a quiz to mark this topic as Mastered.",
        }


class MasteredState(TopicState):
    """
    User has scored ≥ 80% on a quiz for this topic.
    This is the terminal success state.
    """

    MASTERY_SCORE_THRESHOLD = 80.0

    @property
    def state_name(self) -> str: return "mastered"

    @property
    def display_label(self) -> str: return "Mastered"

    @property
    def display_color(self) -> str: return "#2D6A4F"   # Forest Ink (brand primary)

    @property
    def marker_icon(self) -> str: return "✓"           # checkmark

    def allowed_transitions(self) -> list[str]:
        return ["practicing"]   # allow downgrade if user wants more practice

    def on_enter(self, context: "TopicStateContext") -> dict:
        return {
            "action": "achievement",
            "message": "🏆 You've mastered this topic! An achievement has been unlocked.",
            "trigger_achievement": True,
        }

    @classmethod
    def qualifies(cls, quiz_score: float) -> bool:
        """Check if a quiz score qualifies for mastery."""
        return quiz_score >= cls.MASTERY_SCORE_THRESHOLD


# ──────────────────────────────────────────────
# STATE FACTORY
# ──────────────────────────────────────────────

_STATE_CLASSES: dict[str, type[TopicState]] = {
    "not_started": NotStartedState,
    "in_progress": InProgressState,
    "practicing": PracticingState,
    "mastered": MasteredState,
}


def get_state(state_name: str) -> TopicState:
    cls = _STATE_CLASSES.get(state_name)
    if cls is None:
        raise ValueError(f"Unknown state: {state_name!r}. Must be one of {list(_STATE_CLASSES)}")
    return cls()


# ──────────────────────────────────────────────
# CONTEXT
# ──────────────────────────────────────────────

class TopicStateContext:
    """
    Holds the current TopicState and delegates state-specific logic to it.
    Routes call this context instead of working with state strings directly.
    """

    def __init__(self, current_state: str = "not_started"):
        self._state: TopicState = get_state(current_state)

    @property
    def current_state(self) -> TopicState:
        return self._state

    @property
    def state_name(self) -> str:
        return self._state.state_name

    def can_transition_to(self, target: str) -> bool:
        return self._state.can_transition_to(target)

    def transition_to(self, target: str) -> dict:
        """
        Transition to the target state.
        Returns the on_enter result dict.
        Raises ValueError if the transition is not allowed.
        """
        if not self.can_transition_to(target):
            raise ValueError(
                f"Cannot transition from {self._state.state_name!r} to {target!r}. "
                f"Allowed: {self._state.allowed_transitions()}"
            )
        new_state = get_state(target)
        self._state = new_state
        return new_state.on_enter(self)

    def get_state_info(self) -> dict:
        return self._state.to_dict()

    @staticmethod
    def determine_state_from_quiz_score(score: float, current_state: str) -> str:
        """
        Given a quiz score and current state, determine the new state.
        Called by the quiz completion handler.
        """
        if MasteredState.qualifies(score) and current_state in ("practicing", "in_progress"):
            return "mastered"
        if current_state == "in_progress":
            return "practicing"
        return current_state   # no change

    @staticmethod
    def all_states() -> list[dict]:
        """Return info dicts for all states (used by frontend for legend rendering)."""
        return [get_state(s).to_dict() for s in _STATE_CLASSES]
