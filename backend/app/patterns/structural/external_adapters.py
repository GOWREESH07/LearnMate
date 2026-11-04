"""
ADAPTER PATTERN — Structural
==============================
Translates incompatible interfaces into a unified internal format.

ExternalResourceAdapter: normalizes third-party resource metadata
  (YouTube, Khan Academy, etc.) into LearnMate's LearningResource shape.

GeminiAIAdapter: wraps the raw google-generativeai SDK behind a clean
  internal interface so the AI provider can be swapped without touching
  any router or service code.
"""

from __future__ import annotations
import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# INTERNAL INTERFACE (the "target" interface)
# ──────────────────────────────────────────────

class ILearningResource:
    """Target interface that all resource adapters must produce."""
    topic_id: str
    resource_type: str
    title: str
    url: str
    source: str
    duration: Optional[int]
    metadata: dict


class IAIProvider:
    """Target interface for AI providers."""

    async def generate_quiz_questions(
        self, topic_title: str, difficulty: str, num_questions: int
    ) -> list[dict]:
        raise NotImplementedError

    async def chat(self, messages: list[dict], context: str) -> str:
        raise NotImplementedError

    async def generate_recommendation_text(self, user_context: str) -> str:
        raise NotImplementedError

    async def predict_performance(self, topic: str, user_context: str) -> dict:
        raise NotImplementedError


# ──────────────────────────────────────────────
# EXTERNAL RESOURCE ADAPTER
# ──────────────────────────────────────────────

class ExternalResourceAdapter:
    """
    Adapts third-party resource metadata formats (YouTube, Khan Academy,
    Coursera, arXiv, etc.) into LearnMate's internal LearningResource shape.
    """

    @staticmethod
    def from_youtube(video_data: dict, topic_id: str) -> dict:
        """Adapt a YouTube oEmbed/API response dict."""
        return {
            "topic_id": topic_id,
            "type": "video",
            "title": video_data.get("title", "Untitled Video"),
            "url": video_data.get("url") or video_data.get("webpage_url", ""),
            "source": "YouTube",
            "duration": video_data.get("duration"),         # seconds
            "metadata": {
                "thumbnail": video_data.get("thumbnail"),
                "channel": video_data.get("uploader") or video_data.get("channel_title"),
                "views": video_data.get("view_count"),
                "embeddable": True,
                "video_id": _extract_youtube_id(video_data.get("url", "")),
            },
        }

    @staticmethod
    def from_khan_academy(resource_data: dict, topic_id: str) -> dict:
        """Adapt a Khan Academy content item."""
        return {
            "topic_id": topic_id,
            "type": "video" if resource_data.get("kind") == "Video" else "article",
            "title": resource_data.get("display_name", resource_data.get("title", "")),
            "url": f"https://www.khanacademy.org{resource_data.get('canonical_path', '')}",
            "source": "Khan Academy",
            "duration": resource_data.get("duration"),
            "metadata": {
                "description": resource_data.get("description", ""),
                "free": True,
                "kind": resource_data.get("kind"),
                "thumbnail": resource_data.get("image_url"),
            },
        }

    @staticmethod
    def from_coursera(course_data: dict, topic_id: str) -> dict:
        """Adapt a Coursera course object."""
        return {
            "topic_id": topic_id,
            "type": "external_link",
            "title": course_data.get("name", ""),
            "url": f"https://www.coursera.org/learn/{course_data.get('slug', '')}",
            "source": "Coursera",
            "duration": None,
            "metadata": {
                "description": course_data.get("description", ""),
                "partner": course_data.get("partnerIds", []),
                "rating": course_data.get("rating"),
                "enrolled": course_data.get("enrolledCount"),
            },
        }

    @staticmethod
    def from_arxiv(paper_data: dict, topic_id: str) -> dict:
        """Adapt an arXiv paper entry."""
        return {
            "topic_id": topic_id,
            "type": "pdf",
            "title": paper_data.get("title", ""),
            "url": paper_data.get("pdf_url") or paper_data.get("link", ""),
            "source": "arXiv",
            "duration": None,
            "metadata": {
                "authors": paper_data.get("authors", []),
                "abstract": paper_data.get("summary", "")[:500],
                "arxiv_id": paper_data.get("id", ""),
                "published": paper_data.get("published", ""),
            },
        }

    @staticmethod
    def normalize(raw: dict, source_type: str, topic_id: str) -> dict:
        """Dispatch to the correct adapter based on source_type."""
        adapters = {
            "youtube": ExternalResourceAdapter.from_youtube,
            "khan_academy": ExternalResourceAdapter.from_khan_academy,
            "coursera": ExternalResourceAdapter.from_coursera,
            "arxiv": ExternalResourceAdapter.from_arxiv,
        }
        adapter_fn = adapters.get(source_type.lower())
        if adapter_fn:
            return adapter_fn(raw, topic_id)
        # Passthrough for unknown sources
        return {
            "topic_id": topic_id,
            "type": raw.get("type", "external_link"),
            "title": raw.get("title", ""),
            "url": raw.get("url", ""),
            "source": source_type,
            "duration": raw.get("duration"),
            "metadata": raw.get("metadata", {}),
        }


def _extract_youtube_id(url: str) -> str | None:
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"embed/([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


# ──────────────────────────────────────────────
# GEMINI AI ADAPTER
# ──────────────────────────────────────────────

class GeminiAIAdapter(IAIProvider):
    """
    Adapts the raw google-generativeai SDK behind the clean IAIProvider
    interface. Swapping the AI provider means only changing this class.
    """

    def __init__(self):
        from app.patterns.creational.singletons import AIRecommendationEngineSingleton
        self._engine = AIRecommendationEngineSingleton()

    async def generate_quiz_questions(
        self,
        topic_title: str,
        difficulty: str,
        num_questions: int = 5,
    ) -> list[dict]:
        """Generate multiple-choice quiz questions using Gemini."""
        prompt = f"""Generate {num_questions} multiple-choice quiz questions about "{topic_title}".
Difficulty level: {difficulty}.

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question_text": "The question",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Brief explanation of why this is correct"
  }}
]

Rules:
- Each question must have exactly 4 options
- correct_answer must be one of the options verbatim
- Explanations should be educational and concise (1-2 sentences)
- Questions should test genuine understanding, not just memorization
- Vary question types: conceptual, application, analysis"""

        response_text = await self._engine.generate_content(prompt)

        if not response_text:
            return self._fallback_questions(topic_title, difficulty, num_questions)

        return self._parse_quiz_json(response_text, topic_title, difficulty, num_questions)

    async def chat(self, messages: list[dict], context: str = "") -> str:
        """
        Generate a chat response grounded with the student's context.
        messages: list of {"role": "user"|"assistant", "content": str}
        """
        system_context = f"""You are LearnMate, a helpful and encouraging AI study assistant.
You have access to the following information about this student:

{context}

Respond in a warm, specific, student-focused way. Use the student's actual data
(courses, progress, quiz scores) to give personalized, grounded advice.
Keep responses concise but complete. Use markdown formatting when helpful."""

        # Build conversation history for the prompt
        history_text = "\n".join(
            f"{'Student' if m['role'] == 'user' else 'LearnMate'}: {m['content']}"
            for m in messages[-10:]  # last 10 turns for context window
        )

        full_prompt = f"{system_context}\n\nConversation:\n{history_text}\n\nLearnMate:"
        response = await self._engine.generate_content(full_prompt)
        return response or "I'm having trouble generating a response right now. Please try again."

    async def generate_recommendation_text(self, user_context: str) -> str:
        """Generate a personalized recommendation explanation."""
        prompt = f"""Based on this student's learning data:
{user_context}

Generate 3 specific, actionable learning recommendations. For each, explain briefly WHY
you're recommending it in the student's direct voice (e.g., "Because you scored 90% in...").
Format as a JSON array: [{{"topic": "...", "reason": "...", "action": "..."}}]"""

        response = await self._engine.generate_content(prompt)
        if not response:
            return "[]"
        # Extract JSON from response
        try:
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                return match.group(0)
        except Exception:
            pass
        return "[]"

    async def predict_performance(self, topic: str, user_context: str) -> dict:
        """Predict a student's quiz score for a topic based on their history."""
        prompt = f"""You are an educational AI predicting student performance.

Student context:
{user_context}

Predict the student's likely score (0-100) on a quiz about "{topic}".
Return ONLY valid JSON: {{"predicted_score": 75.0, "confidence": 0.80, "rationale": "brief reason"}}
Base the prediction on their progress in related topics and quiz history."""

        response = await self._engine.generate_content(prompt)
        if not response:
            return {"predicted_score": 70.0, "confidence": 0.5, "rationale": "Insufficient data for prediction."}

        try:
            match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return {
                    "predicted_score": float(data.get("predicted_score", 70)),
                    "confidence": float(data.get("confidence", 0.5)),
                    "rationale": str(data.get("rationale", "")),
                }
        except Exception as exc:
            logger.warning(f"Could not parse prediction response: {exc}")
        return {"predicted_score": 70.0, "confidence": 0.5, "rationale": "Prediction based on general patterns."}

    # ── Private helpers ──────────────────────────

    def _parse_quiz_json(
        self,
        text: str,
        topic_title: str,
        difficulty: str,
        num_questions: int,
    ) -> list[dict]:
        """Extract and validate quiz JSON from Gemini's response."""
        try:
            # Strip markdown code blocks if present
            cleaned = re.sub(r'```(?:json)?\s*', '', text).strip().rstrip('`')
            # Find the JSON array
            match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if match:
                questions = json.loads(match.group(0))
                # Validate structure
                validated = []
                for q in questions[:num_questions]:
                    if all(k in q for k in ("question_text", "options", "correct_answer")):
                        validated.append({
                            "question_text": q["question_text"],
                            "options": q["options"][:4],
                            "correct_answer": q["correct_answer"],
                            "explanation": q.get("explanation", ""),
                        })
                if validated:
                    return validated
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning(f"Quiz JSON parse failed: {exc}")
        return self._fallback_questions(topic_title, difficulty, num_questions)

    @staticmethod
    def _fallback_questions(topic_title: str, difficulty: str, num_questions: int) -> list[dict]:
        """Return placeholder questions when AI is unavailable."""
        return [
            {
                "question_text": f"[Placeholder] What is a key concept in {topic_title}?",
                "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
                "correct_answer": "Concept A",
                "explanation": "Configure GEMINI_API_KEY to enable AI-generated questions.",
            }
        ] * min(num_questions, 5)
