<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
    <!-- Enhanced Header -->
    <header class="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-gray-200/50 shadow-sm">
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
              <h1 class="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                Digi Setu AI
              </h1>
              <p class="text-sm text-gray-600 flex items-center">
                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                {{ getProviderName(currentProvider) }} • {{ connectionStatus }}
              </p>
            </div>
          </div>
          
          <ProviderSelector 
            v-model="selectedProvider" 
            @change="handleProviderChange"
          />
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
              <span class="text-white text-3xl">🎯</span>
            </div>
            <div class="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-bounce"></div>
          </div>
          <h2 class="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-4">
            Ready to transform your content?
          </h2>
          <p class="text-gray-600 max-w-2xl mx-auto text-lg leading-relaxed mb-8">
            Upload documents, paste text, or describe what you'd like to create. I'll help you build interactive learning experiences with AI.
          </p>
          
          <!-- Sample Actions -->
          <div class="flex flex-wrap gap-3 justify-center max-w-2xl mx-auto">
            <button
              v-for="sample in samplePrompts"
              :key="sample.text"
              @click="input = sample.text"
              class="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 hover:text-blue-600 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 shadow-sm hover:shadow-md"
            >
              <span>{{ sample.emoji }}</span>
              <span>{{ sample.label }}</span>
            </button>
          </div>
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
    <footer class="sticky bottom-0 bg-white/95 backdrop-blur-xl border-t border-gray-200/50 shadow-lg">
      <div class="max-w-5xl mx-auto px-6 py-6">
        <ChatInput
          v-model="input"
          :loading="isLoading"
          :uploaded-file="uploadedFile"
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
import MessageBubble from './MessageBubble.vue'
import ThinkingIndicator from './ThinkingIndicator.vue'
import ChatInput from './ChatInput.vue'
import ProviderSelector from '../UI/ProviderSelector.vue'

const config = useRuntimeConfig()

// State management
const messages = ref([])
const input = ref('')
const isLoading = ref(false)
const isThinking = ref(false)
const thinkingStage = ref('')
const selectedProvider = ref('openai')
const currentProvider = ref('openai')
const connectionStatus = ref('Ready')
const uploadedFile = ref(null)
const messagesContainer = ref(null)

// Enhanced sample prompts
const samplePrompts = ref([
  { label: 'Explain a concept', text: 'Explain photosynthesis in an engaging way', emoji: '💡' },
  { label: 'Create a quiz', text: 'Create an interactive quiz about the solar system', emoji: '❓' },
  { label: 'Make a timeline', text: 'Create a timeline of World War II events', emoji: '📅' },
  { label: 'Build a diagram', text: 'Create a flowchart showing how rain forms', emoji: '🌧️' }
])

// Enhanced submission with thinking process
const handleSubmit = async () => {
  if (!input.value.trim() || isLoading.value) return

  const userMessage = {
    id: generateId(),
    role: 'user',
    content: input.value.trim(),
    timestamp: new Date(),
    file: uploadedFile.value
  }

  messages.value.push(userMessage)
  const currentInput = input.value
  input.value = ''
  isLoading.value = true
  
  // Enhanced thinking process
  isThinking.value = true
  await simulateThinking()

  try {
    const response = await $fetch(`${config.public.apiBase}/chat`, {
      method: 'POST',
      body: {
        messages: messages.value.map(m => ({ 
          role: m.role, 
          content: m.content
        })),
        provider: selectedProvider.value
      }
    })

    const assistantMessage = {
      id: generateId(),
      role: 'assistant',
      content: response.response || 'No response received',
      timestamp: new Date(),
      thinking: 'I analyzed your request and selected the best approach to provide a comprehensive answer.',
      components: []
    }

    messages.value.push(assistantMessage)
    currentProvider.value = response.provider || selectedProvider.value
    
  } catch (error) {
    console.error('Chat error:', error)
    const errorMessage = {
      id: generateId(),
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
    connectionStatus.value = 'Error'
  } finally {
    isLoading.value = false
    isThinking.value = false
    uploadedFile.value = null
    await scrollToBottom()
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
    'openai': 'GPT-4',
    'grok': 'Grok',
    'anthropic': 'Claude'
  }
  return names[provider] || 'GPT-4'
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