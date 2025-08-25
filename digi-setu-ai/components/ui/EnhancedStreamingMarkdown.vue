<template>
  <div class="enhanced-streaming-markdown" :class="{ 'is-streaming': isStreaming }">
    <!-- Render content blocks with enhanced component support -->
    <div v-for="(block, index) in renderedBlocks" :key="block.id" class="content-block">
      <!-- Enhanced Component Block -->
      <EnhancedComponentRenderer
        v-if="block.type === 'component' && block.component"
        :component-type="block.component.type"
        :component-data="block.component.data"
        :component-title="block.component.title"
        :position="block.component.position"
        :action="block.component.action"
      />
      
      <!-- Text Block with Typewriter Effect -->
      <UiTypewriterText
        v-else-if="block.type === 'text'"
        :content="block.content"
        :is-streaming="isStreaming && index === renderedBlocks.length - 1"
        :speed="mode === 'streaming' ? 30 : 50"
        :immediate="mode === 'static'"
        @typing-complete="onTypingComplete"
      />
    </div>
    
    <!-- Component Processing Indicator -->
    <div v-if="isProcessingComponents" class="component-processing-indicator">
      <div class="processing-spinner">
        <Icon name="lucide:loader-2" :size="16" class="animate-spin" />
      </div>
      <span class="processing-text">Processing components...</span>
    </div>
    
    <!-- Streaming Indicator -->
    <div v-if="isStreaming && showStreamingIndicator" class="streaming-indicator">
      <div class="streaming-dots">
        <span /><span /><span />
      </div>
      <span class="streaming-text">Generating...</span>
    </div>
    
    <!-- Typing Cursor -->
    <span v-if="isStreaming && showCursor" class="typing-cursor">|</span>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref, nextTick } from 'vue'
import { useMarkdown } from '~/composables/useMarkdown'
import { useEnhancedStreaming } from '~/composables/useEnhancedStreaming'

interface Props {
  content: string
  isStreaming?: boolean
  showCursor?: boolean
  showStreamingIndicator?: boolean
  mode?: 'streaming' | 'static' | 'dynamic'
  enableComponentMatching?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: false,
  showCursor: false,
  showStreamingIndicator: true,
  mode: 'static',
  enableComponentMatching: true
})

const emit = defineEmits<{
  'content-updated': [content: string]
  'streaming-complete': []
  'component-processed': [component: any]
  'components-ready': [components: any[]]
}>()

const { render } = useMarkdown()
const {
  processStreamingText,
  renderedBlocks,
  streamingContent,
  startStreaming,
  stopStreaming,
  addComponentFromMatcher
} = useEnhancedStreaming()

const isProcessingComponents = ref(false)

// Process content when it changes
watch(() => props.content, async (newContent) => {
  if (!newContent) return

  try {
    isProcessingComponents.value = true
    
    // Process the streaming text with enhanced parsing
    processStreamingText(newContent)
    
    // Emit content updated event
    emit('content-updated', newContent)
    
    // If components were found, emit components ready event
    if (streamingContent.value.components.length > 0) {
      emit('components-ready', streamingContent.value.components)
    }
    
  } catch (error) {
    console.error('Error processing streaming content:', error)
  } finally {
    isProcessingComponents.value = false
  }
}, { immediate: true })

// Handle streaming state changes
watch(() => props.isStreaming, (streaming) => {
  if (streaming) {
    startStreaming()
  } else {
    stopStreaming()
    emit('streaming-complete')
  }
})

// Handle typing completion
const onTypingComplete = () => {
  // Emit typing complete for individual blocks
  nextTick(() => {
    if (!props.isStreaming) {
      emit('streaming-complete')
    }
  })
}

// Method to add component from external source (like component matcher)
const addComponent = (componentResponse: string) => {
  addComponentFromMatcher(componentResponse)
  emit('component-processed', componentResponse)
}

// Expose methods for parent components
defineExpose({
  addComponent,
  processStreamingText
})
</script>

<style scoped>
.enhanced-streaming-markdown {
  width: 100%;
}

.content-block {
  margin-bottom: 0.5rem;
}

.content-block:last-child {
  margin-bottom: 0;
}

.content-block:empty {
  display: none;
}

.component-processing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0.5rem 0;
}

.processing-spinner {
  display: flex;
  align-items: center;
}

.processing-text {
  font-size: 0.75rem;
}

.streaming-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0.5rem 0;
}

.streaming-dots {
  display: flex;
  gap: 0.25rem;
}

.streaming-dots span {
  width: 0.375rem;
  height: 0.375rem;
  background: var(--text-tertiary);
  border-radius: 50%;
  animation: pulse 1.4s ease-in-out infinite;
}

.streaming-dots span:nth-child(1) {
  animation-delay: 0ms;
}

.streaming-dots span:nth-child(2) {
  animation-delay: 150ms;
}

.streaming-dots span:nth-child(3) {
  animation-delay: 300ms;
}

.streaming-text {
  font-size: 0.75rem;
}

.typing-cursor {
  display: inline-block;
  width: 0.5rem;
  color: var(--text-secondary);
  animation: pulse 1.4s ease-in-out infinite;
}

.is-streaming .content-block:last-child {
  position: relative;
}

/* Enhanced animations for component insertion */
.content-block {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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

/* Component-specific styling */
.content-block:has(.enhanced-component-renderer) {
  margin: 1rem 0;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .content-block {
    font-size: 0.875rem;
  }
  
  .component-processing-indicator,
  .streaming-indicator {
    font-size: 0.75rem;
  }
}
</style>
