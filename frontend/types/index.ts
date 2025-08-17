// Clean type definitions
export interface Message {
  id: number
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  isLoading?: boolean
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
