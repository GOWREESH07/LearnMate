"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { getInitials, cn } from "@/lib/utils";
import { Send, Trash2, Bot, GraduationCap } from "lucide-react";

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!user) return;
    api.chat.history(user.id).then(setMessages).catch(console.error).finally(() => setLoading(false));
  }, [user]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!user || !input.trim() || sending) return;
    const content = input.trim();
    setInput("");
    setSending(true);
    // Optimistically add user message
    setMessages((prev) => [...prev, { id: "tmp", role: "user", content, created_at: new Date().toISOString() }]);
    try {
      const reply = await api.chat.send(content, user.id);
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== "tmp"),
        { id: "tmp-u-" + Date.now(), role: "user", content, created_at: new Date().toISOString() },
        reply,
      ]);
    } catch (err: any) {
      console.error("Chat send error:", err);
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== "tmp"),
        { id: "tmp-u-" + Date.now(), role: "user", content, created_at: new Date().toISOString() },
        {
          id: "tmp-err-" + Date.now(),
          role: "assistant",
          content: "I'm having trouble connecting right now. Please make sure the backend server is active and try again.",
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  async function clearHistory() {
    if (!user || !confirm("Clear all chat history?")) return;
    await api.chat.clear(user.id);
    setMessages([]);
  }

  const userName = user?.user_metadata?.name || user?.email?.split("@")[0] || "You";

  return (
    <div className="flex flex-col h-screen md:h-[calc(100vh-0px)]">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-white">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <GraduationCap className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h1 className="font-semibold text-ink text-sm">AI Tutor</h1>
            <p className="text-2xs text-muted font-mono">Powered by Gemini · Grounded in your progress</p>
          </div>
        </div>
        <button onClick={clearHistory} className="text-muted hover:text-red-500 transition-colors p-1.5 rounded">
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-paper">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted">
            <Bot className="w-12 h-12 mb-3 opacity-30" />
            <p className="font-medium">Your AI tutor is ready</p>
            <p className="text-sm mt-1 max-w-xs">Ask me anything — I know your progress, quiz scores, and study pace, so I can give truly personalized answers.</p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-sm">
              {["Explain linear algebra intuitively", "What should I study next?", "Give me a tip on my weakest topic", "How is my progress?"].map((s) => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  className="text-xs px-3 py-1.5 bg-white border border-border rounded-full hover:border-primary text-muted hover:text-ink transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              userName={userName}
            />
          ))
        )}
        {sending && (
          <div className="flex items-center gap-2 text-muted">
            <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center">
              <GraduationCap className="w-3 h-3 text-primary" />
            </div>
            <span className="text-sm italic animate-pulse-subtle">LearnMate is thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="border-t border-border bg-white px-4 py-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask your AI tutor anything..."
          className="flex-1 px-4 py-2 rounded-full border border-border text-sm bg-paper focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          disabled={sending}
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center hover:bg-primary-600 disabled:opacity-50 transition-colors flex-shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}

function MessageBubble({ message, userName }: { message: any; userName: string }) {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex gap-2.5", isUser ? "flex-row-reverse" : "flex-row")}>
      <div className={cn(
        "w-7 h-7 rounded-full flex items-center justify-center text-2xs font-mono font-bold flex-shrink-0",
        isUser ? "bg-primary/10 text-primary" : "bg-primary text-white"
      )}>
        {isUser ? getInitials(userName) : "AI"}
      </div>
      <div className={cn(
        "max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed",
        isUser
          ? "bg-primary text-white rounded-tr-sm"
          : "bg-white border border-border text-ink rounded-tl-sm"
      )}>
        {message.content}
      </div>
    </div>
  );
}
