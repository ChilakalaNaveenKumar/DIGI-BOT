// Enhanced type definitions with streaming support
export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, any>
  result?: any
  status?: 'running' | 'completed' | 'error'
}

export interface ReasoningStep {
  type: 'thinking' | 'tool_call' | 'conclusion' | 'reasoning' | 'activity'
  content: string
  status?: 'active' | 'completed' | 'error'
  tool_name?: string
  result?: any
  preview?: string
  metadata?: any
}

export interface GeneratedComponent {
  type: string
  markdown: string
  confidence: number
}

export interface Message {
  id: number
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  isLoading?: boolean
  isStreaming?: boolean
  isAnalyzing?: boolean
  reasoning?: string
  reasoningSteps?: ReasoningStep[]
  toolCalls?: ToolCall[]
  components?: GeneratedComponent[]
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
