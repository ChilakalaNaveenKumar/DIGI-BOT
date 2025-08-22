<template>
  <div class="streaming-markdown" :class="{ 'is-streaming': isStreaming }">
    <!-- Render content blocks with chart support -->
    <div v-for="(block, index) in contentBlocks" :key="index" class="content-block">
      <!-- Chart Component -->
      <EnhancedComponentRenderer
        v-if="block.type === 'chart'"
        :component-type="block.chartType"
        :markdown="block.content"
        :title="block.title"
      />
      <!-- Regular markdown -->
      <div v-else v-html="block.content" class="markdown-content" />
    </div>
    <span v-if="showCursor && isStreaming" class="streaming-cursor">|</span>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
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
          content: render(markdownContent)
        })
      }
    }
    
    // Add component block (chart or table)
    blocks.push({
      type: 'chart',
      chartType: match[1],
      content: match[2],
      title: extractTitle(match[2])
    })
    
    lastIndex = componentRegex.lastIndex
  }
  
  // Add remaining markdown
  if (lastIndex < content.length) {
    const remainingContent = content.slice(lastIndex)
    if (remainingContent.trim()) {
      blocks.push({
        type: 'markdown',
        content: render(remainingContent)
      })
    }
  }
  
  // If no charts found, return as single markdown block
  if (blocks.length === 0) {
    blocks.push({
      type: 'markdown',
      content: render(content)
    })
  }
  
  return blocks
})

function extractTitle(chartContent: string): string {
  const titleMatch = chartContent.match(/title:\s*(.+)/)
  return titleMatch ? titleMatch[1].trim() : ''
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
</style>