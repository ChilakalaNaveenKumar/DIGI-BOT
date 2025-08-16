<template>
  <div class="ds-chat-container">
    <!-- AI Chat Interface -->
    <ClientOnly>
      <DigiSetuChatContainer 
        :conversation="currentConversation"
        :messages="messages"
        :is-loading="isLoading"
        :current-activity="currentActivity"
        @send-message="handleSendMessage"
        @regenerate-message="handleRegenerateMessage"
      />
      <template #fallback>
        <div class="ds-loading-state">
          <div class="ds-loading-spinner"></div>
          <p>Loading Digi Setu AI...</p>
        </div>
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DigiSetuChatContainer from '~/components/Chat/DigiSetuChatContainer.vue'

interface Message {
  id: string
  role: string
  content: string
  timestamp: string
  files?: unknown[]
  provider?: string
  selectedModel?: string
  activities?: unknown[]
  reasoning?: string
  isStreaming?: boolean
  error?: boolean
}

interface MessageData {
  content: string
  files?: unknown[]
}

// Initialize reactive state with default values
const currentConversation = ref<Record<string, unknown> | undefined>(undefined)
const messages = ref<Message[]>([])
const isLoading = ref(false)
const currentActivity = ref<string | undefined>(undefined)

// Methods
const handleSendMessage = async (messageData: MessageData) => {
  console.log('Send message:', messageData)
  
  // Set loading state
  isLoading.value = true
  startLoadingTimeout()
  
  try {
    // Add user message to messages
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageData.content,
      timestamp: new Date().toISOString(),
      files: messageData.files
    }
    
    messages.value.push(userMessage)
    
    // Call the backend API
    currentActivity.value = `Connecting to AI orchestrator...`
    
    // Use streaming endpoint for real-time thought process
    const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: messageData.content,
        conversation_id: currentConversation.value?.id || null,
        project_id: null,
        provider: "openai",
        model: null,
        files: messageData.files,
        ai_settings: null,
        stream: true
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    // Create AI message placeholder for streaming
    const aiMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      provider: 'openai',
      selectedModel: 'openai',
      activities: [],  // Will be populated as we stream
      reasoning: '',
      isStreaming: true
    }
    
    messages.value.push(aiMessage)
    const messageIndex = messages.value.length - 1
    
    // Process streaming response
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    if (reader) {
      let buffer = ''
      
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'activity') {
                // Add thought step in real-time
                currentActivity.value = data.content
                const message = messages.value[messageIndex]
                if (message && message.activities) {
                  message.activities.push({
                    content: data.content,
                    content_type: data.content_type || 'text',
                    metadata: data.metadata || {},
                    timestamp: new Date().toISOString(),
                    isLoading: false
                  })
                }
              } else if (data.type === 'content') {
                // Add content chunk
                const message = messages.value[messageIndex]
                if (message) {
                  message.content += data.content
                  message.provider = data.provider
                }
              } else if (data.type === 'done') {
                // Streaming complete
                const message = messages.value[messageIndex]
                if (message) {
                  message.isStreaming = false
                }
                currentActivity.value = undefined
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', line)
            }
          }
        }
      }
    }
    
  } catch (error) {
    console.error('Error calling backend API:', error)
    
    // Show error message
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    const aiMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `Sorry, I'm having trouble connecting to the AI services right now. Error: ${errorMessage}`,
      timestamp: new Date().toISOString(),
      error: true
    }
    
    messages.value.push(aiMessage)
  } finally {
    // Always reset loading state when done
    isLoading.value = false
    currentActivity.value = undefined
    if (loadingTimeout) clearTimeout(loadingTimeout)
  }
}

const handleRegenerateMessage = (messageId: string) => {
  console.log('Regenerate message:', messageId)
  // TODO: Implement message regeneration
}

// Emergency function to reset loading state
const resetLoadingState = () => {
  isLoading.value = false
  currentActivity.value = undefined
  console.log('Loading state manually reset')
}

// Auto-reset loading state if stuck for too long
let loadingTimeout: NodeJS.Timeout | null = null
const startLoadingTimeout = () => {
  if (loadingTimeout) clearTimeout(loadingTimeout)
  loadingTimeout = setTimeout(() => {
    if (isLoading.value) {
      console.warn('Loading state stuck, auto-resetting...')
      resetLoadingState()
    }
  }, 60000) // 60 second safety timeout
}

// Load composable only on client side to avoid hydration issues
onMounted(async () => {
  // Expose reset function globally for debugging
  if (typeof window !== 'undefined') {
    (window as typeof window & { resetDigiSetuLoading: () => void }).resetDigiSetuLoading = resetLoadingState
  }
})

// Page metadata
useHead({
  title: 'Digi Setu AI - Interactive Learning Platform',
  meta: [
    { name: 'description', content: 'Transform static content into interactive learning experiences with AI' }
  ]
})
</script>

<style scoped>
.ds-chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ds-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
  color: var(--ds-text-secondary);
}

.ds-loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--ds-border-primary);
  border-top: 2px solid var(--ds-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
