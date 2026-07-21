"use client"

import { cn } from "@/lib/utils"
import { Icon } from "@/components/shared/Icons"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Message } from "@/types/chat"

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user"

  return (
    <div
      className={cn(
        "flex w-full gap-3 animate-fade-in",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[rgba(255,255,255,0.12)] backdrop-blur-[6px]",
          isUser
            ? "bg-gradient-to-br from-[#1d696e] to-[#2d8f9a]"
            : "bg-[rgba(0,0,0,0.25)]"
        )}
      >
        {isUser ? (
          <Icon name="user" className="text-white" size={16} />
        ) : (
          <span className="text-sm font-black text-transparent bg-gradient-to-br from-white to-[#b2dfdb] bg-clip-text">
            D
          </span>
        )}
      </div>
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-[0_10px_30px_rgba(0,0,0,0.3)] overflow-x-auto",
          isUser
            ? "bg-gradient-to-br from-[#1d696e] to-[#2d8f9a] text-white rounded-tr-md"
            : "glass-card text-white/90 rounded-tl-md"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none prose-headings:text-white prose-a:text-[#b2dfdb] prose-code:bg-white/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-black/30 prose-strong:text-white prose-li:text-white/90">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
