/**
 * Shared conversation types used across stores and composables
 */

export interface Conversation {
  id: number
  title: string
  status: string
  message_count: number
  created_at: string
  updated_at: string
  last_message_at?: string
  storage_type?: string
}

export interface ConversationMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  ai_provider?: string
  ai_model?: string
  token_count?: number
  processing_time?: number
  reasoning_steps?: {
    steps: Array<{
      id: string
      type: 'thinking' | 'tool_call'
      content: string
      status: string
      timestamp: string
      tool_name?: string
      result?: unknown
      inputJson?: string
    }>
  }
  created_at: string
  updated_at: string
}
