"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { getInitials, cn } from "@/lib/utils";
import { Users, Plus, Trophy } from "lucide-react";

export default function GroupsPage() {
  const { user } = useAuth();
  const [groups, setGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<any>(null);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  useEffect(() => {
    if (!user) return;
    api.groups.list(user.id).then(setGroups).catch(console.error).finally(() => setLoading(false));
  }, [user]);

  async function showLeaderboard(group: any) {
    setSelectedGroup(group);
    const lb = await api.groups.leaderboard(group.id);
    setLeaderboard(lb);
  }

  async function joinGroup(groupId: string) {
    if (!user) return;
    await api.groups.join(groupId, user.id);
    setGroups((prev) => prev.map((g) => g.id === groupId ? { ...g, is_member: true } : g));
  }

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-serif text-3xl text-ink">Study Groups</h1>
          <p className="text-muted text-sm mt-1">Collaborate, compete on leaderboards, and learn together.</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-600"
        >
          <Plus className="w-4 h-4" /> New Group
        </button>
      </div>

      {showCreate && (
        <CreateGroupModal
          userId={user!.id}
          onCreated={(g: any) => { setGroups((prev) => [g, ...prev]); setShowCreate(false); }}
          onClose={() => setShowCreate(false)}
        />
      )}

      {selectedGroup && (
        <LeaderboardModal
          group={selectedGroup}
          leaderboard={leaderboard}
          onClose={() => { setSelectedGroup(null); setLeaderboard([]); }}
        />
      )}

      {loading ? (
        <div className="grid md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-36 bg-border rounded-xl animate-pulse" />)}
        </div>
      ) : groups.length === 0 ? (
        <div className="text-center py-16 text-muted">
          <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-medium">No study groups yet</p>
          <p className="text-sm mt-1">Create a group or wait for your teacher to invite you.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {groups.map((group) => (
            <div key={group.id} className="planner-card">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-ink">{group.name}</h3>
                  {group.description && <p className="text-sm text-muted mt-0.5">{group.description}</p>}
                </div>
                <span className="text-2xs font-mono text-muted">
                  {group.member_count || "?"} members
                </span>
              </div>
              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => showLeaderboard(group)}
                  className="flex-1 flex items-center justify-center gap-1.5 py-1.5 border border-border rounded-md text-sm text-ink hover:border-primary hover:text-primary transition-colors"
                >
                  <Trophy className="w-3.5 h-3.5" /> Leaderboard
                </button>
                {!group.is_member && (
                  <button
                    onClick={() => joinGroup(group.id)}
                    className="flex-1 py-1.5 bg-primary text-white rounded-md text-sm hover:bg-primary-600"
                  >
                    Join
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CreateGroupModal({ userId, onCreated, onClose }: any) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const group = await api.groups.create({ name, description }, userId);
      onCreated(group);
    } catch (err: any) { alert(err.message); }
    finally { setLoading(false); }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-sm shadow-xl p-6">
        <h2 className="font-semibold text-ink mb-4">New Study Group</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input value={name} onChange={(e) => setName(e.target.value)} required placeholder="Group name" className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary" />
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description (optional)" className="w-full px-3 py-2 border border-border rounded-md text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary" />
          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose} className="flex-1 py-2 border border-border rounded-md text-sm">Cancel</button>
            <button type="submit" disabled={loading} className="flex-[2] py-2 bg-primary text-white rounded-md text-sm font-medium disabled:opacity-60">
              {loading ? "Creating..." : "Create Group"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function LeaderboardModal({ group, leaderboard, onClose }: any) {
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-sm shadow-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-ink">{group.name} Leaderboard</h2>
          <button onClick={onClose} className="text-muted hover:text-ink text-xl leading-none">×</button>
        </div>
        {leaderboard.length === 0 ? (
          <p className="text-sm text-muted text-center py-4">No data yet — take some quizzes!</p>
        ) : (
          <div className="space-y-2">
            {leaderboard.map((member: any, i: number) => (
              <div key={member.user_id} className={cn("flex items-center gap-3 py-2 px-3 rounded-md", i === 0 ? "bg-amber-50" : "")}>
                <span className="w-6 text-center font-mono font-bold text-sm text-muted">{i + 1}</span>
                <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-2xs font-mono font-bold text-primary">
                  {getInitials(member.name)}
                </div>
                <span className="flex-1 text-sm font-medium text-ink">{member.name}</span>
                <span className="font-mono text-sm font-bold text-primary">{member.avg_score}%</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
