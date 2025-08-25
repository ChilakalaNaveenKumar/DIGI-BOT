<template>
  <div class="streaming-markdown" :class="{ 'streaming-mode': isStreaming }">
    <!-- Enhanced streaming content with component support -->
    <div class="markdown-content">
      <component 
        :is="'div'" 
        v-for="(part, index) in contentParts" 
        :key="`part-${index}`"
        class="content-part"
      >
        <!-- Regular markdown content -->
        <div v-if="part.type === 'markdown'" v-html="render(part.content || '')" />
        
        <!-- Inline component -->
        <div v-else-if="part.type === 'component'" class="inline-component-wrapper">
          <EnhancedComponentRenderer
            :component-type="part.componentType || ''"
            :markdown="part.markdown || ''"
          />
        </div>
      </component>
    </div>
    
    <!-- Streaming indicator -->
    <div v-if="isStreaming && showStreamingIndicator" class="streaming-indicator">
      <div class="streaming-dots">
        <span /><span /><span />
      </div>
      <span class="streaming-text">Generating...</span>
    </div>
    
    <!-- Typing cursor -->
    <span v-if="isStreaming && showCursor" class="typing-cursor">|</span>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, nextTick } from 'vue'
import { useMarkdown } from '~/composables/useMarkdown'

interface Props {
  content?: string
  isStreaming?: boolean
  showCursor?: boolean
  showStreamingIndicator?: boolean
  pauseCursor?: boolean
  mode?: 'streaming' | 'static'
  autoScroll?: boolean
  debug?: boolean
}

interface Emits {
  'content-updated': []
  'streaming-complete': []
  'block-completed': [block: unknown]
}

const props = withDefaults(defineProps<Props>(), {
  content: '',
  isStreaming: false,
  showCursor: true,
  showStreamingIndicator: true,
  pauseCursor: false,
  mode: 'static',
  autoScroll: true,
  debug: false
})

const emit = defineEmits<Emits>()

const { render } = useMarkdown()

// Parse content into markdown and component parts
const contentParts = computed(() => {
  if (!props.content) return []
  
  const parts = []
  const componentRegex = /:::(\w+(?:-\w+)*)\s*\n([\s\S]*?)\n:::/g
  let lastIndex = 0
  let match
  
  while ((match = componentRegex.exec(props.content || '')) !== null) {
    // Add markdown content before component
    if ((match.index || 0) > lastIndex) {
      const markdownContent = (props.content || '').substring(lastIndex, match.index).trim()
      if (markdownContent) {
        parts.push({
          type: 'markdown',
          content: markdownContent
        })
      }
    }
    
    // Add component part
    parts.push({
      type: 'component',
      componentType: match[1],
      markdown: match[0], // Full component markdown including :::
      data: match[2]?.trim() || ''
    })
    
    lastIndex = (match.index || 0) + match[0].length
  }
  
  // Add remaining markdown content
  if (lastIndex < (props.content || '').length) {
    const remainingContent = (props.content || '').substring(lastIndex).trim()
    if (remainingContent) {
      parts.push({
        type: 'markdown',
        content: remainingContent
      })
    }
  }
  
  // If no components found, return all as markdown
  if (parts.length === 0) {
    return [{
      type: 'markdown',
      content: props.content || ''
    }]
  }
  
  return parts
})

const isStreaming = computed(() => props.isStreaming)

// Auto-scroll functionality
const scrollToBottom = () => {
  if (!props.autoScroll) return
  
  nextTick(() => {
    // Only auto-scroll if user is near bottom (within 100px)
    const scrollPosition = window.pageYOffset + window.innerHeight
    const documentHeight = document.documentElement.scrollHeight
    
    if (documentHeight - scrollPosition < 100) {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}

// Watch for content changes and auto-scroll
watch(() => props.content, () => {
  emit('content-updated')
  if (props.autoScroll) {
    scrollToBottom()
  }
})

// Watch for streaming completion
watch(() => props.isStreaming, (newStreaming, oldStreaming) => {
  if (oldStreaming && !newStreaming) {
    // Streaming just finished
    emit('streaming-complete')
  }
})
</script>

<style scoped>
.streaming-markdown {
  width: 100%;
  font-family: inherit;
  line-height: 1.6;
}

.streaming-mode {
  position: relative;
}

.markdown-content {
  width: 100%;
  overflow-wrap: break-word;
}

.content-part {
  margin-bottom: 0;
}

.inline-component-wrapper {
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-secondary);
  background: var(--bg-secondary);
}

/* Streaming indicator */
.streaming-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
  font-style: italic;
}

.streaming-dots {
  display: flex;
  gap: 3px;
}

.streaming-dots span {
  width: 6px;
  height: 6px;
  background: var(--accent-primary);
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out;
}

.streaming-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.streaming-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.streaming-text {
  color: var(--text-secondary);
  font-size: 13px;
}

/* Typing cursor */
.typing-cursor {
  color: var(--accent-primary);
  font-weight: bold;
  animation: blink 1s infinite;
  margin-left: 2px;
}

/* Animations */
@keyframes pulse {
  0%, 60%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  30% {
    transform: scale(1.2);
    opacity: 1;
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* Comprehensive markdown styling */
.markdown-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 24px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--border-primary);
}

.markdown-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 20px 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-primary);
}

.markdown-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 16px 0 8px 0;
}

.markdown-content :deep(h4), 
.markdown-content :deep(h5), 
.markdown-content :deep(h6) {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 12px 0 6px 0;
}

.markdown-content :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.markdown-content :deep(a) {
  color: var(--accent-primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.2s ease;
}

.markdown-content :deep(a:hover) {
  border-bottom-color: var(--accent-primary);
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(del) {
  text-decoration: line-through;
  opacity: 0.7;
}

.markdown-content :deep(code) {
  background: var(--bg-tertiary);
  color: var(--accent-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  border: 1px solid var(--border-primary);
}

.markdown-content :deep(pre) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.markdown-content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-primary);
}

/* Syntax highlighting theme adaptation */
.markdown-content :deep(.hljs) {
  background: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  padding: 0;
  border-radius: 0;
}

/* Light theme syntax highlighting */
:root .markdown-content :deep(.hljs-keyword) { color: #d73a49; }
:root .markdown-content :deep(.hljs-string) { color: #032f62; }
:root .markdown-content :deep(.hljs-comment) { color: #6a737d; }
:root .markdown-content :deep(.hljs-function) { color: #6f42c1; }
:root .markdown-content :deep(.hljs-number) { color: #005cc5; }
:root .markdown-content :deep(.hljs-variable) { color: #e36209; }
:root .markdown-content :deep(.hljs-title) { color: #6f42c1; }
:root .markdown-content :deep(.hljs-params) { color: #24292e; }
:root .markdown-content :deep(.hljs-attr) { color: #005cc5; }
:root .markdown-content :deep(.hljs-built_in) { color: #005cc5; }

/* Dark theme syntax highlighting */
[data-theme="dark"] .markdown-content :deep(.hljs-keyword) { color: #ff7b72; }
[data-theme="dark"] .markdown-content :deep(.hljs-string) { color: #a5d6ff; }
[data-theme="dark"] .markdown-content :deep(.hljs-comment) { color: #8b949e; }
[data-theme="dark"] .markdown-content :deep(.hljs-function) { color: #d2a8ff; }
[data-theme="dark"] .markdown-content :deep(.hljs-number) { color: #79c0ff; }
[data-theme="dark"] .markdown-content :deep(.hljs-variable) { color: #ffa657; }
[data-theme="dark"] .markdown-content :deep(.hljs-title) { color: #d2a8ff; }
[data-theme="dark"] .markdown-content :deep(.hljs-params) { color: #f0f6fc; }
[data-theme="dark"] .markdown-content :deep(.hljs-attr) { color: #79c0ff; }
[data-theme="dark"] .markdown-content :deep(.hljs-built_in) { color: #79c0ff; }

.markdown-content :deep(ul), 
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
  line-height: 1.5;
}

.markdown-content :deep(ul li) {
  list-style: disc;
}

.markdown-content :deep(ol li) {
  list-style: decimal;
}

.markdown-content :deep(blockquote) {
  background: var(--bg-secondary);
  border-left: 4px solid var(--accent-primary);
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 6px 6px 0;
}

.markdown-content :deep(blockquote p) {
  margin: 0;
  color: var(--text-secondary);
  font-style: italic;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-primary);
}

.markdown-content :deep(th), 
.markdown-content :deep(td) {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-primary);
}

.markdown-content :deep(th) {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-content :deep(tr:last-child td) {
  border-bottom: none;
}

.markdown-content :deep(tr:nth-child(even)) {
  background: var(--bg-secondary);
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-primary);
  margin: 24px 0;
}

.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 8px 0;
  border: 1px solid var(--border-primary);
}

/* Task lists */
.markdown-content :deep(input[type="checkbox"]) {
  margin-right: 8px;
}

/* Container styles for AI responses */
.markdown-content :deep(.container) {
  margin: 16px 0;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid;
}

.markdown-content :deep(.container.info) {
  background: var(--info-bg, #dbeafe);
  border-left-color: var(--info-border, #3b82f6);
  color: var(--info-text, #1e40af);
}

[data-theme="dark"] .markdown-content :deep(.container.info) {
  background: var(--info-bg, #1e3a8a);
  border-left-color: var(--info-border, #60a5fa);
  color: var(--info-text, #bfdbfe);
}

.markdown-content :deep(.container.warning) {
  background: var(--warning-bg, #fef3cd);
  border-left-color: var(--warning-border, #f59e0b);
  color: var(--warning-text, #92400e);
}

[data-theme="dark"] .markdown-content :deep(.container.warning) {
  background: var(--warning-bg, #92400e);
  border-left-color: var(--warning-border, #fbbf24);
  color: var(--warning-text, #fef3c7);
}

.markdown-content :deep(.container.tip) {
  background: var(--tip-bg, #d1fae5);
  border-left-color: var(--tip-border, #10b981);
  color: var(--tip-text, #065f46);
}

[data-theme="dark"] .markdown-content :deep(.container.tip) {
  background: var(--tip-bg, #065f46);
  border-left-color: var(--tip-border, #34d399);
  color: var(--tip-text, #d1fae5);
}

.markdown-content :deep(.container.danger) {
  background: var(--danger-bg, #fee2e2);
  border-left-color: var(--danger-border, #ef4444);
  color: var(--danger-text, #991b1b);
}

[data-theme="dark"] .markdown-content :deep(.container.danger) {
  background: var(--danger-bg, #991b1b);
  border-left-color: var(--danger-border, #f87171);
  color: var(--danger-text, #fecaca);
}

.markdown-content :deep(.container-header) {
  font-weight: 600;
  margin-bottom: 8px;
}

/* Enhanced text formatting */
.markdown-content :deep(mark) {
  background: var(--mark-bg, #fef08a);
  color: var(--mark-text, #451a03);
  padding: 2px 4px;
  border-radius: 3px;
}

[data-theme="dark"] .markdown-content :deep(mark) {
  background: var(--mark-bg, #451a03);
  color: var(--mark-text, #fef08a);
}

.markdown-content :deep(ins) {
  background: var(--ins-bg, #dcfce7);
  color: var(--ins-text, #166534);
  text-decoration: none;
  padding: 1px 3px;
  border-radius: 3px;
}

[data-theme="dark"] .markdown-content :deep(ins) {
  background: var(--ins-bg, #166534);
  color: var(--ins-text, #dcfce7);
}

.markdown-content :deep(sub), 
.markdown-content :deep(sup) {
  font-size: 0.8em;
}

/* KaTeX math styling */
.markdown-content :deep(.katex) {
  font-size: 1.1em;
}

.markdown-content :deep(.katex-display) {
  margin: 16px 0;
  text-align: center;
}

.markdown-content :deep(.katex-error) {
  color: var(--error-text, #dc2626);
  background: var(--error-bg, #fee2e2);
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .markdown-content :deep(.katex) {
    font-size: 1em;
  }
  
  .markdown-content :deep(pre) {
    font-size: 12px;
    padding: 12px;
  }
  
  .markdown-content :deep(table) {
    font-size: 14px;
  }
  
  .markdown-content :deep(th), 
  .markdown-content :deep(td) {
    padding: 8px;
  }
}
</style>