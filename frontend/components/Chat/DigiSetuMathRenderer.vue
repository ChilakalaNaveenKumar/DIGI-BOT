<template>
  <div class="ds-math-renderer">
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div class="ds-math-content" v-html="processedMath" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import katex from 'katex'
import 'katex/dist/katex.min.css'

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

// Process LaTeX math notation using KaTeX
const processedMath = computed(() => {
  let content = props.content
  
  try {
    // Handle inline math: \\( ... \\)
    content = content.replace(/\\\\?\\\((.*?)\\\\?\\\)/g, (match, mathContent) => {
      try {
        return katex.renderToString(mathContent, { 
          displayMode: false,
          throwOnError: false,
          strict: false
        })
      } catch {
        return `<span class="math-error">Math Error: ${mathContent}</span>`
      }
    })
    
    // Handle block math: \\[ ... \\]
    content = content.replace(/\\\\?\\\[(.*?)\\\\?\\\]/gs, (match, mathContent) => {
      try {
        return katex.renderToString(mathContent, { 
          displayMode: true,
          throwOnError: false,
          strict: false
        })
      } catch {
        return `<div class="math-error">Math Error: ${mathContent}</div>`
      }
    })
    
    // Convert line breaks
    content = content.replace(/\n/g, '<br>')
    
    return content
  } catch (error) {
    // Fallback to original content if KaTeX fails
    console.warn('KaTeX rendering failed:', error)
    return props.content.replace(/\n/g, '<br>')
  }
})
</script>

<style scoped>
.ds-math-renderer {
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #6366f1;
}

.ds-math-content :deep(.katex-display) {
  margin: 1rem 0;
  text-align: center;
}

.ds-math-content :deep(.katex) {
  font-size: 1.1em;
}

.ds-math-content :deep(.math-error) {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #fecaca;
  font-family: monospace;
  font-size: 0.9em;
}
</style>
