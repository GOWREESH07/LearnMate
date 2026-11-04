"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { formatDate, cn } from "@/lib/utils";
import { Plus, Calendar, CheckSquare, Trash2, Square } from "lucide-react";

export default function StudyPlansPage() {
  const { user } = useAuth();
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    if (!user) return;
    api.studyPlans.list(user.id).then(setPlans).catch(console.error).finally(() => setLoading(false));
  }, [user]);

  async function toggleItem(itemId: string, completed: boolean) {
    await api.studyPlans.updateItem(itemId, !completed);
    setPlans((prev) => prev.map((plan) => ({
      ...plan,
      items: plan.items?.map((item: any) =>
        item.id === itemId ? { ...item, completed: !completed } : item
      ) || [],
    })));
  }

  async function deletePlan(planId: string) {
    if (!user || !confirm("Delete this study plan?")) return;
    await api.studyPlans.delete(planId, user.id);
    setPlans((prev) => prev.filter((p) => p.id !== planId));
  }

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-serif text-3xl text-ink">Study Plans</h1>
          <p className="text-muted text-sm mt-1">Your personalised study schedule, built by the AI planner.</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-600 transition-colors"
        >
          <Plus className="w-4 h-4" /> New Plan
        </button>
      </div>

      {showCreate && (
        <CreatePlanModal
          userId={user!.id}
          onCreated={(plan) => { setPlans((prev) => [plan, ...prev]); setShowCreate(false); }}
          onClose={() => setShowCreate(false)}
        />
      )}

      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="h-48 bg-border rounded-xl animate-pulse" />)}
        </div>
      ) : plans.length === 0 ? (
        <div className="text-center py-16 text-muted">
          <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-medium">No study plans yet</p>
          <p className="text-sm mt-1">Create a plan to schedule your topics and track your sessions.</p>
          <button onClick={() => setShowCreate(true)} className="mt-4 bg-primary text-white px-4 py-2 rounded-md text-sm hover:bg-primary-600">
            Create your first plan
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {plans.map((plan) => (
            <PlanCard key={plan.id} plan={plan} onToggleItem={toggleItem} onDelete={() => deletePlan(plan.id)} />
          ))}
        </div>
      )}
    </div>
  );
}

function PlanCard({ plan, onToggleItem, onDelete }: { plan: any; onToggleItem: (id: string, completed: boolean) => void; onDelete: () => void }) {
  const items = plan.items || [];
  const completed = items.filter((i: any) => i.completed).length;
  const pct = items.length > 0 ? Math.round((completed / items.length) * 100) : 0;

  return (
    <div className="planner-card">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h2 className="font-semibold text-ink">{plan.title}</h2>
          {plan.goal && <p className="text-sm text-muted mt-0.5">{plan.goal}</p>}
          <p className="text-2xs font-mono text-muted mt-1">
            {formatDate(plan.start_date)} → {formatDate(plan.end_date)}
          </p>
        </div>
        <button onClick={onDelete} className="text-muted hover:text-red-500 p-1">
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-2xs font-mono text-muted mb-1">
          <span>{completed}/{items.length} sessions</span>
          <span>{pct}%</span>
        </div>
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {/* Items */}
      {items.length > 0 ? (
        <div className="space-y-2">
          {items.slice(0, 6).map((item: any) => (
            <button
              key={item.id}
              onClick={() => onToggleItem(item.id, item.completed)}
              className={cn(
                "w-full flex items-center gap-3 py-2 px-3 rounded-md text-sm transition-colors text-left",
                item.completed ? "opacity-60" : "hover:bg-paper"
              )}
            >
              {item.completed ? (
                <CheckSquare className="w-4 h-4 text-primary flex-shrink-0" />
              ) : (
                <Square className="w-4 h-4 text-muted flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <span className={cn("font-medium", item.completed && "line-through text-muted")}>
                  {item.topics?.title || "Study Session"}
                </span>
                <span className="text-2xs text-muted font-mono ml-2">{formatDate(item.scheduled_date)} · {item.duration_minutes}m</span>
              </div>
            </button>
          ))}
          {items.length > 6 && (
            <p className="text-2xs text-muted text-center font-mono">+{items.length - 6} more sessions</p>
          )}
        </div>
      ) : (
        <p className="text-sm text-muted italic">No sessions scheduled.</p>
      )}
    </div>
  );
}

function CreatePlanModal({ userId, onCreated, onClose }: { userId: string; onCreated: (p: any) => void; onClose: () => void }) {
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [start, setStart] = useState(new Date().toISOString().slice(0, 10));
  const [end, setEnd] = useState(new Date(Date.now() + 30 * 864e5).toISOString().slice(0, 10));
  const [duration, setDuration] = useState(45);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const plan = await api.studyPlans.create({
        title,
        goal,
        start_date: start,
        end_date: end,
        duration_minutes: duration,
        sessions_per_week: 3,
        topics: [],
      }, userId);
      onCreated(plan);
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-md shadow-xl p-6">
        <h2 className="font-semibold text-ink mb-4">New Study Plan</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Plan name</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary" placeholder="e.g. Exam prep — ML Fundamentals" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Goal (optional)</label>
            <input value={goal} onChange={(e) => setGoal(e.target.value)} className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary" placeholder="e.g. Master all ML topics before the exam" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1.5">Start date</label>
              <input type="date" value={start} onChange={(e) => setStart(e.target.value)} className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">End date</label>
              <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Session duration: {duration} min</label>
            <input type="range" min={15} max={120} step={15} value={duration} onChange={(e) => setDuration(+e.target.value)} className="w-full accent-primary" />
          </div>
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2 rounded-md border border-border text-sm">Cancel</button>
            <button type="submit" disabled={loading} className="flex-[2] py-2 rounded-md bg-primary text-white text-sm font-medium disabled:opacity-60">
              {loading ? "Creating..." : "Create Plan"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
