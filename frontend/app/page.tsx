"use client";

import { useEffect, useRef, useState } from "react";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialMessages: ChatMessage[] = [
  {
    id: "assistant-1",
    role: "assistant",
    content:
      "สวัสดี! พิมพ์คำถามได้เลย เช่น: ดู Subscription ทั้งหมดของครอบครัวชั้นหน่อย",
  },
];

const createId = (prefix: string) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setError(null);
    setIsLoading(true);
    setMessages((prev) => [...prev, { id: createId("user"), role: "user", content: trimmed }]);
    setInput("");

    try {
      const response = await fetch(`${API_BASE}/agent/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: trimmed, language: "auto" }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
      const content =
        typeof data?.answer === "string"
          ? data.answer
          : "ขอโทษค่ะ ระบบตอบกลับไม่สำเร็จ";

      setMessages((prev) => [
        ...prev,
        { id: createId("assistant"), role: "assistant", content },
      ]);
    } catch (caught) {
      setError("เชื่อมต่อระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง");
      setMessages((prev) => [
        ...prev,
        {
          id: createId("assistant"),
          role: "assistant",
          content: "ขอโทษค่ะ ระบบกำลังมีปัญหา ลองใหม่อีกครั้งได้ไหม",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,_#f9e9d2,_#f6f0e8_55%,_#f2dcc0_100%)]">
      <div className="pointer-events-none absolute -top-20 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-[radial-gradient(circle,_rgba(255,122,72,0.35),_transparent_70%)] blur-3xl" />
      <div className="pointer-events-none absolute right-[-10%] top-24 h-80 w-80 rounded-full bg-[radial-gradient(circle,_rgba(28,140,136,0.3),_transparent_70%)] blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 left-10 h-72 w-72 rounded-full bg-[radial-gradient(circle,_rgba(242,214,179,0.6),_transparent_70%)] blur-3xl" />

      <main className="relative z-10 mx-auto flex min-h-screen w-full max-w-4xl flex-col px-6 py-10">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-neutral-500">
              True Home AI
            </p>
            <h1 className="font-display mt-2 text-3xl text-[var(--ink)]">
              Family Chat
            </h1>
          </div>
          <span className="rounded-full bg-[var(--ink)] px-3 py-1 text-xs font-semibold text-white">
            Connected
          </span>
        </header>

        <section className="flex flex-1 flex-col rounded-3xl border border-white/70 bg-[var(--card)] p-6 shadow-[0_24px_60px_rgba(16,20,23,0.12)]">
          <div className="flex-1 space-y-4 overflow-y-auto pr-1">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                    message.role === "user"
                      ? "bg-white/85 text-neutral-700"
                      : "bg-[var(--ink)] text-white"
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </p>
                </div>
              </div>
            ))}
            {isLoading ? (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-[var(--ink)] px-4 py-3 text-xs text-white/70">
                  กำลังพิมพ์...
                </div>
              </div>
            ) : null}
            <div ref={bottomRef} />
          </div>

          <form
            className="mt-6 flex flex-col gap-3 border-t border-white/70 pt-4"
            onSubmit={(event) => {
              event.preventDefault();
              void sendMessage(input);
            }}
          >
            <label className="text-xs uppercase tracking-[0.25em] text-neutral-500">
              Message
            </label>
            <div className="flex flex-wrap gap-3">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="พิมพ์คำถามของคุณ..."
                className="flex-1 rounded-2xl border border-white/70 bg-white/85 px-4 py-3 text-sm text-neutral-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
                aria-label="Chat input"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="rounded-2xl bg-[var(--ink)] px-6 py-3 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-neutral-500"
              >
                Send
              </button>
            </div>
            {error ? <p className="text-xs text-rose-600">{error}</p> : null}
          </form>
        </section>
      </main>
    </div>
  );
}
