<template>
  <form @submit="handleSubmit" class="space-y-3">
    <!-- Top Row: File Upload + Provider Info -->
    <div class="flex items-center justify-between">
      <label class="cursor-pointer group">
        <input
          type="file"
          class="hidden"
          accept="image/*,.pdf,.txt,.docx,.md,.pptx,.xlsx"
          @change="handleFileUpload"
        >
        <div class="flex items-center space-x-2 px-3 py-2 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-200 border border-gray-200 dark:border-gray-600">
          <ImagePlus class="w-4 h-4 text-gray-600 dark:text-gray-400" />
          <span class="text-sm text-gray-600 dark:text-gray-400">Attach</span>
        </div>
      </label>

      <div class="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
        <span>{{ modelValue?.length || 0 }}/2000</span>
        <span>•</span>
        <ProviderIcon :provider="selectedProvider" :size="16" />
        <span>{{ getProviderName(selectedProvider) }}</span>
      </div>
    </div>

    <!-- Main Input Row -->
    <div class="flex items-end space-x-3">
      <!-- Text Input -->
      <div class="flex-1 relative">
        <textarea
          :value="modelValue"
          @input="handleInput"
          placeholder="Describe what you'd like to create, ask a question, or upload a file..."
          :disabled="loading"
          rows="1"
          class="w-full min-h-[52px] max-h-32 px-4 py-3 pr-12 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm hover:shadow-md transition-all duration-200 placeholder-gray-500 dark:placeholder-gray-400 text-gray-800 dark:text-gray-200"
          @keydown.enter.exact.prevent="handleSubmit"
        />
      </div>

      <!-- Send Button -->
      <button
        type="submit"
        :disabled="loading || !modelValue?.trim()"
        class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 disabled:hover:scale-100"
      >
        <Send v-if="!loading" class="w-5 h-5" />
        <div v-else class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      </button>
    </div>
  </form>
</template>

<script setup>
import { ImagePlus, Send } from 'lucide-vue-next'
import ProviderIcon from '../UI/ProviderIcon.vue'

const props = defineProps({
  modelValue: String,
  loading: Boolean,
  providers: Array,
  selectedProvider: String
})

const emit = defineEmits(['submit', 'file-upload', 'update:modelValue'])

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  // Auto-resize textarea
  event.target.style.height = 'auto'
  event.target.style.height = Math.min(event.target.scrollHeight, 128) + 'px'
}

const handleSubmit = (event) => {
  event.preventDefault()
  emit('submit', event)
}

const handleFileUpload = (event) => {
  emit('file-upload', event)
}

const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-4',
    'grok': 'Grok',
    'anthropic': 'Claude'
  }
  return names[provider] || 'GPT-4'
}
</script>
