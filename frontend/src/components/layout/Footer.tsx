export function Footer() {
  return (
    <footer className="bg-gradient-to-br from-[#3A7070] via-[#315f5f] to-[#2a5151] text-white relative overflow-hidden">
      <div className="mx-auto max-w-[1200px] px-4 py-8 sm:px-5 sm:py-10">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5 md:grid-cols-3 md:gap-6">
          <div className="flex flex-col items-center rounded-2xl border border-[rgba(255,255,255,0.14)] bg-[rgba(255,255,255,0.06)] p-5 shadow-[0_10px_28px_rgba(0,0,0,0.25)] backdrop-blur-[6px] min-h-[200px] md:min-h-[240px]">
            <div className="flex flex-col items-center gap-2.5 text-center">
              <div className="flex h-[96px] w-[96px] items-center justify-center md:h-[120px] md:w-[120px]">
                <span className="text-5xl font-black tracking-[0.08em] text-white drop-shadow-[0_8px_18px_rgba(0,0,0,0.35)] md:text-6xl">
                  D
                </span>
              </div>
              <h1 className="mt-1.5 text-lg font-black uppercase tracking-[0.08em] text-transparent bg-gradient-to-r from-white to-[#e1f3f3] bg-clip-text md:text-[1.8rem]">
                DRAX
              </h1>
              <p className="mt-1 text-sm leading-snug text-[#e8f7f7] opacity-90 md:text-[0.98rem]">
                Digital Resource Assistant of ARDRAXIS
              </p>
            </div>
          </div>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-[rgba(255,255,255,0.14)] bg-[rgba(255,255,255,0.06)] p-5 shadow-[0_10px_28px_rgba(0,0,0,0.25)] backdrop-blur-[6px] min-h-[200px] md:min-h-[240px]">
            <div className="flex flex-col items-center gap-2.5 text-center">
              <svg className="h-14 w-14 text-white drop-shadow-[0_6px_14px_rgba(0,0,0,0.3)] md:h-16 md:w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
              </svg>
              <p className="mx-auto max-w-[28ch] text-sm leading-relaxed text-[#e8f7f7] md:text-[0.98rem]">
                SMA Ignatius Global School
                <br />
                Palembang
              </p>
            </div>
          </div>
          <div className="flex flex-col items-center rounded-2xl border border-[rgba(255,255,255,0.14)] bg-[rgba(255,255,255,0.06)] p-5 shadow-[0_10px_28px_rgba(0,0,0,0.25)] backdrop-blur-[6px] min-h-[200px] md:min-h-[240px] sm:col-span-2 md:col-span-1">
            <div className="grid w-full grid-cols-3 gap-3">
              {[
                { label: "Instagram", href: "https://www.instagram.com/osis.smaigs/" },
                { label: "Twitter", href: "https://x.com/osis_smaigs" },
                { label: "Tiktok", href: "https://www.tiktok.com/@osis.smaigs" },
                { label: "Line", href: "https://line.me/R/ti/p/@053dzdrl" },
                { label: "Youtube", href: "https://www.youtube.com/channel/UCJcG1VCjXHNig5JIDEgYH7w" },
                { label: "Github", href: "https://github.com/OSISSMAIGS" },
              ].map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex flex-col items-center justify-center gap-2 rounded-xl border border-[rgba(255,255,255,0.18)] bg-[rgba(255,255,255,0.08)] px-2.5 py-3.5 text-center no-underline text-inherit transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(255,255,255,0.3)] hover:bg-[rgba(255,255,255,0.14)] hover:shadow-[0_10px_28px_rgba(0,0,0,0.28)]"
                >
                  <span className="text-lg">{social.label === "Instagram" ? "📸" : social.label === "Twitter" ? "𝕏" : social.label === "Tiktok" ? "🎵" : social.label === "Line" ? "💬" : social.label === "Youtube" ? "▶" : "⌘"}</span>
                  <span className="text-xs text-[#e8f7f7] md:text-[0.95rem]">{social.label}</span>
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
