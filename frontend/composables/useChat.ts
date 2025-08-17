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
      // TODO: Temporarily disabled for UI/UX development - simulate response with enhanced reasoning steps
      setTimeout(() => {
        const index = messages.value.findIndex(m => m.id === assistantMessage.id)
        if (index !== -1) {
          messages.value[index] = {
            ...assistantMessage,
            content: 'Hi there! How can I help you today? I can assist with coding, writing, analysis, research, and much more.',
            isLoading: false,
            reasoning: 'The user has just said "hi" - this is a simple greeting. I should respond in a warm, natural way without being overly formal or using lists/bullet points since this is casual conversation. I\'ll keep it brief and friendly, and maybe ask how I can help them today.',
            reasoningSteps: [
              {
                type: 'thinking',
                content: 'The user has sent a simple greeting "hi". This is a casual, friendly opening to our conversation.',
                status: 'completed',
                result: 'This is a basic social interaction. The user is initiating contact in a casual way, which suggests they want a friendly, approachable response rather than something formal or robotic. I should match their casual tone while being helpful.'
              },
              {
                type: 'thinking', 
                content: 'I should analyze what kind of response would be most appropriate here. Since this is just a greeting, I want to be warm and welcoming.',
                status: 'completed',
                result: 'For greeting responses, the key elements are: acknowledgment of their greeting, reciprocal friendliness, and an invitation to continue the conversation. I should avoid being overly enthusiastic or too brief. A balanced approach works best.'
              },
              {
                type: 'tool_call',
                tool_name: 'codebase_search',
                content: 'Searching for appropriate greeting patterns and response templates',
                status: 'completed',
                result: 'Found several greeting patterns in the codebase. Analysis shows that warm, casual responses work best for initial contact. Common patterns include: greeting acknowledgment, brief self-introduction of capabilities, and open-ended question to encourage further interaction.'
              },
              {
                type: 'thinking',
                content: 'I should keep my response brief but informative. I\'ll acknowledge the greeting and offer help.',
                status: 'completed',
                result: 'The optimal response length for greetings is 1-2 sentences. This provides enough information to be helpful without overwhelming the user. I should include a subtle mention of my capabilities and end with an invitation for them to share what they need help with.'
              },
              {
                type: 'tool_call',
                tool_name: 'web_search', 
                content: 'Checking for best practices in conversational AI greetings',
                status: 'completed',
                result: 'Research indicates that effective AI greetings should be conversational, helpful, and authentic. Users respond better to natural language rather than formal or robotic responses. The greeting should establish a collaborative tone and make the user feel comfortable asking questions.'
              },
              {
                type: 'thinking',
                content: 'Perfect! I\'ll craft a response that\'s friendly, helpful, and invites further conversation without being too formal.',
                status: 'completed',
                result: 'Based on my analysis, I\'ll structure my response as: friendly greeting acknowledgment + brief capability mention + open question. This creates a natural conversation flow and encourages the user to engage further with specific requests or questions.'
              },
              {
                type: 'conclusion',
                content: 'Final response will be warm, brief, and offer assistance while maintaining a conversational tone.',
                status: 'completed',
                result: 'My final response strategy: "Hi there! How can I help you today? I can assist with coding, writing, analysis, research, and much more." This balances friendliness with utility, gives concrete examples of capabilities, and invites further interaction.'
              }
            ]
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
