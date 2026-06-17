"use client"

import { Icon } from "@/components/shared/Icons"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center gap-3 px-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Icon name="sparkles" className="text-primary-foreground" size={18} />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold leading-tight">DRAX</span>
            <span className="text-[10px] leading-tight text-muted-foreground">
              AI Assistant ARDRAXIS
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
