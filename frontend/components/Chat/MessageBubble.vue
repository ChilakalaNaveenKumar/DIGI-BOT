<template>
  <div class="group relative animate-fade-in">
    <!-- AI Message -->
    <div v-if="message.role === 'assistant'" class="flex items-start space-x-4">
      <!-- Enhanced Avatar -->
      <div class="relative flex-shrink-0">
        <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-200">
          <span class="text-white text-lg">{{ getProviderEmoji(provider) }}</span>
        </div>
        <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></div>
      </div>
      
      <!-- Message Content -->
      <div class="flex-1 max-w-4xl space-y-4">
        <!-- Thinking Process -->
        <div v-if="message.thinking" class="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-2xl p-4 shadow-sm">
          <div class="flex items-center space-x-2 mb-3">
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span class="text-sm font-medium text-blue-700">💭 Thinking process</span>
          </div>
          <p class="text-sm text-blue-600 italic leading-relaxed">{{ message.thinking }}</p>
        </div>
        
        <!-- Main Response -->
        <div class="bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden">
          <!-- Content with Enhanced Rendering -->
          <div class="p-6">
            <MarkdownRenderer :content="message.content" />
          </div>
          
          <!-- Interactive Components -->
          <div v-if="message.components && message.components.length > 0" class="border-t border-gray-100 p-4 bg-gray-50">
            <div class="text-sm font-medium text-gray-700 mb-3">🎮 Interactive Elements:</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                v-for="component in message.components"
                :key="component.type"
                class="flex items-center space-x-2 p-3 bg-white rounded-xl border hover:border-blue-300 hover:bg-blue-50 transition-all"
              >
                <span>{{ component.emoji }}</span>
                <span class="text-sm">{{ component.label }}</span>
              </button>
            </div>
          </div>
          
          <!-- Enhanced Action Bar -->
          <div class="border-t border-gray-100 px-6 py-4 bg-gray-50/50 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all duration-300">
            <div class="flex space-x-4">
              <button @click="copyMessage" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200" title="Copy message">
                📋
              </button>
              <button @click="regenerateMessage" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200" title="Regenerate">
                🔄
              </button>
              <button @click="exportMessage" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200" title="Export">
                💾
              </button>
              <button @click="likeMessage" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200" title="Like">
                ❤️
              </button>
            </div>
            <span class="text-xs text-gray-500">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced User Message -->
    <div v-else class="flex items-start space-x-4 justify-end">
      <div class="max-w-2xl">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl px-6 py-4 shadow-lg hover:shadow-xl transition-shadow">
          <p class="text-sm whitespace-pre-wrap leading-relaxed">{{ message.content }}</p>
          
          <!-- File Attachment Preview -->
          <div v-if="message.file" class="mt-4 p-3 bg-blue-400/20 rounded-xl border border-blue-300/30">
            <div class="flex items-center space-x-2 text-sm">
              <span>📎</span>
              <span class="font-medium">{{ message.file.name }}</span>
              <span class="opacity-75">({{ formatFileSize(message.file.size) }})</span>
            </div>
          </div>
        </div>
        <div class="text-xs text-gray-500 mt-2 text-right">{{ formatTime(message.timestamp) }}</div>
      </div>
      
      <div class="w-10 h-10 bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0">
        <span class="text-white text-lg">👤</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps({
  message: Object,
  provider: String
})

const emit = defineEmits(['regenerate', 'copy', 'export', 'like'])

const getProviderEmoji = (provider) => {
  const emojis = {
    'openai': '⚡',
    'anthropic': '🧠',
    'grok': '✨'
  }
  return emojis[provider] || '🤖'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format(new Date(timestamp))
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Enhanced action handlers
const copyMessage = () => {
  navigator.clipboard.writeText(props.message.content)
  emit('copy', props.message)
}

const regenerateMessage = () => {
  emit('regenerate', props.message)
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