"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { STATE_CONFIG, cn, type TopicState } from "@/lib/utils";
import { ChevronRight, BookOpen } from "lucide-react";
import Link from "next/link";

export default function CoursesPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.courses.list().then(setCourses).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen p-6 md:p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="font-serif text-3xl text-ink">Courses</h1>
        <p className="text-muted text-sm mt-1">Explore topics and track your mastery across subjects.</p>
      </div>

      {loading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-40 bg-border rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} userId={user?.id} />
          ))}
        </div>
      )}
    </div>
  );
}

function CourseCard({ course, userId }: { course: any; userId?: string }) {
  const subjectEmoji: Record<string, string> = {
    Mathematics: "📐", "Computer Science": "💻", Biology: "🧬",
    Physics: "⚛️", "Data Science": "📊", Chemistry: "⚗️",
    History: "📜", Literature: "📚", Economics: "📈",
  };
  const emoji = subjectEmoji[course.subject] || "📖";
  const difficultyColor: Record<string, string> = {
    beginner: "bg-green-100 text-green-700",
    intermediate: "bg-amber-100 text-amber-700",
    advanced: "bg-red-100 text-red-700",
  };
  const diffClass = difficultyColor[course.difficulty_level || "beginner"] || "bg-gray-100 text-gray-600";

  return (
    <Link
      href={`/courses/${course.id}`}
      className="planner-card hover:shadow-ink-md hover:border-primary/30 transition-all group block"
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-2xl">{emoji}</span>
        <span className={cn("text-2xs font-mono px-2 py-0.5 rounded-full font-medium capitalize", diffClass)}>
          {course.difficulty_level}
        </span>
      </div>
      <h3 className="font-semibold text-ink group-hover:text-primary transition-colors">{course.title}</h3>
      <p className="text-sm text-muted mt-1 line-clamp-2">{course.description}</p>
      <div className="flex items-center justify-between mt-4">
        <span className="text-2xs text-muted font-mono">{course.total_topics || 0} topics</span>
        <ChevronRight className="w-4 h-4 text-muted group-hover:text-primary transition-colors" />
      </div>
    </Link>
  );
}
