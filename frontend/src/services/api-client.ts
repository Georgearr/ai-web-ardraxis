import type { ChatRequest, ChatResponse, SuggestionsResponse } from "@/types/api"

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `/api${endpoint}`

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
