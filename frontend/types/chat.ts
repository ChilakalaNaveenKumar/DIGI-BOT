// types/chat.ts
// TypeScript definitions for the chat system

export interface MultimodalContent {
  type: 'text' | 'image' | 'audio' | 'json' | 'markdown' | 'table' | 'diagram' | 'tool_call' | 'reasoning' | 'thinking' | 'tool_loading' | 'tool_executing'
  data: unknown
  format?: string
  metadata?: Record<string, unknown>
  url?: string
}

export interface MessagePart {
  type: 'text' | 'reasoning' | 'thinking' | 'tool_loading' | 'tool_executing' | 'file' | 'tool-call' | 'tool-result' | 'image' | 'json' | 'table' | 'diagram' | 'markdown'
  text?: string
  url?: string
  mediaType?: string
  filename?: string
  content?: string
  data?: unknown
  format?: string
  metadata?: Record<string, unknown>
  state?: 'streaming' | 'done' | 'error' | 'pending' | 'input-streaming' | 'input-available' | 'output-available' | 'output-error' | 'loading' | 'executing'
  multimodal_content?: MultimodalContent[]
  content_type?: string
  preserve_formatting?: boolean
  toolName?: string
  toolId?: string
  input?: Record<string, unknown>
  output?: Record<string, unknown>
  errorText?: string
  tool_info?: {
    name?: string
    status?: string
    description?: string
  }
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  parts?: MessagePart[]
  createdAt: string
  hasReasoning?: boolean
  hasTools?: boolean
  hasFiles?: boolean
  reasoning?: MessagePart[]
  tools?: MessagePart[]
  files?: MessagePart[]
}

export interface FileUIPart {
  type: 'file'
  url: string
  mediaType: string
  filename?: string
}

export interface Provider {
  id: string
  name: string
  icon: string
  models: string[]
  description: string
  reasoning: boolean
}

export interface ToolDefinition {
  description: string
  parameters: {
    type: 'object'
    properties: Record<string, unknown>
    required: string[]
  }
}

export interface ChatOptions {
  files?: FileList
  enableReasoning?: boolean
}

export interface ChatError {
  message: string
}

export interface StreamChunk {
  content?: string
  reasoning?: string
  error?: string
  type?: string
  delta?: string
  content_type?: string
  multimodal_content?: MultimodalContent[]
  preserve_formatting?: boolean
  provider?: string
  model?: string
  tool_call?: {
    id: string
    name: string
    arguments: string
  }
}

// Tool-specific interfaces
export interface TableData {
  title: string
  headers: string[]
  rows: unknown[][]
  sortable?: boolean
  searchable?: boolean
}

export interface QuizQuestion {
  question: string
  options: string[]
  correct: number
  explanation: string
}

export interface QuizData {
  title: string
  questions: QuizQuestion[]
}

export interface ChartData {
  title: string
  type: 'bar' | 'line' | 'pie' | 'scatter'
  data: Array<{ label: string; value: number }>
  xAxis?: string
  yAxis?: string
}

export interface FlashcardData {
  title: string
  cards: Array<{
    front: string
    back: string
    category?: string
  }>
}
