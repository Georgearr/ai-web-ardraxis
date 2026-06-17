"use client"

import { useState, useCallback, useRef } from "react"
import type { Message, ChatState } from "@/types/chat"
import { sendMessage } from "@/services/api-client"

function generateId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

const INITIAL_STATE: ChatState = {
  messages: [],
  isStreaming: false,
  error: null,
}

export function useChat() {
  const [state, setState] = useState<ChatState>(INITIAL_STATE)
  const abortRef = useRef<AbortController | null>(null)

  const addMessage = useCallback((role: "user" | "assistant", content: string) => {
    const message: Message = {
      id: generateId(),
      role,
      content,
      timestamp: Date.now(),
    }
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, message],
    }))
    return message
  }, [])

  const send = useCallback(
    async (content: string) => {
      if (!content.trim() || state.isStreaming) return

      addMessage("user", content)

      setState((prev) => ({ ...prev, isStreaming: true, error: null }))

      try {
        abortRef.current = new AbortController()
        const result = await sendMessage(content)
        addMessage("assistant", result.response)
      } catch (err) {
        const errorMsg =
          err instanceof Error ? err.message : "Terjadi kesalahan. Silakan coba lagi."
        setState((prev) => ({ ...prev, error: errorMsg }))
      } finally {
        setState((prev) => ({ ...prev, isStreaming: false }))
        abortRef.current = null
      }
    },
    [state.isStreaming, addMessage]
  )

  const clear = useCallback(() => {
    setState(INITIAL_STATE)
  }, [])

  return {
    messages: state.messages,
    isStreaming: state.isStreaming,
    error: state.error,
    send,
    clear,
  }
}
