import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const STATE_CONFIG = {
  not_started: {
    label: "Not Started",
    color: "#9CA3AF",
    bgClass: "state-badge--not-started",
    icon: "○",
    description: "You haven't started this topic yet.",
  },
  in_progress: {
    label: "In Progress",
    color: "#3B82F6",
    bgClass: "state-badge--in-progress",
    icon: "◑",
    description: "You're working through the resources.",
  },
  practicing: {
    label: "Practicing",
    color: "#F59E0B",
    bgClass: "state-badge--practicing",
    icon: "◕",
    description: "You've attempted a quiz — keep practicing!",
  },
  mastered: {
    label: "Mastered",
    color: "#2D6A4F",
    bgClass: "state-badge--mastered",
    icon: "✓",
    description: "You've scored 80%+ — this topic is yours.",
  },
} as const;

export type TopicState = keyof typeof STATE_CONFIG;

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatScore(score: number): string {
  return `${score.toFixed(0)}%`;
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function pluralize(count: number, singular: string, plural?: string): string {
  return count === 1 ? singular : (plural || `${singular}s`);
}
