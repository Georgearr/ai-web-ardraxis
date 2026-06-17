export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: number
}

export interface ChatState {
  messages: Message[]
  isStreaming: boolean
  error: string | null
}
