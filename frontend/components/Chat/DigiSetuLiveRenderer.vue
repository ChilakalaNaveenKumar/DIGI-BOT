<template>
  <div class="ds-live-renderer">
    <!-- Render each segment with its appropriate component -->
    <div 
      v-for="(segment, index) in segments" 
      :key="`segment-${index}`"
      class="ds-content-segment"
      :class="{
        'ds-segment-incomplete': !segment.metadata?.isComplete,
        'ds-segment-streaming': isStreaming && index === segments.length - 1
      }"
    >
      <!-- Segment type indicator for debugging (only in dev) -->
      <div v-if="showDebugInfo" class="ds-segment-debug">
        {{ segment.type }} ({{ segment.metadata?.isComplete ? 'complete' : 'streaming' }})
      </div>
      
      <!-- Dynamic component rendering -->
      <component 
        :is="getSegmentComponent(segment)"
        :content="segment.content"
        :content-type="segment.type"
        :metadata="segment.metadata || {}"
        :is-streaming="isStreaming && index === segments.length - 1"
        class="ds-segment-content"
      />
      
      <!-- Streaming indicator for incomplete segments -->
      <div 
        v-if="!segment.metadata?.isComplete && isStreaming && index === segments.length - 1" 
        class="ds-streaming-indicator"
      >
        <div class="ds-streaming-dot"></div>
        <span class="ds-streaming-text">Streaming...</span>
      </div>
    </div>
    
    <!-- Fallback for empty content -->
    <div v-if="segments.length === 0" class="ds-empty-content">
      <div class="ds-streaming-placeholder">
        <div class="ds-streaming-dot"></div>
        <span>Waiting for content...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Import all possible components
import DigiSetuText from './DigiSetuText.vue'
import DigiSetuMarkdown from './DigiSetuMarkdown.vue'
import DigiSetuCodeBlock from './DigiSetuCodeBlock.vue'
import DigiSetuJsonViewer from './DigiSetuJsonViewer.vue'
import DigiSetuTable from './DigiSetuTable.vue'
import DigiSetuDiagram from './DigiSetuDiagram.vue'
import DigiSetuToolResult from './DigiSetuToolResult.vue'
import DigiSetuSearchResults from './DigiSetuSearchResults.vue'

const props = defineProps({
  segments: {
    type: Array,
    default: () => []
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  showDebugInfo: {
    type: Boolean,
    default: false // Set to true for development
  }
})

const componentMap = {
  text: DigiSetuText,
  thinking: DigiSetuText, // Thinking uses text component
  markdown: DigiSetuMarkdown,
  code: DigiSetuCodeBlock,
  json: DigiSetuJsonViewer,
  table: DigiSetuTable,
  diagram: DigiSetuDiagram,
  tool: DigiSetuToolResult,
  search: DigiSetuSearchResults
}

const getSegmentComponent = (segment) => {
  return componentMap[segment.type] || DigiSetuText
}
</script>

<style scoped>
.ds-live-renderer {
  width: 100%;
}

.ds-content-segment {
  margin-bottom: var(--ds-space-2);
  position: relative;
}

.ds-content-segment:last-child {
  margin-bottom: 0;
}

.ds-segment-incomplete {
  opacity: 0.9;
}

.ds-segment-streaming {
  border-left: 2px solid var(--ds-primary);
  padding-left: var(--ds-space-3);
  background: linear-gradient(90deg, 
    color-mix(in srgb, var(--ds-primary) 3%, transparent) 0%,
    transparent 100%);
  border-radius: 0 var(--ds-radius-md) var(--ds-radius-md) 0;
}

.ds-segment-debug {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-tertiary);
  background: var(--ds-surface-tertiary);
  padding: var(--ds-space-1) var(--ds-space-2);
  border-radius: var(--ds-radius-sm);
  margin-bottom: var(--ds-space-1);
  font-family: var(--ds-font-mono);
}

.ds-segment-content {
  width: 100%;
}

.ds-streaming-indicator {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-top: var(--ds-space-2);
  color: var(--ds-text-tertiary);
  font-size: var(--ds-text-sm);
}

.ds-streaming-text {
  font-style: italic;
}

.ds-streaming-dot {
  width: 8px;
  height: 8px;
  background: var(--ds-primary);
  border-radius: 50%;
  animation: ds-pulse 1.5s ease-in-out infinite;
}

.ds-empty-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-4);
  color: var(--ds-text-tertiary);
  font-style: italic;
}

.ds-streaming-placeholder {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
}

@keyframes ds-pulse {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .ds-segment-streaming {
    padding-left: var(--ds-space-2);
  }
  
  .ds-streaming-indicator {
    margin-top: var(--ds-space-1);
  }
}
</style>
