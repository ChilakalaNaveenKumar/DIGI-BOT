import type { Message, ReasoningStep } from '~/types'

export const useStreamingChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isStreaming = ref(false)
  
  // Conversation state
  const conversationId = ref<number | null>(null)
  const conversationTitle = ref<string>('')
  
  // Reasoning state
  const currentReasoningSteps = ref<ReasoningStep[]>([])
  const isReasoning = ref(false)
  
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

      // Immediately show "thinking" state
      const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (messageIndex !== -1) {
        const currentMessage = messages.value[messageIndex]
        if (currentMessage) {
          messages.value[messageIndex] = {
            ...currentMessage,
            content: '*Thinking...*',
            isLoading: true,
            isStreaming: false
          }
        }
      }

      // Cancel any existing request
      if (currentAbortController.value) {
        currentAbortController.value.abort()
      }
      
      // Create new AbortController for this request
      currentAbortController.value = new AbortController()

      console.log('Sending message to stream API:', content) // Debug log

      // Call the backend's stream API endpoint (cookies will be sent automatically)
      const response = await fetch('http://localhost:8000/api/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          messages: [{ role: 'user', content: content }], // Send just the current message
          conversation_id: conversationId.value,
          model: "claude-sonnet-4-20250514",
          enable_thinking: true,
          thinking_budget: 5000,
          enable_web_search: true,
          temperature: 0.7
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
                
                // Handle different message types from Anthropic stream API
                if (data.type === 'thinking_start') {
                  // Start thinking mode
                  isReasoning.value = true
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: '*Thinking...*',
                        isLoading: false,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'thinking_delta') {
                  // Handle thinking content - add to reasoning steps
                  if (data.text) {
                    // Check if this is a continuation of existing reasoning or new step
                    const lastStep = currentReasoningSteps.value[currentReasoningSteps.value.length - 1]
                    
                    if (lastStep && lastStep.status === 'active') {
                      // Continue existing reasoning step
                      lastStep.content += data.text
                      lastStep.timestamp = new Date()
                    } else {
                      // Create new reasoning step
                      const stepId = `thinking-${Date.now()}-${Math.random()}`
                      const reasoningStep: ReasoningStep = {
                        id: stepId,
                        type: 'thinking',
                        content: data.text,
                        status: 'active',
                        timestamp: new Date()
                      }
                      currentReasoningSteps.value.push(reasoningStep)
                    }
                    
                    // Update the assistant message with reasoning steps
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      const currentMessage = messages.value[messageIndex]
                      if (currentMessage) {
                        messages.value[messageIndex] = {
                          ...currentMessage,
                          reasoningSteps: [...currentReasoningSteps.value],
                          isLoading: false,
                          isStreaming: true
                        }
                      }
                    }
                  }
                } else if (data.type === 'thinking_stop') {
                  // Stop thinking mode and mark reasoning steps as completed
                  isReasoning.value = false
                  
                  // Mark all active reasoning steps as completed
                  currentReasoningSteps.value.forEach(step => {
                    if (step.status === 'active') {
                      step.status = 'completed'
                    }
                  })
                  
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: '',
                        reasoningSteps: [...currentReasoningSteps.value],
                        isLoading: false,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'content_block_start') {
                  // Content block started
                  console.log('Content block started')
                } else if (data.type === 'content_block_delta') {
                  // Handle actual content streaming
                  if (data.delta && data.delta.type === 'text_delta' && data.delta.text) {
                    accumulatedContent += data.delta.text
                    
                    // Update message content in real-time
                    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                    if (messageIndex !== -1) {
                      const currentMessage = messages.value[messageIndex]
                      if (currentMessage) {
                        messages.value[messageIndex] = {
                          ...currentMessage,
                          content: accumulatedContent,
                          isLoading: false,
                          isStreaming: true
                        }
                      }
                    }
                  }
                } else if (data.type === 'message_stop') {
                  // Message completed
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: accumulatedContent,
                        isLoading: false,
                        isStreaming: false
                      }
                    }
                  }
                  isStreaming.value = false
                  break
                } else if (data.type === 'metadata') {
                  // Handle conversation metadata
                  if (data.conversation_id) {
                    conversationId.value = data.conversation_id
                  }
                  if (data.title) {
                    conversationTitle.value = data.title
                  }
                } else if (data.type === 'activity') {
                  // Handle activity messages (like "Creating visualizations...")
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        content: `*${data.content}*`,
                        isLoading: true,
                        isStreaming: false
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
                } else if (data.type === 'reasoning') {
                  // Handle reasoning/thinking steps - can happen anywhere during conversation
                  isReasoning.value = true
                  
                  // Check if this is a continuation of existing reasoning or new step
                  const lastStep = currentReasoningSteps.value[currentReasoningSteps.value.length - 1]
                  
                  if (lastStep && lastStep.status === 'active') {
                    // Continue existing reasoning step
                    lastStep.content += data.content || ''
                    lastStep.timestamp = new Date()
                  } else {
                    // Create new reasoning step
                    const stepId = `reasoning-${Date.now()}-${Math.random()}`
                    const reasoningStep: ReasoningStep = {
                      id: stepId,
                      type: 'thinking',
                      content: data.content || '',
                      status: 'active',
                      timestamp: new Date()
                    }
                    currentReasoningSteps.value.push(reasoningStep)
                  }
                  
                  // Update the assistant message with reasoning steps
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        reasoningSteps: [...currentReasoningSteps.value],
                        isLoading: false,
                        isStreaming: true
                      }
                    }
                  }
                } else if (data.type === 'conversation_created') {
                  // Handle conversation creation (first message only)
                  conversationId.value = data.conversation_id
                  conversationTitle.value = data.title
                  console.log('Conversation created:', data.conversation_id, data.title)
                } else if (data.type === 'status') {
                  // Handle status messages (like "Thinking...", "Creating visualization...")
                  console.log('Status:', data.content)
                } else if (data.type === 'complete') {
                  // Stream is complete
                  isReasoning.value = false
                  
                  // Mark all reasoning steps as completed
                  currentReasoningSteps.value = currentReasoningSteps.value.map(step => ({
                    ...step,
                    status: 'completed' as const
                  }))
                  
                  // Update the assistant message with final reasoning steps
                  const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
                  if (messageIndex !== -1) {
                    const currentMessage = messages.value[messageIndex]
                    if (currentMessage) {
                      messages.value[messageIndex] = {
                        ...currentMessage,
                        reasoningSteps: [...currentReasoningSteps.value]
                      }
                    }
                  }
                  
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
    conversationId.value = null
    conversationTitle.value = ''
  }
  
  const startNewConversation = () => {
    clearMessages()
    conversationId.value = null
    conversationTitle.value = ''
    currentReasoningSteps.value = []
    isReasoning.value = false
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
    conversationId: readonly(conversationId),
    conversationTitle: readonly(conversationTitle),
    currentReasoningSteps: readonly(currentReasoningSteps),
    isReasoning: readonly(isReasoning),
    sendMessage: sendStreamingMessage,
    clearMessages,
    startNewConversation,
    regenerateMessage
  }
}
