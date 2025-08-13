<template>
  <div class="group relative animate-fade-in">
    <!-- AI Message -->
    <div v-if="message.role === 'assistant'" class="flex items-start space-x-4">
      <!-- Real Provider Icon Avatar -->
      <div class="relative flex-shrink-0">
        <div class="w-10 h-10 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-2xl flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-200">
          <ProviderIcon :provider="provider" :size="24" />
        </div>
        <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-800"></div>
      </div>
      
      <!-- Message Content -->
      <div class="flex-1 max-w-4xl space-y-4">
        <!-- Thinking Process (AI SDK Style) -->
        <div v-if="isLoading && message.content === ''" class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 border border-blue-200 dark:border-gray-600 rounded-2xl p-4 shadow-sm">
          <div class="flex items-center space-x-2 mb-3">
            <div class="flex space-x-1">
              <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce"></div>
              <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.15s"></div>
              <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.3s"></div>
            </div>
            <span class="text-sm font-medium text-blue-700 dark:text-blue-300 flex items-center gap-2">
              <Icon name="lucide:brain" size="16" class="text-blue-600 dark:text-blue-400" />
              AI is thinking...
            </span>
          </div>
          <p class="text-sm text-blue-600 dark:text-blue-400 italic leading-relaxed">Processing your request...</p>
        </div>
        
        <!-- Main Response with AI SDK 5 Rendering -->
        <div v-if="message.parts || message.content" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden">
          <!-- AI SDK 5 - Content with Parts Rendering -->
          <div class="p-6">
            <!-- Handle AI SDK 5 message parts -->
            <div v-for="(part, partIndex) in message.parts" :key="`${message.id}-${part.type}-${partIndex}`">
              <AiCodeBlock v-if="part.type === 'text'" :content="part.text" />
              <!-- Handle tool calls if present -->
              <div v-else-if="part.type.startsWith('tool-')" class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg my-2">
                <strong class="text-blue-700 dark:text-blue-300">Tool Call:</strong> {{ part.toolName || part.type }}
                <pre class="text-xs mt-2 text-blue-600 dark:text-blue-400">{{ JSON.stringify(part, null, 2) }}</pre>
              </div>
            </div>
            
            <!-- Fallback for old message format -->
            <AiCodeBlock v-if="!message.parts && message.content" :content="message.content" />
          </div>
          
          <!-- Enhanced Action Bar -->
          <div class="border-t border-gray-100 dark:border-gray-600 px-6 py-4 bg-gray-50/50 dark:bg-gray-700/50 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all duration-300">
            <div class="flex space-x-4">
              <button @click="copyMessage" class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Copy message">
                <Copy class="w-4 h-4" />
              </button>
              <button @click="regenerateMessage" class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Regenerate">
                <RotateCcw class="w-4 h-4" />
              </button>
              <button v-if="isLoading && props.onStop" @click="props.onStop" class="p-2 text-red-400 dark:text-red-500 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all duration-200" title="Stop generation">
                <Icon name="lucide:square" class="w-4 h-4" />
              </button>
              <button @click="exportMessage" class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Export">
                <Download class="w-4 h-4" />
              </button>
              <button @click="likeMessage" class="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-all duration-200" title="Like">
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
import { Copy, RotateCcw, Download, Heart } from 'lucide-vue-next'
import ProviderIcon from '../UI/ProviderIcon.vue'
import AiCodeBlock from './AiCodeBlock.vue'

const props = defineProps({
  message: Object,
  isLoading: Boolean,
  provider: String,
  // AI SDK integration props
  onReload: Function,
  onStop: Function
})

const emit = defineEmits(['regenerate', 'copy', 'export', 'like'])

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

