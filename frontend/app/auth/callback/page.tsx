"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { GraduationCap } from "lucide-react";

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    async function handleAuthCallback() {
      try {
        // Check hash & query params for OAuth errors
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const searchParams = new URLSearchParams(window.location.search);
        
        const errorDesc = hashParams.get("error_description") || searchParams.get("error_description");
        const errorMsg = hashParams.get("error") || searchParams.get("error");

        if (errorDesc || errorMsg) {
          const detail = errorDesc || errorMsg || "Authentication failed";
          router.replace(`/login?error=${encodeURIComponent(detail)}`);
          return;
        }

        const { data: { session }, error } = await supabase.auth.getSession();
        if (error || !session?.user) {
          console.error("Auth callback error:", error);
          const msg = error?.message || "Google authentication failed";
          router.replace(`/login?error=${encodeURIComponent(msg)}`);
          return;
        }

        const userId = session.user.id;
        const userEmail = session.user.email || "";
        const userName =
          session.user.user_metadata?.full_name ||
          session.user.user_metadata?.name ||
          userEmail.split("@")[0] ||
          "Student";
        const userAvatar =
          session.user.user_metadata?.avatar_url ||
          session.user.user_metadata?.picture ||
          null;

        // Fetch profile to check onboarding status
        const { data: profile } = await supabase
          .from("profiles")
          .select("onboarding_done")
          .eq("id", userId)
          .single();

        if (!profile) {
          // Upsert profile row safely if missing
          await supabase.from("profiles").upsert({
            id: userId,
            name: userName,
            avatar_url: userAvatar,
            onboarding_done: false,
          });
          router.replace("/onboarding");
        } else if (profile.onboarding_done) {
          router.replace("/dashboard");
        } else {
          router.replace("/onboarding");
        }
      } catch (err: any) {
        console.error("Unexpected callback error:", err);
        router.replace(`/login?error=${encodeURIComponent(err.message || "Unexpected authentication error")}`);
      }
    }

    handleAuthCallback();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper">
      <div className="text-center">
        <GraduationCap className="w-10 h-10 text-primary mx-auto mb-3 animate-pulse" />
        <h1 className="font-serif text-2xl text-ink mb-1">Authenticating with Google...</h1>
        <p className="text-muted text-sm font-mono">Setting up your study space</p>
        <div className="mt-4 w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
    </div>
  );
}
