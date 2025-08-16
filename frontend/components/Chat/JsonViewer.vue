<template>
  <div class="json-viewer">
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center space-x-2">
        <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">JSON Data</span>
      </div>
      
      <div class="flex items-center space-x-2">
        <button
          @click="toggleExpanded"
          class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          {{ isExpanded ? 'Collapse' : 'Expand' }}
        </button>
        
        <button
          @click="copyJson"
          class="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          :class="{ 'text-green-600 dark:text-green-400': copied }"
        >
          <Copy v-if="!copied" class="w-3 h-3" />
          <Check v-else class="w-3 h-3" />
          <span>{{ copied ? 'Copied!' : 'Copy' }}</span>
        </button>
      </div>
    </div>
    
    <div class="bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <pre 
        class="p-4 text-sm overflow-x-auto"
        :class="{ 'max-h-64 overflow-y-auto': !isExpanded }"
      ><code class="json-content" v-html="formattedJson"></code></pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Copy, Check } from 'lucide-vue-next'

interface Props {
  data: any
  format?: string
  maxHeight?: string
  initiallyExpanded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  format: 'json',
  maxHeight: '300px',
  initiallyExpanded: false
})

const isExpanded = ref(props.initiallyExpanded)
const copied = ref(false)

// Format and highlight JSON
const formattedJson = computed(() => {
  try {
    const jsonString = typeof props.data === 'string' 
      ? props.data 
      : JSON.stringify(props.data, null, 2)
    
    return highlightJson(jsonString)
  } catch (error) {
    return escapeHtml(String(props.data))
  }
})

// Get raw JSON string for copying
const rawJson = computed(() => {
  try {
    return typeof props.data === 'string' 
      ? props.data 
      : JSON.stringify(props.data, null, 2)
  } catch (error) {
    return String(props.data)
  }
})

// Toggle expanded state
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

// Copy JSON to clipboard
const copyJson = async () => {
  try {
    await navigator.clipboard.writeText(rawJson.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy JSON:', err)
  }
}

// Escape HTML
const escapeHtml = (text: string): string => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// Highlight JSON syntax
const highlightJson = (jsonString: string): string => {
  try {
    // Parse and re-stringify to ensure valid JSON
    const parsed = JSON.parse(jsonString)
    const formatted = JSON.stringify(parsed, null, 2)
    
    return formatted
      // Highlight keys
      .replace(/("([^"\\]|\\.)*")\s*:/g, '<span class="json-key">$1</span>:')
      // Highlight string values
      .replace(/:\s*("([^"\\]|\\.)*")/g, ': <span class="json-string">$1</span>')
      // Highlight boolean values
      .replace(/:\s*(true|false)/g, ': <span class="json-boolean">$1</span>')
      // Highlight null values
      .replace(/:\s*(null)/g, ': <span class="json-null">$1</span>')
      // Highlight number values
      .replace(/:\s*(-?\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
      // Highlight brackets and braces
      .replace(/([{}[\]])/g, '<span class="json-bracket">$1</span>')
      // Highlight commas
      .replace(/(,)/g, '<span class="json-comma">$1</span>')
  } catch (error) {
    // If JSON is invalid, just escape HTML
    return escapeHtml(jsonString)
  }
}
</script>

<style scoped>
.json-viewer {
  @apply font-mono text-sm;
}

/* JSON syntax highlighting */
:deep(.json-key) {
  @apply text-blue-600 dark:text-blue-400 font-medium;
}

:deep(.json-string) {
  @apply text-green-600 dark:text-green-400;
}

:deep(.json-number) {
  @apply text-purple-600 dark:text-purple-400;
}

:deep(.json-boolean) {
  @apply text-orange-600 dark:text-orange-400 font-medium;
}

:deep(.json-null) {
  @apply text-gray-500 dark:text-gray-400 font-medium;
}

:deep(.json-bracket) {
  @apply text-gray-700 dark:text-gray-300 font-bold;
}

:deep(.json-comma) {
  @apply text-gray-600 dark:text-gray-400;
}

/* Scrollbar styling */
pre::-webkit-scrollbar {
  @apply w-2 h-2;
}

pre::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800 rounded;
}

pre::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded;
}

pre::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}
</style>