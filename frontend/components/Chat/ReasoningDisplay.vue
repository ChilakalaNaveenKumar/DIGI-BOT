<template>
  <div class="thought-process-container">
    <!-- Simple Header -->
    <div class="flex items-center justify-between p-3 cursor-pointer" @click="toggleExpanded">
      <h3 class="text-sm font-medium text-black dark:text-white">Thought process</h3>
      <ChevronDown 
        class="w-4 h-4 text-black dark:text-white transition-transform duration-200"
        :class="{ 'rotate-180': isExpanded }"
      />
    </div>

    <!-- Simple Content -->
    <div v-if="isExpanded" class="thought-content">
      <div class="thought-text" v-html="processedReasoningText"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  reasoning: {
    type: Array,
    default: () => []
  },
  state: {
    type: String,
    default: 'done'
  },
  currentThinking: {
    type: String,
    default: ''
  },
  initialExpanded: {
    type: Boolean,
    default: false // Default closed as requested
  }
})

const isExpanded = ref(props.initialExpanded)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

// Simple markdown processing
const processMarkdown = (content) => {
  if (!content) return ''
  
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-gray-700 px-1 py-0.5 rounded text-red-400">$1</code>')
    .replace(/^### (.*$)/gm, '<h3 class="font-medium text-gray-200 mt-3 mb-1">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="font-medium text-gray-200 mt-3 mb-1">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="font-medium text-gray-200 mt-3 mb-1">$1</h1>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>')
}

// Process all reasoning into simple text
const processedReasoningText = computed(() => {
  if (!props.reasoning || props.reasoning.length === 0) return ''
  
  // Combine all reasoning parts into one simple text
  let allText = ''
  
  props.reasoning.forEach((reasoningPart) => {
    const content = reasoningPart.text || reasoningPart.content || reasoningPart
    if (content) {
      allText += content + '\n\n'
    }
  })
  
  // Add current thinking if streaming
  if (props.currentThinking && props.state === 'streaming') {
    allText += props.currentThinking
  }
  
  return processMarkdown(allText.trim())
})
</script>

<style scoped>
.thought-process-container {
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  margin-bottom: 1rem;
  backdrop-filter: blur(8px);
}

.dark .thought-process-container {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.thought-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 0 1rem 1rem 1rem;
}

.thought-text {
  color: #000000;
  font-size: 0.875rem;
  line-height: 1.5;
}

.dark .thought-text {
  color: #ffffff;
}

.thought-text :deep(strong) {
  color: #000000;
  font-weight: 600;
}

.dark .thought-text :deep(strong) {
  color: #ffffff;
}

.thought-text :deep(em) {
  color: #000000;
  font-style: italic;
}

.dark .thought-text :deep(em) {
  color: #ffffff;
}

.thought-text :deep(code) {
  background: rgba(0, 0, 0, 0.1) !important;
  color: #dc2626 !important;
  padding: 2px 4px !important;
  border-radius: 4px !important;
  font-size: 0.8em !important;
}

.dark .thought-text :deep(code) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #fca5a5 !important;
}

.thought-text :deep(h1),
.thought-text :deep(h2), 
.thought-text :deep(h3) {
  color: #000000;
  font-weight: 600;
  margin: 0.75rem 0 0.25rem 0;
}

.dark .thought-text :deep(h1),
.dark .thought-text :deep(h2),
.dark .thought-text :deep(h3) {
  color: #ffffff;
}

/* Custom scrollbar */
.thought-content::-webkit-scrollbar {
  width: 6px;
}

.thought-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.dark .thought-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.thought-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.dark .thought-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.thought-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

.dark .thought-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>