<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
    <!-- Enhanced Header -->
    <header class="sticky top-0 z-50 backdrop-blur-xl bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm opacity-95">
      <div class="max-w-5xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <!-- Enhanced Logo -->
            <div class="relative">
              <div class="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg rotate-3 hover:rotate-0 transition-transform duration-300">
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
          
          <!-- Enhanced Status Bar -->
          <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-2xl border border-blue-200 dark:border-blue-700">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-2">
                  <div class="w-3 h-3 rounded-full animate-pulse" :class="{
                    'bg-green-400': connectionStatus === 'Ready',
                    'bg-blue-400': connectionStatus === 'Generating...',
                    'bg-purple-400': connectionStatus === 'Thinking...',
                    'bg-red-400': connectionStatus === 'Error'
                  }"></div>
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ connectionStatus }}
                  </span>
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  {{ getProviderDisplayName(selectedProvider) }}
                </div>
                <UBadge color="blue" variant="soft" size="xs">
                  AI SDK 5 Enhanced
                </UBadge>
              </div>
              
              <div class="flex items-center space-x-2">
                <UButton 
                  @click="showSettings = !showSettings"
                  size="xs" 
                  variant="ghost"
                  :icon="showSettings ? 'i-lucide-settings-x' : 'i-lucide-settings'"
                />
                <UButton 
                  @click="handleExport"
                  size="xs" 
                  variant="ghost"
                  icon="i-lucide-download"
                  :disabled="messages.length === 0"
                />
                <UButton 
                  @click="handleClear"
                  size="xs" 
                  variant="ghost" 
                  color="red"
                  icon="i-lucide-trash-2"
                  :disabled="messages.length === 0"
                />
              </div>
            </div>
            
            <!-- Settings Panel -->
            <UCollapsible v-model="showSettings">
              <div class="mt-4 pt-4 border-t border-blue-200 dark:border-blue-700">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                      AI Provider
                    </label>
                    <USelectMenu
                      v-model="selectedProvider"
                      :options="providers"
                      option-attribute="name"
                      value-attribute="id"
                      @change="handleProviderChange"
                      size="sm"
                    />
                  </div>
                  <div v-if="providers.find(p => p.id === selectedProvider)?.models?.length > 1">
                    <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Model
                    </label>
                    <USelectMenu
                      v-model="selectedModel"
                      :options="providers.find(p => p.id === selectedProvider)?.models || []"
                      @change="handleModelChange"
                      size="sm"
                    />
                  </div>
                </div>
              </div>
            </UCollapsible>
          </div>

          <!-- Welcome State -->
          <div v-if="messages.length === 0" class="text-center py-20">
            <div class="relative mb-8">
              <div class="w-28 h-28 bg-blue-600 rounded-3xl mx-auto flex items-center justify-center shadow-2xl hover:scale-105 transition-transform duration-500">
                <Sparkles class="w-12 h-12 text-white animate-pulse" />
              </div>
              <div class="absolute -top-2 -right-2 w-8 h-8 bg-green-400 rounded-full animate-bounce flex items-center justify-center">
                <span class="text-white text-xs font-bold">AI</span>
              </div>
            </div>
            <h2 class="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-6">
              Digi Setu AI Enhanced
            </h2>
            <p class="text-gray-600 dark:text-gray-300 max-w-3xl mx-auto text-lg leading-relaxed mb-8">
              Experience the power of AI SDK 5 with reasoning, tool calling, and interactive learning components. 
              Upload documents, ask questions, or create interactive content.
            </p>
            
            <!-- Feature Highlights -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
              <div class="p-4 bg-blue-50 dark:bg-blue-900 rounded-xl border border-blue-200 dark:border-blue-700">
                <div class="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Icon name="lucide:brain" class="w-5 h-5 text-white" />
                </div>
                <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">AI Reasoning</h3>
                <p class="text-sm text-blue-700 dark:text-blue-300">See how AI thinks through problems step by step</p>
              </div>
              
              <div class="p-4 bg-green-50 dark:bg-green-900 rounded-xl border border-green-200 dark:border-green-700">
                <div class="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Icon name="lucide:wrench" class="w-5 h-5 text-white" />
                </div>
                <h3 class="font-semibold text-green-900 dark:text-green-100 mb-2">Tool Calling</h3>
                <p class="text-sm text-green-700 dark:text-green-300">Interactive tables, quizzes, and learning components</p>
              </div>
              
              <div class="p-4 bg-purple-50 dark:bg-purple-900 rounded-xl border border-purple-200 dark:border-purple-700">
                <div class="w-10 h-10 bg-purple-500 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Icon name="lucide:file-up" class="w-5 h-5 text-white" />
                </div>
                <h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-2">Multi-Modal</h3>
                <p class="text-sm text-purple-700 dark:text-purple-300">Upload PDFs, images, and documents</p>
              </div>
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="error" class="mb-6 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-800 rounded-2xl">
            <div class="flex items-center space-x-3">
              <Icon name="lucide:alert-circle" class="w-5 h-5 text-red-500" />
              <div class="flex-1">
                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                  Connection Error
                </h3>
                <p class="text-sm text-red-600 dark:text-red-300 mt-1">
                  {{ error }}
                </p>
              </div>
              <UButton 
                @click="clearError" 
                size="xs"
                color="red"
                variant="soft"
              >
                Retry
              </UButton>
            </div>
          </div>

          <!-- Enhanced Messages -->
          <div class="space-y-6">
            <EnhancedMessageBubble
              v-for="(message, index) in messages"
              :key="message.id || index"
              :message="message"
              :provider="selectedProvider"
              :is-streaming="isLoading && index === messages.length - 1"
              :current-thought="isThinking && index === messages.length - 1 ? currentThought : ''"
              @regenerate="handleRegenerate"
              @stop="handleStop"
              @copy="(msg) => console.log('Copied:', msg.id)"
              @export="(msg) => console.log('Exported:', msg.id)"
              @like="(msg) => console.log('Liked:', msg.id)"
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

    <!-- Enhanced Input Area -->
    <footer class="sticky bottom-0 bg-white dark:bg-gray-900 backdrop-blur-xl border-t border-gray-200 dark:border-gray-700 shadow-lg opacity-95">
      <div class="max-w-5xl mx-auto px-6 py-6">
        <ClientOnly>
          <!-- Uploaded Files Display -->
          <div v-if="uploadedFiles.length > 0" class="mb-4">
            <div class="flex flex-wrap gap-2">
              <div 
                v-for="(file, index) in uploadedFiles" 
                :key="index"
                class="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-3 py-2 rounded-xl border border-blue-200 dark:border-blue-700"
              >
                <Icon name="lucide:file" class="w-4 h-4" />
                <span class="text-sm font-medium">{{ file.filename || 'Uploaded file' }}</span>
                <button 
                  @click="removeFile(index)" 
                  class="p-1 hover:bg-blue-200 dark:hover:bg-blue-800 rounded-full transition-colors"
                >
                  <Icon name="lucide:x" class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>

          <!-- Enhanced Input Form -->
          <form @submit="handleSubmit" class="space-y-3">
            <!-- Input Row -->
            <div class="flex items-end space-x-4">
              <!-- Main Input -->
              <div class="flex-1 relative">
                <textarea
                  v-model="input"
                  :disabled="isLoading"
                  placeholder="Ask me anything, upload files, or request interactive content..."
                  rows="1"
                  class="w-full min-h-[56px] max-h-32 px-6 py-4 pr-16 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm hover:shadow-md transition-all duration-200 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white"
                  @keydown.enter.exact.prevent="handleSubmit"
                  @keydown.enter.shift.exact="input += '\n'"
                  @input="autoResize"
                />
                
                <!-- Character Counter -->
                <div class="absolute bottom-2 right-2 text-xs text-gray-400 dark:text-gray-500">
                  {{ input.length }}/2000
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center space-x-2">
                <!-- File Upload -->
                <label class="cursor-pointer group">
                  <input 
                    type="file" 
                    multiple 
                    accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.gif,.webp,.md,.csv,.xlsx"
                    @change="handleFileUploadEvent"
                    class="hidden"
                  />
                  <div class="p-3 bg-gray-100 dark:bg-gray-700 hover:bg-blue-100 dark:hover:bg-blue-800 rounded-xl border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200 group-hover:scale-105">
                    <Upload class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" />
                  </div>
                </label>

                <!-- Send Button -->
                <button
                  type="submit"
                  :disabled="!input.trim() || isLoading"
                  class="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95 disabled:hover:scale-100"
                >
                  <Icon v-if="isLoading" name="lucide:loader-2" class="w-5 h-5 animate-spin" />
                  <Icon v-else name="lucide:send" class="w-5 h-5" />
                </button>
                
                <!-- Stop Button (when generating) -->
                <button
                  v-if="isLoading"
                  @click="handleStop"
                  type="button"
                  class="p-3 bg-red-500 hover:bg-red-600 text-white rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95"
                >
                  <Icon name="lucide:square" class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                <Icon name="lucide:zap" class="w-3 h-3" />
                <span>AI SDK 5 Enhanced • Reasoning • Tool Calling • Multi-Modal</span>
              </div>
              
              <div class="flex items-center space-x-2">
                <button 
                  @click="input = 'Create an interactive table from this data: [sample data]'"
                  class="px-3 py-1 text-xs bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors"
                >
                  📊 Table
                </button>
                <button 
                  @click="input = 'Create a quiz about this topic'"
                  class="px-3 py-1 text-xs bg-green-50 dark:bg-green-900 text-green-600 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-800 transition-colors"
                >
                  🧠 Quiz
                </button>
                <button 
                  @click="input = 'Explain your reasoning step by step'"
                  class="px-3 py-1 text-xs bg-purple-50 dark:bg-purple-900 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-800 transition-colors"
                >
                  🤔 Reasoning
                </button>
              </div>
            </div>
          </form>
          
          <!-- Input fallback for SSR -->
          <template #fallback>
            <div class="flex items-center space-x-3">
              <div class="flex-1 h-14 bg-gray-100 dark:bg-gray-800 rounded-2xl animate-pulse"></div>
              <div class="w-14 h-14 bg-gray-100 dark:bg-gray-800 rounded-2xl animate-pulse"></div>
            </div>
          </template>
        </ClientOnly>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Sun, Moon, Sparkles, Upload } from 'lucide-vue-next'
import { useTheme } from '~/composables/useTheme.js'
import { useDigiSetuChatSSR } from '~/composables/useDigiSetuChatSSR'
import ProviderSelector from '../UI/ProviderSelector.vue'
import EnhancedMessageBubble from './EnhancedMessageBubble.vue'

// Theme management
const { theme, toggleTheme } = useTheme()

// Enhanced AI SDK 5 Chat with SSR support
const {
  chat,
  messages,
  isLoading,
  error,
  isThinking,
  currentThought,
  input: chatInput,
  selectedProvider,
  selectedModel,
  providers,
  changeProvider,
  changeModel,
  uploadedFiles,
  handleFileUpload,
  removeFile,
  sendMessage,
  regenerateMessage,
  clearChat,
  stopGeneration,
  exportChat,
  scrollToBottom,
  isInitialized,
  clearError
} = useDigiSetuChatSSR()

// Local state
const messagesContainer = ref(null)
const input = ref('')
const showSettings = ref(false)

// Connection status
const connectionStatus = computed(() => {
  if (error.value) return 'Error'
  if (isLoading.value) return 'Generating...'
  if (isThinking.value) return 'Thinking...'
  return 'Ready'
})

// Enhanced form submission
const handleSubmit = async (e) => {
  e?.preventDefault()
  if (!input.value?.trim() || isLoading.value) return

  console.log('📤 Enhanced AI SDK 5 Send:', {
    provider: selectedProvider.value,
    model: selectedModel.value,
    hasFiles: uploadedFiles.value.length > 0,
    reasoning: true
  })
  
  try {
    await sendMessage(input.value.trim(), {
      enableReasoning: true,
      metadata: {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      }
    })
    input.value = ''
  } catch (error) {
    console.error('Send message error:', error)
  }
}

// Provider management
const handleProviderChange = (newProvider) => {
  changeProvider(newProvider)
}

const handleModelChange = (newModel) => {
  changeModel(newModel)
}

// File handling
const handleFileUploadEvent = async (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    await handleFileUpload(files)
  }
}

// Message actions
const handleRegenerate = (messageId) => {
  regenerateMessage(messageId)
}

const handleStop = () => {
  stopGeneration()
}

const handleExport = () => {
  exportChat()
}

const handleClear = () => {
  if (confirm('Are you sure you want to clear the chat history?')) {
    clearChat()
  }
}

// Utility functions
const getProviderDisplayName = (provider) => {
  const providerInfo = providers.find(p => p.id === provider)
  return providerInfo ? `${providerInfo.name} ${providerInfo.description}` : provider
}

const autoResize = (event) => {
  const textarea = event.target
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 128) + 'px'
}

// Auto-scroll on new messages
watch(() => messages.value.length, () => {
  scrollToBottom()
})

// Auto-scroll on thinking updates
watch([isThinking, currentThought], () => {
  if (isThinking.value) {
    scrollToBottom()
  }
})

// Utility functions
const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-5 (128k/64k)',
    'grok': 'Grok-4 (256k/256k)',
    'anthropic': 'Claude-4-Opus (1M/200k)'
  }
  return names[provider] || 'GPT-5 (128k/64k)'
}

// Initialize
onMounted(() => {
  selectedProvider.value = 'openai'
  console.log('🚀 Enhanced AI SDK 5 Chat Container initialized')
})
</script>
