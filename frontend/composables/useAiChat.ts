import { ref } from 'vue'

export const useAiChat = () => {
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const selectedProvider = ref('openai')

  // AI SDK-style streaming implementation
  const append = async (message: { content: string; role: string }) => {
    if (isLoading.value) return

    // Add user message
    const userMessage = {
      id: generateId(),
      role: 'user',
      content: message.content,
      createdAt: new Date().toISOString()
    }
    messages.value.push(userMessage)

    isLoading.value = true
    error.value = null

    try {
      // Create assistant message for streaming
      const assistantMessage = {
        id: generateId(),
        role: 'assistant',
        content: '',
        createdAt: new Date().toISOString(),
        thinking: 'Analyzing your request and selecting the best approach...'
      }
      messages.value.push(assistantMessage)

      // Make streaming request
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages.value.slice(0, -1).map(m => ({
            role: m.role,
            content: m.content
          })),
          provider: selectedProvider.value,
          streamMode: 'text'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      // Handle streaming data
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            
            if (data.trim() === '[DONE]') {
              break
            }
            
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                // Append content to the assistant message
                const lastMessage = messages.value[messages.value.length - 1]
                lastMessage.content += parsed.content
              } else if (parsed.error) {
                throw new Error(parsed.error)
              }
            } catch (parseError) {
              // Skip invalid JSON chunks
              continue
            }
          }
        }
      }

    } catch (err) {
      console.error('Chat error:', err)
      error.value = err.message
      
      // Update the last message with error
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content = `Error: ${err.message}`
      }
    } finally {
      isLoading.value = false
    }
  }

  const reload = async () => {
    if (messages.value.length === 0) return
    
    // Remove last assistant message and regenerate
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage.role === 'assistant') {
      messages.value.pop()
    }
    
    // Get the user message to regenerate from
    const userMessage = messages.value[messages.value.length - 1]
    if (userMessage && userMessage.role === 'user') {
      await append(userMessage)
    }
  }

  const sendMessage = async (content: string) => {
    await append({ content, role: 'user' })
  }

  const generateId = () => Date.now() + '-' + Math.random().toString(36).substr(2, 9)

  return {
    messages,
    isLoading,
    error,
    selectedProvider,
    append,
    reload,
    sendMessage
  }
}
