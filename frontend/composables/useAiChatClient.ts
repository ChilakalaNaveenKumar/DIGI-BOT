import { ref, onMounted, watch, nextTick } from 'vue'

export const useAiChatClient = () => {
  // SSR-safe reactive refs
  const messages = ref([])
  const input = ref('')
  const isLoading = ref(false)
  const error = ref(null)
  const mounted = ref(false)
  const selectedProvider = ref('openai')
  
  // AI SDK functions (will be populated on client)
  let chatInstance = null

  // Only initialize AI SDK on client side
  onMounted(async () => {
    try {
      console.log('🚀 Initializing AI SDK...')
      
      // Dynamic import to avoid SSR issues
      const { useChat } = await import('@ai-sdk/vue')
      
      if (!useChat || typeof useChat !== 'function') {
        throw new Error('useChat is not available from @ai-sdk/vue')
      }
      
      // Initialize AI SDK chat with correct configuration
      chatInstance = useChat({
        // Use Nuxt API route, not external backend
        api: '/api/chat',
        
        // Correct way to send additional data
        body: {
          provider: selectedProvider.value
        },
        
        // Error handling
        onError: (chatError) => {
          console.error('❌ AI SDK Chat error:', chatError)
          error.value = chatError.message || 'Chat error occurred'
        },
        
        // Success callback
        onFinish: (message) => {
          console.log('✅ AI SDK Chat finished:', message)
        }
      })
      
      console.log('✅ AI SDK chat instance created:', chatInstance)
      
      // Wait for next tick to ensure everything is initialized
      await nextTick()
      
      // Sync AI SDK state with our reactive refs
      if (chatInstance.messages?.value) {
        messages.value = chatInstance.messages.value
      }
      if (chatInstance.input?.value !== undefined) {
        input.value = chatInstance.input.value
      }
      if (chatInstance.isLoading?.value !== undefined) {
        isLoading.value = chatInstance.isLoading.value
      }
      
      // Set up watchers AFTER chatInstance is ready
      if (chatInstance.messages) {
        watch(chatInstance.messages, (newMessages) => {
          console.log('📨 Messages updated:', newMessages)
          messages.value = newMessages
        }, { deep: true, immediate: true })
      }
      
      if (chatInstance.input) {
        watch(chatInstance.input, (newInput) => {
          input.value = newInput
        }, { immediate: true })
        
        // Bi-directional sync for input
        watch(input, (newInput) => {
          if (chatInstance.input.value !== newInput) {
            chatInstance.input.value = newInput
          }
        })
      }
      
      if (chatInstance.isLoading) {
        watch(chatInstance.isLoading, (newLoading) => {
          isLoading.value = newLoading
        }, { immediate: true })
      }
      
      if (chatInstance.error) {
        watch(chatInstance.error, (newError) => {
          error.value = newError?.message || newError
        }, { immediate: true })
      }
      
      mounted.value = true
      console.log('🎉 AI SDK initialization complete!')
      
    } catch (err) {
      console.error('💥 Failed to initialize AI SDK:', err)
      error.value = `Failed to initialize AI SDK: ${err.message}`
      mounted.value = true // Still set to true so UI can show error
    }
  })

  // Wrapper functions with error handling
  const reload = () => {
    if (chatInstance?.reload) {
      return chatInstance.reload()
    } else {
      console.warn('⚠️ AI SDK not ready, cannot reload')
    }
  }

  const stop = () => {
    if (chatInstance?.stop) {
      return chatInstance.stop()
    } else {
      console.warn('⚠️ AI SDK not ready, cannot stop')
    }
  }

  const append = (message) => {
    if (chatInstance?.append) {
      return chatInstance.append(message)
    } else {
      console.warn('⚠️ AI SDK not ready, cannot append')
    }
  }

  const handleSubmit = (e) => {
    if (e) e.preventDefault()
    
    if (chatInstance?.handleSubmit) {
      return chatInstance.handleSubmit(e)
    } else {
      console.warn('⚠️ AI SDK not ready, cannot submit')
    }
  }

  const sendMessage = async (content) => {
    if (!content?.trim()) return
    
    if (chatInstance?.append) {
      return chatInstance.append({
        role: 'user',
        content: content.trim()
      })
    } else {
      console.warn('⚠️ AI SDK not ready, cannot send message')
    }
  }

  return {
    messages,
    input,
    isLoading,
    error,
    mounted,
    selectedProvider,
    reload,
    stop,
    append,
    handleSubmit,
    sendMessage
  }
}
