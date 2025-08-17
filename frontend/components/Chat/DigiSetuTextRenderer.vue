<template>
  <div class="ds-text-renderer">
    <div class="ds-text-content" v-html="processedText"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})

// Configure marked for better markdown processing
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (e) {
        console.warn('Highlight.js error:', e)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

// Process markdown text with proper library
const processedText = computed(() => {
  if (!props.content) return ''
  
  let content = props.content
  
  // Process with marked for proper markdown (headers, lists, etc.) - no math protection needed
  let processed = marked.parse(content)
  
  // Highlight specific terms (like 'elements')
  processed = processed.replace(/\b(elements|algorithm|complexity|efficiency)\b/g, '<span class="ds-highlight-term">$1</span>')
  
  return processed
})
</script>

<style scoped>
.ds-text-renderer {
  margin: 0;
  line-height: 1.6;
}

.ds-text-content {
  color: #374151;
}

.ds-text-content :deep(h1) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  color: #111827;
}

.ds-text-content :deep(h2) {
  font-size: 1.3em;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  color: #111827;
}

.ds-text-content :deep(h3) {
  font-size: 1.1em;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  color: #111827;
}

.ds-text-content :deep(strong) {
  font-weight: 600;
  color: #111827;
}

.ds-text-content :deep(em) {
  font-style: italic;
}

.ds-text-content :deep(code) {
  background: #f3f4f6;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.ds-text-content :deep(a) {
  color: #3b82f6;
  text-decoration: underline;
}

.ds-text-content :deep(a:hover) {
  color: #1d4ed8;
}

.ds-text-content :deep(.ds-highlight-term) {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
}

.ds-text-content :deep(h1) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  color: #111827;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.ds-text-content :deep(h2) {
  font-size: 1.3em;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  color: #111827;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.25rem;
}

.ds-text-content :deep(h3) {
  font-size: 1.1em;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  color: #374151;
}
</style>
