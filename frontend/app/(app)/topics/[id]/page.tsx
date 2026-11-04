"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { STATE_CONFIG, cn, type TopicState } from "@/lib/utils";
import { ArrowLeft, Zap, ExternalLink, BookOpen, Video, FileText } from "lucide-react";
import Link from "next/link";

export default function TopicDirectPage() {
  const { id } = useParams() as { id: string };
  const { user } = useAuth();
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!id || !user) return;
    api.topics.detail(id, user.id)
      .then(setDetail)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id, user]);

  async function generateQuiz() {
    if (!user || !detail || !id) return;
    setGenerating(true);
    try {
      const quiz = await api.quizzes.generate({
        topic_id: id,
        topic_title: detail.title,
        difficulty: "intermediate",
      }, user.id);
      window.location.href = `/quizzes/${quiz.id}`;
    } catch (err: any) {
      alert(`Quiz generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen p-6 md:p-8 max-w-4xl mx-auto animate-pulse">
        <div className="h-6 bg-border rounded w-32 mb-8" />
        <div className="h-8 bg-border rounded w-72 mb-4" />
        <div className="grid md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-32 bg-border rounded-lg" />)}
        </div>
      </div>
    );
  }

  if (!detail) return null;

  const state: TopicState = detail.current_state || "in_progress";
  const stateInfo = STATE_CONFIG[state] || STATE_CONFIG["in_progress"];
  const resources = detail.resources || [];

  const resourceIcon = (type: string) => {
    if (type === "video") return <Video className="w-4 h-4 text-red-500" />;
    if (type === "pdf") return <FileText className="w-4 h-4 text-red-400" />;
    return <BookOpen className="w-4 h-4 text-blue-500" />;
  };

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-4xl mx-auto">
      <Link
        href={detail.course?.id ? `/courses/${detail.course.id}` : "/courses"}
        className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink mb-6"
      >
        <ArrowLeft className="w-4 h-4" /> {detail.course?.title ? `Back to ${detail.course.title}` : "Back to courses"}
      </Link>

      {/* Topic header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
        <div>
          <span className="text-2xs font-mono text-muted uppercase tracking-wide">{detail.course?.subject}</span>
          <h1 className="font-serif text-3xl text-ink mt-1">{detail.title}</h1>
          {detail.description && <p className="text-muted text-sm mt-2">{detail.description}</p>}
        </div>
        {/* State badge + action */}
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span
            className="state-badge"
            style={{ background: `${stateInfo.color}20`, color: stateInfo.color }}
          >
            {stateInfo.icon} {stateInfo.label}
          </span>
          <p className="text-2xs text-muted text-right">{stateInfo.description}</p>
        </div>
      </div>

      {/* Gamification badges from Decorator pattern */}
      {detail.badges && detail.badges.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          {detail.badges.map((badge: string, i: number) => (
            <span key={i} className="text-2xs px-2 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-full font-mono">
              {badge}
            </span>
          ))}
        </div>
      )}

      {/* XP / gamification stats */}
      {detail.xp_points !== undefined && (
        <div className="planner-card mb-6 flex items-center gap-6">
          <div>
            <p className="text-2xs text-muted font-mono uppercase tracking-wide">XP Points</p>
            <p className="text-xl font-mono font-bold text-primary">{detail.xp_points}</p>
          </div>
          <div>
            <p className="text-2xs text-muted font-mono uppercase tracking-wide">Resources completed</p>
            <p className="text-xl font-mono font-bold text-ink">{detail.resources_completed}/{resources.length}</p>
          </div>
          {detail.next_xp_threshold && (
            <div>
              <p className="text-2xs text-muted font-mono uppercase tracking-wide">Next milestone</p>
              <p className="text-xl font-mono font-bold text-accent">{detail.next_xp_threshold} XP</p>
            </div>
          )}
        </div>
      )}

      {/* Learning resources */}
      <div className="mb-8">
        <h2 className="font-semibold text-ink mb-4">Learning Resources</h2>
        {resources.length === 0 ? (
          <p className="text-sm text-muted italic planner-card">
            No resources available yet for this topic.
          </p>
        ) : (
          <div className="space-y-3">
            {resources.map((res: any) => (
              <a
                key={res.id}
                href={res.url}
                target="_blank"
                rel="noopener noreferrer"
                className="planner-card flex items-center gap-3 hover:border-primary/30 hover:shadow-ink-md transition-all group"
              >
                {resourceIcon(res.type || res.resource_type)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink group-hover:text-primary">{res.title}</p>
                  {res.source && <p className="text-2xs text-muted font-mono">{res.source}</p>}
                </div>
                {res.duration && (
                  <span className="text-2xs text-muted font-mono flex-shrink-0">{res.duration} min</span>
                )}
                <ExternalLink className="w-3.5 h-3.5 text-muted group-hover:text-primary flex-shrink-0" />
              </a>
            ))}
          </div>
        )}
      </div>

      {/* AI Quiz button */}
      <div className="planner-card border-primary/20 bg-primary/5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="font-semibold text-ink mb-1">Test Your Knowledge</h2>
            <p className="text-sm text-muted">
              Generate an AI-powered quiz for this topic. Score 80%+ to mark it as <strong>Mastered</strong>.
            </p>
          </div>
          <button
            onClick={generateQuiz}
            disabled={generating}
            className="flex-shrink-0 flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-600 transition-colors disabled:opacity-60"
          >
            <Zap className="w-4 h-4" />
            {generating ? "Generating..." : "Generate Quiz"}
          </button>
        </div>
        {state === "mastered" && (
          <div className="mt-3 flex items-center gap-2 text-sm text-primary font-medium">
            <span>✓</span> You've mastered this topic! Take another quiz to reinforce it.
          </div>
        )}
      </div>
    </div>
  );
}
