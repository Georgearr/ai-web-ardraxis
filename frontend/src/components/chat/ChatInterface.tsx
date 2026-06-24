"use client"

import { useState, useEffect } from "react"
import { useChat } from "@/hooks/useChat"
import { getSuggestions } from "@/services/api-client"
import { EmptyState } from "./EmptyState"
import { MessageList } from "./MessageList"
import { ChatInput } from "./ChatInput"
import { LoadingIndicator } from "./LoadingIndicator"

export function ChatInterface() {
  const { messages, isStreaming, error, send } = useChat()
  const [suggestions, setSuggestions] = useState<string[]>([])

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

  const hasMessages = messages.length > 0

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto scrollbar-thin">
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
          <EmptyState
            suggestions={suggestions}
            onSuggestionClick={send}
          />
        )}
      </div>
      <ChatInput onSend={send} disabled={isStreaming} />
    </div>
  )
}
