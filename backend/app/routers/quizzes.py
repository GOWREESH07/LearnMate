"""Quizzes router — Factory Method + Command + State pattern integration."""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import GenerateQuizRequest, QuizResponse, QuizAttemptRequest, QuizAttemptResponse, QuizQuestion
from app.services.database import get_supabase
from app.patterns.behavioral.commands import GenerateQuizCommand, command_invoker
from app.patterns.behavioral.topic_state import TopicStateContext, MasteredState
import logging
import uuid
from datetime import datetime

router = APIRouter(prefix="/quizzes", tags=["quizzes"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(req: GenerateQuizRequest, user_id: str = Query(...)):
    """
    Generate an AI quiz via GenerateQuizCommand (Command pattern).
    Internally uses QuizFactory + GeminiAIAdapter + QuizGeneratedObserver.
    """
    sb = get_supabase()
    cmd = GenerateQuizCommand(
        topic_id=req.topic_id,
        topic_title=req.topic_title,
        difficulty=req.difficulty.value,
        user_id=user_id,
        supabase=sb,
    )
    try:
        result = await command_invoker.execute_command(cmd)
        questions = [QuizQuestion(**q) for q in result.get("questions", [])]
        return QuizResponse(
            id=result["id"],
            topic_id=result["topic_id"],
            title=result["title"],
            difficulty=result["difficulty"],
            generated_by=result["generated_by"],
            questions=questions,
        )
    except RuntimeError as exc:
        raise HTTPException(503, f"Quiz generation failed: {exc}. Configure GEMINI_API_KEY.")
    except Exception as exc:
        logger.error(f"Generate quiz error: {exc}")
        raise HTTPException(500, str(exc))


@router.get("/topic/{topic_id}", response_model=list[QuizResponse])
async def get_quizzes_for_topic(topic_id: str):
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("quizzes").select("*, quiz_questions(*)").eq("topic_id", topic_id).order("created_at", desc=True).execute()
        quizzes = []
        for q in (res.data or []):
            questions = [QuizQuestion(**qq) for qq in (q.pop("quiz_questions", []) or [])]
            quizzes.append(QuizResponse(**q, questions=questions))
        return quizzes
    except Exception as exc:
        logger.error(f"Get quizzes error: {exc}")
        return []


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str):
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        res = sb.table("quizzes").select("*").eq("id", quiz_id).single().execute()
        if not res.data:
            raise HTTPException(404, "Quiz not found")
        qs_res = sb.table("quiz_questions").select("*").eq("quiz_id", quiz_id).order("order_index").execute()
        questions = [QuizQuestion(**q) for q in (qs_res.data or [])]
        return QuizResponse(**res.data, questions=questions)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.post("/attempt", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(req: QuizAttemptRequest, user_id: str = Query(...)):
    """
    Score a quiz attempt, update topic state via State pattern if eligible.
    """
    sb = get_supabase()
    if not sb:
        raise HTTPException(503, "Database not configured")
    try:
        # Fetch questions
        qs_res = sb.table("quiz_questions").select("*").eq("quiz_id", req.quiz_id).execute()
        questions = qs_res.data or []
        if not questions:
            raise HTTPException(404, "Quiz questions not found")

        # Score the attempt
        correct = sum(
            1 for q in questions
            if req.answers.get(q["id"]) == q["correct_answer"]
        )
        score = round(correct / len(questions) * 100, 1) if questions else 0

        # Save attempt
        attempt_id = str(uuid.uuid4())
        now = datetime.utcnow()
        sb.table("quiz_attempts").insert({
            "id": attempt_id,
            "user_id": user_id,
            "quiz_id": req.quiz_id,
            "score": score,
            "answers": req.answers,
            "completed_at": now.isoformat(),
        }).execute()

        # Determine new topic state via State pattern
        quiz_res = sb.table("quizzes").select("topic_id").eq("id", req.quiz_id).single().execute()
        topic_id = quiz_res.data.get("topic_id") if quiz_res.data else None
        new_state = None

        if topic_id:
            prog = sb.table("topic_progress").select("state").eq("user_id", user_id).eq("topic_id", topic_id).execute()
            current_state = prog.data[0]["state"] if prog.data else "in_progress"
            new_state = TopicStateContext.determine_state_from_quiz_score(score, current_state)

            if new_state != current_state:
                from app.patterns.behavioral.commands import UpdateProgressCommand
                cmd = UpdateProgressCommand(user_id=user_id, topic_id=topic_id, new_state=new_state, supabase=sb)
                try:
                    await command_invoker.execute_command(cmd)
                except Exception as exc:
                    logger.warning(f"State transition failed: {exc}")

            # Perfect score achievement
            if score == 100:
                from app.patterns.behavioral.notification_observer import NotificationSubject, AchievementObserver
                subj = NotificationSubject()
                subj.attach(AchievementObserver())
                try:
                    await subj.notify("perfect_score", {"user_id": user_id})
                except Exception:
                    pass

        return QuizAttemptResponse(
            id=attempt_id,
            quiz_id=req.quiz_id,
            user_id=user_id,
            score=score,
            answers=req.answers,
            completed_at=now,
            new_topic_state=new_state,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Quiz attempt error: {exc}")
        raise HTTPException(500, str(exc))


@router.get("/user/{user_id}/attempts")
async def get_user_quiz_attempts(user_id: str, limit: int = 20):
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("quiz_attempts").select("*, quizzes(title, topic_id, topics(title))").eq("user_id", user_id).order("completed_at", desc=True).limit(limit).execute()
        return res.data or []
    except Exception as exc:
        logger.error(f"Get attempts error: {exc}")
        return []
