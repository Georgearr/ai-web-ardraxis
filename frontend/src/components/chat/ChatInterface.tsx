"use client"

import { useState, useEffect, useRef } from "react"
import { useChat } from "@/hooks/useChat"
import { getSuggestions } from "@/services/api-client"
import { EmptyState } from "./EmptyState"
import { MessageList } from "./MessageList"
import { ChatInput } from "./ChatInput"
import { LoadingIndicator } from "./LoadingIndicator"

const NEAR_BOTTOM_THRESHOLD = 160

export function ChatInterface() {
  const { messages, isStreaming, error, send } = useChat()
  const [suggestions, setSuggestions] = useState<string[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)
  const nearBottomRef = useRef(true)

  useEffect(() => {
    getSuggestions()
      .then((res) => setSuggestions(res.suggestions))
      .catch(() => {
        setSuggestions([
          "Siapa Ketua OSIS?",
          "Event terdekat apa?",
          "Siapa yang mengurus website?",
        ])
      })
  }, [])

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    nearBottomRef.current =
      el.scrollHeight - el.scrollTop - el.clientHeight < NEAR_BOTTOM_THRESHOLD
  }

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    if (nearBottomRef.current) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" })
    }
  }, [messages, isStreaming, error])

  const handleSend = (message: string) => {
    nearBottomRef.current = true
    send(message)
  }

  const hasMessages = messages.length > 0

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="min-h-0 flex-1 overflow-y-auto scrollbar-thin"
      >
        {hasMessages ? (
          <>
            <MessageList messages={messages} />
            {isStreaming && <LoadingIndicator />}
            {error && (
              <div className="px-4 pb-4">
                <div className="rounded-xl border border-red-500/50 bg-red-500/10 px-4 py-3 text-sm text-red-400 backdrop-blur-[6px]">
                  {error}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex min-h-full flex-col">
            <div className="flex-1" />
            <EmptyState
              suggestions={suggestions}
              onSuggestionClick={handleSend}
            />
            <div className="flex-1" />
          </div>
        )}
      </div>
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  )
}
