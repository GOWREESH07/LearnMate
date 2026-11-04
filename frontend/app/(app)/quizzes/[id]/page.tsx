"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { formatScore, cn } from "@/lib/utils";
import { ArrowLeft, CheckCircle, XCircle, Loader2 } from "lucide-react";
import Link from "next/link";

type QuizState = "idle" | "taking" | "submitted";

export default function QuizTakePage() {
  const { id } = useParams() as { id: string };
  const { user } = useAuth();
  const router = useRouter();
  const [quiz, setQuiz] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [quizState, setQuizState] = useState<QuizState>("idle");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!id) return;
    api.quizzes.get(id).then((q) => {
      setQuiz(q);
      setQuizState("taking");
    }).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit() {
    if (!user || !quiz) return;
    const allAnswered = quiz.questions.every((q: any) => answers[q.id]);
    if (!allAnswered) {
      alert("Please answer all questions before submitting.");
      return;
    }
    setSubmitting(true);
    try {
      const res = await api.quizzes.submitAttempt({ quiz_id: quiz.id, answers }, user.id);
      setResult(res);
      setQuizState("submitted");
    } catch (err: any) {
      alert(`Submit failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-paper">
      <Loader2 className="w-8 h-8 animate-spin text-primary" />
    </div>
  );

  if (!quiz) return <div className="p-8 text-center text-muted">Quiz not found.</div>;

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-3xl mx-auto">
      <Link href="/quizzes" className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink mb-6">
        <ArrowLeft className="w-4 h-4" /> All quizzes
      </Link>

      <div className="mb-6">
        <span className="text-2xs font-mono text-muted uppercase tracking-wide">{quiz.difficulty} · AI Generated</span>
        <h1 className="font-serif text-2xl text-ink mt-1">{quiz.title}</h1>
      </div>

      {quizState === "submitted" && result ? (
        <ResultView result={result} quiz={quiz} answers={answers} onRetry={() => { setAnswers({}); setResult(null); setQuizState("taking"); }} />
      ) : (
        <>
          {/* Progress */}
          <div className="flex items-center justify-between text-2xs font-mono text-muted mb-6">
            <span>{Object.keys(answers).length} / {quiz.questions.length} answered</span>
            <span>{quiz.questions.length} questions</span>
          </div>

          {/* Questions */}
          <div className="space-y-6">
            {quiz.questions.map((q: any, idx: number) => (
              <div key={q.id} className="planner-card">
                <p className="font-medium text-ink mb-3">
                  <span className="font-mono text-muted text-sm mr-2">{idx + 1}.</span>
                  {q.question_text}
                </p>
                <div className="space-y-2">
                  {q.options.map((opt: string) => (
                    <button
                      key={opt}
                      onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                      className={cn(
                        "w-full text-left px-4 py-2.5 rounded-md text-sm border transition-all",
                        answers[q.id] === opt
                          ? "border-primary bg-primary/5 text-primary font-medium"
                          : "border-border text-ink hover:border-primary/40"
                      )}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8">
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="w-full bg-primary text-white py-3 rounded-lg font-medium hover:bg-primary-600 disabled:opacity-60 transition-colors"
            >
              {submitting ? "Submitting..." : "Submit Answers"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function ResultView({ result, quiz, answers, onRetry }: any) {
  const isPassing = result.score >= 80;
  return (
    <div className="space-y-6">
      {/* Score card */}
      <div className={cn(
        "planner-card text-center border-2",
        isPassing ? "border-primary bg-primary/5" : "border-amber-300 bg-amber-50"
      )}>
        <div className="text-5xl font-mono font-bold mb-2" style={{ color: isPassing ? "#2D6A4F" : "#E07B39" }}>
          {formatScore(result.score)}
        </div>
        <p className="font-semibold text-ink">
          {isPassing ? "🏆 Excellent! Topic mastered!" : "📚 Keep practicing!"}
        </p>
        {result.new_topic_state && (
          <p className="text-sm text-muted mt-1">
            Progress updated → <strong className="text-primary capitalize">{result.new_topic_state.replace("_", " ")}</strong>
          </p>
        )}
      </div>

      {/* Question review */}
      <h2 className="font-semibold text-ink">Review</h2>
      <div className="space-y-4">
        {quiz.questions.map((q: any, idx: number) => {
          const userAnswer = answers[q.id];
          const isCorrect = userAnswer === q.correct_answer;
          return (
            <div key={q.id} className={cn("planner-card border-l-4", isCorrect ? "border-l-primary" : "border-l-red-400")}>
              <div className="flex items-start gap-2">
                {isCorrect ? <CheckCircle className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" /> : <XCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />}
                <div className="flex-1">
                  <p className="font-medium text-sm text-ink">{q.question_text}</p>
                  {!isCorrect && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-red-600">Your answer: {userAnswer}</p>
                      <p className="text-xs text-primary font-medium">Correct: {q.correct_answer}</p>
                    </div>
                  )}
                  {q.explanation && <p className="text-xs text-muted mt-2 italic">{q.explanation}</p>}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex gap-3">
        <button onClick={onRetry} className="flex-1 py-2.5 rounded-lg border border-border text-ink text-sm hover:bg-paper">
          Try Again
        </button>
        <Link href="/courses" className="flex-1 py-2.5 rounded-lg bg-primary text-white text-sm text-center font-medium hover:bg-primary-600">
          Back to Courses
        </Link>
      </div>
    </div>
  );
}
