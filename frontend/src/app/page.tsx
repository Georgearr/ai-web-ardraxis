import { ChatInterface } from "@/components/chat/ChatInterface"

export default function HomePage() {
  return (
    <div className="flex flex-1 flex-col px-3 sm:px-4">
      <div className="glass-card mx-auto flex h-[calc(100dvh-56px)] w-full max-w-4xl flex-col overflow-hidden rounded-2xl shadow-[0_10px_30px_rgba(0,0,0,0.3)]">
        <ChatInterface />
      </div>
    </div>
  )
}
