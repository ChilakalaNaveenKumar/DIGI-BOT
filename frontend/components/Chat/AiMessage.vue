<template>
  <div class="group relative animate-fade-in">
    <!-- AI Message -->
    <div v-if="message.role === 'assistant'" class="flex items-start space-x-4">
      <!-- Real Provider Icon Avatar -->
      <div class="relative flex-shrink-0">
        <div class="w-10 h-10 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-2xl flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-200">
          <ProviderIcon :provider="provider" :size="24" />
        </div>
        <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-800" />
      </div>
      
      <!-- Message Content -->
      <div class="flex-1 max-w-4xl space-y-4">
        <!-- Thinking Process (AI SDK Style) -->
        <div v-if="isLoading && message.content === ''" class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 border border-blue-200 dark:border-gray-600 rounded-2xl p-4 shadow-sm">
          <div class="flex items-center space-x-2 mb-3">
            <div class="flex space-x-1">
              <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce" />
              <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.15s" />
              <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.3s" />
            </div>
            <span class="text-sm font-medium text-blue-700 dark:text-blue-300 flex items-center gap-2">
              <Icon name="lucide:brain" size="16" class="text-blue-600 dark:text-blue-400" />
              AI is thinking...
            </span>
          </div>
          <p class="text-sm text-blue-600 dark:text-blue-400 italic leading-relaxed">Processing your request...</p>
        </div>
        
        <!-- AI SDK 5 - Reasoning Section -->
        <div v-if="hasReasoning" class="mb-6">
          <div class="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden bg-gray-50 dark:bg-gray-800/50">
            <!-- Thinking Header (Always Visible) -->
            <button 
              class="w-full flex items-center justify-between p-4 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors"
              @click="toggleReasoning"
            >
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                <div class="flex flex-col items-start">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ getReasoningHeader() }}</span>
                  <span class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Click to expand reasoning</span>
                </div>
              </div>
              <ChevronDown 
                :class="['w-5 h-5 text-gray-500 transition-transform duration-200', showReasoning ? 'rotate-0' : '-rotate-90']" 
              />
            </button>
            
            <!-- Reasoning Content (Collapsible) -->
            <div v-if="showReasoning" class="border-t border-gray-200 dark:border-gray-600">
              <div class="p-4 bg-white dark:bg-gray-900">
                <div class="prose dark:prose-invert max-w-none text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  <AiCodeBlock :content="reasoningParts[0]?.text" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Response with AI SDK 5 Rendering -->
        <div v-if="message.parts || message.content" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden">
          <!-- AI SDK 5 - Content with Parts Rendering -->
          <div class="p-6 space-y-4">
            <!-- Handle AI SDK 5 message parts -->
            <div v-for="(part, partIndex) in textParts" :key="`${message.id}-text-${partIndex}`">
              <DigiSetuCodeBlock :content="part.text" />
            </div>
            
            <!-- Handle tool calls with enhanced display -->
            <div 
              v-for="(part, partIndex) in toolParts" 
              :key="`${message.id}-tool-${partIndex}`" 
              class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 my-3"
            >
              <div class="flex items-center space-x-2 mb-3">
                <div class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                  <Icon name="lucide:wrench" size="14" class="text-white" />
                </div>
                <strong class="text-blue-700 dark:text-blue-300 font-medium">{{ getToolDisplayName(part) }}</strong>
                <span class="text-xs bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-300 px-2 py-1 rounded-full">
                  {{ part.state || 'executed' }}
                </span>
              </div>
              
              <!-- Tool Input -->
              <div v-if="part.input" class="bg-white dark:bg-gray-800 rounded-lg p-3 mb-3 border border-gray-200 dark:border-gray-600">
                <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Input:</div>
                <pre class="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ JSON.stringify(part.input, null, 2) }}</pre>
              </div>
              
              <!-- Tool Output -->
              <div v-if="part.output" class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800">
                <div class="text-xs font-medium text-green-600 dark:text-green-400 mb-2">Output:</div>
                <AiCodeBlock :content="typeof part.output === 'string' ? part.output : JSON.stringify(part.output, null, 2)" />
              </div>
              
              <!-- Tool Error -->
              <div v-if="part.errorText" class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-200 dark:border-red-800">
                <div class="text-xs font-medium text-red-600 dark:text-red-400 mb-2">Error:</div>
                <div class="text-sm text-red-700 dark:text-red-300">{{ part.errorText }}</div>
              </div>
            </div>
            
            <!-- Fallback for old message format -->
            <AiCodeBlock v-if="!message.parts && message.content" :content="message.content" />
          </div>
          
          <!-- Enhanced Action Bar -->
          <div class="border-t border-gray-100 dark:border-gray-600 px-6 py-4 bg-gray-50/50 dark:bg-gray-700/50 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all duration-300">
            <div class="flex space-x-4">
              <button class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Copy message" @click="copyMessage">
                <Copy class="w-4 h-4" />
              </button>
              <button class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Regenerate" @click="regenerateMessage">
                <RotateCcw class="w-4 h-4" />
              </button>
              <button v-if="isLoading && props.onStop" class="p-2 text-red-400 dark:text-red-500 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all duration-200" title="Stop generation" @click="props.onStop">
                <Icon name="lucide:square" class="w-4 h-4" />
              </button>
              <button class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Export" @click="exportMessage">
                <Download class="w-4 h-4" />
              </button>
              <button class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Like" @click="likeMessage">
                <Heart class="w-4 h-4" />
              </button>
            </div>
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatTime(message.createdAt) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- User Message -->
    <div v-else class="flex items-start space-x-4 justify-end">
      <div class="max-w-2xl">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl px-6 py-4 shadow-lg hover:shadow-xl transition-shadow">
          <p class="text-sm whitespace-pre-wrap leading-relaxed">{{ message.content }}</p>
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400 mt-2 text-right">{{ formatTime(message.createdAt) }}</div>
      </div>
      
      <div class="w-10 h-10 bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0">
        <Icon name="lucide:user" size="20" class="text-white" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Copy, RotateCcw, Download, Heart, ChevronDown } from 'lucide-vue-next'
import ProviderIcon from '../UI/ProviderIcon.vue'
import DigiSetuCodeBlock from './DigiSetuCodeBlock.vue'

const props = defineProps({
  message: {
    type: Object,
    default: () => ({})
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  provider: {
    type: String,
    default: 'openai'
  },
  // AI SDK integration props
  onReload: {
    type: Function,
    default: () => {}
  },
  onStop: {
    type: Function,
    default: () => {}
  }
})

const emit = defineEmits(['regenerate', 'copy', 'export', 'like'])

// Reactive state for reasoning toggle
const showReasoning = ref(false)

// Toggle reasoning display
const toggleReasoning = () => {
  showReasoning.value = !showReasoning.value
}

// Message part analysis
const textParts = computed(() => {
  if (!props.message || !props.message.parts || !Array.isArray(props.message.parts)) return []
  return props.message.parts.filter(part => part && part.type === 'text')
})

const reasoningParts = computed(() => {
  if (!props.message || !props.message.parts || !Array.isArray(props.message.parts)) return []
  return props.message.parts.filter(part => part && part.type === 'reasoning')
})

const toolParts = computed(() => {
  if (!props.message || !props.message.parts || !Array.isArray(props.message.parts)) return []
  return props.message.parts.filter(part => part && (part.type?.startsWith('tool-') || part.type === 'dynamic-tool'))
})

// Enhanced content checks
const hasReasoning = computed(() => reasoningParts.value.length > 0)

// Get reasoning header (first sentence or "Thinking...")
const getReasoningHeader = () => {
  if (!reasoningParts.value.length || !reasoningParts.value[0]?.text) {
    return 'Thinking...'
  }
  
  const fullText = reasoningParts.value[0].text
  // Extract first sentence (look for period, exclamation, or question mark followed by space/newline)
  const firstSentenceMatch = fullText.match(/^[^.!?]*[.!?](?:\s|$)/)
  
  if (firstSentenceMatch) {
    const firstSentence = firstSentenceMatch[0].trim()
    // Limit length to avoid too long headers
    return firstSentence.length > 80 ? firstSentence.substring(0, 80) + '...' : firstSentence
  }
  
  // Fallback: use first 80 characters if no sentence boundary found
  return fullText.length > 80 ? fullText.substring(0, 80) + '...' : fullText
}

// Tool utilities
const getToolDisplayName = (toolPart) => {
  return toolPart.toolName || toolPart.type?.replace('tool-', '') || 'Tool'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format(new Date(timestamp))
}

// Action handlers
const copyMessage = async () => {
  try {
    // AI SDK 5 - Extract text from parts array
    let textContent = ''
    if (props.message.parts) {
      textContent = props.message.parts
        .filter(part => part.type === 'text')
        .map(part => part.text)
        .join('')
    } else {
      textContent = props.message.content || ''
    }
    
    await navigator.clipboard.writeText(textContent)
    console.log('Message copied to clipboard')
    emit('copy', props.message)
  } catch (err) {
    console.error('Failed to copy message:', err)
  }
}

const regenerateMessage = () => {
  // Use AI SDK reload function if available, otherwise emit event
  if (props.onReload) {
    props.onReload()
  } else {
    emit('regenerate', props.message)
  }
}

const exportMessage = () => {
  emit('export', props.message)
}

const likeMessage = () => {
  emit('like', props.message)
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

