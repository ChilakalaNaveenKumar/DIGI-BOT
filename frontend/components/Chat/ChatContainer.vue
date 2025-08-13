<template>
  <div class="min-h-screen bg-white dark:bg-gray-900">
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
                {{ getProviderName(currentProvider) }} • {{ connectionStatus }}
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

    <!-- Enhanced Messages Area -->
    <main class="max-w-5xl mx-auto flex-1">
      <div class="px-6 py-8 min-h-[calc(100vh-200px)]" ref="messagesContainer">
        
        <!-- Enhanced Welcome State -->
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

        <!-- Enhanced Chat Messages -->
        <div class="space-y-8">
          <MessageBubble
            v-for="message in messages"
            :key="message.id"
            :message="message"
            :provider="currentProvider"
            @regenerate="handleRegenerate"
            @copy="handleCopy"
            @export="handleExport"
            @like="handleLike"
          />

          <!-- Enhanced Thinking Indicator -->
          <ThinkingIndicator 
            v-if="isThinking"
            :provider="selectedProvider"
            :stage="thinkingStage"
          />
        </div>
      </div>
    </main>

    <!-- Enhanced Input Area (Fixed Bottom) -->
    <footer class="sticky bottom-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border-t border-gray-200 dark:border-gray-700 shadow-lg">
      <div class="max-w-5xl mx-auto px-6 py-6">
        <ChatInput
          v-model="input"
          :loading="isLoading"
          :uploaded-file="uploadedFile"
          :selected-provider="getProviderName(selectedProvider)"
          @submit="handleSubmit"
          @file-upload="handleFileUpload"
          @file-remove="removeFile"
        />
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { Sun, Moon } from 'lucide-vue-next'
import MessageBubble from './MessageBubble.vue'
import ThinkingIndicator from './ThinkingIndicator.vue'
import ChatInput from './ChatInput.vue'
import ProviderSelector from '../UI/ProviderSelector.vue'
import { useTheme } from '~/composables/useTheme.js'
import { useAiChat } from '~/composables/useAiChat.ts'

const config = useRuntimeConfig()

// Theme management
const { theme, toggleTheme } = useTheme()

// AI SDK Chat management
const { messages, isLoading, sendMessage, reload, selectedProvider: aiSelectedProvider } = useAiChat()

// Local state
const input = ref('')
const isThinking = ref(false)
const thinkingStage = ref('')
const selectedProvider = ref('openai')
const currentProvider = ref('openai')
const connectionStatus = ref('Ready')
const uploadedFile = ref(null)
const messagesContainer = ref(null)



// AI SDK-style submission
const handleSubmit = async () => {
  if (!input.value.trim() || isLoading.value) return

  // Enhanced thinking process
  isThinking.value = true
  await simulateThinking()

  try {
    await sendMessage(input.value.trim())
    input.value = ''
    uploadedFile.value = null
    await scrollToBottom()
  } catch (error) {
    console.error('Chat error:', error)
    connectionStatus.value = 'Error'
  } finally {
    isThinking.value = false
  }
}

// Enhanced thinking simulation
const simulateThinking = async () => {
  const stages = [
    { text: 'Analyzing your content...', delay: 800 },
    { text: 'Understanding context and requirements...', delay: 1000 },
    { text: 'Selecting optimal approach...', delay: 700 },
    { text: 'Generating response...', delay: 900 },
    { text: 'Finalizing answer...', delay: 500 }
  ]
  
  for (const stage of stages) {
    thinkingStage.value = stage.text
    await new Promise(resolve => setTimeout(resolve, stage.delay))
  }
}

// Provider management
const handleProviderChange = (newProvider) => {
  selectedProvider.value = newProvider
  currentProvider.value = newProvider
  aiSelectedProvider.value = newProvider // Sync with AI SDK
  connectionStatus.value = 'Connecting...'
  
  setTimeout(() => {
    connectionStatus.value = 'Ready'
  }, 1000)
}

// File handling
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    uploadedFile.value = file
  }
}

const removeFile = () => {
  uploadedFile.value = null
}

// Message actions
const handleRegenerate = (message) => {
  console.log('Regenerating message:', message.id)
}

const handleCopy = (message) => {
  console.log('Message copied:', message.id)
}

const handleExport = (message) => {
  console.log('Exporting message:', message.id)
}

const handleLike = (message) => {
  console.log('Message liked:', message.id)
}

// Utility functions
const generateId = () => Date.now() + '-' + Math.random().toString(36).substr(2, 9)

const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-5',
    'grok': 'Grok 4',
    'anthropic': 'Claude 4'
  }
  return names[provider] || 'GPT-5'
}

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
  handleProviderChange('openai')
})
</script>