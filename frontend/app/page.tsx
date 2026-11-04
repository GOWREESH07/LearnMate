"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [showManualBtn, setShowManualBtn] = useState(false);

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }

    const timer = setTimeout(() => {
      setShowManualBtn(true);
      if (user) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [user, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper">
      <div className="text-center p-6">
        <h1 className="font-serif text-3xl text-ink mb-2">LearnMate</h1>
        <p className="text-muted text-sm font-mono">Entering your study space...</p>
        <div className="mt-4 w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />

        {showManualBtn && (
          <div className="mt-4">
            <button
              onClick={() => router.replace(user ? "/dashboard" : "/login")}
              className="px-4 py-2 bg-primary text-white text-xs font-medium rounded-md hover:bg-primary-600 transition-colors shadow-ink-sm"
            >
              {user ? "Go to Dashboard →" : "Go to Sign In →"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
