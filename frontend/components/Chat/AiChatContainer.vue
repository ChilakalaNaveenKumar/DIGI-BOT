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
          
          <!-- Client-Only AI SDK Integration -->
          <ClientOnly>
          
          <!-- AI SDK 5 Debug Info -->
          <div class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm">
            <p class="text-blue-700 dark:text-blue-300">
              🚀 AI SDK 5 Chat Class | 
              Status: {{ chat.status }} | 
              Messages: {{ chat.messages.length }} | 
              Provider: {{ selectedProvider }} |
              Error: {{ chat.error ? chat.error.message : 'None' }}
            </p>
          </div>

          <!-- Welcome State -->
          <div v-if="chat.messages.length === 0" class="text-center py-16">
            <div class="relative mb-8">
              <div class="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl mx-auto flex items-center justify-center shadow-2xl hover:scale-105 transition-transform duration-300">
                <Icon name="lucide:sparkles" size="32" class="text-white" />
              </div>
              <div class="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-bounce"></div>
            </div>
            <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              AI SDK 5 Chat Ready! 🚀
            </h2>
            <p class="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto text-lg leading-relaxed">
              Using the new Chat class from AI SDK 5. Upload documents, paste text, or describe what you'd like to create.
            </p>
          </div>

          <!-- AI SDK Error Display -->
          <div v-if="chat.error" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl">
            <div class="flex items-center space-x-3">
              <Icon name="lucide:alert-circle" class="w-5 h-5 text-red-500" />
              <div class="flex-1">
                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                  Connection Error
                </h3>
                <p class="text-sm text-red-600 dark:text-red-300 mt-1">
                  {{ chat.error.message || chat.error || 'Failed to connect to AI service' }}
                </p>
              </div>
              <button 
                @click="reloadChat()" 
                class="px-3 py-1 text-sm bg-red-100 dark:bg-red-800 text-red-700 dark:text-red-200 rounded-lg hover:bg-red-200 dark:hover:bg-red-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>

            <!-- AI SDK Messages -->
            <div class="space-y-8">
                          <AiMessage
              v-for="(message, index) in chat.messages"
              :key="message.id || index"
              :message="message"
              :is-loading="chat.status === 'streaming' && message === chat.messages[chat.messages.length - 1]"
              :provider="selectedProvider"
              :on-reload="reloadChat"
              :on-stop="() => chat.stop()"
              class="mb-4"
            />
            </div>
            
            <!-- SSR Fallback -->
            <template #fallback>
              <div class="flex items-center justify-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span class="ml-3 text-gray-600 dark:text-gray-300">Loading AI Chat...</span>
              </div>
            </template>
          </ClientOnly>
        </div>
      </div>
    </main>

    <!-- AI SDK Input Area -->
    <footer class="sticky bottom-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border-t border-gray-200 dark:border-gray-700 shadow-lg">
      <div class="max-w-5xl mx-auto px-6 py-6">
        <ClientOnly>
                  <AiInput 
          v-model="input"
          :loading="chat.status === 'streaming'"
          :providers="providers"
          :selected-provider="selectedProvider"
          :on-submit="handleSubmit"
          @file-upload="handleFileUpload"
        />
          <!-- Input fallback for SSR -->
          <template #fallback>
            <div class="flex items-center space-x-3">
              <div class="flex-1 h-12 bg-gray-100 dark:bg-gray-800 rounded-2xl animate-pulse"></div>
              <div class="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-2xl animate-pulse"></div>
            </div>
          </template>
        </ClientOnly>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { Chat } from '@ai-sdk/vue'  // ✅ AI SDK 5 - Use Chat class
import { Sun, Moon } from 'lucide-vue-next'
import { useTheme } from '~/composables/useTheme.js'
import ProviderSelector from '../UI/ProviderSelector.vue'
import AiMessage from './AiMessage.vue'
import AiInput from './AiInput.vue'

// Theme management
const { theme, toggleTheme } = useTheme()

// State
const selectedProvider = ref('openai')
const messagesContainer = ref(null)
const input = ref('')

// AI SDK 5 - Chat Class Implementation
const chat = new Chat({
  api: '/api/chat',  // Nuxt API route (proxy to Python backend)
  onError: (err) => {
    console.error('❌ AI SDK 5 Chat Error:', err)
  },
  onFinish: (message) => {
    console.log('✅ AI SDK 5 Chat Success:', message)
    scrollToBottom()
  }
})

const providers = [
  { id: 'openai', name: 'GPT-5', icon: 'openai' },
  { id: 'anthropic', name: 'Claude 4 Opus', icon: 'claude' },
  { id: 'grok', name: 'Grok-4', icon: 'xai' }
]

// Custom reload function for AI SDK 5
const reloadChat = () => {
  console.log('🔄 Reloading chat...')
  // Clear current messages and restart
  if (chat.messages && chat.messages.length > 0) {
    // Get the last user message
    const lastUserMessage = [...chat.messages].reverse().find(msg => msg.role === 'user')
    if (lastUserMessage) {
      // Resend the last user message
      chat.sendMessage(lastUserMessage.content, {
        data: { provider: selectedProvider.value }
      })
    }
  }
}

// AI SDK 5 - Form submission handler
const handleSubmit = (e) => {
  e?.preventDefault()
  if (!input.value?.trim() || chat.status === 'streaming') return

  console.log('📤 Sending message with provider:', selectedProvider.value)
  
  // AI SDK 5 - Use sendMessage method
  chat.sendMessage({ 
    text: input.value.trim(),
    data: { provider: selectedProvider.value }  // Send provider info
  })
  input.value = ''
}

// Watch provider changes
watch(selectedProvider, (newProvider) => {
  console.log('Provider changed to:', newProvider)
})

// Provider management
const handleProviderChange = (newProvider) => {
  selectedProvider.value = newProvider
}

// File handling - Enhanced with AI SDK support
const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('File uploaded:', file.name)
    // AI SDK supports file uploads through append
    try {
      await append({
        role: 'user',
        content: `Uploaded file: ${file.name}`,
        experimental_attachments: [
          {
            name: file.name,
            contentType: file.type,
            url: URL.createObjectURL(file)
          }
        ]
      })
    } catch (error) {
      console.error('File upload error:', error)
    }
  }
}

// Utility functions
const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-5 (1M tokens)',
    'grok': 'Grok-4 (256k tokens)', 
    'anthropic': 'Claude 4 Opus (200k tokens)'
  }
  return names[provider] || 'GPT-5'
}

// AI SDK handles ID generation automatically

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
