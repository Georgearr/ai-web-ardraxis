import type { ChatRequest, ChatResponse, SuggestionsResponse } from "@/types/api"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api/v1"

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null)
    throw new Error(errorBody?.error || `Request failed: ${response.status}`)
  }

  return response.json()
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ message } satisfies ChatRequest),
  })
}

export async function getSuggestions(): Promise<SuggestionsResponse> {
  return request<SuggestionsResponse>("/suggestions")
}
