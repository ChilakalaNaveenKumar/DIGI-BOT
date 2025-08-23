<template>
  <div class="streaming-markdown" :class="{ 'is-streaming': isStreaming }">
    <!-- Render content blocks with chart support -->
    <div v-for="(block, index) in contentBlocks" :key="index" class="content-block">
      <!-- Chart Component -->
      <EnhancedComponentRenderer
        v-if="block.type === 'chart'"
        :component-type="block.chartType || ''"
        :markdown="block.content || ''"
        :title="block.title || ''"
      />
      <!-- Regular markdown with typewriter effect -->
      <UiTypewriterText
        v-else
        :content="block.rawContent || ''"
        :is-streaming="isStreaming && index === contentBlocks.length - 1"
        :speed="mode === 'streaming' ? 30 : 50"
        :immediate="mode === 'static'"
        @typing-complete="onTypingComplete"
      />
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
import { computed, watch } from 'vue'
import { useMarkdown } from '~/composables/useMarkdown'

interface Props {
  content: string
  isStreaming?: boolean
  showCursor?: boolean
  showStreamingIndicator?: boolean
  mode?: 'streaming' | 'static' | 'dynamic'
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: false,
  showCursor: false,
  showStreamingIndicator: true,
  mode: 'static'
})

const emit = defineEmits<{
  'content-updated': [content: string]
  'streaming-complete': []
}>()

const { render } = useMarkdown()

// Parse content into blocks (charts and markdown)
const contentBlocks = computed(() => {
  if (!props.content) return []
  
  const blocks = []
  const content = props.content
  
  // Find chart blocks with :::chart-type syntax and data tables
  const componentRegex = /:::([\w-]+)(?:-chart|)\n([\s\S]*?)\n:::/g
  let lastIndex = 0
  let match
  
  while ((match = componentRegex.exec(content)) !== null) {
    // Add markdown before component
    if (match.index > lastIndex) {
      const markdownContent = content.slice(lastIndex, match.index)
      if (markdownContent.trim()) {
        blocks.push({
          type: 'markdown',
          content: render(markdownContent),
          rawContent: markdownContent
        })
      }
    }
    
    // Add component block (chart or table)
    blocks.push({
      type: 'chart',
      chartType: match[1],
      content: match[2],
      title: extractTitle(match[2]),
      rawContent: match[2]
    })
    
    lastIndex = componentRegex.lastIndex
  }
  
  // Add remaining markdown
  if (lastIndex < content.length) {
    const remainingContent = content.slice(lastIndex)
    if (remainingContent.trim()) {
      blocks.push({
        type: 'markdown',
        content: render(remainingContent),
        rawContent: remainingContent
      })
    }
  }
  
  // If no charts found, return as single markdown block
  if (blocks.length === 0) {
    blocks.push({
      type: 'markdown',
      content: render(content),
      rawContent: content
    })
  }
  
  return blocks
})

function extractTitle(chartContent: string): string {
  const titleMatch = chartContent?.match(/title:\s*(.+)/)
  return titleMatch ? titleMatch[1].trim() : ''
}

function onTypingComplete() {
  if (!props.isStreaming) {
    emit('streaming-complete')
  }
}

// Watch for content changes and emit events
watch(() => props.content, (newContent) => {
  emit('content-updated', newContent)
  
  if (!props.isStreaming) {
    emit('streaming-complete')
  }
}, { immediate: true })
</script>

<style scoped>
.streaming-markdown {
  position: relative;
  line-height: 1.6;
}

.markdown-content {
  /* Inherit all markdown styles from global CSS */
  line-height: 1.6;
}

.streaming-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  font-weight: bold;
  color: #3b82f6;
  margin-left: 2px;
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

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}
</style>