<template>
  <div class="ai-code-content" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  theme: {
    type: String,
    default: 'auto'
  }
})

// Configure marked with enhanced syntax highlighting
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('Highlight.js error:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
  headerIds: false,
  mangle: false
})

const renderedContent = computed(() => {
  return marked(props.content)
})
</script>

<style scoped>
/* AI SDK Style Code Rendering - HIGH CONTRAST */
.ai-code-content {
  color: #1f2937;
  line-height: 1.625;
  font-size: 14px;
}

:root.dark .ai-code-content {
  color: #ffffff !important;
}

/* Force white text in dark mode */
.dark .ai-code-content,
.ai-code-content {
  color: #ffffff !important;
}

/* Enhanced Typography */
.ai-code-content :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 1rem;
  margin-top: 1.5rem;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

:root.dark .ai-code-content :deep(h1),
.dark .ai-code-content :deep(h1) {
  color: #ffffff !important;
  border-bottom-color: #374151;
}

.ai-code-content :deep(h2) {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.75rem;
  margin-top: 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.25rem;
}

:root.dark .ai-code-content :deep(h2) {
  color: #ffffff;
  border-bottom-color: #374151;
}

.ai-code-content :deep(h3) {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
  margin-top: 1rem;
}

:root.dark .ai-code-content :deep(h3) {
  color: #ffffff;
}

.ai-code-content :deep(p) {
  margin-bottom: 1rem;
  line-height: 1.625;
  color: #ffffff !important;
}

.dark .ai-code-content :deep(p) {
  color: #ffffff !important;
}

/* Professional Code Blocks */
.ai-code-content :deep(pre) {
  background-color: #0f172a;
  color: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.75rem;
  overflow-x: auto;
  margin: 1.5rem 0;
  border: 1px solid #334155;
  position: relative;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}

:root.dark .ai-code-content :deep(pre) {
  background-color: #111827;
  border-color: #374151;
}

.ai-code-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* Inline Code */
.ai-code-content :deep(code) {
  background-color: #f1f5f9;
  color: #e11d48;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-weight: 500;
}

:root.dark .ai-code-content :deep(code) {
  background-color: #374151;
  color: #fbbf24;
}

/* Professional Syntax Highlighting */
.ai-code-content :deep(.hljs) {
  background: transparent !important;
}

.ai-code-content :deep(.hljs-comment),
.ai-code-content :deep(.hljs-quote) {
  color: #64748b;
  font-style: italic;
}

.ai-code-content :deep(.hljs-keyword),
.ai-code-content :deep(.hljs-selector-tag),
.ai-code-content :deep(.hljs-subst) {
  color: #f472b6;
  font-weight: 600;
}

.ai-code-content :deep(.hljs-number),
.ai-code-content :deep(.hljs-literal),
.ai-code-content :deep(.hljs-variable) {
  color: #fbbf24;
}

.ai-code-content :deep(.hljs-string),
.ai-code-content :deep(.hljs-doctag) {
  color: #34d399;
}

.ai-code-content :deep(.hljs-title),
.ai-code-content :deep(.hljs-section) {
  color: #60a5fa;
  font-weight: 600;
}

.ai-code-content :deep(.hljs-type),
.ai-code-content :deep(.hljs-class .hljs-title) {
  color: #a78bfa;
  font-weight: 600;
}

.ai-code-content :deep(.hljs-tag),
.ai-code-content :deep(.hljs-name),
.ai-code-content :deep(.hljs-attribute) {
  color: #f87171;
}

.ai-code-content :deep(.hljs-built_in),
.ai-code-content :deep(.hljs-builtin-name) {
  color: #60a5fa;
}

/* Lists */
.ai-code-content :deep(ul) {
  list-style-type: disc;
  list-style-position: inside;
  margin-bottom: 1rem;
  padding-left: 1rem;
}

.ai-code-content :deep(ol) {
  list-style-type: decimal;
  list-style-position: inside;
  margin-bottom: 1rem;
  padding-left: 1rem;
}

.ai-code-content :deep(li) {
  color: #ffffff !important;
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

:root.dark .ai-code-content :deep(li),
.dark .ai-code-content :deep(li) {
  color: #ffffff !important;
}

/* Links */
.ai-code-content :deep(a) {
  color: #2563eb;
  text-decoration: underline;
  text-decoration-color: #93c5fd;
  text-underline-offset: 2px;
  transition: all 0.2s ease;
}

:root.dark .ai-code-content :deep(a) {
  color: #60a5fa;
  text-decoration-color: #3b82f6;
}

/* Tables */
.ai-code-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e5e7eb;
  margin: 1.5rem 0;
  border-radius: 0.5rem;
  overflow: hidden;
}

:root.dark .ai-code-content :deep(table) {
  border-color: #374151;
}

.ai-code-content :deep(th) {
  border: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
  background-color: #f9fafb;
  font-weight: 600;
  text-align: left;
}

:root.dark .ai-code-content :deep(th) {
  border-color: #374151;
  background-color: #1f2937;
}

.ai-code-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
}

:root.dark .ai-code-content :deep(td) {
  border-color: #374151;
}

/* Blockquotes */
.ai-code-content :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  padding-left: 1rem;
  font-style: italic;
  color: #4b5563;
  margin: 1rem 0;
  background-color: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
}

:root.dark .ai-code-content :deep(blockquote) {
  color: #9ca3af;
  background-color: #1f2937;
  border-left-color: #60a5fa;
}

/* Text formatting */
.ai-code-content :deep(strong) {
  font-weight: 600;
  color: #111827;
}

:root.dark .ai-code-content :deep(strong) {
  color: #ffffff;
}

.ai-code-content :deep(em) {
  font-style: italic;
}
</style>
