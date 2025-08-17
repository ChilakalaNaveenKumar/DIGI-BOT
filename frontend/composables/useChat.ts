// Enhanced chat logic with streaming support
import type { Message } from '~/types'

export const useChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const input = ref('')
  const isStreaming = ref(false)
  
  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading.value) return
    
    // Add user message
    const userMessage: Message = {
      id: Date.now(),
      content,
      role: 'user' as const,
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    input.value = ''
    isLoading.value = true
    isStreaming.value = true
    
    // Prepare assistant message for streaming
    const assistantMessage: Message = {
      id: Date.now() + 1,
      content: '',
      role: 'assistant' as const,
      timestamp: new Date(),
      isLoading: true,
      reasoning: ''
    }
    messages.value.push(assistantMessage)
    
    try {
      // TODO: Temporarily disabled for UI/UX development - simulate response
      setTimeout(() => {
        const index = messages.value.findIndex(m => m.id === assistantMessage.id)
        if (index !== -1) {
          messages.value[index] = {
            ...assistantMessage,
            content: 'Hi there! How can I help you today?',
            isLoading: false,
            reasoning: 'The user has just said "hi" - this is a simple greeting. I should respond in a warm, natural way without being overly formal or using lists/bullet points since this is casual conversation. I\'ll keep it brief and friendly, and maybe ask how I can help them today.'
          }
          isLoading.value = false
          isStreaming.value = false
        }
      }, 1500)
      return
      
      // Call the enhanced API endpoint (disabled)
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages.value.slice(0, -1).map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          provider: 'openai',
          model: 'gpt-4',
          enableReasoning: true,
          streamMode: 'enhanced'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Handle streaming response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      
      if (!reader) {
        throw new Error('No response body')
      }

      let hasStarted = false
      
      while (true) {
        const { done, value } = await reader!.read()
        
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            
            if (data === '[DONE]') continue
            if (!data) continue
            
            try {
              const parsed = JSON.parse(data)
              
              // Handle different stream types
              switch (parsed.type) {
                case 'text-start':
                  if (!hasStarted) {
                    assistantMessage.isLoading = false
                    hasStarted = true
                  }
                  break
                  
                case 'text-delta':
                  if (parsed.delta) {
                    assistantMessage.content += parsed.delta
                  }
                  break
                  
                case 'reasoning-start':
                  // Start reasoning section
                  break
                  
                case 'reasoning-delta':
                  if (parsed.delta) {
                    assistantMessage.reasoning = (assistantMessage.reasoning || '') + parsed.delta
                  }
                  break
                  
                case 'tool_call':
                  // Handle tool calls
                  if (!assistantMessage.toolCalls) {
                    assistantMessage.toolCalls = []
                  }
                  assistantMessage.toolCalls!.push(parsed.tool_call)
                  break
                  
                case 'tool_result':
                  // Handle tool results
                  if (assistantMessage.toolCalls && assistantMessage.toolCalls!.length > 0) {
                    const toolCall = assistantMessage.toolCalls!.find(
                      tc => tc.id === parsed.tool_result.call_id
                    )
                    toolCall!.result = parsed.tool_result.content
                  }
                  break
                  
                case 'error':
                  throw new Error(parsed.errorText || 'Unknown error occurred')
                  
                case 'finish':
                  // Stream finished
                  break
              }
            } catch (parseError) {
              console.warn('Failed to parse streaming chunk:', data, parseError)
              continue
            }
          }
        }
      }
      
      // Final cleanup
      assistantMessage.isLoading = false
      
    } catch (error) {
      console.error('Chat error:', error)
      
      // Update the assistant message with error
      assistantMessage.content = 'Sorry, I encountered an error. Please try again.'
      assistantMessage.isLoading = false
      assistantMessage.error = error instanceof Error ? error.message : String(error)
    } finally {
      isLoading.value = false
      isStreaming.value = false
    }
  }
  
  const clearMessages = () => {
    messages.value = []
  }
  
  return {
    messages,
    isLoading: readonly(isLoading),
    isStreaming: readonly(isStreaming),
    input,
    sendMessage,
    clearMessages
  }
}
