"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { getInitials, formatDate } from "@/lib/utils";

export default function ProfilePage() {
  const { user, signOut } = useAuth();
  const [profile, setProfile] = useState<any>(null);
  const [achievements, setAchievements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<any>({});

  useEffect(() => {
    if (!user) return;
    Promise.all([api.profiles.get(user.id), api.profiles.achievements(user.id)])
      .then(([p, a]) => { setProfile(p); setForm(p); setAchievements(a); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user]);

  async function saveProfile() {
    if (!user) return;
    const updated = await api.profiles.update(user.id, {
      name: form.name,
      study_pace: form.study_pace,
      target_career: form.target_career,
    });
    setProfile(updated);
    setEditing(false);
  }

  if (loading) return <div className="min-h-screen p-8 flex items-center justify-center"><div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-3xl mx-auto">
      <h1 className="font-serif text-3xl text-ink mb-8">Profile</h1>

      {/* Profile card */}
      <div className="planner-card mb-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-xl font-mono font-bold text-primary">
              {getInitials(profile?.name || "?")}
            </div>
            <div>
              {editing ? (
                <input
                  value={form.name || ""}
                  onChange={(e) => setForm((p: any) => ({ ...p, name: e.target.value }))}
                  className="px-2 py-1 border border-primary rounded text-ink font-semibold"
                />
              ) : (
                <h2 className="font-semibold text-ink text-lg">{profile?.name}</h2>
              )}
              <p className="text-sm text-muted">{user?.email}</p>
            </div>
          </div>
          {editing ? (
            <div className="flex gap-2">
              <button onClick={() => setEditing(false)} className="text-sm text-muted hover:text-ink px-3 py-1 border border-border rounded-md">Cancel</button>
              <button onClick={saveProfile} className="text-sm bg-primary text-white px-3 py-1 rounded-md hover:bg-primary-600">Save</button>
            </div>
          ) : (
            <button onClick={() => setEditing(true)} className="text-sm text-primary hover:underline">Edit</button>
          )}
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-border">
          <div className="text-center">
            <p className="text-2xl font-mono font-bold text-accent">{profile?.streak_days || 0}</p>
            <p className="text-2xs text-muted font-mono uppercase tracking-wide mt-0.5">Day Streak</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-mono font-bold text-primary">{achievements.length}</p>
            <p className="text-2xs text-muted font-mono uppercase tracking-wide mt-0.5">Achievements</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-mono font-bold text-ink capitalize">{profile?.study_pace || "—"}</p>
            <p className="text-2xs text-muted font-mono uppercase tracking-wide mt-0.5">Study Pace</p>
          </div>
        </div>

        {/* Editable fields */}
        {editing && (
          <div className="mt-4 pt-4 border-t border-border space-y-3">
            <div>
              <label className="text-sm font-medium text-ink block mb-1">Study Pace</label>
              <select
                value={form.study_pace || "moderate"}
                onChange={(e) => setForm((p: any) => ({ ...p, study_pace: e.target.value }))}
                className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="slow">Slow — 30-45 min, 3×/week</option>
                <option value="moderate">Moderate — 45-60 min, 4×/week</option>
                <option value="fast">Fast — 60-90 min, daily</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-ink block mb-1">Target Career</label>
              <input
                value={form.target_career || ""}
                onChange={(e) => setForm((p: any) => ({ ...p, target_career: e.target.value }))}
                className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="e.g. Machine Learning Engineer"
              />
            </div>
          </div>
        )}
      </div>

      {/* Interests */}
      {profile?.interests?.length > 0 && (
        <div className="planner-card mb-6">
          <h2 className="font-semibold text-ink mb-3">Interests</h2>
          <div className="flex flex-wrap gap-2">
            {profile.interests.map((interest: string) => (
              <span key={interest} className="px-3 py-1 bg-primary/10 text-primary text-sm rounded-full font-medium">
                {interest}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Achievements */}
      <div className="planner-card mb-6">
        <h2 className="font-semibold text-ink mb-4">Achievements</h2>
        {achievements.length === 0 ? (
          <p className="text-sm text-muted italic">Complete quizzes and master topics to earn achievements!</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {achievements.map((ach: any, i: number) => (
              <div key={i} className="planner-card bg-amber-50 border-amber-200 text-center">
                <div className="text-2xl mb-1">
                  {ach.badge_icon === "fire" ? "🔥" : ach.badge_icon === "star" ? "⭐" : "🏆"}
                </div>
                <p className="text-xs font-semibold text-ink">{ach.title}</p>
                <p className="text-2xs text-muted mt-0.5">{ach.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Sign out */}
      <button
        onClick={signOut}
        className="w-full py-2.5 border border-red-200 text-red-600 rounded-lg text-sm hover:bg-red-50 transition-colors"
      >
        Sign out
      </button>
    </div>
  );
}
