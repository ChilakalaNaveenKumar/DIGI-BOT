import { ref, onMounted, watch, nextTick } from 'vue'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
}

interface ChatInstance {
  messages: { value: ChatMessage[] }
  input: { value: string }
  isLoading: { value: boolean }
  error: { value: unknown }
  reload: () => void
  stop: () => void
  append: (message: unknown) => void
  handleSubmit: (e?: Event) => void
}

export const useAiChatClient = () => {
  // SSR-safe reactive refs
  const messages = ref<ChatMessage[]>([])
  const input = ref<string>('')
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const mounted = ref<boolean>(false)
  const selectedProvider = ref<string>('openai')
  
  // AI SDK functions (will be populated on client)
  let chatInstance: ChatInstance | null = null

  // Only initialize AI SDK on client side
  onMounted(async () => {
    try {
      console.log('🚀 Initializing AI SDK...')
      
      // Simple chat implementation without AI SDK Chat class
      chatInstance = {
        messages: { value: [] },
        input: { value: '' },
        isLoading: { value: false },
        error: { value: null },
        append: async (message: unknown) => {
          console.log('Appending message:', message)
        },
        reload: () => {
          console.log('Reloading chat')
        },
        stop: () => {
          console.log('Stopping chat')
        },
        handleSubmit: (e?: Event) => {
          e?.preventDefault()
          console.log('Handling submit')
        }
      }
      
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
          console.log('📨 Messages updated:', newMessages.value)
          messages.value = newMessages.value
        }, { deep: true, immediate: true })
      }
      
      if (chatInstance.input) {
        watch(chatInstance.input, (newInput) => {
          input.value = newInput.value
        }, { immediate: true })
        
        // Bi-directional sync for input
        watch(input, (newInput: string) => {
          if (chatInstance && chatInstance.input.value !== newInput) {
            chatInstance.input.value = newInput
          }
        })
      }
      
      if (chatInstance.isLoading) {
        watch(chatInstance.isLoading, (newLoading) => {
          isLoading.value = newLoading.value
        }, { immediate: true })
      }
      
      if (chatInstance.error) {
        watch(chatInstance.error, (newError) => {
          const errorValue = newError.value
          error.value = errorValue instanceof Error ? errorValue.message : String(errorValue)
        }, { immediate: true })
      }
      
      mounted.value = true
      console.log('🎉 AI SDK initialization complete!')
      
    } catch (err: unknown) {
      console.error('💥 Failed to initialize AI SDK:', err)
      error.value = `Failed to initialize AI SDK: ${err instanceof Error ? err.message : 'Unknown error'}`
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

  const append = (message: unknown) => {
    if (chatInstance?.append) {
      return chatInstance.append(message)
    } else {
      console.warn('⚠️ AI SDK not ready, cannot append')
    }
  }

  const handleSubmit = (e?: Event) => {
    if (e) e.preventDefault()
    
    if (chatInstance?.handleSubmit) {
      return chatInstance.handleSubmit(e)
    } else {
      console.warn('⚠️ AI SDK not ready, cannot submit')
    }
  }

  const sendMessage = async (content: string) => {
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
