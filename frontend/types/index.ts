// Enhanced type definitions with streaming support
export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, any>
  result?: any
  status?: 'running' | 'completed' | 'error'
}

export interface Message {
  id: number
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  isLoading?: boolean
  reasoning?: string
  toolCalls?: ToolCall[]
  error?: string
}

export interface Tool {
  id: string
  name: string
  status: 'running' | 'completed' | 'error'
  description?: string
  icon?: string
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  input: string
}

export type Theme = 'light' | 'dark'
