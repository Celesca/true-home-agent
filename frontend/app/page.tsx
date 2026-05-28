"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type AssistantResponse = {
  answer?: string;
};

type QuickAction = {
  label: string;
  prompt: string;
  hint: string;
};

// Default to proxy path '/api' so the frontend can call the backend through
// the same origin (nginx). If NEXT_PUBLIC_API_URL is provided at build/runtime
// it will be used instead (useful for development or direct backend calls).
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api";

const initialMessages: ChatMessage[] = [
  {
    id: "assistant-1",
    role: "assistant",
    content:
      "สวัสดีครับ ฉันช่วยดูแพ็กเกจครอบครัว โปรมือถือ อุปกรณ์ในบ้าน และสถานะเราเตอร์ได้\n\nลองพิมพ์: **ดูแพ็กเกจครอบครัวทั้งหมดของฉันหน่อย**",
  },
];

const quickActions: QuickAction[] = [
  {
    label: "แพ็กเกจครอบครัว",
    prompt: "ขอดูรายการแพ็กเกจครอบครัวทั้งหมด พร้อมงวดชำระ ผู้ดูแล ชื่อ และราคา",
    hint: "งวดชำระ + ผู้ดูแล + ชื่อ + ราคา",
  },
  {
    label: "โปร True Mobile",
    prompt: "ช่วยเช็กโปรโมชันปัจจุบันของแพ็กเกจ True Mobile ของฉัน",
    hint: "โปรโมชันของแพ็กเกจปัจจุบัน",
  },
  {
    label: "ควบคุมอุปกรณ์ในบ้าน",
    prompt: "ช่วยปิดอุปกรณ์ทีวีในบ้านให้หน่อย",
    hint: "พัก/ปิดอุปกรณ์",
  },
  {
    label: "เราเตอร์ TrueWiFi",
    prompt: "ช่วยปรับความเร็วเราเตอร์ TrueWiFi และตรวจสอบสถานะเราเตอร์",
    hint: "ปรับสปีด + ตรวจสถานะ",
  },
];

const createId = (prefix: string) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;

function MarkdownMessage({ content }: { content: string }) {
  const components = useMemo(
    () => ({
      a: ({ children, href }: { children?: React.ReactNode; href?: string }) => (
        <a
          href={href}
          target="_blank"
          rel="noreferrer"
          className="font-semibold text-[var(--accent)] underline decoration-[var(--accent)]/40 underline-offset-4"
        >
          {children}
        </a>
      ),
      p: ({ children }: { children?: React.ReactNode }) => <p>{children}</p>,
      ul: ({ children }: { children?: React.ReactNode }) => <ul className="list-disc">{children}</ul>,
      ol: ({ children }: { children?: React.ReactNode }) => <ol className="list-decimal">{children}</ol>,
      li: ({ children }: { children?: React.ReactNode }) => <li>{children}</li>,
      strong: ({ children }: { children?: React.ReactNode }) => (
        <strong className="font-bold text-[var(--ink)]">{children}</strong>
      ),
      em: ({ children }: { children?: React.ReactNode }) => <em className="italic">{children}</em>,
      blockquote: ({ children }: { children?: React.ReactNode }) => <blockquote>{children}</blockquote>,
      hr: () => <hr />,
      code: ({ inline, children }: { inline?: boolean; children?: React.ReactNode }) =>
        inline ? <code>{children}</code> : <code className="block whitespace-pre-wrap">{children}</code>,
      pre: ({ children }: { children?: React.ReactNode }) => <pre>{children}</pre>,
      table: ({ children }: { children?: React.ReactNode }) => (
        <div className="my-4 overflow-x-auto rounded-2xl border border-[var(--accent)]/12 bg-white/95 shadow-[0_16px_30px_rgba(0,0,0,0.06)]">
          <table>{children}</table>
        </div>
      ),
      thead: ({ children }: { children?: React.ReactNode }) => <thead>{children}</thead>,
      tbody: ({ children }: { children?: React.ReactNode }) => <tbody>{children}</tbody>,
      tr: ({ children }: { children?: React.ReactNode }) => <tr>{children}</tr>,
      th: ({ children }: { children?: React.ReactNode }) => <th>{children}</th>,
      td: ({ children }: { children?: React.ReactNode }) => <td>{children}</td>,
    }),
    []
  );

  return (
    <div className="markdown-content text-[15px] leading-7 text-[#1a1a1a]">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}

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

      const data = (await response.json()) as AssistantResponse;
      const content = typeof data.answer === "string" ? data.answer : "ขอโทษครับ ระบบตอบกลับไม่สำเร็จ";

      setMessages((prev) => [
        ...prev,
        { id: createId("assistant"), role: "assistant", content },
      ]);
    } catch {
      setError("เชื่อมต่อระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง");
      setMessages((prev) => [
        ...prev,
        {
          id: createId("assistant"),
          role: "assistant",
          content: "ขอโทษครับ ระบบกำลังมีปัญหา ลองใหม่อีกครั้งได้ไหม",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="wallet-glow relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-56 bg-[linear-gradient(180deg,rgba(230,0,18,0.16),transparent_80%)]" />
      <div className="pointer-events-none absolute -left-24 top-28 h-72 w-72 rounded-full bg-[radial-gradient(circle,rgba(230,0,18,0.16),transparent_70%)] blur-3xl" />
      <div className="pointer-events-none absolute right-[-6rem] top-36 h-80 w-80 rounded-full bg-[radial-gradient(circle,rgba(230,0,18,0.10),transparent_70%)] blur-3xl" />

      <main className="relative z-10 mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="mb-4 flex items-center justify-between rounded-[28px] border border-white/70 bg-white/90 px-5 py-4 shadow-[0_18px_40px_rgba(0,0,0,0.08)] backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <div className="h-12 w-32 flex items-center">
              <img src="/true_logo.png" alt="True logo" className="h-10 object-contain" />
            </div>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#9b4b4f]">
                True Assistant
              </p>
              <h1 className="font-display text-2xl text-[var(--ink)] sm:text-3xl">
                ศูนย์ช่วยเหลือ True ครอบครัว
              </h1>
            </div>
          </div>
          <span className="hidden rounded-full bg-[#ffe9ea] px-3 py-1 text-xs font-semibold text-[#b4000d] sm:inline-flex">
            เชื่อมต่อระบบแล้ว
          </span>
        </header>

        <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[32px] border border-white/70 bg-[var(--card)] shadow-[0_28px_70px_rgba(30,17,8,0.12)] backdrop-blur-xl">
          <div className="border-b border-white/70 bg-[linear-gradient(180deg,rgba(255,250,250,0.95),rgba(255,245,246,0.92))] px-5 py-4 sm:px-6">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#a04a52]">
                  คำถามแนะนำ
                </p>
                <p className="mt-1 font-display text-lg text-[#1a1a1a] sm:text-xl">
                  ช่วยสรุปแพ็กเกจครอบครัวทั้งหมดให้หน่อย
                </p>
              </div>
              <div className="inline-flex items-center gap-2 self-start rounded-full bg-white/90 px-3 py-1 text-xs font-semibold text-[#a04a52] shadow-sm">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                รองรับ Markdown
              </div>
            </div>
          </div>

          <div className="grid gap-3 border-b border-white/70 bg-white/70 px-4 py-4 sm:grid-cols-2 xl:grid-cols-4 sm:px-6">
            {quickActions.map((action) => (
              <button
                key={action.label}
                type="button"
                onClick={() => {
                  void sendMessage(action.prompt);
                }}
                className="group rounded-[22px] border border-white/80 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(255,245,246,0.92))] p-4 text-left shadow-[0_10px_24px_rgba(0,0,0,0.06)] transition hover:-translate-y-0.5 hover:border-[var(--accent)]/18 hover:shadow-[0_16px_28px_rgba(0,0,0,0.08)]"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#a04a52]">
                  สกิล
                </p>
                <h2 className="mt-1 font-display text-base text-[#1a1a1a]">
                  {action.label}
                </h2>
                <p className="mt-2 text-sm leading-6 text-[#6a4a4f]">
                  {action.hint}
                </p>
              </button>
            ))}
          </div>

          <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-4 py-4 sm:px-6 sm:py-5">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <article
                  className={`max-w-[92%] rounded-[28px] px-4 py-3 shadow-[0_10px_28px_rgba(30,17,8,0.08)] sm:max-w-[82%] ${
                    message.role === "user"
                      ? "bg-[linear-gradient(145deg,#ff5a5f,#e60012)] text-white"
                      : "border border-white/80 bg-white/92 text-[#1a1a1a]"
                  }`}
                >
                  {message.role === "assistant" ? (
                    <MarkdownMessage content={message.content} />
                  ) : (
                    <p className="whitespace-pre-wrap text-[15px] leading-7 font-medium text-white/95">
                      {message.content}
                    </p>
                  )}
                </article>
              </div>
            ))}

            {isLoading ? (
              <div className="flex justify-start">
                <div className="inline-flex items-center gap-2 rounded-full border border-[var(--accent)]/15 bg-white/95 px-4 py-2 text-sm text-[#a04a52] shadow-sm">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-[var(--accent)]" />
                  กำลังตอบกลับ...
                </div>
              </div>
            ) : null}
            <div ref={bottomRef} />
          </div>

          <form
            className="border-t border-white/70 bg-[linear-gradient(180deg,rgba(255,252,252,0.94),rgba(255,247,248,0.98))] p-4 sm:p-5"
            onSubmit={(event) => {
              event.preventDefault();
              void sendMessage(input);
            }}
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="พิมพ์คำถามของคุณ..."
                className="min-h-14 flex-1 rounded-[22px] border border-[var(--accent)]/12 bg-white px-4 py-3 text-[15px] text-[#1a1a1a] shadow-[0_8px_20px_rgba(0,0,0,0.05)] outline-none transition focus:border-[var(--accent)]/30 focus:ring-4 focus:ring-[var(--accent)]/10"
                aria-label="Chat input"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="inline-flex min-h-14 items-center justify-center rounded-[22px] bg-[linear-gradient(145deg,#ff5a5f,#e60012)] px-7 py-3 text-sm font-semibold text-white shadow-[0_16px_30px_rgba(230,0,18,0.28)] transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
              >
                ส่ง
              </button>
            </div>
            {error ? (
              <p className="mt-3 text-sm font-medium text-rose-600">{error}</p>
            ) : null}
          </form>
        </section>
      </main>
    </div>
  );
}
