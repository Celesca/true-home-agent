const subscriptions = [
  {
    service: "TrueID Plus Family",
    category: "Streaming",
    price: 249,
    status: "Active",
    owner: "Family",
    nextBill: "2026-06-01",
  },
  {
    service: "True Fiber 1Gbps",
    category: "Home Internet",
    price: 899,
    status: "Active",
    owner: "Home",
    nextBill: "2026-06-03",
  },
  {
    service: "True Move H 5G Family",
    category: "Mobile",
    price: 1199,
    status: "Active",
    owner: "Parents",
    nextBill: "2026-06-05",
  },
];

const alerts = [
  {
    label: "Fiber status",
    value: "Degraded · 78ms latency",
    tone: "bg-amber-100 text-amber-900",
  },
  {
    label: "Kids devices",
    value: "2 online, 1 paused",
    tone: "bg-teal-100 text-teal-900",
  },
  {
    label: "Next payment",
    value: "TrueID · 2026-06-01",
    tone: "bg-rose-100 text-rose-900",
  },
];

const formatThb = (value: number) => `THB ${value.toLocaleString("en-US")}`;

export default function Home() {
  const totalMonthly = subscriptions.reduce((sum, item) => sum + item.price, 0);
  const assistantMarkdown = `### สรุป Subscription ครอบครัว\n\n| บริการ | ประเภท | ราคา/เดือน | สถานะ | รอบบิล |\n| --- | --- | --- | --- | --- |\n| TrueID Plus Family | Streaming | ${formatThb(249)} | Active | 2026-06-01 |\n| True Fiber 1Gbps | Home Internet | ${formatThb(899)} | Active | 2026-06-03 |\n| True Move H 5G Family | Mobile | ${formatThb(1199)} | Active | 2026-06-05 |\n\n**รวมรายเดือน:** ${formatThb(totalMonthly)}\n\nต้องการให้ช่วยเปรียบเทียบแพ็กอื่นไหม?`;

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,_#f9e9d2,_#f6f0e8_55%,_#f2dcc0_100%)]">
      <div className="pointer-events-none absolute -top-20 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-[radial-gradient(circle,_rgba(255,122,72,0.45),_transparent_70%)] blur-3xl" />
      <div className="pointer-events-none absolute right-[-10%] top-24 h-80 w-80 rounded-full bg-[radial-gradient(circle,_rgba(28,140,136,0.35),_transparent_70%)] blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 left-10 h-72 w-72 rounded-full bg-[radial-gradient(circle,_rgba(242,214,179,0.7),_transparent_70%)] blur-3xl" />

      <main className="relative z-10 mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 py-12 lg:px-10">
        <header className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--ink)] text-lg font-semibold text-white shadow-lg">
              TH
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-neutral-500">
                True Home AI
              </p>
              <h1 className="font-display text-3xl font-semibold text-[var(--ink)] sm:text-4xl">
                Family Dashboard + Chat
              </h1>
              <p className="mt-2 max-w-xl text-sm text-neutral-600">
                A single view for subscriptions, connectivity, and household questions.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-full border border-white/70 bg-white/70 px-4 py-2 text-sm text-neutral-700 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            26 May 2026 · Bangkok
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="flex flex-col gap-6">
            <div className="rounded-3xl border border-white/70 bg-[var(--card)] p-6 shadow-[0_24px_60px_rgba(16,20,23,0.12)]">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.25em] text-neutral-500">
                    Subscription Snapshot
                  </p>
                  <h2 className="font-display mt-2 text-2xl text-[var(--ink)]">
                    Family subscriptions overview
                  </h2>
                </div>
                <div className="rounded-2xl bg-white/80 px-4 py-3 text-sm text-neutral-700">
                  <p className="text-xs uppercase text-neutral-500">Monthly total</p>
                  <p className="font-display text-xl text-[var(--ink)]">
                    {formatThb(totalMonthly)}
                  </p>
                </div>
              </div>
              <div className="mt-6 space-y-4">
                {subscriptions.map((item) => (
                  <div
                    key={item.service}
                    className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/60 bg-[var(--card-strong)] px-4 py-3"
                  >
                    <div>
                      <p className="font-display text-lg text-[var(--ink)]">
                        {item.service}
                      </p>
                      <p className="text-sm text-neutral-600">
                        {item.category} · {item.owner}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-neutral-500">Next bill</p>
                      <p className="font-semibold text-[var(--ink)]">{item.nextBill}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-neutral-500">Price</p>
                      <p className="font-semibold text-[var(--ink)]">
                        {formatThb(item.price)}
                      </p>
                    </div>
                    <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-900">
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {alerts.map((alert) => (
                <div
                  key={alert.label}
                  className="rounded-2xl border border-white/70 bg-[var(--card)] p-5 shadow-[0_18px_40px_rgba(16,20,23,0.1)]"
                >
                  <p className="text-xs uppercase tracking-[0.25em] text-neutral-500">
                    {alert.label}
                  </p>
                  <p className="mt-3 text-lg font-semibold text-[var(--ink)]">
                    {alert.value}
                  </p>
                  <span
                    className={`mt-4 inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${alert.tone}`}
                  >
                    Live signal
                  </span>
                </div>
              ))}
            </div>
          </div>

          <aside className="flex flex-col rounded-3xl border border-white/70 bg-[var(--card)] p-6 shadow-[0_24px_60px_rgba(16,20,23,0.12)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-neutral-500">
                  Family Chat
                </p>
                <h3 className="font-display mt-2 text-2xl text-[var(--ink)]">
                  Subscription assistant
                </h3>
              </div>
              <span className="rounded-full bg-[var(--ink)] px-3 py-1 text-xs font-semibold text-white">
                Online
              </span>
            </div>

            <div className="mt-6 flex flex-1 flex-col gap-4">
              <div className="max-w-[85%] self-end rounded-2xl bg-white/85 px-4 py-3 text-sm text-neutral-700 shadow-sm">
                ดู Subscription ทั้งหมดของครอบครัวชั้นหน่อย
              </div>
              <div className="max-w-[90%] self-start rounded-2xl bg-[var(--ink)] px-4 py-4 text-sm text-white shadow-lg">
                <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-white/60">
                  Markdown output
                  <span className="h-1.5 w-1.5 rounded-full bg-[var(--accent)]" />
                </div>
                <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-white/90">
                  {assistantMarkdown}
                </pre>
              </div>
            </div>

            <div className="mt-6 rounded-2xl border border-white/60 bg-white/80 px-4 py-3 text-sm text-neutral-500">
              Ask about bundles, upgrades, or savings...
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className="rounded-full border border-white/70 bg-white/70 px-3 py-1 text-neutral-600">
                Compare cheaper plans
              </span>
              <span className="rounded-full border border-white/70 bg-white/70 px-3 py-1 text-neutral-600">
                Check Netflix add-on
              </span>
              <span className="rounded-full border border-white/70 bg-white/70 px-3 py-1 text-neutral-600">
                Pause kids devices
              </span>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}
