"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { STATE_CONFIG, cn, type TopicState } from "@/lib/utils";
import { ArrowLeft, Zap, BookOpen } from "lucide-react";
import Link from "next/link";

export default function CourseDetailPage() {
  const { id } = useParams() as { id: string };
  const { user } = useAuth();
  const router = useRouter();
  const [course, setCourse] = useState<any>(null);
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingTopicId, setGeneratingTopicId] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.courses.get(id),
      api.topics.forCourse(id, user?.id),
    ]).then(([c, t]) => {
      setCourse(c);
      setTopics(t);
    }).catch(console.error).finally(() => setLoading(false));
  }, [id, user?.id]);

  async function handleGenerateQuiz(e: React.MouseEvent, topic: any) {
    e.preventDefault();
    e.stopPropagation();
    if (!user) return;
    setGeneratingTopicId(topic.id);
    try {
      const quiz = await api.quizzes.generate({
        topic_id: topic.id,
        topic_title: topic.title,
        difficulty: "intermediate",
      }, user.id);
      router.push(`/quizzes/${quiz.id}`);
    } catch (err: any) {
      alert(`Quiz generation failed: ${err.message}`);
    } finally {
      setGeneratingTopicId(null);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen p-6 md:p-8 max-w-4xl mx-auto animate-pulse">
        <div className="h-6 bg-border rounded w-24 mb-6" />
        <div className="h-8 bg-border rounded w-72 mb-2" />
        <div className="h-4 bg-border rounded w-96 mb-8" />
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => <div key={i} className="h-16 bg-border rounded-lg" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-4xl mx-auto">
      <Link href="/courses" className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink mb-6">
        <ArrowLeft className="w-4 h-4" /> Back to courses
      </Link>

      <div className="mb-8">
        <span className="text-2xs font-mono text-muted uppercase tracking-wide">{course?.subject}</span>
        <h1 className="font-serif text-3xl text-ink mt-1">{course?.title}</h1>
        <p className="text-muted text-sm mt-1">{course?.description}</p>
      </div>

      {/* Progress summary */}
      <div className="planner-card mb-6">
        <h2 className="font-semibold text-sm text-ink mb-3">Your Progress Trail</h2>
        <div className="flex items-center gap-4 flex-wrap">
          {(["not_started", "in_progress", "practicing", "mastered"] as TopicState[]).map((state) => {
            const count = topics.filter((t) => (t.state || "not_started") === state).length;
            return (
              <div key={state} className="flex items-center gap-1.5">
                <span className="text-sm">{STATE_CONFIG[state].icon}</span>
                <span className="text-2xs font-mono text-muted">{STATE_CONFIG[state].label}</span>
                <span className="text-2xs font-mono font-bold text-ink">({count})</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Topic list — progress trail */}
      <div className="trail-track space-y-3 pl-8">
        {topics.map((topic, idx) => {
          const state: TopicState = topic.state || "not_started";
          const cfg = STATE_CONFIG[state] || STATE_CONFIG["not_started"];
          return (
            <div key={topic.id} className="relative">
              {/* Trail marker */}
              <div
                className="absolute -left-5 top-5 w-4 h-4 rounded-full border-2 border-white flex items-center justify-center text-2xs font-bold shadow-sm"
                style={{ background: cfg.color }}
                title={cfg.label}
              >
                {cfg.icon}
              </div>

              {/* Topic card with inline Generate Quiz button */}
              <div className="planner-card hover:shadow-ink-md hover:border-primary/20 transition-all group flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <Link
                  href={`/topics/${topic.id}`}
                  className="flex-1 min-w-0"
                >
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-2xs font-mono text-muted">#{topic.order_index + 1}</span>
                    <h3 className="font-medium text-ink group-hover:text-primary transition-colors">
                      {topic.title}
                    </h3>
                    <span className={cn("state-badge text-2xs flex-shrink-0 ml-1", `state-badge--${state.replace("_", "-")}`)}>
                      {cfg.label}
                    </span>
                  </div>
                  <p className="text-sm text-muted mt-1 line-clamp-1">{topic.description}</p>
                </Link>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link
                    href={`/topics/${topic.id}`}
                    className="px-3 py-1.5 rounded-md text-xs font-medium border border-border text-muted hover:text-ink hover:bg-paper transition-colors flex items-center gap-1.5"
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    Content
                  </Link>

                  <button
                    onClick={(e) => handleGenerateQuiz(e, topic)}
                    disabled={generatingTopicId === topic.id}
                    className="px-3 py-1.5 rounded-md text-xs font-medium bg-primary text-white hover:bg-primary-600 transition-colors flex items-center gap-1.5 disabled:opacity-60 shadow-sm"
                    title="Generate AI quiz for this topic"
                  >
                    <Zap className="w-3.5 h-3.5" />
                    {generatingTopicId === topic.id ? "Generating..." : "Generate Quiz"}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {topics.length === 0 && (
        <p className="text-center text-muted py-12">No topics found for this course.</p>
      )}
    </div>
  );
}
