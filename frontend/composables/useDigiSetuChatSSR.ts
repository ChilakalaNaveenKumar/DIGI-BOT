// composables/useDigiSetuChatSSR.ts
// SSR-safe AI SDK 5 composable with enhanced features

import { ref, computed, watch, onMounted, nextTick } from 'vue'

export const useDigiSetuChatSSR = () => {
  // Provider and model management
  const selectedProvider = ref('openai')
  const selectedModel = ref('')
  const uploadedFiles = ref([])
  
  // SSR-safe state
  const messages = ref([])
  const isLoading = ref(false)
  const chatError = ref(null)
  const isThinking = ref(false)
  const currentThought = ref('')
  const input = ref('')
  
  // Chat instance (client-only)
  const chat = ref(null)
  const isInitialized = ref(false)
  const interactiveTools = ref(null)
  
  // Provider options
  const providers = [
    { 
      id: 'openai', 
      name: 'GPT-5', 
      icon: 'openai',
      models: ['gpt-5', 'gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini'],
      description: '1M context, 64k output',
      reasoning: true
    },
    { 
      id: 'anthropic', 
      name: 'Claude 4 Opus', 
      icon: 'claude',
      models: ['claude-opus-4-20250514', 'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022'],
      description: '1M context, 200k output',
      reasoning: true
    },
    { 
      id: 'grok', 
      name: 'Grok-4', 
      icon: 'xai',
      models: ['grok-4', 'grok-4-vision', 'grok-2-1212'],
      description: '256k context, 256k output',
      reasoning: false
    }
  ]

  // Initialize chat system (no longer using AI SDK Chat class)
  const initializeChat = async () => {
    if (process.client && !isInitialized.value) {
      try {
        const { tool } = await import('ai')
        
        // Initialize tools on client side
        interactiveTools.value = {
          createTable: tool({
            description: 'Create an interactive data table from information',
            parameters: {
              type: 'object',
              properties: {
                title: { type: 'string', description: 'Table title' },
                headers: { type: 'array', items: { type: 'string' }, description: 'Column headers' },
                rows: { type: 'array', description: 'Table data rows' },
                sortable: { type: 'boolean', description: 'Enable sorting' },
                searchable: { type: 'boolean', description: 'Enable search' }
              },
              required: ['title', 'headers', 'rows']
            }
          }),
          
          createQuiz: tool({
            description: 'Create an interactive quiz from content',
            parameters: {
              type: 'object',
              properties: {
                title: { type: 'string', description: 'Quiz title' },
                questions: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      question: { type: 'string' },
                      options: { type: 'array', items: { type: 'string' } },
                      correct: { type: 'number' },
                      explanation: { type: 'string' }
                    }
                  }
                }
              },
              required: ['title', 'questions']
            }
          }),
          
          createChart: tool({
            description: 'Create an interactive chart from data',
            parameters: {
              type: 'object',
              properties: {
                title: { type: 'string', description: 'Chart title' },
                type: { type: 'string', enum: ['bar', 'line', 'pie', 'scatter'], description: 'Chart type' },
                data: { type: 'array', description: 'Chart data points' },
                xAxis: { type: 'string', description: 'X-axis label' },
                yAxis: { type: 'string', description: 'Y-axis label' }
              },
              required: ['title', 'type', 'data']
            }
          }),
          
          createFlashcards: tool({
            description: 'Create interactive flashcards for learning',
            parameters: {
              type: 'object',
              properties: {
                title: { type: 'string', description: 'Flashcard set title' },
                cards: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      front: { type: 'string' },
                      back: { type: 'string' },
                      category: { type: 'string' }
                    }
                  }
                }
              },
              required: ['title', 'cards']
            }
          })
        }
        
        // Direct streaming approach - no Chat class needed
        console.log('🚀 Direct streaming chat initialized')
        
        isInitialized.value = true
        console.log('🚀 AI SDK 5 Chat initialized')
        
      } catch (error) {
        console.error('Failed to initialize Chat:', error)
        chatError.value = 'Failed to initialize chat system'
      }
    }
  }

  // Enhanced message processing
  const enhancedMessages = computed(() => {
    if (!messages.value || !Array.isArray(messages.value)) {
      return []
    }
    return messages.value.map(message => {
      const hasReasoning = message.parts?.some(part => part.type === 'reasoning')
      const hasTools = message.parts?.some(part => part.type?.startsWith('tool-'))
      const hasFiles = message.parts?.some(part => part.type === 'file')
      
      return {
        ...message,
        hasReasoning,
        hasTools,
        hasFiles,
        reasoning: message.parts?.filter(part => part.type === 'reasoning') || [],
        tools: message.parts?.filter(part => part.type?.startsWith('tool-')) || [],
        files: message.parts?.filter(part => part.type === 'file') || []
      }
    })
  })

  // Provider management
  const changeProvider = (newProvider) => {
    selectedProvider.value = newProvider
    const provider = providers.find(p => p.id === newProvider)
    if (provider && provider.models.length > 0) {
      selectedModel.value = provider.models[0]
    }
    console.log('🔄 Provider changed:', newProvider)
  }

  const changeModel = (newModel) => {
    selectedModel.value = newModel
    console.log('🔄 Model changed:', newModel)
  }

  // File upload handling
  const handleFileUpload = async (files) => {
    try {
      if (process.client) {
        const { convertFileListToFileUIParts } = await import('ai')
        const fileUIParts = await convertFileListToFileUIParts(files)
        uploadedFiles.value = [...uploadedFiles.value, ...fileUIParts]
        console.log('📁 Files processed:', fileUIParts.length)
        return fileUIParts
      }
      return []
    } catch (error) {
      console.error('File upload error:', error)
      chatError.value = `File upload failed: ${error.message}`
      return []
    }
  }

  const removeFile = (index) => {
    uploadedFiles.value.splice(index, 1)
  }

  const clearFiles = () => {
    uploadedFiles.value = []
  }

  // Enhanced message sending
  const sendMessage = async (content, options = {}) => {
    if (!isInitialized.value) {
      console.warn('Chat not initialized yet')
      return
    }
    
    try {
      chatError.value = null
      isLoading.value = true
      isThinking.value = true
      
      // Add user message immediately
      const userMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: content,
        parts: [{ type: 'text', text: content }],
        createdAt: new Date().toISOString()
      }
      messages.value.push(userMessage)
      
      // Prepare assistant message
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        parts: [{ type: 'text', text: '' }],
        createdAt: new Date().toISOString()
      }
      messages.value.push(assistantMessage)
      
      // Process files if provided
      let filesToSend = uploadedFiles.value
      if (options.files) {
        const newFiles = await handleFileUpload(options.files)
        filesToSend = [...filesToSend, ...newFiles]
      }

      // Direct fetch to backend (bypass AI SDK Chat class)
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages.value.slice(0, -1).map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          provider: selectedProvider.value,
          model: selectedModel.value,
          enableReasoning: options.enableReasoning ?? true,
          files: filesToSend
        })
      })

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`)
      }

      // Process streaming response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      
      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.trim().startsWith('data: ')) {
              const data = line.trim().slice(6)
              console.log('📦 Received chunk:', data)
              
              if (data === '[DONE]') {
                console.log('✅ Stream completed')
                continue
              }
              
              try {
                const parsed = JSON.parse(data)
                console.log('🔍 Parsed data:', parsed)
                
                if (parsed.content !== undefined) {
                  // Update the last assistant message
                  const lastMessage = messages.value[messages.value.length - 1]
                  if (lastMessage && lastMessage.role === 'assistant') {
                    lastMessage.content += parsed.content
                    // Also update the parts array for compatibility
                    if (lastMessage.parts && lastMessage.parts[0]) {
                      lastMessage.parts[0].text = lastMessage.content
                    }
                    console.log('💬 Updated message content:', lastMessage.content)
                    // Trigger reactivity and scroll
                    nextTick(() => scrollToBottom())
                  }
                }
                if (parsed.reasoning) {
                  currentThought.value = parsed.reasoning
                  isThinking.value = true
                  console.log('🤔 Updated reasoning:', parsed.reasoning)
                }
                if (parsed.error) {
                  throw new Error(parsed.error)
                }
              } catch (parseError) {
                console.warn('❌ Parse error for line:', line, parseError)
              }
            }
          }
        }
      }

      // Clear uploaded files after sending
      clearFiles()
      isLoading.value = false
      isThinking.value = false
      
      // Final scroll to bottom
      nextTick(() => scrollToBottom())
      
    } catch (error) {
      console.error('Send message error:', error)
      chatError.value = error.message
      isLoading.value = false
      isThinking.value = false
    }
  }

  // Enhanced regeneration
  const regenerateMessage = async (messageId) => {
    if (!chat.value) return
    
    try {
      chatError.value = null
      isLoading.value = true
      await chat.value.regenerate({ 
        messageId,
        body: {
          provider: selectedProvider.value,
          model: selectedModel.value,
          enableReasoning: true
        }
      })
    } catch (error) {
      console.error('Regenerate error:', error)
      chatError.value = error.message
      isLoading.value = false
    }
  }

  // Chat management
  const clearChat = () => {
    if (chat.value) {
      chat.value.messages = []
    }
    messages.value = []
    clearFiles()
    chatError.value = null
    currentThought.value = ''
    isThinking.value = false
    isLoading.value = false
  }

  const stopGeneration = async () => {
    try {
      isLoading.value = false
      isThinking.value = false
      // Note: Direct fetch doesn't support stop, but we can set loading states
    } catch (error) {
      console.error('Stop generation error:', error)
    }
  }

  // Export functionality
  const exportChat = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      provider: selectedProvider.value,
      model: selectedModel.value,
      messages: (messages.value || []).map(msg => ({
        role: msg?.role || 'user',
        content: msg.parts?.filter(part => part && part.type === 'text').map(part => part.text || '').join('') || msg?.content || '',
        reasoning: msg.parts?.filter(part => part && part.type === 'reasoning').map(part => part.text || '').join('') || '',
        timestamp: msg?.createdAt || new Date().toISOString()
      }))
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `digi-setu-chat-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Utility functions
  const scrollToBottom = () => {
    setTimeout(() => {
      const container = document.querySelector('[data-messages-container]')
      if (container) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth'
        })
      }
    }, 100)
  }

  // Clear error function
  const clearError = () => {
    chatError.value = null
    isLoading.value = false
    isThinking.value = false
  }

  // Initialize on mount (client-side only)
  onMounted(() => {
    initializeChat()
  })

  return {
    // Chat instance and state
    chat: computed(() => null), // No longer using Chat class
    isInitialized,
    
    // Enhanced messages
    messages: enhancedMessages,
    
    // State
    isLoading,
    status: computed(() => isLoading.value ? 'streaming' : 'ready'),
    error: chatError,
    isThinking,
    currentThought,
    input,
    
    // Provider management
    selectedProvider,
    selectedModel,
    providers,
    changeProvider,
    changeModel,
    
    // File management
    uploadedFiles,
    handleFileUpload,
    removeFile,
    clearFiles,
    
    // Message operations
    sendMessage,
    regenerateMessage,
    
    // Chat controls
    clearChat,
    stopGeneration,
    exportChat,
    
    // Tools
    interactiveTools: computed(() => interactiveTools?.value || null),
    
    // Utilities
    scrollToBottom,
    initializeChat,
    clearError
  }
}

// Helper functions for message processing
export const extractTextFromMessage = (message) => {
  if (!message) return ''
  if (!message.parts && message.content) return message.content
  if (!message.parts || !Array.isArray(message.parts)) return ''
  
  return message.parts
    .filter(part => part && part.type === 'text')
    .map(part => part.text || '')
    .join('')
}

export const extractReasoningFromMessage = (message) => {
  if (!message || !message.parts || !Array.isArray(message.parts)) return ''
  
  return message.parts
    .filter(part => part && part.type === 'reasoning')
    .map(part => part.text || '')
    .join('')
}

export const getToolCallsFromMessage = (message) => {
  if (!message || !message.parts || !Array.isArray(message.parts)) return []
  
  return message.parts.filter(part => 
    part && part.type?.startsWith('tool-')
  )
}
