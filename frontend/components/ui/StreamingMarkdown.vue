<template>
  <div class="streaming-markdown" :class="{ 'is-streaming': isStreaming }">
    <!-- Render charts as Vue components -->
    <div v-for="(block, index) in contentBlocks" :key="index" class="content-block">
      <!-- Chart Component -->
      <EnhancedComponentRenderer
        v-if="block.type === 'component'"
        :component-type="block.componentType"
        :markdown="block.markdown"
        :title="block.title"
      />
      <!-- Regular markdown content -->
      <div v-else v-html="block.content" class="markdown-content"></div>
    </div>
    <span v-if="showCursor && isStreaming" class="streaming-cursor">|</span>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue'
import { useMarkdown } from '~/composables/useMarkdown'

interface Props {
  content: string
  isStreaming?: boolean
  showCursor?: boolean
  mode?: 'streaming' | 'static' | 'dynamic'
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: false,
  showCursor: false,
  mode: 'static'
})

const emit = defineEmits<{
  'content-updated': [content: string]
  'streaming-complete': []
  'block-completed': [block: string]
}>()

const { render } = useMarkdown()

// Parse content into blocks (components and markdown)
const contentBlocks = computed(() => {
  if (!props.content) return []
  
  const blocks = []
  let content = props.content
  
  // Extract chart components
  const chartPatterns = [
    { type: 'pie-chart', pattern: /:::pie-chart\s*\n([\s\S]*?):::/g },
    { type: 'bar-chart', pattern: /:::bar-chart\s*\n([\s\S]*?):::/g },
    { type: 'line-chart', pattern: /:::line-chart\s*\n([\s\S]*?):::/g }
  ]
  
  let lastIndex = 0
  const matches = []
  
  // Find all chart matches
  chartPatterns.forEach(({ type, pattern }) => {
    let match
    while ((match = pattern.exec(content)) !== null) {
      matches.push({
        type: 'component',
        componentType: type,
        markdown: match[0], // Full match including :::
        start: match.index,
        end: match.index + match[0].length,
        title: extractTitle(match[1])
      })
    }
  })
  
  // Sort matches by position
  matches.sort((a, b) => a.start - b.start)
  
  // Build blocks array
  matches.forEach((match) => {
    // Add text content before this match
    if (match.start > lastIndex) {
      const textContent = content.slice(lastIndex, match.start).trim()
      if (textContent) {
        blocks.push({
          type: 'markdown',
          content: render(textContent)
        })
      }
    }
    
    // Add the component
    blocks.push(match)
    lastIndex = match.end
  })
  
  // Add remaining content
  if (lastIndex < content.length) {
    const remainingContent = content.slice(lastIndex).trim()
    if (remainingContent) {
      blocks.push({
        type: 'markdown',
        content: render(remainingContent)
      })
    }
  }
  
  // If no components found, render as markdown
  if (blocks.length === 0) {
    blocks.push({
      type: 'markdown',
      content: render(content)
    })
  }
  
  return blocks
})

// Helper function to extract title from component content
const extractTitle = (content: string): string => {
  const lines = content.trim().split('\n')
  for (const line of lines) {
    if (line.startsWith('title:')) {
      return line.replace('title:', '').trim()
    }
  }
  return 'Chart'
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
}

.streaming-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  font-weight: bold;
  color: #3b82f6;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.content-block {
  margin-bottom: 0.5rem;
}

.content-block:last-child {
  margin-bottom: 0;
}
</style>
