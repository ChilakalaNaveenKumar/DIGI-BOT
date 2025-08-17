<template>
  <div class="ds-code-highlighter">
    <!-- Language badge -->
    <div v-if="detectedLanguage" class="ds-language-badge">
      {{ detectedLanguage }}
    </div>
    
    <!-- Code content -->
    <pre class="ds-code-block"><code 
      :class="languageClass"
      v-html="highlightedCode"
    ></code></pre>
    
    <!-- Copy button -->
    <button @click="copyCode" class="ds-copy-btn" :title="copyButtonText">
      {{ copied ? '✓' : '📋' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

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

const copied = ref(false)

// Extract language from ```language
const detectedLanguage = computed(() => {
  const match = props.content.match(/```(\w+)/)
  return match ? match[1] : null
})

// Extract code content (remove ``` wrappers)
const codeContent = computed(() => {
  const match = props.content.match(/```\w*\n?([\s\S]*?)```/)
  if (match) {
    return match[1].trim()
  }
  // If no closing ```, return content after opening ```
  const openMatch = props.content.match(/```\w*\n?([\s\S]*)/)
  return openMatch ? openMatch[1] : props.content
})

// Language class for highlighting
const languageClass = computed(() => {
  return detectedLanguage.value ? `language-${detectedLanguage.value}` : 'language-text'
})

// Simple highlighting (can be enhanced with highlight.js later)
const highlightedCode = computed(() => {
  // For now, just escape HTML and preserve formatting
  return escapeHtml(codeContent.value)
})

// Copy functionality
const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(codeContent.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const copyButtonText = computed(() => {
  return copied.value ? 'Copied!' : 'Copy code'
})

// Utility function
const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
</script>

<style scoped>
.ds-code-highlighter {
  position: relative;
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  margin: 1rem 0;
}

.ds-language-badge {
  position: absolute;
  top: 8px;
  right: 50px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
  z-index: 2;
}

.ds-code-block {
  margin: 0;
  padding: 1rem;
  background: transparent;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  overflow-x: auto;
}

.ds-copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  z-index: 2;
}

.ds-copy-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

code {
  background: transparent;
  padding: 0;
  border-radius: 0;
}
</style>
