"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { cn, getInitials } from "@/lib/utils";
import {
  LayoutDashboard, BookOpen, Calendar, FileQuestion,
  MessageSquare, Bell, Users, User, LogOut, Flame, GraduationCap,
} from "lucide-react";

const navItems = [
  { href: "/dashboard",     label: "Dashboard",    icon: LayoutDashboard },
  { href: "/courses",       label: "Courses",       icon: BookOpen },
  { href: "/study-plans",   label: "Study Plans",   icon: Calendar },
  { href: "/quizzes",       label: "Quizzes",       icon: FileQuestion },
  { href: "/chat",          label: "AI Tutor",      icon: MessageSquare },
  { href: "/notifications", label: "Notifications", icon: Bell },
  { href: "/groups",        label: "Study Groups",  icon: Users },
  { href: "/profile",       label: "Profile",       icon: User },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-paper">
        <div className="text-center">
          <GraduationCap className="w-10 h-10 text-primary mx-auto mb-3" />
          <p className="text-muted text-sm font-mono">Loading your workspace...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  const userName = user.user_metadata?.name || user.email?.split("@")[0] || "Student";

  return (
    <div className="min-h-screen flex bg-paper">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-60 bg-white border-r border-border fixed inset-y-0 left-0 z-40">
        {/* Logo */}
        <div className="h-16 flex items-center px-5 border-b border-border">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-primary" />
            <span className="font-serif text-xl text-ink">LearnMate</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={cn("nav-item", isActive && "nav-item--active")}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User footer */}
        <div className="p-3 border-t border-border">
          <div className="flex items-center gap-3 px-2 py-1.5 mb-1">
            <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-xs font-mono font-bold text-primary flex-shrink-0">
              {getInitials(userName)}
            </div>
            <span className="text-sm font-medium text-ink truncate">{userName}</span>
          </div>
          <button
            onClick={signOut}
            className="nav-item w-full text-left text-red-500 hover:bg-red-50 hover:text-red-600"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-14 bg-white border-b border-border z-40 flex items-center px-4 gap-3">
        <GraduationCap className="w-5 h-5 text-primary" />
        <span className="font-serif text-lg text-ink">LearnMate</span>
      </div>

      {/* Main content */}
      <main className="flex-1 md:ml-60 pt-0 md:pt-0">
        <div className="md:hidden h-14" /> {/* mobile spacer */}
        <div className="page-enter">{children}</div>
      </main>

      {/* Mobile nav bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-border z-40 flex">
        {navItems.slice(0, 5).map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex-1 flex flex-col items-center py-2 gap-0.5 text-2xs transition-colors",
                isActive ? "text-primary" : "text-muted"
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="truncate">{label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
