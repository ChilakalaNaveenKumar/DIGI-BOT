/**
 * Digi Setu AI Composable
 * 
 * Manages AI interactions, streaming responses, and orchestration.
 */

import { ref, computed, watch } from 'vue'

// Global AI state
const messages = ref([])
const isLoading = ref(false)
const currentActivity = ref('')
const currentProvider = ref('openai')
const availableProviders = ref([
  {
    id: 'openai',
    name: 'GPT-5',
    description: '1M context, 64k output',
    status: 'healthy',
    models: ['gpt-5', 'gpt-4o', 'gpt-4o-mini']
  },
  {
    id: 'anthropic',
    name: 'Claude-4',
    description: '200k context, 64k output',
    status: 'healthy',
    models: ['claude-4', 'claude-3.5-sonnet', 'claude-3.7-sonnet']
  },
  {
    id: 'grok',
    name: 'Grok-4',
    description: '256k context, live search',
    status: 'healthy',
    models: ['grok-4', 'grok-4-vision']
  }
])

const error = ref(null)
const streamingResponse = ref(null)
const orchestrationPlan = ref(null)

export const useDigiSetuAI = () => {
  // Computed properties
  const healthyProviders = computed(() => {
    return availableProviders.value.filter(provider => provider.status === 'healthy')
  })
  
  const currentProviderInfo = computed(() => {
    return availableProviders.value.find(p => p.id === currentProvider.value)
  })
  
  const isStreaming = computed(() => {
    return streamingResponse.value !== null
  })
  
  const hasError = computed(() => {
    return error.value !== null
  })
  
  // Methods
  const sendMessage = async (content, options = {}) => {
    if (!content || content.trim() === '') {
      throw new Error('Message content is required')
    }
    
    isLoading.value = true
    error.value = null
    currentActivity.value = 'Preparing request...'
    
    try {
      // Add user message to messages array
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
        files: options.files || []
      }
      
      messages.value.push(userMessage)
      
      // Prepare request data
      const requestData = {
        message: content.trim(),
        conversation_id: options.conversationId,
        project_id: options.projectId,
        provider: options.provider || currentProvider.value,
        model: options.model,
        files: options.files,
        ai_settings: options.aiSettings
      }
      
      // Start streaming response
      await streamChatResponse(requestData)
      
    } catch (err) {
      error.value = err.message || 'Failed to send message'
      console.error('Failed to send message:', err)
      throw err
    } finally {
      isLoading.value = false
      currentActivity.value = ''
    }
  }
  
  const streamChatResponse = async (requestData) => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/v1/chat/stream', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${authToken}`
      //   },
      //   body: JSON.stringify(requestData)
      // })
      
      // Mock streaming implementation
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        parts: [],
        provider: requestData.provider,
        model: requestData.model,
        timestamp: new Date().toISOString(),
        isStreaming: true
      }
      
      messages.value.push(assistantMessage)
      streamingResponse.value = assistantMessage
      
      // Simulate orchestration plan
      orchestrationPlan.value = {
        primary_provider: requestData.provider,
        secondary_providers: [],
        reasoning_required: true,
        tools_required: [],
        estimated_time: 5.2,
        confidence: 0.85
      }
      
      // Simulate streaming chunks
      await simulateStreamingResponse(assistantMessage, requestData)
      
    } catch (err) {
      error.value = err.message || 'Failed to stream response'
      console.error('Streaming error:', err)
      throw err
    }
  }
  
  const simulateStreamingResponse = async (assistantMessage, requestData) => {
    const activities = [
      'Analyzing your request...',
      'Selecting best AI approach...',
      'Thinking through the problem...',
      'Generating response...',
      'Finalizing answer...'
    ]
    
    const reasoningSteps = [
      'Let me break down this request to understand what you\'re looking for.',
      'I need to consider the context and provide a comprehensive response.',
      'Based on the information provided, I can formulate a structured approach.',
      'Now I\'ll generate a detailed response that addresses your specific needs.'
    ]
    
    const responseContent = `Based on your request, I'll provide a comprehensive analysis.

## Key Points

1. **Understanding the Request**: Your question touches on several important aspects that require careful consideration.

2. **Analysis Approach**: I'll examine this from multiple angles to ensure a thorough response.

3. **Recommendations**: Here are my suggestions based on the analysis:
   - Consider the broader context
   - Evaluate multiple options
   - Implement a systematic approach

## Detailed Response

The topic you've raised is quite interesting and multifaceted. Let me walk through the key considerations:

\`\`\`javascript
// Example code snippet
function analyzeRequest(input) {
  const analysis = {
    complexity: 'medium',
    approach: 'systematic',
    confidence: 0.85
  };
  
  return analysis;
}
\`\`\`

This approach ensures we cover all the important aspects while maintaining clarity and actionability.

## Conclusion

In summary, the best path forward involves a balanced approach that considers both immediate needs and long-term implications.`
    
    // Stream activities
    for (const activity of activities) {
      currentActivity.value = activity
      await new Promise(resolve => setTimeout(resolve, 800))
    }
    
    // Stream reasoning
    if (orchestrationPlan.value.reasoning_required) {
      const reasoningPart = {
        type: 'reasoning',
        content: '',
        steps: []
      }
      
      assistantMessage.parts.push(reasoningPart)
      
      for (let i = 0; i < reasoningSteps.length; i++) {
        const step = reasoningSteps[i]
        reasoningPart.steps.push({
          step: i + 1,
          content: step,
          timestamp: new Date().toISOString()
        })
        reasoningPart.content += `${i + 1}. ${step}\n\n`
        
        await new Promise(resolve => setTimeout(resolve, 600))
      }
    }
    
    // Stream main content
    const contentPart = {
      type: 'content',
      content: '',
      content_type: 'markdown'
    }
    
    assistantMessage.parts.push(contentPart)
    
    // Simulate typing effect
    const words = responseContent.split(' ')
    for (let i = 0; i < words.length; i++) {
      contentPart.content += (i > 0 ? ' ' : '') + words[i]
      assistantMessage.content = contentPart.content
      
      // Small delay between words
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    
    // Finalize message
    assistantMessage.isStreaming = false
    streamingResponse.value = null
    currentActivity.value = ''
    
    console.log('✅ Streaming response completed')
  }
  
  const regenerateMessage = async (messageId) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) {
      throw new Error('Message not found')
    }
    
    const message = messages.value[messageIndex]
    if (message.role !== 'assistant') {
      throw new Error('Can only regenerate assistant messages')
    }
    
    // Find the previous user message
    let userMessage = null
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages.value[i].role === 'user') {
        userMessage = messages.value[i]
        break
      }
    }
    
    if (!userMessage) {
      throw new Error('No user message found to regenerate from')
    }
    
    // Remove the old assistant message
    messages.value.splice(messageIndex, 1)
    
    // Regenerate with the same user message
    await sendMessage(userMessage.content, {
      provider: message.provider,
      model: message.model
    })
  }
  
  const stopGeneration = () => {
    if (streamingResponse.value) {
      streamingResponse.value.isStreaming = false
      streamingResponse.value = null
    }
    
    isLoading.value = false
    currentActivity.value = ''
    
    console.log('⏹️ Generation stopped')
  }
  
  const clearMessages = () => {
    messages.value = []
    error.value = null
    currentActivity.value = ''
    streamingResponse.value = null
    orchestrationPlan.value = null
    
    console.log('🧹 Messages cleared')
  }
  
  const setProvider = (providerId) => {
    const provider = availableProviders.value.find(p => p.id === providerId)
    if (provider && provider.status === 'healthy') {
      currentProvider.value = providerId
      
      // Save to localStorage
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('digi-setu-ai-provider', providerId)
      }
      
      console.log('🔄 AI provider changed to:', provider.name)
    } else {
      throw new Error('Provider not available or unhealthy')
    }
  }
  
  const getProviderStatus = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await $fetch('/api/v1/chat/providers/status')
      // availableProviders.value = response.providers
      
      // Mock implementation - simulate some status changes
      availableProviders.value.forEach(provider => {
        // Randomly simulate status changes for demo
        provider.status = Math.random() > 0.1 ? 'healthy' : 'unhealthy'
      })
      
      console.log('📊 Provider status updated')
      return availableProviders.value
    } catch (err) {
      console.error('Failed to get provider status:', err)
      throw err
    }
  }
  
  const exportConversation = (format = 'json') => {
    const exportData = {
      messages: messages.value,
      provider: currentProvider.value,
      timestamp: new Date().toISOString(),
      total_messages: messages.value.length
    }
    
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `digi-setu-conversation-${Date.now()}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
    
    console.log('📤 Conversation exported')
  }
  
  // Load saved provider preference
  const loadSavedProvider = () => {
    if (typeof localStorage !== 'undefined') {
      try {
        const saved = localStorage.getItem('digi-setu-ai-provider')
        if (saved && availableProviders.value.find(p => p.id === saved)) {
          currentProvider.value = saved
        }
      } catch (err) {
        console.warn('Failed to load saved provider:', err)
      }
    }
  }
  
  // Initialize
  loadSavedProvider()
  
  // Periodically check provider status
  if (typeof window !== 'undefined') {
    setInterval(() => {
      getProviderStatus().catch(console.error)
    }, 30000) // Check every 30 seconds
  }
  
  return {
    // State
    messages: readonly(messages),
    isLoading: readonly(isLoading),
    currentActivity: readonly(currentActivity),
    currentProvider: readonly(currentProvider),
    availableProviders: readonly(availableProviders),
    error: readonly(error),
    streamingResponse: readonly(streamingResponse),
    orchestrationPlan: readonly(orchestrationPlan),
    
    // Computed
    healthyProviders,
    currentProviderInfo,
    isStreaming,
    hasError,
    
    // Methods
    sendMessage,
    regenerateMessage,
    stopGeneration,
    clearMessages,
    setProvider,
    getProviderStatus,
    exportConversation,
    loadSavedProvider
  }
}
