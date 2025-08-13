// composables/useAiChatSimple.ts
// Simplified AI SDK integration for testing

import { ref } from 'vue'

export const useAiChatSimple = () => {
  const messages = ref([])
  const input = ref('')
  const isLoading = ref(false)
  const error = ref(null)
  const aiSdk = ref(null)

  // Initialize AI SDK (call this from onMounted in component)
  const initializeChat = async () => {
    if (process.server) return null // Skip on server
    
    try {
      console.log('🚀 Initializing simple AI SDK...')
      
      const { useChat } = await import('@ai-sdk/vue')
      
      if (!useChat || typeof useChat !== 'function') {
        throw new Error('useChat is not available from @ai-sdk/vue')
      }
      
      const chat = useChat({
        api: '/api/chat', // Use Nuxt API route (proxy to Python backend)
        onError: (err) => {
          console.error('❌ AI SDK Error:', err)
          error.value = err.message
        },
        onFinish: (message) => {
          console.log('✅ AI SDK Message finished:', message)
        }
      })
      
      aiSdk.value = chat
      console.log('✅ Simple AI SDK initialized successfully')
      
      return chat
      
    } catch (err) {
      console.error('💥 AI SDK init failed:', err)
      error.value = err.message
      return null
    }
  }

  return {
    messages,
    input,
    isLoading,
    error,
    aiSdk,
    initializeChat
  }
}

