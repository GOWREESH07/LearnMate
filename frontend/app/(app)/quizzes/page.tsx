"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { formatScore, formatDate } from "@/lib/utils";
import { Zap } from "lucide-react";
import Link from "next/link";

export default function QuizzesPage() {
  const { user } = useAuth();
  const [attempts, setAttempts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    api.quizzes.userAttempts(user.id).then(setAttempts).catch(console.error).finally(() => setLoading(false));
  }, [user]);

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="font-serif text-3xl text-ink">Quizzes</h1>
        <p className="text-muted text-sm mt-1">All your quiz attempts. Generate new ones from any topic.</p>
      </div>

      {/* Generate tip */}
      <div className="planner-card border-primary/20 bg-primary/5 mb-8 flex items-center gap-4">
        <Zap className="w-8 h-8 text-primary flex-shrink-0" />
        <div>
          <p className="font-medium text-ink text-sm">Generate AI Quizzes</p>
          <p className="text-sm text-muted">Go to any <Link href="/courses" className="text-primary underline">Course → Topic</Link> and click <strong>Generate Quiz</strong> to create a personalised quiz using Gemini AI.</p>
        </div>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-border rounded-lg animate-pulse" />)}
        </div>
      ) : attempts.length === 0 ? (
        <div className="text-center py-16 text-muted">
          <FileQuestion className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-medium">No quiz attempts yet</p>
          <p className="text-sm mt-1">Head to a topic and generate your first AI quiz!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {attempts.map((attempt: any) => {
            const isPassing = attempt.score >= 80;
            return (
              <div key={attempt.id} className="planner-card flex items-center gap-4">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-sm font-mono font-bold text-white flex-shrink-0"
                  style={{ background: isPassing ? "#2D6A4F" : "#E07B39" }}
                >
                  {Math.round(attempt.score)}%
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-ink truncate">
                    {attempt.quizzes?.title || "Quiz"}
                  </p>
                  <p className="text-2xs text-muted font-mono">
                    {attempt.quizzes?.topics?.title && `${attempt.quizzes.topics.title} · `}
                    {formatDate(attempt.completed_at)}
                  </p>
                </div>
                <span className={`text-2xs font-mono px-2 py-1 rounded-full ${isPassing ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700"}`}>
                  {isPassing ? "Passed" : "Practice"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function FileQuestion({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="12" y1="18" x2="12" y2="12" />
      <line x1="9" y1="15" x2="15" y2="15" />
    </svg>
  );
}
