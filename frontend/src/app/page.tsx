import { ChatInterface } from "@/components/chat/ChatInterface"

export default function HomePage() {
  return (
    <div className="relative flex min-h-[calc(100vh-3.5rem-12rem)] items-start justify-center px-3 py-4 sm:px-4 sm:py-6 md:items-center">
      <div className="glass-card w-full max-w-4xl overflow-hidden rounded-2xl shadow-[0_10px_30px_rgba(0,0,0,0.3)] md:min-h-[600px] md:max-h-[calc(100vh-10rem)]">
        <ChatInterface />
      </div>
    </div>
  )
}
