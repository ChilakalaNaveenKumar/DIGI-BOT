import { ref, computed, nextTick } from 'vue'

export interface Message {
  id: string | number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isLoading?: boolean
  isStreaming?: boolean
  error?: string
  components?: any[]
  metadata?: {
    conversationId?: number
    title?: string
    componentMatcherResults?: any[]
  }
}

export interface ComponentMatcherResult {
  type: string
  title: string
  position: number
  action: 'insert' | 'update'
  data: any
  rawContent: string
}

export const useEnhancedStreamingChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isStreaming = ref(false)
  const isProcessingComponents = ref(false)
  const conversationId = ref<number | null>(null)
  const conversationTitle = ref<string>('Untitled')
  
  let currentAbortController: AbortController | null = null

  /**
   * Send a streaming message with enhanced component matching
   */
  const sendStreamingMessage = async (content: string) => {
    if (!content.trim() || isLoading.value || isStreaming.value) return

    // Create user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    // Create assistant message placeholder
    const assistantMessage: Message = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
      isStreaming: false,
      components: [],
      metadata: {}
    }

    messages.value.push(userMessage, assistantMessage)

    try {
      isLoading.value = true
      isStreaming.value = true

      // Show thinking state
      const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (messageIndex !== -1) {
        messages.value[messageIndex] = {
          ...messages.value[messageIndex],
          content: '*Thinking...*',
          isLoading: true,
          isStreaming: false
        }
      }

      // Cancel any existing request
      if (currentAbortController) {
        currentAbortController.abort()
      }
      
      currentAbortController = new AbortController()

      // Prepare conversation history
      const conversationMessages = messages.value
        .slice(0, -2) // Exclude the messages we just added
        .filter(msg => msg.content.trim())
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      
      conversationMessages.push({
        role: 'user',
        content: content
      })

      console.log('Enhanced streaming request:', {
        messages: conversationMessages,
        conversationId: conversationId.value,
        enableComponentMatching: true
      })

      // Call the enhanced streaming API
      const response = await fetch('http://localhost:8000/api/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: conversationMessages,
          conversation_id: conversationId.value,
          user_id: 1, // TODO: Get from auth store
          model: "claude-sonnet-4-20250514",
          enable_thinking: true,
          thinking_budget: 5000,
          enable_web_search: true,
          temperature: 0.7
        }),
        signal: currentAbortController.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Process streaming response
      await processStreamingResponse(response, assistantMessage.id)

    } catch (error: any) {
      console.error('Streaming error:', error)
      
      if (error.name !== 'AbortError') {
        const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
        if (messageIndex !== -1) {
          messages.value[messageIndex] = {
            ...messages.value[messageIndex],
            content: '',
            error: `Error: ${error.message}`,
            isLoading: false,
            isStreaming: false
          }
        }
      }
    } finally {
      isLoading.value = false
      isStreaming.value = false
      currentAbortController = null
    }
  }

  /**
   * Process streaming response with component matching integration
   */
  const processStreamingResponse = async (response: Response, messageId: string | number) => {
    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let assistantContent = ''
    let isInThinking = false
    let componentMatcherResults: ComponentMatcherResult[] = []

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              // Handle different event types
              switch (data.type) {
                case 'thinking_start':
                  isInThinking = true
                  updateMessage(messageId, {
                    content: '*Thinking...*',
                    isLoading: false,
                    isStreaming: true
                  })
                  break

                case 'thinking_delta':
                  // Don't show thinking content to user, just indicate thinking
                  break

                case 'thinking_stop':
                  isInThinking = false
                  updateMessage(messageId, {
                    content: '',
                    isStreaming: true
                  })
                  break

                case 'content_block_start':
                  if (!isInThinking) {
                    updateMessage(messageId, {
                      content: assistantContent,
                      isStreaming: true
                    })
                  }
                  break

                case 'content_block_delta':
                  if (!isInThinking && data.delta?.type === 'text_delta') {
                    assistantContent += data.delta.text || ''
                    updateMessage(messageId, {
                      content: assistantContent,
                      isStreaming: true
                    })
                  }
                  break

                case 'message_stop':
                  // Stream completed, now process with component matcher
                  await processWithComponentMatcher(assistantContent, messageId)
                  break

                case 'metadata':
                  // Handle conversation metadata
                  if (data.conversation_id) {
                    conversationId.value = data.conversation_id
                  }
                  if (data.title) {
                    conversationTitle.value = data.title
                  }
                  updateMessage(messageId, {
                    metadata: {
                      conversationId: data.conversation_id,
                      title: data.title
                    }
                  })
                  break

                case 'activity':
                  // Show activity status
                  console.log('Activity:', data.content)
                  break

                case 'error':
                  throw new Error(data.content || 'Streaming error')

                case 'completion':
                  updateMessage(messageId, {
                    isStreaming: false
                  })
                  break
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
  }

  /**
   * Process content with component matcher
   */
  const processWithComponentMatcher = async (content: string, messageId: string | number) => {
    if (!content.trim()) return

    try {
      isProcessingComponents.value = true
      
      console.log('Processing with component matcher:', content.substring(0, 100) + '...')

      // Call component matcher API
      const response = await fetch('http://localhost:8000/api/component-matcher/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content
        })
      })

      if (response.ok) {
        // Process component matcher streaming response
        const reader = response.body?.getReader()
        if (reader) {
          const decoder = new TextDecoder()
          let componentContent = ''

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n')

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  
                  if (data.type === 'content' && data.content !== 'NO_MATCH') {
                    componentContent += data.content
                  }
                } catch (parseError) {
                  console.warn('Failed to parse component matcher data:', parseError)
                }
              }
            }
          }

          // If we got component content, integrate it with the message
          if (componentContent.trim() && componentContent !== 'NO_MATCH') {
            const enhancedContent = integrateComponentsWithContent(content, componentContent)
            updateMessage(messageId, {
              content: enhancedContent,
              metadata: {
                componentMatcherResults: [componentContent]
              }
            })
          } else {
            // No components found, just update with original content
            updateMessage(messageId, {
              content: content
            })
          }

          reader.releaseLock()
        }
      } else {
        // Component matcher failed, use original content
        console.warn('Component matcher failed:', response.status)
        updateMessage(messageId, {
          content: content
        })
      }
    } catch (error) {
      console.error('Component matcher error:', error)
      // Fallback to original content
      updateMessage(messageId, {
        content: content
      })
    } finally {
      isProcessingComponents.value = false
    }
  }

  /**
   * Integrate component matcher results with content
   */
  const integrateComponentsWithContent = (originalContent: string, componentContent: string): string => {
    // Parse component blocks from component matcher response
    const componentRegex = /:::([\w-]+)(?:\n)([\s\S]*?)(?:\n):::/g
    const components: ComponentMatcherResult[] = []
    let match

    while ((match = componentRegex.exec(componentContent)) !== null) {
      const componentType = match[1]
      const componentBody = match[2]
      const fullMatch = match[0]

      try {
        const component: Partial<ComponentMatcherResult> = {
          type: componentType,
          rawContent: fullMatch
        }

        // Parse component properties
        const lines = componentBody.split('\n')
        for (const line of lines) {
          const trimmedLine = line.trim()
          if (trimmedLine.startsWith('title:')) {
            component.title = trimmedLine.replace('title:', '').trim()
          } else if (trimmedLine.startsWith('position:')) {
            component.position = parseInt(trimmedLine.replace('position:', '').trim())
          } else if (trimmedLine.startsWith('action:')) {
            component.action = trimmedLine.replace('action:', '').trim() as 'insert' | 'update'
          } else if (trimmedLine.startsWith('data:')) {
            const dataStartIndex = componentBody.indexOf('data:')
            const dataContent = componentBody.substring(dataStartIndex + 5).trim()
            try {
              component.data = JSON.parse(dataContent)
            } catch (e) {
              console.warn('Failed to parse component data:', e)
              component.data = null
            }
          }
        }

        if (component.type && component.position !== undefined && component.action) {
          components.push(component as ComponentMatcherResult)
        }
      } catch (error) {
        console.error('Error parsing component:', error)
      }
    }

    // Sort components by position and integrate them
    components.sort((a, b) => a.position - b.position)

    let enhancedContent = originalContent
    let offset = 0

    for (const component of components) {
      const insertPosition = component.position + offset
      
      if (component.action === 'insert') {
        // Insert component at specified position
        const before = enhancedContent.slice(0, insertPosition)
        const after = enhancedContent.slice(insertPosition)
        enhancedContent = before + '\n\n' + component.rawContent + '\n\n' + after
        offset += component.rawContent.length + 4 // Account for added newlines
      }
      // TODO: Handle 'update' action with start/end positions
    }

    return enhancedContent
  }

  /**
   * Update a specific message
   */
  const updateMessage = (messageId: string | number, updates: Partial<Message>) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex !== -1) {
      messages.value[messageIndex] = {
        ...messages.value[messageIndex],
        ...updates
      }
    }
  }

  /**
   * Start a new conversation
   */
  const startNewConversation = () => {
    messages.value = []
    conversationId.value = null
    conversationTitle.value = 'Untitled'
    
    if (currentAbortController) {
      currentAbortController.abort()
      currentAbortController = null
    }
    
    isLoading.value = false
    isStreaming.value = false
    isProcessingComponents.value = false
  }

  /**
   * Regenerate the last assistant message
   */
  const regenerateMessage = async (messageId: string | number) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    // Find the user message that preceded this assistant message
    const userMessageIndex = messageIndex - 1
    if (userMessageIndex < 0 || messages.value[userMessageIndex].role !== 'user') return

    const userContent = messages.value[userMessageIndex].content

    // Remove the assistant message and any messages after it
    messages.value = messages.value.slice(0, messageIndex)

    // Resend the user message
    await sendStreamingMessage(userContent)
  }

  return {
    // State
    messages: computed(() => messages.value),
    isLoading: computed(() => isLoading.value),
    isStreaming: computed(() => isStreaming.value),
    isProcessingComponents: computed(() => isProcessingComponents.value),
    conversationId: computed(() => conversationId.value),
    conversationTitle: computed(() => conversationTitle.value),

    // Methods
    sendMessage: sendStreamingMessage,
    startNewConversation,
    regenerateMessage
  }
}
