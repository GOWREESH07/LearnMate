"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Bell, CheckCheck } from "lucide-react";

export default function NotificationsPage() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    api.notifications.list(user.id).then(setNotifications).catch(console.error).finally(() => setLoading(false));
  }, [user]);

  async function markRead(id: string) {
    await api.notifications.markRead(id);
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
  }

  async function markAllRead() {
    if (!user) return;
    await api.notifications.markAllRead(user.id);
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-serif text-3xl text-ink">Notifications</h1>
          {unreadCount > 0 && (
            <p className="text-muted text-sm mt-1">{unreadCount} unread</p>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            onClick={markAllRead}
            className="flex items-center gap-1.5 text-sm text-primary hover:underline"
          >
            <CheckCheck className="w-4 h-4" /> Mark all read
          </button>
        )}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-border rounded-lg animate-pulse" />)}
        </div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-16 text-muted">
          <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-medium">You&apos;re all caught up!</p>
          <p className="text-sm mt-1">Notifications appear here when you earn achievements, get quiz results, or have study reminders.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((notif) => (
            <button
              key={notif.id}
              onClick={() => !notif.read && markRead(notif.id)}
              className={`w-full text-left planner-card flex items-start gap-3 transition-all hover:shadow-ink-md ${
                !notif.read ? "border-primary/30 bg-primary/5" : ""
              }`}
            >
              {!notif.read && (
                <div className="w-2 h-2 rounded-full bg-primary mt-1.5 flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-ink">{notif.title}</p>
                <p className="text-sm text-muted mt-0.5">{notif.message}</p>
                <p className="text-2xs font-mono text-muted mt-1">
                  {new Date(notif.created_at).toLocaleString()}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
