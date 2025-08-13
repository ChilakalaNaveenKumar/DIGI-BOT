<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
    <!-- Enhanced Header -->
    <header class="sticky top-0 z-50 backdrop-blur-xl bg-white/95 dark:bg-gray-900/95 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="max-w-5xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <!-- Enhanced Logo -->
            <div class="relative">
              <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg rotate-3 hover:rotate-0 transition-transform duration-300">
                <span class="text-white font-bold text-lg">DS</span>
              </div>
              <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900 dark:text-white">
                Digi Setu AI
              </h1>
              <p class="text-sm text-gray-600 dark:text-gray-300 flex items-center">
                <span class="w-2 h-2 bg-green-400 rounded-full mr-2 inline-block"></span>
                {{ getProviderName(selectedProvider) }} • Ready
              </p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <button
              @click="toggleTheme"
              class="p-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
              :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
            >
              <Sun v-if="theme === 'dark'" class="w-5 h-5" />
              <Moon v-else class="w-5 h-5" />
            </button>
            
            <ProviderSelector 
              v-model="selectedProvider" 
              @change="handleProviderChange"
            />
          </div>
        </div>
      </div>
    </header>

    <!-- AI SDK Chat Area -->
    <main class="flex-1 overflow-hidden">
      <div class="max-w-5xl mx-auto h-full">
        <div class="px-6 py-8 h-full overflow-y-auto" ref="messagesContainer">
          
          <!-- Welcome State -->
          <div v-if="messages.length === 0" class="text-center py-16">
            <div class="relative mb-8">
              <div class="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl mx-auto flex items-center justify-center shadow-2xl hover:scale-105 transition-transform duration-300">
                <Icon name="lucide:sparkles" size="32" class="text-white" />
              </div>
              <div class="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-bounce"></div>
            </div>
            <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Ready to transform your content?
            </h2>
            <p class="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto text-lg leading-relaxed">
              Upload documents, paste text, or describe what you'd like to create. I'll help you build interactive learning experiences with AI.
            </p>
          </div>

          <!-- AI SDK Messages -->
          <div class="space-y-8">
            <AiMessage
              v-for="message in messages"
              :key="message.id"
              :message="message"
              :is-loading="isLoading && message === messages[messages.length - 1]"
              :provider="selectedProvider"
              class="mb-4"
            />
          </div>
        </div>
      </div>
    </main>

    <!-- AI SDK Input Area -->
    <footer class="sticky bottom-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border-t border-gray-200 dark:border-gray-700 shadow-lg">
      <div class="max-w-5xl mx-auto px-6 py-6">
        <AiInput 
          v-model="input"
          :loading="isLoading"
          :providers="providers"
          :selected-provider="selectedProvider"
          @submit="handleSubmit"
          @file-upload="handleFileUpload"
        />
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
// Using custom implementation for now
// import { useChat } from '@ai-sdk/vue'
import { Sun, Moon } from 'lucide-vue-next'
import { useTheme } from '~/composables/useTheme.js'
import ProviderSelector from '../UI/ProviderSelector.vue'
import AiMessage from './AiMessage.vue'
import AiInput from './AiInput.vue'

// Theme management
const { theme, toggleTheme } = useTheme()

// Custom Chat Implementation (AI SDK style)
const messages = ref([])
const input = ref('')
const isLoading = ref(false)
const error = ref(null)

// State
const selectedProvider = ref('openai')
const messagesContainer = ref(null)

const providers = [
  { id: 'openai', name: 'GPT-4o', icon: 'openai' },
  { id: 'anthropic', name: 'Claude 3.5', icon: 'claude' },
  { id: 'grok', name: 'Grok-2', icon: 'xai' }
]

// Enhanced submission with provider data
const handleSubmit = async (e) => {
  e?.preventDefault()
  if (!input.value?.trim() || isLoading.value) return

  const userMessage = {
    id: generateId(),
    role: 'user',
    content: input.value.trim(),
    createdAt: new Date().toISOString()
  }

  messages.value.push(userMessage)
  const currentInput = input.value
  input.value = ''
  isLoading.value = true

  try {
    // Create assistant message for streaming
    const assistantMessage = {
      id: generateId(),
      role: 'assistant',
      content: '',
      createdAt: new Date().toISOString()
    }
    messages.value.push(assistantMessage)

    // Use backend API (port 8000) with timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 120000) // 2 minute timeout
    
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages.value.slice(0, -1).map(m => ({ 
          role: m.role, 
          content: m.content
        })),
        provider: selectedProvider.value
      }),
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)

    // Handle streaming response
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    const lastMessage = messages.value[messages.value.length - 1]

    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            
            if (data === '[DONE]') {
              console.log('Stream completed successfully')
              break
            }
            
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                lastMessage.content += parsed.content
                await scrollToBottom()
              } else if (parsed.error) {
                console.error('Stream error:', parsed.error)
                lastMessage.content += `\n\n❌ **Error:** ${parsed.error}`
                break
              }
            } catch (parseError) {
              console.warn('Failed to parse chunk:', data)
              // Skip invalid JSON lines but continue streaming
              continue
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
    
  } catch (error) {
    console.error('Chat error:', error)
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      lastMessage.content = `Error: ${error.message}`
    }
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

// Provider management
const handleProviderChange = (newProvider) => {
  selectedProvider.value = newProvider
  console.log('Provider changed to:', newProvider)
}

// File handling
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('File uploaded:', file.name)
    // Handle file upload logic
  }
}

// Utility functions
const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-4o (16k tokens)',
    'grok': 'Grok-2 (32k tokens)', 
    'anthropic': 'Claude 3.5 (8k tokens)'
  }
  return names[provider] || 'GPT-4o'
}

// Utility functions
const generateId = () => Date.now() + '-' + Math.random().toString(36).substr(2, 9)

// Enhanced scroll behavior
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

// Initialize
onMounted(() => {
  selectedProvider.value = 'openai'
})
</script>
