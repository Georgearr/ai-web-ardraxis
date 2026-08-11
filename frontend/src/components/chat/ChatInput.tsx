"use client"

import { useState, useRef, type KeyboardEvent } from "react"
import { Icon } from "@/components/shared/Icons"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setInput("")
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t border-[rgba(255,255,255,0.08)] px-4 pt-2 md:pt-3 pb-[max(0.5rem,env(safe-area-inset-bottom))] flex-shrink-0">
      <div className="mx-auto flex max-w-3xl items-center gap-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Tanyakan tentang OSIS..."
          disabled={disabled}
          suppressHydrationWarning
          className="flex h-10 w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(0,0,0,0.25)] px-4 text-sm text-white placeholder:text-[#b2dfdb]/50 shadow-[0_6px_18px_rgba(0,0,0,0.35)] backdrop-blur-[6px] transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#96cccd] disabled:cursor-not-allowed disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[rgba(255,255,255,0.3)] bg-gradient-to-br from-[#1d696e] to-[#2d8f9a] text-white shadow-[0_6px_18px_rgba(0,0,0,0.35)] transition-all duration-250 hover:scale-105 hover:border-[rgba(255,255,255,0.6)] hover:shadow-[0_10px_24px_rgba(0,0,0,0.45),0_0_0_6px_rgba(255,255,255,0.06)] active:scale-96 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <Icon name="send" size={18} />
        </button>
      </div>
    </div>
  )
}
