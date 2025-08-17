// Enhanced chat logic with streaming support
import type { Message } from '~/types'
import { mockMarkdownContent } from '~/utils/mockMarkdownContent'

export const useChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const input = ref('')
  const isStreaming = ref(false)
  
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
    isLoading.value = false // Don't show global loading when streaming
    isStreaming.value = true
    
    // Prepare assistant message for streaming
    const assistantMessage: Message = {
      id: Date.now() + 1,
      content: '',
      role: 'assistant' as const,
      timestamp: new Date(),
      isLoading: false, // Don't show message loading when streaming
      isStreaming: true,
      reasoning: ''
    }
    messages.value.push(assistantMessage)
    
    try {
      // Check if user said "hi" to show markdown demo
      const isHiMessage = content.toLowerCase().trim() === 'hi'
      
      // Simulate streaming for "hi" message
      if (isHiMessage) {
        simulateStreaming(assistantMessage.id, mockMarkdownContent)
      } else {
        // Regular non-streaming response - use loading state
        isLoading.value = true // Show global loading for non-streaming
        const messageIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
        if (messageIndex !== -1) {
          const message = messages.value[messageIndex]
          if (message) {
            message.isLoading = true // Show message loading
            message.isStreaming = false
          }
        }
        
        setTimeout(() => {
          const index = messages.value.findIndex(m => m.id === assistantMessage.id)
          if (index !== -1) {
            messages.value[index] = {
              ...assistantMessage,
              content: 'Hi there! How can I help you today? I can assist with coding, writing, analysis, research, and much more.',
              isLoading: false,
              isStreaming: false,
              reasoning: 'The user has just said something other than "hi" - I should respond in a helpful, friendly way and ask how I can assist them.',
              reasoningSteps: [
                {
                  type: 'thinking',
                  content: 'The user has sent a message - I should provide a helpful response',
                  status: 'completed',
                  result: 'I\'ll respond with a friendly greeting and offer assistance.'
                },
                {
                  type: 'conclusion',
                  content: 'Providing a warm, helpful response',
                  status: 'completed',
                  result: 'Ready to assist with any questions or tasks!'
                }
              ]
            }
          }
          
          isLoading.value = false
          isStreaming.value = false
        }, 1500)
      }
      
    } catch (error) {
      console.error('Chat error:', error)
      
      // Update the assistant message with error
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
  
  const clearMessages = () => {
    messages.value = []
  }
  
  // Simulate streaming response
  const simulateStreaming = async (messageId: number, content: string) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    let currentContent = ''
    let charIndex = 0
    
    // Start streaming - update in place to preserve object reference
    const message = messages.value[messageIndex]
    if (!message) return
    
    message.isLoading = false
    message.isStreaming = true
    message.content = ''
    message.reasoning = `The user said "hi" - I'll showcase **comprehensive markdown features** including:

## Features to Demonstrate:
- **Headers** (H1-H6)
- *Text formatting* (bold, italic, strikethrough)
- \`Code blocks\` with syntax highlighting
- Lists (ordered, unordered, tasks)
- [Links](https://example.com) and images
- Tables with proper formatting
- > Blockquotes with styling
- Horizontal rules and more!

This will show the full **markdown rendering capabilities** of the digi-setu chat interface.`
    message.reasoningSteps = [
        {
          type: 'thinking',
          content: 'The user said **"hi"** - I should showcase the comprehensive **markdown rendering capabilities**!',
          status: 'completed',
          result: `I'll demonstrate all markdown features including:
- **Headers** (H1-H6)  
- *Text formatting* (bold, italic, strikethrough)
- \`Code blocks\` with syntax highlighting
- Lists and tables
- Links and images
- > Blockquotes and more!`
        },
        {
          type: 'tool_call',
          tool_name: 'markdown_renderer',
          content: 'Preparing comprehensive markdown demonstration content',
          status: 'completed',
          result: `**Content prepared** including:
- Math equations with KaTeX
- Custom containers (info, warning, tip, danger)
- Enhanced text formatting (mark, insert, sub/sup)
- Task lists with real checkboxes
- Code highlighting with 100+ languages
- Tables, links, images, and more!`
        },
        {
          type: 'conclusion',
          content: 'Streaming comprehensive markdown demonstration with all features',
          status: 'completed',
          result: '🚀 **Ready to showcase** the complete markdown rendering system with streaming support!'
        }
      ]

    // Stream content character by character with realistic delays
    const streamInterval = setInterval(() => {
      if (charIndex >= content.length) {
        // Streaming complete
        clearInterval(streamInterval)
        // Streaming complete - update in place to preserve object reference
        const message = messages.value[messageIndex]
        if (message) {
          message.isStreaming = false
          message.content = content
        }
        isLoading.value = false
        isStreaming.value = false
        return
      }

      // Add characters in smaller chunks for smoother streaming
      const chunkSize = Math.random() > 0.8 ? Math.floor(Math.random() * 3) + 1 : Math.floor(Math.random() * 2) + 1
      const nextIndex = Math.min(charIndex + chunkSize, content.length)
      currentContent = content.substring(0, nextIndex)
      charIndex = nextIndex

      // Update message content (preserve object reference for Vue reactivity)
      const message = messages.value[messageIndex]
      if (message) {
        message.content = currentContent
      }

    }, 30 + Math.random() * 20) // Comfortable reading speed
  }

  return {
    messages,
    isLoading: readonly(isLoading),
    isStreaming: readonly(isStreaming),
    input,
    sendMessage,
    clearMessages,
    simulateStreaming
  }
}