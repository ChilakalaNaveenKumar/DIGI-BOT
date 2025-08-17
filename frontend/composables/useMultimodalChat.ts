/**
 * Multimodal Chat Composable
 * 
 * Enhanced chat functionality that automatically uses multimodal capabilities
 */

import { ref, computed } from 'vue'
import { useEnhancedContentDetection } from './useEnhancedContentDetection.js'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: any
  timestamp?: Date
}

interface MultimodalChatRequest {
  message: string
  conversation_history?: ChatMessage[]
  files?: any[]
  preferences?: any
}

interface MultimodalChatResponse {
  message: string
  content_type: string
  metadata: any
  tool_calls?: any[]
  reasoning?: string
}

export const useMultimodalChat = () => {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const { detectContentType, getContentTypeDisplayName, getContentTypeIcon } = useEnhancedContentDetection()
  
  // Get API base URL from runtime config
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  /**
   * Send a message using the multimodal chat endpoint
   */
  const sendMessage = async (
    message: string, 
    files: any[] = [], 
    preferences: any = {}
  ): Promise<MultimodalChatResponse | null> => {
    try {
      isLoading.value = true
      error.value = null

      // Add user message to conversation
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date()
      }
      messages.value.push(userMessage)

      // Prepare request
      const request: MultimodalChatRequest = {
        message,
        conversation_history: messages.value.slice(-10), // Last 10 messages for context
        files,
        preferences
      }

      // Call multimodal chat API
      const response = await fetch(`${apiBase}/v1/multimodal/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Chat request failed')
      }

      const result: MultimodalChatResponse = await response.json()

      // Add assistant response to conversation
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: result.message,
        metadata: {
          ...result.metadata,
          content_type: result.content_type,
          tool_calls: result.tool_calls,
          reasoning: result.reasoning
        },
        timestamp: new Date()
      }
      messages.value.push(assistantMessage)

      return result

    } catch (err: any) {
      error.value = err.message
      console.error('Multimodal chat failed:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get available multimodal capabilities
   */
  const getCapabilities = async () => {
    try {
      const response = await fetch(`${apiBase}/v1/multimodal/capabilities`)
      if (!response.ok) {
        throw new Error('Failed to get capabilities')
      }
      return await response.json()
    } catch (err) {
      console.error('Failed to get capabilities:', err)
      return null
    }
  }

  /**
   * Test intent detection for a message
   */
  const testIntent = async (message: string) => {
    try {
      const response = await fetch(`${apiBase}/v1/multimodal/test-intent?message=${encodeURIComponent(message)}`, {
        method: 'POST'
      })
      if (!response.ok) {
        throw new Error('Intent detection failed')
      }
      return await response.json()
    } catch (err) {
      console.error('Intent detection failed:', err)
      return null
    }
  }

  /**
   * Clear conversation history
   */
  const clearConversation = () => {
    messages.value = []
    error.value = null
  }

  /**
   * Get the last assistant message
   */
  const lastAssistantMessage = computed(() => {
    const assistantMessages = messages.value.filter(m => m.role === 'assistant')
    return assistantMessages[assistantMessages.length - 1] || null
  })

  /**
   * Get conversation statistics
   */
  const conversationStats = computed(() => {
    const userMessages = messages.value.filter(m => m.role === 'user').length
    const assistantMessages = messages.value.filter(m => m.role === 'assistant').length
    const toolCalls = messages.value
      .filter(m => m.role === 'assistant' && m.metadata?.tool_calls)
      .reduce((total, m) => total + (m.metadata.tool_calls?.length || 0), 0)

    return {
      totalMessages: messages.value.length,
      userMessages,
      assistantMessages,
      toolCalls
    }
  })

  /**
   * Format message content based on type
   */
  const formatMessage = (message: ChatMessage) => {
    if (message.role === 'user') {
      return {
        content: message.content,
        type: 'text',
        displayName: 'User Message',
        icon: 'mdi:account'
      }
    }

    // For assistant messages, detect content type
    const contentType = message.metadata?.content_type || 
                       detectContentType(message.content, message.metadata)
    
    return {
      content: message.content,
      type: contentType,
      displayName: getContentTypeDisplayName(contentType),
      icon: getContentTypeIcon(contentType),
      metadata: message.metadata
    }
  }

  /**
   * Check if a message has tool calls
   */
  const hasToolCalls = (message: ChatMessage): boolean => {
    return message.metadata?.tool_calls && message.metadata.tool_calls.length > 0
  }

  /**
   * Get tool calls from a message
   */
  const getToolCalls = (message: ChatMessage) => {
    return message.metadata?.tool_calls || []
  }

  /**
   * Export conversation as JSON
   */
  const exportConversation = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      messageCount: messages.value.length,
      stats: conversationStats.value,
      messages: messages.value.map(m => ({
        ...m,
        timestamp: m.timestamp?.toISOString()
      }))
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return {
    // State
    messages: readonly(messages),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Computed
    lastAssistantMessage,
    conversationStats,
    
    // Methods
    sendMessage,
    getCapabilities,
    testIntent,
    clearConversation,
    formatMessage,
    hasToolCalls,
    getToolCalls,
    exportConversation
  }
}
