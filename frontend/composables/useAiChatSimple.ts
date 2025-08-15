// composables/useAiChatSimple.ts
// Simplified AI SDK integration for testing

import { ref } from 'vue'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
}

export const useAiChatSimple = () => {
  const messages = ref<ChatMessage[]>([])
  const input = ref<string>('')
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const aiSdk = ref<unknown>(null)

  // Initialize AI SDK (call this from onMounted in component)
  const initializeChat = async () => {
    if (import.meta.server) return null // Skip on server
    
    try {
      
      // Simple chat implementation without AI SDK Chat class
      const chat = {
        messages: [],
        api: '/api/chat',
        append: async (message: { role: string; content: string }) => {
          // Implementation would go here
          console.log('Appending message:', message)
        }
      }
      
      aiSdk.value = chat
      
      return chat
      
    } catch (err: unknown) {
      console.error('💥 AI SDK init failed:', err)
      error.value = err instanceof Error ? err.message : 'Initialization failed'
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

