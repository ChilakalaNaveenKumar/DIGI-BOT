<template>
  <div class="ds-diagram-renderer">
    <!-- Simple clean display without unnecessary header -->
    <div class="ds-diagram-content">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="ds-diagram-text" v-html="processedContent" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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

// Process diagram content with ASCII art support
const processedContent = computed(() => {
  let processed = props.content
  
  // Check if this looks like ASCII art (including parentheses and underscores)
  const hasAsciiPatterns = /[\|\+\-=\/\\○●◯()_]{2,}/.test(processed) || 
                          /```[\s\S]*?[\/\\()\-_|]+[\s\S]*?```/.test(processed)
  
  if (hasAsciiPatterns) {
    // Preserve ASCII art formatting
    processed = `<pre class="ascii-diagram">${processed}</pre>`
  } else {
    // Basic markdown processing for diagram descriptions
    // Bold: **text** -> <strong>text</strong>
    processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    
    // Italic: *text* -> <em>text</em>
    processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>')
    
    // Line breaks
    processed = processed.replace(/\n/g, '<br>')
    
    // Highlight key diagram terms
    const diagramTerms = [
      'Venn diagram', 'overlapping circles', 'sets', 'intersection', 
      'union', 'elements', 'relationships', 'visual tool'
    ]
    
    diagramTerms.forEach(term => {
      const regex = new RegExp(`\\b${term}\\b`, 'gi')
      processed = processed.replace(regex, `<span class="diagram-term">${term}</span>`)
    })
  }
  
  return processed
})
</script>

<style scoped>
.ds-diagram-renderer {
  margin: 1rem 0;
}

.ds-diagram-content {
  padding: 0;
}

.ds-diagram-text {
  line-height: 1.7;
  color: #374151;
  font-size: 1rem;
}

.ds-diagram-text :deep(strong) {
  color: #111827;
  font-weight: 600;
}

.ds-diagram-text :deep(em) {
  font-style: italic;
  color: #6b7280;
}

.ds-diagram-text :deep(.diagram-term) {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.95em;
}

.ds-diagram-text :deep(.ascii-diagram) {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
  line-height: 1.2;
  overflow-x: auto;
  white-space: pre;
  color: #495057;
  margin: 1rem 0;
}

/* Visual indicator for streaming */
.ds-diagram-renderer.streaming {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
</style>
