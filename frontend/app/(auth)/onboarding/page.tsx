"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";

const INTERESTS = [
  "Mathematics", "Computer Science", "Biology", "Physics", "Data Science",
  "Chemistry", "History", "Literature", "Economics", "Psychology",
  "AI / Machine Learning", "Engineering", "Medicine", "Astronomy",
];

const CAREERS = [
  "Machine Learning Engineer", "Data Scientist", "Software Engineer",
  "Research Physicist", "Bioinformatician", "Doctor / Physician",
  "Data Analyst", "Researcher", "Other",
];

export default function OnboardingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [studyPace, setStudyPace] = useState<"slow" | "moderate" | "fast">("moderate");
  const [targetCareer, setTargetCareer] = useState("");
  const [loading, setLoading] = useState(false);

  function toggleInterest(interest: string) {
    setSelectedInterests((prev) =>
      prev.includes(interest) ? prev.filter((i) => i !== interest) : [...prev, interest]
    );
  }

  async function handleFinish() {
    if (!user) return;
    setLoading(true);
    try {
      await api.auth.onboarding(
        { interests: selectedInterests, study_pace: studyPace, target_career: targetCareer },
        user.id
      );
      router.push("/dashboard");
    } catch {
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-paper flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="text-center mb-6">
          <h1 className="font-serif text-3xl text-ink">Set up your study profile</h1>
          <p className="text-muted text-sm mt-1">Step {step} of 3 — takes about 60 seconds</p>
          <div className="flex gap-1 mt-3 justify-center">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`h-1.5 w-12 rounded-full transition-colors ${s <= step ? "bg-primary" : "bg-border"}`}
              />
            ))}
          </div>
        </div>

        <div className="bg-white border border-border rounded-xl p-8 shadow-ink-sm">
          {step === 1 && (
            <div>
              <h2 className="font-semibold text-ink mb-1">What are you interested in?</h2>
              <p className="text-sm text-muted mb-4">Choose as many as apply — we&apos;ll tailor your recommendations.</p>
              <div className="flex flex-wrap gap-2">
                {INTERESTS.map((interest) => (
                  <button
                    key={interest}
                    onClick={() => toggleInterest(interest)}
                    className={`px-3 py-1.5 rounded-full text-sm border transition-all ${
                      selectedInterests.includes(interest)
                        ? "bg-primary text-white border-primary"
                        : "bg-paper text-ink border-border hover:border-primary"
                    }`}
                  >
                    {interest}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setStep(2)}
                disabled={selectedInterests.length === 0}
                className="mt-6 w-full bg-primary text-white py-2.5 rounded-md text-sm font-medium disabled:opacity-50"
              >
                Continue →
              </button>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="font-semibold text-ink mb-1">How do you prefer to study?</h2>
              <p className="text-sm text-muted mb-4">This helps us schedule your study sessions at a comfortable pace.</p>
              <div className="space-y-3">
                {(["slow", "moderate", "fast"] as const).map((pace) => (
                  <button
                    key={pace}
                    onClick={() => setStudyPace(pace)}
                    className={`w-full flex items-start gap-3 p-4 rounded-lg border text-left transition-all ${
                      studyPace === pace ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <span className="text-lg">{pace === "slow" ? "🐢" : pace === "moderate" ? "🚶" : "🚀"}</span>
                    <div>
                      <div className="font-medium text-sm capitalize">{pace}</div>
                      <div className="text-xs text-muted mt-0.5">
                        {pace === "slow" ? "30–45 min sessions, 3×/week"
                          : pace === "moderate" ? "45–60 min sessions, 4×/week"
                          : "60–90 min sessions, daily"}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              <div className="flex gap-2 mt-6">
                <button onClick={() => setStep(1)} className="flex-1 py-2.5 rounded-md text-sm border border-border text-ink hover:bg-paper">
                  ← Back
                </button>
                <button onClick={() => setStep(3)} className="flex-[2] bg-primary text-white py-2.5 rounded-md text-sm font-medium">
                  Continue →
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h2 className="font-semibold text-ink mb-1">What&apos;s your learning goal?</h2>
              <p className="text-sm text-muted mb-4">
                We&apos;ll use this to recommend topics most relevant to your future career.
              </p>
              <div className="grid grid-cols-2 gap-2 mb-4">
                {CAREERS.map((career) => (
                  <button
                    key={career}
                    onClick={() => setTargetCareer(career)}
                    className={`px-3 py-2 rounded-md border text-sm text-left transition-all ${
                      targetCareer === career
                        ? "border-primary bg-primary/5 text-primary font-medium"
                        : "border-border text-ink hover:border-primary/50"
                    }`}
                  >
                    {career}
                  </button>
                ))}
              </div>
              <div className="flex gap-2 mt-6">
                <button onClick={() => setStep(2)} className="flex-1 py-2.5 rounded-md text-sm border border-border text-ink hover:bg-paper">
                  ← Back
                </button>
                <button
                  onClick={handleFinish}
                  disabled={loading}
                  className="flex-[2] bg-primary text-white py-2.5 rounded-md text-sm font-medium disabled:opacity-60"
                >
                  {loading ? "Setting up..." : "Start learning →"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
