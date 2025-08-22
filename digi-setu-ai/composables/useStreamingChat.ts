import type { Message } from '~/types'

export const useStreamingChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isStreaming = ref(false)
  
  // Add request deduplication and cancellation
  const lastRequestContent = ref<string>('')
  const lastRequestTime = ref<number>(0)
  const currentAbortController = ref<AbortController | null>(null)

  const sendStreamingMessage = async (content: string) => {
    if (!content.trim() || isLoading.value || isStreaming.value) return
    
    // Prevent duplicate requests within 1 second
    const now = Date.now()
    if (content === lastRequestContent.value && now - lastRequestTime.value < 1000) {
      console.log('Duplicate request prevented:', content)
      return
    }
    
    lastRequestContent.value = content
    lastRequestTime.value = now
    console.log('Sending message:', content) // Debug log

    // Add user message
    const userMessage: Message = {
      id: Date.now() + Math.random(),
      content: content.trim(),
      role: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    // Create assistant message placeholder
    const assistantMessage: Message = {
      id: Date.now() + Math.random() + 1,
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isLoading: true,
      isStreaming: false
    }
    messages.value.push(assistantMessage)

    try {
      isLoading.value = true

      // Cancel any existing request
      if (currentAbortController.value) {
        currentAbortController.value.abort()
      }
      
      // Create new AbortController for this request
      currentAbortController.value = new AbortController()

      // Prepare conversation history for the API (excluding the message we just added)
      const conversationMessages = messages.value
        .slice(0, -2) // Exclude the last user message and assistant placeholder we just added
        .filter(msg => msg.content.trim()) // Only include messages with content
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      
      // Add the current user message
      conversationMessages.push({
        role: 'user',
        content: content
      })

      console.log('Conversation history being sent:', conversationMessages) // Debug log

      // Call the backend's direct_chat API endpoint
      const response = await fetch('http://localhost:8000/api/direct-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: conversationMessages
        }),
        signal: currentAbortController.value.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Check if response has a body and is readable
      if (!response.body) {
        throw new Error('No response body available for streaming')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      // Update message to start streaming
      const index = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (index !== -1) {
        const currentMessage = messages.value[index]
        if (currentMessage) {
          messages.value[index] = {
            ...currentMessage,
            isLoading: false,
            isStreaming: true
          }
        }
      }

      isLoading.value = false
      isStreaming.value = true

      let accumulatedContent = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          
          if (done) break

          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true })
          
          // Parse SSE format (data: {...})
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                // Handle different message types from backend
                if (data.type === 'content' && data.content) {
                  accumulatedContent += data.content
                  
                  // Update message content in real-time
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: accumulatedContent,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'activity') {
                  // Handle activity messages (like "Creating visualizations...")
                  accumulatedContent += `\n\n*${data.content}*\n\n`
                  
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: accumulatedContent,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'tool_output' && data.content) {
                  // Handle tool outputs (charts, tables, etc.)
                  accumulatedContent += data.content + '\n\n'
                  
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: accumulatedContent,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'status') {
                  // Handle status messages (like "Thinking...", "Creating visualization...")
                  console.log('Status:', data.content)
                } else if (data.type === 'complete') {
                  // Stream is complete
                  break
                } else if (data.type === 'error') {
                  throw new Error(data.content || 'Unknown error from backend')
                }
              } catch (parseError) {
                console.warn('Failed to parse streaming data:', parseError)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      // Mark streaming as complete
      const finalIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (finalIndex !== -1) {
        const finalMessage = messages.value[finalIndex]
        if (finalMessage) {
          messages.value[finalIndex] = {
            ...finalMessage,
            isStreaming: false
          }
        }
      }

    } catch (error) {
      // Handle aborted requests silently
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was cancelled')
        return
      }
      
      console.error('Streaming chat error:', error)
      
      // Update message with error
      const errorIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (errorIndex !== -1) {
        const errorMessage = messages.value[errorIndex]
        if (errorMessage) {
          messages.value[errorIndex] = {
            ...errorMessage,
            content: 'Sorry, I encountered an error while processing your request. Please try again.',
            isLoading: false,
            isStreaming: false,
            error: error instanceof Error ? error.message : 'Unknown error'
          }
        }
      }
    } finally {
      isLoading.value = false
      isStreaming.value = false
      currentAbortController.value = null
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  const regenerateMessage = async (messageId: string | number) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    const message = messages.value[messageIndex]
    if (!message || message.role !== 'assistant') return

    // Find the user message before this assistant message
    const userMessageIndex = messageIndex - 1
    if (userMessageIndex < 0) return

    const userMessage = messages.value[userMessageIndex]
    if (!userMessage) return
    
    // Remove the assistant message and regenerate
    messages.value.splice(messageIndex, 1)
    await sendStreamingMessage(userMessage.content)
  }

  return {
    messages,
    isLoading,
    isStreaming,
    sendMessage: sendStreamingMessage,
    clearMessages,
    regenerateMessage
  }
}
