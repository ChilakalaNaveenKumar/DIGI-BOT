<template>
  <div class="space-y-4">
    <!-- Enhanced File Preview -->
    <div v-if="uploadedFile" class="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-2xl p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-gradient-to-r from-blue-100 to-purple-100 rounded-xl flex items-center justify-center">
            <span class="text-2xl">📎</span>
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
          ❌
        </button>
      </div>
    </div>

    <!-- Enhanced Input Form -->
    <form @submit.prevent="emit('submit')" class="flex items-end space-x-4">
      <!-- Enhanced File Upload -->
      <label class="cursor-pointer group">
        <input
          type="file"
          class="hidden"
          accept="image/*,.pdf,.txt,.docx,.md,.pptx,.xlsx"
          @change="handleFileUpload"
        >
        <div class="w-12 h-12 bg-gradient-to-r from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center shadow-sm hover:shadow-lg group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-300 border-2 border-dashed border-gray-300 group-hover:border-blue-400 hover:scale-105">
          <span class="text-2xl text-gray-500 group-hover:text-blue-600 transition-colors">📎</span>
        </div>
      </label>

      <!-- Enhanced Text Input -->
      <div class="flex-1 relative">
        <textarea
          :value="modelValue"
          @input="handleInput"
          placeholder="Describe what you'd like to create, ask a question, or upload a file..."
          :disabled="loading"
          rows="1"
          class="w-full min-h-[48px] max-h-32 px-6 py-4 bg-white border-2 border-gray-200 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm hover:shadow-md transition-all duration-200 placeholder-gray-500 text-gray-800"
          @keydown.enter.exact.prevent="emit('submit')"
        />
        
        <!-- Character count -->
        <div class="absolute bottom-2 right-4 text-xs text-gray-400">
          {{ modelValue ? modelValue.length : 0 }}/2000
        </div>
      </div>

      <!-- Enhanced Send Button -->
      <button
        type="submit"
        :disabled="loading || !modelValue || !modelValue.trim()"
        class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 disabled:hover:scale-100"
      >
        <span v-if="!loading" class="text-xl">🚀</span>
        <div v-else class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      </button>
    </form>

    <!-- Enhanced Quick Actions -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="quickAction in quickActions"
        :key="quickAction.text"
        @click="emit('update:modelValue', quickAction.text)"
        type="button"
        class="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:text-blue-600 hover:border-blue-300 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105"
      >
        <span class="text-base">{{ quickAction.emoji }}</span>
        <span class="font-medium">{{ quickAction.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: String,
  loading: Boolean,
  uploadedFile: Object
})

const emit = defineEmits(['submit', 'file-upload', 'file-remove', 'update:modelValue'])

const quickActions = [
  { label: 'Explain concept', text: 'Explain this concept in simple terms with examples', emoji: '💡' },
  { label: 'Create quiz', text: 'Create an interactive quiz with multiple choice questions', emoji: '❓' },
  { label: 'Make summary', text: 'Summarize this content with key points', emoji: '📝' },
  { label: 'Build timeline', text: 'Create a timeline showing the sequence of events', emoji: '📅' },
  { label: 'Design flowchart', text: 'Create a flowchart to visualize this process', emoji: '📊' }
]

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