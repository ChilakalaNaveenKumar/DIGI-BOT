<template>
  <div class="chart-test-page">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">
        Chart.js Direct Streaming Test
      </h1>
      
      <!-- Test Messages like Chat Interface -->
      <div class="messages-container space-y-6">
        <!-- Test Buttons -->
        <div class="test-controls">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h3 class="font-semibold mb-3">Quick Tests</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <UiButton
                @click="sendTestMessage('pie')"
                :disabled="isLoading"
                variant="primary"
                size="sm"
              >
                📊 Pie Chart Test
              </UiButton>
              
              <UiButton
                @click="sendTestMessage('bar')"
                :disabled="isLoading"
                variant="primary"
                size="sm"
              >
                📈 Bar Chart Test
              </UiButton>
              
              <UiButton
                @click="sendTestMessage('line')"
                :disabled="isLoading"
                variant="primary"
                size="sm"
              >
                📉 Line Chart Test
              </UiButton>
            </div>
          </div>
        </div>
        
        <!-- Messages Display (like ChatContainer) -->
        <div v-for="message in messages" :key="message.id" class="message">
          <div class="message-container">
            <div class="message-avatar">
              <UiAvatar 
                v-if="message.role === 'assistant'"
                icon="lucide:cpu"
                variant="primary"
                size="md"
              />
              <UiAvatar 
                v-else
                initials="You"
                variant="secondary"
                size="md"
              />
            </div>
            
            <div class="message-content">
              <div class="message-header">
                <span class="message-author">
                  {{ message.role === 'assistant' ? 'Claude (Direct)' : 'You' }}
                </span>
                <span class="message-time">
                  {{ formatTime(message.timestamp) }}
                </span>
              </div>
              
              <div class="message-body">
                <UiLoadingDots v-if="message.isLoading" size="sm" />
                
                <UiStreamingMarkdown
                  v-else
                  :content="message.content"
                  :is-streaming="message.isLoading"
                  :show-cursor="message.isLoading"
                  mode="dynamic"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Input Area -->
        <div class="input-area">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div class="flex gap-3">
              <input
                v-model="customMessage"
                placeholder="Type your message..."
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                @keyup.enter="sendCustomMessage"
                :disabled="isLoading"
              />
              <UiButton
                @click="sendCustomMessage"
                :disabled="isLoading || !customMessage.trim()"
                variant="primary"
              >
                Send
              </UiButton>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Debug Info -->
      <div v-if="debugInfo" class="debug-info mt-8">
        <details class="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
          <summary class="cursor-pointer font-medium">Debug Information</summary>
          <pre class="mt-4 text-sm overflow-auto">{{ JSON.stringify(debugInfo, null, 2) }}</pre>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Reactive state like ChatContainer
const isLoading = ref(false)
const messages = ref([])
const customMessage = ref('')
const debugInfo = ref(null)

// Helper function to format time
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

// Test messages
const testMessages = {
  pie: "Analyze social media market share: Instagram 45%, TikTok 30%, Facebook 15%, Twitter 10%. Create a visualization and provide insights about market dynamics.",
  bar: "Our quarterly sales performance: Q1 $120k, Q2 $150k, Q3 $180k, Q4 $200k. Visualize this data and analyze growth trends.",
  line: "Company user growth: Jan 1000, Feb 1500, Mar 2200, Apr 3100, May 4500 users. Create a trend visualization and analyze growth patterns."
}

// Send predefined test message
const sendTestMessage = (type) => {
  const message = testMessages[type]
  if (message) {
    sendMessage(message)
  }
}

// Send custom message
const sendCustomMessage = () => {
  if (customMessage.value.trim()) {
    sendMessage(customMessage.value.trim())
    customMessage.value = ''
  }
}

// Main message sending function (like ChatContainer)
const sendMessage = async (messageText) => {
  if (isLoading.value) return
  
  isLoading.value = true
  
  // Get runtime config for API base
  const config = useRuntimeConfig()
  
  // Add user message
  const userMessage = {
    id: Date.now() + '-user',
    role: 'user',
    content: messageText,
    timestamp: Date.now(),
    isLoading: false
  }
  messages.value.push(userMessage)
  
  // Add assistant message (initially loading)
  const assistantMessage = {
    id: Date.now() + '-assistant',
    role: 'assistant',
    content: '',
    timestamp: Date.now(),
    isLoading: true
  }
  messages.value.push(assistantMessage)
  
  try {
    // Prepare request
    const requestData = {
      messages: [
        { role: 'user', content: messageText }
      ]
    }
    
    const endpoint = `${config.public.apiBase}/v1/api/direct-chat`
    
    debugInfo.value = {
      endpoint: endpoint,
      request: requestData,
      timestamp: new Date().toISOString()
    }
    
    // Make streaming request
    const response_stream = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    })
    
    if (!response_stream.ok) {
      throw new Error(`HTTP ${response_stream.status}: ${response_stream.statusText}`)
    }
    
    // Process streaming response
    const reader = response_stream.body.getReader()
    const decoder = new TextDecoder()
    
    while (true) {
      const { value, done } = await reader.read()
      
      if (done) {
        break
      }
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6))
            
            if (data.type === 'content') {
              assistantMessage.content += data.content
            } else if (data.type === 'complete') {
              assistantMessage.isLoading = false
            } else if (data.type === 'error') {
              throw new Error(data.content)
            }
          } catch (e) {
            console.error('Error parsing streaming data:', e)
          }
        }
      }
    }
    
  } catch (error) {
    console.error('Error sending message:', error)
    assistantMessage.content = `❌ Error: ${error.message}`
    assistantMessage.isLoading = false
    debugInfo.value = {
      ...debugInfo.value,
      error: error.message,
      stack: error.stack
    }
  } finally {
    isLoading.value = false
  }
}

// Page meta
definePageMeta({
  title: 'Chart.js Test',
  description: 'Test direct streaming with Chart.js components'
})
</script>

<style scoped>
.chart-test-page {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f9fafb, #f3f4f6);
}

.dark .chart-test-page {
  background: linear-gradient(to bottom, #111827, #1f2937);
}

.container {
  max-width: 1200px;
}

/* Message styling like ChatContainer */
.message {
  margin-bottom: 1.5rem;
}

.message-container {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.message-author {
  font-weight: 600;
  color: #374151;
}

.dark .message-author {
  color: #d1d5db;
}

.message-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.dark .message-time {
  color: #9ca3af;
}

.message-body {
  background: white;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.dark .message-body {
  background: #1f2937;
  color: #f3f4f6;
}

.debug-info {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.messages-container {
  max-width: 800px;
  margin: 0 auto;
}

.test-controls {
  margin-bottom: 2rem;
}

.input-area {
  position: sticky;
  bottom: 0;
  background: rgba(249, 250, 251, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 0;
}

.dark .input-area {
  background: rgba(17, 24, 39, 0.95);
}
</style>
