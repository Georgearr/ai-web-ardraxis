import { ChatInterface } from "@/components/chat/ChatInterface"

export default function HomePage() {
  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-4xl flex-col rounded-xl border bg-card shadow-sm md:my-4 md:h-[calc(100vh-10rem)]">
      <ChatInterface />
    </div>
  )
}
