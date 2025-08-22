// Message types for chat interface
export interface Message {
  id: string | number
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  isLoading?: boolean
  isStreaming?: boolean
  error?: string
  reasoningSteps?: ReasoningStep[]
  reasoning?: string
  toolCalls?: ToolCall[]
  components?: GeneratedComponent[]
}

export interface ReasoningStep {
  id: string
  title: string
  content: string
  status: 'pending' | 'processing' | 'completed'
  timestamp?: Date
}

export interface ToolCall {
  id: string
  name: string
  status?: 'running' | 'completed' | 'failed'
  result?: unknown
  error?: string
}

export interface GeneratedComponent {
  id: string
  type: string
  data: unknown
  confidence?: number
}

// Enhanced content types
export interface EnhancedContent {
  id: string
  messageId: string | number
  content: string
  components: ComponentData[]
  metadata?: Record<string, unknown>
}

export interface ComponentData {
  id: string
  type: 'chart' | 'table' | 'widget'
  subtype?: string
  data: unknown
  title?: string
  description?: string
}

// Chat composable types
export interface ChatState {
  messages: Message[]
  isLoading: boolean
  isStreaming: boolean
  error: string | null
}

export interface ChatActions {
  sendMessage: (content: string) => Promise<void>
  clearMessages: () => void
  regenerateMessage: (messageId: string | number) => Promise<void>
}
