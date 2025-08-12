<template>
  <div class="space-y-4">
    <!-- Enhanced File Preview -->
    <div v-if="uploadedFile" class="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-2xl p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-gradient-to-r from-blue-100 to-purple-100 rounded-xl flex items-center justify-center">
            <FileText class="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p class="font-medium text-blue-900">{{ uploadedFile.name }}</p>
            <div class="flex items-center space-x-2 text-sm text-blue-600">
              <span>{{ formatFileSize(uploadedFile.size) }}</span>
              <span>•</span>
              <span>{{ getFileType(uploadedFile) }}</span>
            </div>
          </div>
        </div>
        <button
          @click="emit('file-remove')"
          class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all duration-200"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Enhanced Input Form -->
    <form @submit.prevent="emit('submit')" class="space-y-3">
      <!-- Top Row: File Upload + Model Selector -->
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
          <span>{{ modelValue ? modelValue.length : 0 }}/2000</span>
          <span>•</span>
          <span>{{ selectedProvider }}</span>
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
            @keydown.enter.exact.prevent="emit('submit')"
          />
        </div>

        <!-- Send Button -->
        <button
          type="submit"
          :disabled="loading || !modelValue || !modelValue.trim()"
          class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 disabled:hover:scale-100"
        >
          <Send v-if="!loading" class="w-5 h-5" />
          <div v-else class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        </button>
      </div>
    </form>


  </div>
</template>

<script setup>
import { FileText, X, ImagePlus, Send } from 'lucide-vue-next'

defineProps({
  modelValue: String,
  loading: Boolean,
  uploadedFile: Object,
  selectedProvider: String
})

const emit = defineEmits(['submit', 'file-upload', 'file-remove', 'update:modelValue'])

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  // Auto-resize textarea
  event.target.style.height = 'auto'
  event.target.style.height = Math.min(event.target.scrollHeight, 128) + 'px'
}

const handleFileUpload = (event) => {
  emit('file-upload', event)
}

const getFileType = (file) => {
  if (!file) return 'Unknown'
  
  const type = file.type
  if (type.startsWith('image/')) return 'Image'
  if (type.includes('pdf')) return 'PDF'
  if (type.includes('text')) return 'Text'
  if (type.includes('document')) return 'Document'
  return 'File'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>