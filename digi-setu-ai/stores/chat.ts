/**
 * Chat Store using Pinia
 * Manages chat messages, streaming, and conversation state
 */

import { defineStore } from 'pinia'
import type { Message, ReasoningStep } from '~/types'
import { useAuthenticatedFetch } from '~/composables/useAuthenticatedFetch'

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  isStreaming: boolean
  conversationId: number | null
  conversationTitle: string
  currentReasoningSteps: ReasoningStep[]
  isReasoning: boolean
  isProcessingComponents: boolean
}

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    messages: [],
    isLoading: false,
    isStreaming: false,
    conversationId: null,
    conversationTitle: '',
    currentReasoningSteps: [],
    isReasoning: false,
    isProcessingComponents: false,
  }),

  getters: {
    hasMessages: (state) => state.messages.length > 0,
    lastMessage: (state) => state.messages[state.messages.length - 1],
    userMessages: (state) => state.messages.filter(m => m.role === 'user'),
    assistantMessages: (state) => state.messages.filter(m => m.role === 'assistant'),
  },

  actions: {
    // Set conversation state
    setConversationState(id: number | null, title: string) {
      this.conversationId = id
      this.conversationTitle = title
    },

    // Clear all messages
    clearMessages() {
      this.messages = []
      this.currentReasoningSteps = []
      this.isReasoning = false
    },

    // Start new conversation
    startNewConversation() {
      this.clearMessages()
      this.conversationId = null
      this.conversationTitle = 'New Conversation'
      this.currentReasoningSteps = []
      this.isReasoning = false
    },

    // Load conversation messages from API
    loadConversationMessages(conversationMessages: Array<{
      id: number
      role: 'user' | 'assistant'
      content: string
      reasoning_steps?: {
        steps: Array<{
          id: string
          type: 'thinking' | 'tool_call'
          content: string
          status: string
          timestamp: string
          tool_name?: string
          result?: unknown
          inputJson?: string
        }>
      }
      created_at: string
    }>) {
      // Convert API messages to frontend Message format
      const convertedMessages: Message[] = conversationMessages.map(msg => ({
        id: msg.id,
        content: msg.content,
        role: msg.role,
        timestamp: new Date(msg.created_at),
        isLoading: false,
        isStreaming: false,
        reasoningSteps: msg.reasoning_steps?.steps?.map(step => ({
          id: step.id,
          type: step.type,
          content: step.content,
          status: step.status as 'pending' | 'active' | 'completed' | 'error',
          timestamp: new Date(step.timestamp),
          tool_name: step.tool_name,
          result: step.result,
          inputJson: step.inputJson
        })) || []
      }))
      
      this.messages = convertedMessages
      
    },

    // Add a new message
    addMessage(message: Message) {
      this.messages.push(message)
    },

    // Update a message
    updateMessage(messageId: string | number, updates: Partial<Message>) {
      const index = this.messages.findIndex(m => m.id === messageId)
      if (index !== -1 && this.messages[index]) {
        // Use array replacement to trigger Vue reactivity
        this.messages[index] = { ...this.messages[index], ...updates }
      } else {
        console.error('Message not found for update:', messageId, 'in', this.messages.length, 'messages')
      }
    },

    // Save complete conversation after processing
    async saveCompleteConversation(
      userMessage: string, 
      assistantMessage: string, 
      reasoningSteps: ReasoningStep[]
    ) {
      try {
        const { post } = useAuthenticatedFetch()
        
        if (!this.conversationId) {
          // NEW CONVERSATION: Create conversation with both messages
          const title = userMessage.length > 50 
            ? userMessage.substring(0, 47) + "..." 
            : userMessage

          const response = await post<{id: number, title: string}>('http://localhost:8000/api/conversations/save-complete', {
            title: title.trim(),
            user_message: userMessage,
            assistant_message: assistantMessage,
            reasoning_steps: reasoningSteps.map(step => ({
              id: step.id,
              type: step.type,
              content: step.content,
              status: step.status,
              timestamp: step.timestamp?.toISOString() || new Date().toISOString(),
              tool_name: step.tool_name,
              result: step.result,
              inputJson: step.inputJson
            })),
            ai_provider: "anthropic",
            ai_model: "claude-sonnet-4-20250514"
          })

          // Update conversation state
          this.conversationId = response.id
          this.conversationTitle = response.title
          
          // Note: Conversation store will be updated by the component
          // to avoid circular imports
          
          console.log('New conversation created and saved:', response.id, response.title)
          
        } else {
          // EXISTING CONVERSATION: Add messages to existing conversation
          
          // Save user message
          await post(`http://localhost:8000/api/conversations/${this.conversationId}/messages`, {
            role: 'user',
            content: userMessage,
            token_count: Math.ceil(userMessage.length / 4) // Rough estimate
          })
          
          // Save assistant message with reasoning steps
          await post(`http://localhost:8000/api/conversations/${this.conversationId}/messages`, {
            role: 'assistant',
            content: assistantMessage,
            ai_provider: "anthropic",
            ai_model: "claude-sonnet-4-20250514",
            reasoning_steps: {
              steps: reasoningSteps.map(step => ({
                id: step.id,
                type: step.type,
                content: step.content,
                status: step.status,
                timestamp: step.timestamp?.toISOString() || new Date().toISOString(),
                tool_name: step.tool_name,
                result: step.result,
                inputJson: step.inputJson
              }))
            },
            token_count: Math.ceil(assistantMessage.length / 4) // Rough estimate
          })
          
          console.log('Messages added to existing conversation:', this.conversationId)
        }
        
      } catch (error) {
        console.error('Chat Store: Failed to save conversation:', error)
      }
    },

    // Set loading states
    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    setStreaming(streaming: boolean) {
      this.isStreaming = streaming
    },

    setProcessingComponents(processing: boolean) {
      this.isProcessingComponents = processing
    },

    setReasoning(reasoning: boolean) {
      this.isReasoning = reasoning
    },

    // Update reasoning steps
    setReasoningSteps(steps: ReasoningStep[]) {
      this.currentReasoningSteps = steps
    },

    addReasoningStep(step: ReasoningStep) {
      this.currentReasoningSteps.push(step)
    },

    updateReasoningStep(stepId: string, updates: Partial<ReasoningStep>) {
      const index = this.currentReasoningSteps.findIndex(s => s.id === stepId)
      if (index !== -1 && this.currentReasoningSteps[index]) {
        Object.assign(this.currentReasoningSteps[index], updates)
      }
    },

    // Streaming message functionality
    async sendMessage(content: string) {
      if (!content.trim() || this.isLoading || this.isStreaming) return

      this.setLoading(true)
      
      try {
        // Add user message immediately
        const userMessage: Message = {
          id: Date.now(),
          content: content.trim(),
          role: 'user',
          timestamp: new Date(),
          isLoading: false,
          isStreaming: false
        }
        this.addMessage(userMessage)

        // Create assistant message placeholder
        const assistantMessage: Message = {
          id: Date.now() + 1,
          content: '',
          role: 'assistant',
          timestamp: new Date(),
          isLoading: true,
          isStreaming: false,
          reasoningSteps: []
        }
        this.addMessage(assistantMessage)

        // Start streaming
        await this.streamFromAPI(content, assistantMessage.id)
        
      } catch (error) {
        console.error('Failed to send message:', error)
      } finally {
        this.setLoading(false)
      }
    },

    async streamFromAPI(content: string, assistantMessageId: string | number) {
      this.setStreaming(true)
      this.setReasoning(true)
      this.currentReasoningSteps = []

      // Set assistant message to not loading when streaming starts
      this.updateMessage(assistantMessageId, { isLoading: false, isStreaming: true })

      try {
        // Build conversation history
        const history = this.buildConversationHistory()

        const response = await fetch('http://localhost:8000/api/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            messages: history,
            conversation_id: this.conversationId,
            model: "claude-sonnet-4-20250514",
            enable_thinking: true,
            thinking_budget: 5000,
            enable_web_search: true,
            temperature: 0.7
          })
        })

        if (!response.body) throw new Error('No response body')

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let accumulatedContent = ''
        let currentStep: ReasoningStep | null = null

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))

                
                if (data.type === 'content_block_start' && data.content_block?.type === 'thinking') {
                  // Start new thinking step
                  currentStep = {
                    id: `thinking-${Date.now()}-${Math.random()}`,
                    type: 'thinking',
                    content: '',
                    status: 'active',
                    timestamp: new Date()
                  }
                  this.addReasoningStep(currentStep)
                  
                  // Immediately update the assistant message with the new reasoning step
                  this.updateMessage(assistantMessageId, { 
                    reasoningSteps: [...this.currentReasoningSteps]
                  })
                } else if (data.type === 'content_block_delta' && data.delta?.type === 'thinking_delta') {
                  // Update thinking step
                  if (currentStep && data.delta.thinking) {
                    currentStep.content += data.delta.thinking
                    this.updateReasoningStep(currentStep.id, { content: currentStep.content })
                    
                    // Also update the assistant message with current reasoning steps
                    this.updateMessage(assistantMessageId, { 
                      reasoningSteps: [...this.currentReasoningSteps]
                    })
                  }
                } else if (data.type === 'content_block_stop') {
                  // Complete thinking step
                  if (currentStep) {
                    this.updateReasoningStep(currentStep.id, { status: 'completed' })
                    currentStep = null
                    
                    // Update the assistant message with completed reasoning steps
                    this.updateMessage(assistantMessageId, { 
                      reasoningSteps: [...this.currentReasoningSteps]
                    })
                  }
                } else if (data.type === 'content_block_delta' && data.delta?.type === 'text_delta') {
                  // Regular content
                  accumulatedContent += data.delta.text || ''

                  this.updateMessage(assistantMessageId, { 
                    content: accumulatedContent,
                    isStreaming: true 
                  })
                } else if (data.type === 'message_delta' && data.delta?.type === 'text_delta') {
                  // Alternative text delta format
                  accumulatedContent += data.delta.text || ''

                  this.updateMessage(assistantMessageId, { 
                    content: accumulatedContent,
                    isStreaming: true 
                  })
                } else if (data.type === 'message_stop') {
                  // Stream complete - attach reasoning steps to the message

                  this.updateMessage(assistantMessageId, { 
                    content: accumulatedContent,
                    isStreaming: false,
                    isLoading: false,
                    reasoningSteps: [...this.currentReasoningSteps]
                  })
                  break
                }
              } catch (e) {
                console.error('Error parsing stream data:', e, 'Line:', line)
              }
            }
          }
        }

        // Process components and save
        await this.processComponentsAndSave(content, accumulatedContent, assistantMessageId)

      } catch (error) {
        console.error('Streaming error:', error)
        this.updateMessage(assistantMessageId, { 
          content: 'Error: Failed to get response',
          isStreaming: false,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        })
      } finally {
        this.setStreaming(false)
        this.setReasoning(false)
      }
    },

    buildConversationHistory() {
      const history: Array<{ role: 'user' | 'assistant', content: string }> = []
      
      // Get recent messages (last 10 for existing conversations, all for new ones)
      const messagesToInclude = this.conversationId ? this.messages.slice(-10) : this.messages
      
      for (const msg of messagesToInclude) {
        if ((msg.role === 'user' || msg.role === 'assistant') && msg.content.trim()) {
          history.push({
            role: msg.role,
            content: msg.content
          })
        }
      }
      
      return history
    },

    async processComponentsAndSave(userMessage: string, assistantMessage: string, assistantMessageId: string | number) {
      try {
        console.log('Starting component processing for message:', assistantMessage.substring(0, 100) + '...')
        this.setProcessingComponents(true)

        // Call component matcher
        const response = await fetch('http://localhost:8000/api/component-matcher/analyze-simple', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ query: assistantMessage })
        })

        if (response.ok) {
          const result = await response.json()
          console.log('Component matcher result:', result)
          if (result.success && result.has_matches) {
            console.log('Found', result.data.matches.length, 'component matches')
            console.log('Original content length:', assistantMessage.length)
            console.log('Processing content for component insertion...')
            // Process components and insert them into the content
            let processedContent = assistantMessage
            const components: Array<{
              id: string
              type: string
              data: unknown
              confidence: number
              title: string
              markdown: string
            }> = []
            
            // Sort matches by their position in the text (forward order, then process in reverse to avoid index shifting)
            const sortedMatches = result.data.matches.sort((a: { placement: { anchor_sentence: string } }, b: { placement: { anchor_sentence: string } }) => {
              const aIndex = processedContent.indexOf(a.placement.anchor_sentence)
              const bIndex = processedContent.indexOf(b.placement.anchor_sentence)
              return aIndex - bIndex // Forward order for sorting
            })
            
            // Process matches in reverse order to avoid index shifting issues
            for (let i = sortedMatches.length - 1; i >= 0; i--) {
              const match = sortedMatches[i]
              const anchorSentence = match.placement.anchor_sentence
              let anchorIndex = processedContent.indexOf(anchorSentence)
              
              // If exact match fails, try to find a partial match
              if (anchorIndex === -1) {
                // Try finding the first few words of the sentence
                const firstWords = anchorSentence.split(' ').slice(0, 5).join(' ')
                anchorIndex = processedContent.indexOf(firstWords)
                console.log('Exact match failed, trying partial match:', firstWords, 'found at:', anchorIndex)
              }
              
              if (anchorIndex !== -1) {
                const componentId = `component-${Date.now()}-${i}`
                
                // Insert the actual markdown component that will be rendered by UiStreamingMarkdown
                const componentMarkdown = `\n\n${match.block_content}\n\n`
                
                console.log(`Processing component ${i + 1}:`, {
                  type: match.block_content.split('\n')[0].replace(':::', ''),
                  anchorFound: anchorIndex,
                  anchorSentence: anchorSentence.substring(0, 50) + '...'
                })
                
                let insertPosition: number
                
                // Check position: before or after sentence
                if (match.placement.position === 'before_sentence') {
                  // Insert before the anchor sentence
                  insertPosition = anchorIndex
                } else {
                  // Insert after the anchor sentence (default)
                  // Find the end of the sentence by looking for the next period, newline, or end of text
                  const sentenceEnd = processedContent.indexOf('.', anchorIndex)
                  const nextNewline = processedContent.indexOf('\n', anchorIndex)
                  
                  if (sentenceEnd !== -1 && (nextNewline === -1 || sentenceEnd < nextNewline)) {
                    insertPosition = sentenceEnd + 1
                  } else if (nextNewline !== -1) {
                    insertPosition = nextNewline
                  } else {
                    insertPosition = anchorIndex + anchorSentence.length
                  }
                }
                
                // Insert the component markdown directly into content
                processedContent = processedContent.slice(0, insertPosition) + 
                                componentMarkdown + 
                                processedContent.slice(insertPosition)
                
                // Store component data for reference
                components.push({
                  id: componentId,
                  type: match.block_content.split('\n')[0].replace(':::', ''),
                  data: match,
                  confidence: 0.9,
                  title: match.block_content.split('\n')[1]?.replace('title: ', '') || '',
                  markdown: match.block_content
                })
              } else {
                console.warn('Could not find anchor sentence in content:', anchorSentence.substring(0, 100) + '...')
              }
            }
            
            // Update the assistant message with processed content and components using message ID
            console.log('Updating message with ID:', assistantMessageId, 'with processed content')
            console.log('Original content length:', assistantMessage.length)
            console.log('Processed content length:', processedContent.length)
            console.log('Components:', components.length)
            
            // Use updateMessage method which finds by ID
            this.updateMessage(assistantMessageId, {
              content: processedContent,
              components: components
            })
          }
        }

        // Save messages to conversation (use the processed content if components were added)
        const assistantMsg = this.messages.find(m => m.role === 'assistant' && m.content.includes(assistantMessage.substring(0, 50)))
        const finalAssistantMessage = assistantMsg?.content || assistantMessage
        
        await this.saveCompleteConversation(userMessage, finalAssistantMessage, this.currentReasoningSteps)

      } catch (error) {
        console.error('Component processing failed:', error)
      } finally {
        this.setProcessingComponents(false)
      }
    },

    // Regenerate message
    async regenerateMessage(messageId: string | number) {
      const messageIndex = this.messages.findIndex(m => m.id === messageId)
      if (messageIndex === -1) return

      const message = this.messages[messageIndex]
      if (!message || message.role !== 'assistant') return

      // Find the previous user message
      let userMessage = ''
      for (let i = messageIndex - 1; i >= 0; i--) {
        const msg = this.messages[i]
        if (msg?.role === 'user') {
          userMessage = msg.content
          break
        }
      }

      if (!userMessage) return

      // Remove the assistant message and regenerate
      this.messages.splice(messageIndex, 1)
      await this.sendMessage(userMessage)
    }
  },

  // Persist state on refresh
  persist: {
    key: 'digi-setu-chat',
    pick: ['conversationId', 'conversationTitle'] // Only persist essential data, not messages
  }
})
