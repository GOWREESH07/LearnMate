"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { STATE_CONFIG, formatScore, formatDate, cn } from "@/lib/utils";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";
import { Flame, Trophy, BookOpen, Target, ChevronRight, TrendingUp } from "lucide-react";
import Link from "next/link";

const STATE_COLORS = ["#9CA3AF", "#3B82F6", "#F59E0B", "#2D6A4F"];
const STATE_KEYS = ["not_started", "in_progress", "practicing", "mastered"] as const;

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    api.dashboard.get(user.id).then(setData).catch(console.error).finally(() => setLoading(false));
  }, [user]);

  if (loading) return <DashboardSkeleton />;

  const profile = data?.profile || {};
  const stateCounts = data?.state_counts || {};
  const attempts = data?.quiz_attempts || [];
  const upcomingItems = data?.upcoming_items || [];
  const achievements = data?.achievements || [];

  // Build pie chart data
  const pieData = STATE_KEYS.map((k, i) => ({
    name: STATE_CONFIG[k].label,
    value: stateCounts[k] || 0,
    color: STATE_COLORS[i],
  })).filter((d) => d.value > 0);

  // Build quiz score trend
  const scoreTrend = attempts.slice(0, 8).reverse().map((a: any, i: number) => ({
    name: `Quiz ${i + 1}`,
    score: Math.round(a.score),
  }));

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-serif text-3xl text-ink">
          Good {getTimeOfDay()}, {profile.name?.split(" ")[0] || "there"}
        </h1>
        <p className="text-muted text-sm mt-1 font-mono">
          {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Day streak"
          value={`${profile.streak_days || 0}`}
          icon={<Flame className="w-4 h-4 text-accent" />}
          accent
        />
        <StatCard
          label="Topics mastered"
          value={`${stateCounts.mastered || 0}`}
          icon={<Trophy className="w-4 h-4 text-primary" />}
        />
        <StatCard
          label="Mastery rate"
          value={`${data?.mastery_percentage || 0}%`}
          icon={<TrendingUp className="w-4 h-4 text-blue-500" />}
        />
        <StatCard
          label="In progress"
          value={`${stateCounts.in_progress || 0}`}
          icon={<BookOpen className="w-4 h-4 text-amber-500" />}
        />
      </div>

      {/* Charts row */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {/* Topic mastery pie */}
        <div className="planner-card md:col-span-1">
          <h2 className="font-semibold text-sm text-ink mb-4">Topic Mastery</h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value">
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(v, n) => [v, n]} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[180px] flex items-center justify-center text-muted text-sm">
              Start learning to see your progress
            </div>
          )}
          <div className="flex flex-wrap gap-2 mt-2">
            {pieData.map((d) => (
              <div key={d.name} className="flex items-center gap-1.5 text-2xs text-muted">
                <div className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                {d.name}: <span className="font-mono font-medium text-ink">{d.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quiz score trend */}
        <div className="planner-card md:col-span-2">
          <h2 className="font-semibold text-sm text-ink mb-4">Quiz Score Trend</h2>
          {scoreTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={scoreTrend}>
                <defs>
                  <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2D6A4F" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#2D6A4F" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(v) => [`${v}%`, "Score"]} />
                <Area type="monotone" dataKey="score" stroke="#2D6A4F" strokeWidth={2} fill="url(#scoreGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[180px] flex items-center justify-center text-muted text-sm">
              Take your first quiz to see score trends here
            </div>
          )}
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Upcoming study items */}
        <div className="planner-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-sm text-ink">Upcoming Sessions</h2>
            <Link href="/study-plans" className="text-2xs text-primary hover:underline font-mono">
              View all →
            </Link>
          </div>
          {upcomingItems.length === 0 ? (
            <p className="text-sm text-muted italic">
              No sessions scheduled. <Link href="/study-plans" className="text-primary hover:underline">Create a study plan</Link> to get started.
            </p>
          ) : (
            <div className="space-y-2">
              {upcomingItems.slice(0, 5).map((item: any, i: number) => (
                <div key={i} className="flex items-center gap-3 py-2 border-b border-border last:border-0">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-ink truncate">
                      {item.topics?.title || "Study Session"}
                    </p>
                    <p className="text-2xs text-muted font-mono">
                      {formatDate(item.scheduled_date)} · {item.duration_minutes} min
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent achievements */}
        <div className="planner-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-sm text-ink">Recent Achievements</h2>
            <Link href="/profile" className="text-2xs text-primary hover:underline font-mono">
              View all →
            </Link>
          </div>
          {achievements.length === 0 ? (
            <p className="text-sm text-muted italic">
              Complete quizzes and master topics to earn achievements. Your first one awaits!
            </p>
          ) : (
            <div className="space-y-2">
              {achievements.slice(0, 5).map((ach: any, i: number) => (
                <div key={i} className="flex items-start gap-3 py-2 border-b border-border last:border-0">
                  <span className="text-lg">{ach.badge_icon === "fire" || ach.badge_icon === "flame" ? "🔥" : ach.badge_icon === "star" ? "⭐" : "🏆"}</span>
                  <div>
                    <p className="text-sm font-medium text-ink">{ach.title}</p>
                    <p className="text-2xs text-muted">{ach.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, accent }: { label: string; value: string; icon: React.ReactNode; accent?: boolean }) {
  return (
    <div className={cn("planner-card", accent && "border-accent/30 bg-accent/5")}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xs text-muted uppercase tracking-wide font-mono">{label}</span>
        {icon}
      </div>
      <div className={cn("text-2xl font-mono font-bold", accent ? "text-accent" : "text-ink")}>
        {value}
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="min-h-screen p-6 md:p-8 max-w-7xl mx-auto animate-pulse">
      <div className="h-8 bg-border rounded w-64 mb-2" />
      <div className="h-4 bg-border rounded w-40 mb-8" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-border rounded-lg" />)}
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        <div className="h-64 bg-border rounded-lg" />
        <div className="md:col-span-2 h-64 bg-border rounded-lg" />
      </div>
    </div>
  );
}

function getTimeOfDay() {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
