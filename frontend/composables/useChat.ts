// Simple chat logic
import type { Message } from '~/types'

export const useChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const input = ref('')
  
  const sendMessage = async (content: string) => {
    if (!content.trim()) return
    
    // Add user message
    messages.value.push({
      id: Date.now(),
      content,
      role: 'user' as const,
      timestamp: new Date()
    })
    
    input.value = ''
    isLoading.value = true
    
    try {
      // TODO: Implement actual chat API call
      // Placeholder response
      setTimeout(() => {
        messages.value.push({
          id: Date.now() + 1,
          content: 'This is a placeholder response. Chat functionality will be implemented here.',
          role: 'assistant' as const,
          timestamp: new Date()
        })
        isLoading.value = false
      }, 1000)
    } catch (error) {
      console.error('Chat error:', error)
      isLoading.value = false
    }
  }
  
  return {
    messages: readonly(messages),
    isLoading: readonly(isLoading),
    input,
    sendMessage
  }
}
