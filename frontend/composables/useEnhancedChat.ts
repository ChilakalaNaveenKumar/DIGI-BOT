// Enhanced chat with streaming + component analysis integration
import type { Message } from '~/types'
import { mockMarkdownContent } from '~/utils/mockMarkdownContent'
import { getRandomMockResponse } from '~/utils/complexMockData'

export const useEnhancedChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const input = ref('')
  const isStreaming = ref(false)
  
  // Use component analysis composable
  const { analyzeContent, isAnalyzing } = useComponentAnalysis()
  
  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading.value || isStreaming.value) return
    
    // Add user message
    const userMessage: Message = {
      id: Date.now(),
      content,
      role: 'user' as const,
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    input.value = ''
    isLoading.value = false
    isStreaming.value = true
    
    // Prepare assistant message for streaming
    const assistantMessage: Message = {
      id: Date.now() + 1,
      content: '',
      role: 'assistant' as const,
      timestamp: new Date(),
      isLoading: false,
      isStreaming: true,
      reasoning: '',
      components: [] // New field for generated components
    }
    messages.value.push(assistantMessage)
    
    try {
      const isHiMessage = content.toLowerCase().trim() === 'hi'
      
      if (isHiMessage) {
        // Stream the markdown content first (original demo)
        await simulateStreamingWithAnalysis(assistantMessage.id, mockMarkdownContent)
      } else if (content.toLowerCase().includes('test') || content.toLowerCase().includes('demo')) {
        // Use complex mock data for testing component analysis
        const mockResponse = getRandomMockResponse()
        console.log(`🎯 Using mock data: ${mockResponse.id} (expects: ${mockResponse.expectedComponents.join(', ')})`)
        await simulateStreamingWithAnalysis(assistantMessage.id, mockResponse.content)
      } else {
        // For other messages, analyze content for components
        await handleRegularMessage(assistantMessage, content)
      }
      
    } catch (error) {
      console.error('Enhanced chat error:', error)
      
      const index = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (index !== -1) {
        messages.value[index] = {
          ...assistantMessage,
          content: 'Sorry, I encountered an error. Please try again.',
          isLoading: false,
          isStreaming: false,
          error: error instanceof Error ? error.message : String(error)
        }
      }
      
      isLoading.value = false
      isStreaming.value = false
    }
  }
  
  // Handle regular messages with potential component analysis
  const handleRegularMessage = async (assistantMessage: Message, userContent: string) => {
    const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
    if (messageIndex === -1) return

    // First, provide a regular response
    const response = `I understand you're asking about: "${userContent}". Let me help you with that!`
    
    // Stream the regular response
    await simulateStreaming(assistantMessage.id, response)
    
    // Then analyze if we should add components
    try {
      console.log('🔍 Analyzing content for potential components...')
      
      const decision = await analyzeContent({
        content: userContent,
        context: 'User chat message'
      })
      
      if (decision?.decision === 'GENERATE_NOW' && decision.markdown) {
        console.log('✅ Component should be generated:', decision.component_type)
        
        // Add component to the message
        const message = messages.value[messageIndex]
        if (message) {
          message.components = message.components || []
          message.components.push({
            type: decision.component_type!,
            markdown: decision.markdown,
            confidence: decision.confidence
          })
          
          // Append component info to content
          message.content += `\n\n---\n\n**📊 I've generated an interactive ${decision.component_type} component based on your data:**\n\n${decision.markdown}`
        }
      } else {
        console.log('ℹ️ No component generated:', decision?.reasoning)
      }
    } catch (error) {
      console.error('Component analysis failed:', error)
    }
  }
  
  // Enhanced streaming that can trigger component analysis
  const simulateStreamingWithAnalysis = async (messageId: number, content: string) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    // First stream the content normally
    await simulateStreaming(messageId, content)
    
    // After streaming is complete, analyze for components
    try {
      console.log('🔍 Analyzing streamed content for components...')
      
      const decision = await analyzeContent({
        content: content,
        context: 'Streamed markdown content'
      })
      
      if (decision?.decision === 'GENERATE_NOW' && decision.markdown) {
        console.log('✅ Component detected in streamed content:', decision.component_type)
        
        // Add component to the message
        const message = messages.value[messageIndex]
        if (message) {
          message.components = message.components || []
          message.components.push({
            type: decision.component_type!,
            markdown: decision.markdown,
            confidence: decision.confidence
          })
          
          // Optionally append component notification
          message.content += `\n\n---\n\n**🎯 Enhanced Component Generated:**\n*${decision.reasoning}*\n\n${decision.markdown}`
        }
      }
    } catch (error) {
      console.error('Post-stream component analysis failed:', error)
    }
  }
  
  // Regular streaming function (same as before)
  const simulateStreaming = async (messageId: number, content: string): Promise<void> => {
    return new Promise((resolve) => {
      const messageIndex = messages.value.findIndex(m => m.id === messageId)
      if (messageIndex === -1) {
        resolve()
        return
      }

      let currentContent = ''
      let charIndex = 0
      
      const message = messages.value[messageIndex]
      if (!message) {
        resolve()
        return
      }
      
      message.isLoading = false
      message.isStreaming = true
      message.content = ''
      message.reasoning = `Streaming comprehensive content with potential component analysis...`

      // Stream content character by character
      const streamInterval = setInterval(() => {
        if (charIndex >= content.length) {
          clearInterval(streamInterval)
          const message = messages.value[messageIndex]
          if (message) {
            message.isStreaming = false
            message.content = content
          }
          isLoading.value = false
          isStreaming.value = false
          resolve() // Resolve the promise when streaming is complete
          return
        }

        const chunkSize = Math.random() > 0.8 ? Math.floor(Math.random() * 3) + 1 : Math.floor(Math.random() * 2) + 1
        const nextIndex = Math.min(charIndex + chunkSize, content.length)
        currentContent = content.substring(0, nextIndex)
        charIndex = nextIndex

        const message = messages.value[messageIndex]
        if (message) {
          message.content = currentContent
        }

      }, 30 + Math.random() * 20)
    })
  }
  
  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    isLoading: readonly(isLoading),
    isStreaming: readonly(isStreaming),
    isAnalyzing: readonly(isAnalyzing),
    input,
    sendMessage,
    clearMessages,
    simulateStreaming,
    simulateStreamingWithAnalysis
  }
}
