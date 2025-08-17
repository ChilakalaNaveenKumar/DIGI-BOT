// Enhanced type definitions with streaming support
export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, any>
  result?: any
  status?: 'running' | 'completed' | 'error'
}

export interface ReasoningStep {
  type: 'thinking' | 'tool_call' | 'conclusion'
  content: string
  status?: 'active' | 'completed' | 'error'
  tool_name?: string
  result?: any
  preview?: string
}

export interface Message {
  id: number
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  isLoading?: boolean
  isStreaming?: boolean
  reasoning?: string
  reasoningSteps?: ReasoningStep[]
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
