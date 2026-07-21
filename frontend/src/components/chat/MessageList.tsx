"use client"

import { useEffect, useRef } from "react"
import { MessageBubble } from "./MessageBubble"
import type { Message } from "@/types/chat"
import type { RefObject } from "react"

interface MessageListProps {
  messages: Message[]
  scrollRef: RefObject<HTMLDivElement | null>
}

export function MessageList({ messages, scrollRef }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({
      top: el.scrollHeight,
      behavior: "smooth",
    })
  }, [messages, scrollRef])

  if (messages.length === 0) return null

  return (
    <div className="flex flex-col gap-4 px-4 py-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
