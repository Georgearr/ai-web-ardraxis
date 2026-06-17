export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  response: string
}

export interface SuggestionsResponse {
  suggestions: string[]
}

export interface ErrorResponse {
  error: string
}
