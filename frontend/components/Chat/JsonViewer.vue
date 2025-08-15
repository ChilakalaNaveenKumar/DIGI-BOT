<template>
  <div class="json-viewer">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-2">
        <div class="p-1.5 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
          <Code class="w-4 h-4 text-purple-600 dark:text-purple-400" />
        </div>
        <span class="text-sm font-medium text-purple-700 dark:text-purple-300">JSON Data</span>
        <UBadge color="purple" variant="soft" size="xs">
          {{ Object.keys(data).length }} {{ Object.keys(data).length === 1 ? 'property' : 'properties' }}
        </UBadge>
      </div>
      <div class="flex items-center space-x-2">
        <UButton @click="toggleExpanded" size="xs" variant="ghost">
          <ChevronRight :class="['w-3 h-3 transition-transform', expanded ? 'rotate-90' : '']" />
          {{ expanded ? 'Collapse' : 'Expand' }}
        </UButton>
        <UButton @click="copyJson" size="xs" variant="ghost" icon="i-lucide-copy" />
        <UButton @click="downloadJson" size="xs" variant="ghost" icon="i-lucide-download" />
      </div>
    </div>
    
    <div v-if="expanded" class="json-content">
      <pre class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-sm overflow-x-auto border border-gray-200 dark:border-gray-700"><code class="language-json" v-html="highlightedJson"></code></pre>
    </div>
    
    <div v-else class="json-preview">
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <div class="text-sm text-gray-600 dark:text-gray-400 font-mono">
          {{ jsonPreview }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Code, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: [Object, Array],
    required: true
  },
  initialExpanded: {
    type: Boolean,
    default: false
  }
})

const expanded = ref(props.initialExpanded)

// JSON syntax highlighting
const highlightedJson = computed(() => {
  const jsonString = JSON.stringify(props.data, null, 2)
  
  return jsonString
    .replace(/(".*?")(:)/g, '<span class="text-blue-600 dark:text-blue-400">$1</span><span class="text-gray-500">$2</span>')
    .replace(/(".*?")(,|$)/g, '<span class="text-green-600 dark:text-green-400">$1</span>$2')
    .replace(/(\b\d+\.?\d*\b)/g, '<span class="text-orange-600 dark:text-orange-400">$1</span>')
    .replace(/(\btrue\b|\bfalse\b)/g, '<span class="text-purple-600 dark:text-purple-400">$1</span>')
    .replace(/(\bnull\b)/g, '<span class="text-red-600 dark:text-red-400">$1</span>')
    .replace(/([{}[\]])/g, '<span class="text-gray-700 dark:text-gray-300 font-bold">$1</span>')
})

// JSON preview (first few properties)
const jsonPreview = computed(() => {
  const keys = Object.keys(props.data)
  if (keys.length === 0) return '{}'
  
  const preview = keys.slice(0, 3).map(key => {
    const value = props.data[key]
    const valueStr = typeof value === 'object' 
      ? Array.isArray(value) ? `[${value.length} items]` : '{...}'
      : typeof value === 'string' ? `"${value.substring(0, 20)}${value.length > 20 ? '...' : ''}"`
      : String(value)
    return `${key}: ${valueStr}`
  }).join(', ')
  
  return `{ ${preview}${keys.length > 3 ? `, ... +${keys.length - 3} more` : ''} }`
})

const toggleExpanded = () => {
  expanded.value = !expanded.value
}

const copyJson = async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(props.data, null, 2))
    console.log('JSON copied to clipboard')
  } catch (error) {
    console.error('Failed to copy JSON:', error)
  }
}

const downloadJson = () => {
  const blob = new Blob([JSON.stringify(props.data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `data-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.json-content code {
  font-family: 'Fira Code', 'Monaco', 'Menlo', 'Courier New', monospace;
  line-height: 1.5;
}

.json-preview {
  transition: all 0.2s ease;
}

.json-preview:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>



