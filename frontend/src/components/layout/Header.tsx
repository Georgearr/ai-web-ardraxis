"use client"

import Link from "next/link"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full bg-[rgb(29,105,110)] backdrop-blur-[8px] border-b border-[rgba(255,255,255,0.08)] shadow-[0_3px_25px_rgba(0,0,0,0.8)]">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-3 no-underline text-inherit group">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
            <span className="text-lg font-black text-white">D</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-black tracking-[0.5px] text-white drop-shadow-[0_0_5px_#0e3a42] group-hover:animate-[glowUp_0.4s_ease-in-out_forwards]">
              DRAX
            </span>
            <span className="text-[10px] leading-tight text-[#b2dfdb] font-light tracking-[1px]">
              AI Assistant ARDRAXIS
            </span>
          </div>
        </Link>
        <div className="hidden items-center gap-5 sm:flex">
          <span className="px-3 py-2 text-xs font-extrabold tracking-[0.3px] text-white/70">
            Empowering Information, Igniting Innovation.
          </span>
        </div>
      </div>
    </header>
  )
}
