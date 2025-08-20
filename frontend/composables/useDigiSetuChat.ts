// Digi Setu Orchestrator Integration - Enhanced with batch analysis system
import type { Message, ReasoningStep, GeneratedComponent } from '~/types'
import { useEnhancedContent, type EnhancedContentPacket } from './useEnhancedContent'

interface DigiSetuStreamResponse {
  type: 'conversation_id' | 'thinking' | 'reasoning' | 'activity' | 'tool_output' | 'content' | 'error' | 'enhanced_content' | 'analysis_status' | 'complete'
  content: string
  metadata?: {
    step?: string
    tool?: string
    tools?: string[]
    confidence?: number
    orchestrator?: string
    tools_used?: string[]
    reasoning?: string
    processed?: boolean
    segmentation_time?: number
    analysis_time?: number
    blocks_found?: number
    components_generated?: number
    original_length?: number
    enhanced_length?: number
    block_start?: boolean
    thinking_delta?: boolean
    error?: string
  }
  final?: boolean
  // Enhanced content fields (new batch system)
  enhanced_content?: string
  components?: any[]
  reasoning?: string
}

// Type alias for compatibility
type Claude4StreamResponse = DigiSetuStreamResponse

export const useDigiSetuChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const input = ref('')
  const isStreaming = ref(false)
  
  // Enhanced content system
  const enhancedContent = useEnhancedContent()
  
  // Get runtime config for API base URL
  const config = useRuntimeConfig()

  const sendMessage = async (userMessage: string) => {
    if (!userMessage.trim() || isLoading.value) return

    isLoading.value = true
    isStreaming.value = true

    try {
      // Add user message
      const userMsg: Message = {
        id: Date.now(),
        role: 'user',
        content: userMessage,
        timestamp: new Date()
      }
      messages.value.push(userMsg)

      // Add assistant message placeholder
      const assistantMsg: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isLoading: true,
        isStreaming: true,
        reasoningSteps: [],
        components: []
      }
      messages.value.push(assistantMsg)

      // Clear input
      input.value = ''

      // Stream the response
      await streamDigiSetuResponse(assistantMsg.id, userMessage)

    } catch (error) {
      console.error('Send message error:', error)
    } finally {
      isLoading.value = false
      isStreaming.value = false
    }
  }

  /**
   * Stream Digi Setu orchestrator response
   */
  const streamDigiSetuResponse = async (messageId: number, userContent: string) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) {
      console.log('❌ Message not found for streaming:', messageId)
      return
    }

    try {
      // Call Digi Setu streaming endpoint
      const response = await fetch(`${config.public.apiBase}/v1/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          message: userContent,
          user_preferences: {},
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No response body reader available')
      }

      let conversationId = ''
      let accumulatedContent = ''
      let currentReasoning = ''
      let reasoningSteps: ReasoningStep[] = []
      let toolsUsed: string[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonString = line.slice(6).trim()
              
              // Skip empty or malformed JSON
              if (!jsonString || !jsonString.startsWith('{')) {
                continue
              }
              
              // Try to parse JSON, skip if malformed
              let data: Claude4StreamResponse
              try {
                data = JSON.parse(jsonString)
              } catch (jsonError) {
                console.warn('⚠️ Skipping malformed JSON chunk:', jsonString.substring(0, 100) + '...')
                continue
              }
              
              // Handle different stream types
              switch (data.type) {
                case 'conversation_id':
                  conversationId = data.content
                  break

                case 'thinking':
                  // Handle thinking blocks properly based on metadata
                  if (data.metadata?.block_start) {
                    // Start new thinking step
                    reasoningSteps.push({
                      type: 'thinking',
                      content: '',
                      result: '', // Will accumulate content
                      status: 'active'
                    })
                  } else if (data.metadata?.thinking_delta && data.content) {
                    // Add content to current thinking step
                    const currentStep = reasoningSteps[reasoningSteps.length - 1]
                    if (currentStep && currentStep.type === 'thinking' && currentStep.status === 'active') {
                      currentStep.content += data.content
                      currentStep.result += data.content
                    } else {
                      // Fallback: create new step if no active thinking step exists
                      reasoningSteps.push({
                        type: 'thinking',
                        content: data.content,
                        result: data.content,
                        status: 'active'
                      })
                    }
                  }
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  break

                case 'reasoning':
                  // Handle reasoning conclusion based on metadata
                  if (data.metadata?.block_start) {
                    // Start new reasoning step
                    reasoningSteps.push({
                      type: 'reasoning',
                      content: '',
                      result: '',
                      status: 'active'
                    })
                  } else if (data.content) {
                    // Add to current reasoning step or create new one
                    const currentStep = reasoningSteps[reasoningSteps.length - 1]
                    if (currentStep && currentStep.type === 'reasoning' && currentStep.status === 'active') {
                      currentStep.content += data.content
                      currentStep.result += data.content
                    } else {
                      reasoningSteps.push({
                        type: 'reasoning',
                        content: data.content,
                        result: data.content,
                        status: 'active'
                      })
                    }
                  }
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  break

                case 'activity':
                  // Handle activity updates
                  console.log('🔄 Activity:', data.content, data.metadata)
                  
                  // Create activity reasoning step
                  reasoningSteps.push({
                    type: 'activity',
                    content: data.content,
                    result: data.content,
                    status: 'completed',
                    metadata: data.metadata
                  })
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  break

                case 'tool_output':
                  // Handle tool output
                  console.log('🔧 Tool output:', data.content)
                  
                  // Mark current reasoning step as completed and add result
                  if (reasoningSteps.length > 0) {
                    const lastStep = reasoningSteps[reasoningSteps.length - 1]
                    if (lastStep && lastStep.status === 'active') {
                      lastStep.status = 'completed'
                      lastStep.result = data.content
                    }
                  }
                  
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  
                  // Track tools used
                  if (data.metadata?.tools) {
                    toolsUsed.push(...data.metadata.tools)
                  }
                  break

                case 'content':
                  // Handle main content streaming
                  // Backend sends FULL accumulated content in each chunk, not deltas
                  accumulatedContent = data.content  // Use assignment, not addition!
                  
                  console.log(`📝 Content update: ${data.content.length} chars (ID: ${data.id})`)
                  
                  updateMessage(messageIndex, {
                    content: accumulatedContent,
                    isStreaming: true,
                    isLoading: false
                  })
                  
                  // No need for additional analysis - backend has already handled it
                  break

                case 'analysis_status':
                  // Handle analysis keep-alive messages
                  console.log('🔄 Analysis status:', data.content, data.metadata)
                  // Don't update message content, just log the status
                  break

                case 'enhanced_content':
                  // Handle enhanced content packet from new batch system
                  console.log('✨ Enhanced content packet received:', data.metadata)
                  
                  if (data.enhanced_content && data.components) {
                    const enhancedPacket: EnhancedContentPacket = {
                      enhanced_content: data.enhanced_content,
                      components: data.components,
                      metadata: {
                        processed: data.metadata?.processed || false,
                        segmentation_time: data.metadata?.segmentation_time,
                        analysis_time: data.metadata?.analysis_time,
                        blocks_found: data.metadata?.blocks_found,
                        components_generated: data.metadata?.components_generated,
                        original_length: data.metadata?.original_length,
                        enhanced_length: data.metadata?.enhanced_length,
                        error: data.metadata?.error
                      }
                    }
                    
                    // Process enhanced content packet
                    const messageId = messages.value[messageIndex]?.id
                    if (messageId) {
                      enhancedContent.processEnhancedPacket(
                        messageId, 
                        enhancedPacket, 
                        accumulatedContent
                      )
                    }
                    
                    console.log(`✅ Enhanced content processed: ${data.components?.length || 0} components generated`)
                  }
                  break

                case 'error':
                  console.error('❌ Digi Setu error:', data.content)
                  updateMessage(messageIndex, {
                    error: data.content,
                    isStreaming: false,
                    isLoading: false
                  })
                  break

                case 'complete':
                  // Stream complete
                  updateMessage(messageIndex, {
                    isStreaming: false,
                    isLoading: false
                  })
                  
                  // Mark final reasoning step as completed
                  if (reasoningSteps.length > 0) {
                    const lastStep = reasoningSteps[reasoningSteps.length - 1]
                    if (lastStep && lastStep.status === 'active') {
                      lastStep.status = 'completed'
                    }
                  }
                  
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  break
              }

            } catch (parseError) {
              console.error('JSON parse error:', parseError, line)
            }
          }
        }
      }

    } catch (error) {
      console.error('Streaming error:', error)
      throw error
    } finally {
      isLoading.value = false
      isStreaming.value = false
    }
  }

  /**
   * Update message by index (preserves existing pattern)
   */
  const updateMessage = (index: number, updates: Partial<Message>) => {
    if (index >= 0 && index < messages.value.length) {
      const currentMessage = messages.value[index]
      if (currentMessage) {
        console.log(`🔄 Updating message ${currentMessage.id} at index ${index}:`, {
          oldContentLength: currentMessage.content.length,
          newContentLength: updates.content?.length || 0,
          isStreaming: updates.isStreaming,
          updateKeys: Object.keys(updates),
          hasContent: 'content' in updates,
          contentValue: updates.content
        })
        
        // Don't overwrite content with empty/undefined values
        const safeUpdates = { ...updates }
        if ('content' in updates && (!updates.content || updates.content.length === 0)) {
          console.warn('⚠️ Preventing content clear - removing content from updates')
          delete safeUpdates.content
        }
        
        messages.value[index] = { ...currentMessage, ...safeUpdates }
      }
    } else {
      console.error(`❌ Invalid message index: ${index} (total: ${messages.value.length})`)
    }
  }

  return {
    messages,
    isLoading,
    isStreaming,
    input,
    sendMessage,
    enhancedContent
  }
}