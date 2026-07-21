import { ChatInterface } from "@/components/chat/ChatInterface"

export default function HomePage() {
  return (
    <div className="relative flex min-h-0 flex-1 flex-col items-center justify-center px-3 py-4 sm:px-4 sm:py-6">
      <div className="glass-card flex w-full max-w-4xl flex-1 flex-col overflow-hidden rounded-2xl shadow-[0_10px_30px_rgba(0,0,0,0.3)] md:max-h-[calc(100vh-12rem)]">
        <ChatInterface />
      </div>
    </div>
  )
}
