<template>
  <div class="ds-progressive-content-renderer" :class="contentTypeClass">
    <!-- Stable Container to Prevent Layout Shifts -->
    <div class="ds-stable-container">
    <!-- Progressive Table -->
    <div v-if="routedContent.contentType === 'table'" class="ds-progressive-table-wrapper">
      <DigiSetuProgressiveTable
        :content="routedContent.cleanContent"
        :is-streaming="routedContent.isStreaming"
        :show-controls="true"
        :show-stats="true"
        :animation-delay="50"
        :chunk-size="2"
      />
    </div>

    <!-- Progressive Code -->
    <div v-else-if="routedContent.contentType === 'code'" class="ds-progressive-code-wrapper">
      <DigiSetuProgressiveCodeBlock
        :content="routedContent.cleanContent"
        :language="routedContent.progressiveData?.codeLanguage || 'text'"
        :is-streaming="routedContent.isStreaming"
        :show-controls="true"
        :show-stats="true"
        :animation-delay="30"
        :chunk-size="3"
      />
    </div>

    <!-- Progressive JSON -->
    <div v-else-if="routedContent.contentType === 'json'" class="ds-progressive-json-wrapper">
      <DigiSetuProgressiveJsonViewer
        :content="routedContent.cleanContent"
        :is-streaming="routedContent.isStreaming"
        :show-controls="true"
        :show-stats="true"
        :animation-delay="80"
        :chunk-size="3"
      />
    </div>

    <!-- Progressive Diagram -->
    <div v-else-if="routedContent.contentType === 'diagram'" class="ds-progressive-diagram-wrapper">
      <!-- User requirement: "load until it gets whole output" -->
      <!-- Only show diagram when streaming is complete (END tag received) -->
      <div v-if="routedContent.isStreaming" class="ds-diagram-loading">
        <div class="ds-loading-text">📊 Building diagram... (waiting for complete output)</div>
        <div class="ds-loading-spinner"></div>
      </div>
      <DigiSetuProgressiveDiagram
        v-else
        :content="routedContent.cleanContent"
        :is-streaming="false"
      />
    </div>

    <!-- Thought Process / Thinking -->
    <div v-else-if="routedContent.contentType === 'thinking'" class="ds-thinking-content">
      <DigiSetuThoughtProcess 
        :content="routedContent.cleanContent"
        :is-streaming="routedContent.isStreaming"
        :show-typing-indicator="true"
      />
    </div>

    <!-- Tool Results -->
    <div v-else-if="routedContent.contentType === 'tool'" class="ds-tool-content">
      <DigiSetuToolResult 
        :content="routedContent.cleanContent"
        :tool-name="extractToolName(routedContent.content)"
        :is-streaming="routedContent.isStreaming"
      />
    </div>

    <!-- Search Results -->
    <div v-else-if="routedContent.contentType === 'search'" class="ds-search-content">
      <DigiSetuSearchResults 
        :content="routedContent.cleanContent"
        :is-streaming="routedContent.isStreaming"
      />
    </div>

    <!-- Default Text Content -->
    <div v-else class="ds-text-content">
      <DigiSetuText 
        :content="routedContent.cleanContent"
        :is-streaming="routedContent.isStreaming"
        :enable-markdown="true"
      />
    </div>

    <!-- Debug Info (only in development) -->
    <div v-if="showDebugInfo && isDevelopment" class="ds-debug-info">
      <details class="ds-debug-details">
        <summary class="ds-debug-summary">
          🔍 Content Routing Debug ({{ routedContent.contentType }} - {{ Math.round(routedContent.confidence * 100) }}% confidence)
        </summary>
        <div class="ds-debug-content">
          <div class="ds-debug-section">
            <h4>Detection Info</h4>
            <ul>
              <li><strong>Type:</strong> {{ routedContent.contentType }}</li>
              <li><strong>Component:</strong> {{ routedContent.component }}</li>
              <li><strong>Confidence:</strong> {{ Math.round(routedContent.confidence * 100) }}%</li>
              <li><strong>Streaming:</strong> {{ routedContent.isStreaming }}</li>
              <li><strong>Stream ID:</strong> {{ routedContent.streamId }}</li>
            </ul>
          </div>
          
          <div v-if="routedContent.detectionHistory?.length" class="ds-debug-section">
            <h4>Detection History</h4>
            <div class="ds-detection-history">
              <div 
                v-for="(detection, index) in routedContent.detectionHistory.slice(-3)"
                :key="index"
                class="ds-detection-item"
              >
                <span class="ds-detection-type">{{ detection.type }}</span>
                <span class="ds-detection-confidence">{{ Math.round(detection.confidence * 100) }}%</span>
                <span class="ds-detection-method">{{ detection.method }}</span>
              </div>
            </div>
          </div>

          <div v-if="routedContent.progressiveData" class="ds-debug-section">
            <h4>Progressive Data</h4>
            <pre class="ds-debug-json">{{ JSON.stringify(routedContent.progressiveData, null, 2) }}</pre>
          </div>
        </div>
      </details>
    </div>
    </div> <!-- Close ds-stable-container -->
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useUnifiedContentRouter } from '@/composables/useUnifiedContentRouter'

// Import progressive components
import DigiSetuProgressiveTable from './DigiSetuProgressiveTable.vue'
import DigiSetuProgressiveCodeBlock from './DigiSetuProgressiveCodeBlock.vue'
import DigiSetuProgressiveJsonViewer from './DigiSetuProgressiveJsonViewer.vue'
import DigiSetuProgressiveDiagram from './DigiSetuProgressiveDiagram.vue'

// Import existing components
import DigiSetuThoughtProcess from './DigiSetuThoughtProcess.vue'
import DigiSetuToolResult from './DigiSetuToolResult.vue'
import DigiSetuSearchResults from './DigiSetuSearchResults.vue'
import DigiSetuText from './DigiSetuText.vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  streamId: {
    type: String,
    default: 'default'
  },
  showDebugInfo: {
    type: Boolean,
    default: false
  }
})

// Unified content router
const { routeContent, completeStream } = useUnifiedContentRouter()

// Route the content
const routedContent = computed(() => {
  const chunk = {
    content: props.content,
    isStreaming: props.isStreaming
  }
  
  return routeContent(chunk, props.streamId)
})

// Content type class for styling
const contentTypeClass = computed(() => {
  return `ds-content-${routedContent.value.contentType}`
})

// Development mode check
const isDevelopment = computed(() => {
  return process.env.NODE_ENV === 'development'
})

// Utility methods
const tryParseJson = (content) => {
  try {
    return JSON.parse(content.trim())
  } catch (e) {
    return { error: 'Invalid JSON', content }
  }
}

const extractToolName = (content) => {
  // Extract tool name from content patterns
  const toolMatch = content.match(/🔧 DIGI_TOOL_START.*?(\w+)/i)
  return toolMatch ? toolMatch[1] : 'Unknown Tool'
}

// Complete streaming when component unmounts or streaming stops
watch(() => props.isStreaming, (streaming) => {
  if (!streaming) {
    setTimeout(() => {
      completeStream(props.streamId)
    }, 1000) // Give a bit of time for final chunks
  }
})

// Expose methods for parent components
defineExpose({
  routedContent,
  completeStream: () => completeStream(props.streamId)
})
</script>

<style scoped>
.ds-progressive-content-renderer {
  width: 100%;
  min-height: 0; /* Allow shrinking */
}

/* === STABLE CONTAINER TO PREVENT UI SHAKING === */
.ds-stable-container {
  min-height: 1.5rem; /* Prevent collapse and layout shifts */
  transition: all 0.15s ease-out; /* Smooth transitions */
  will-change: height; /* Optimize for height changes */
  contain: layout style; /* Prevent layout thrashing */
  transform: translateZ(0); /* Force GPU acceleration */
}

/* === CONTENT TYPE WRAPPERS === */
/* Consistent container design for all content types */
.ds-progressive-table-wrapper,
.ds-progressive-code-wrapper,
.ds-progressive-json-wrapper,
.ds-progressive-diagram-wrapper,
.ds-thinking-content,
.ds-tool-content,
.ds-search-content,
.ds-text-content {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-subtle);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
  margin: var(--ds-space-3) 0;
  transition: all 0.2s ease-out;
  contain: layout style;
}

/* Content type specific styling */
.ds-content-table .ds-progressive-table-wrapper {
  border-left: 4px solid var(--ds-success);
}

.ds-content-code .ds-progressive-code-wrapper {
  border-left: 4px solid var(--ds-info);
}

.ds-content-json .ds-progressive-json-wrapper {
  border-left: 4px solid var(--ds-warning);
}

.ds-content-diagram .ds-progressive-diagram-wrapper {
  border-left: 4px solid var(--ds-secondary);
}

.ds-content-thinking .ds-thinking-content {
  border-left: 4px solid var(--ds-primary);
  background: color-mix(in srgb, var(--ds-primary) 3%, var(--ds-surface-primary));
}

.ds-content-tool .ds-tool-content {
  border-left: 4px solid var(--ds-secondary);
  background: color-mix(in srgb, var(--ds-secondary) 3%, var(--ds-surface-primary));
}

.ds-content-search .ds-search-content {
  border-left: 4px solid var(--ds-info);
  background: color-mix(in srgb, var(--ds-info) 3%, var(--ds-surface-primary));
}

.ds-content-text .ds-text-content {
  border-left: 4px solid var(--ds-text-secondary);
  padding: var(--ds-space-4);
}

/* === DIAGRAM LOADING STATE === */
.ds-diagram-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-6);
  min-height: 120px;
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
}

.ds-loading-text {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  margin-bottom: var(--ds-space-3);
}

.ds-loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--ds-border-subtle);
  border-top: 2px solid var(--ds-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* === DEBUG INFO === */
.ds-debug-info {
  margin-top: var(--ds-space-4);
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-xs);
}

.ds-debug-details {
  width: 100%;
}

.ds-debug-summary {
  cursor: pointer;
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  padding: var(--ds-space-2);
  background: var(--ds-surface-tertiary);
  border-radius: var(--ds-radius-sm);
  margin-bottom: var(--ds-space-2);
}

.ds-debug-summary:hover {
  background: var(--ds-surface-hover);
}

.ds-debug-content {
  display: grid;
  gap: var(--ds-space-3);
  margin-top: var(--ds-space-3);
}

.ds-debug-section {
  background: var(--ds-surface-primary);
  padding: var(--ds-space-3);
  border-radius: var(--ds-radius-sm);
  border: 1px solid var(--ds-border-secondary);
}

.ds-debug-section h4 {
  margin: 0 0 var(--ds-space-2) 0;
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
  font-weight: var(--ds-font-medium);
}

.ds-debug-section ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.ds-debug-section li {
  padding: var(--ds-space-1) 0;
  color: var(--ds-text-muted);
}

.ds-debug-section strong {
  color: var(--ds-text-primary);
  font-weight: var(--ds-font-medium);
}

.ds-detection-history {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-1);
}

.ds-detection-item {
  display: flex;
  gap: var(--ds-space-2);
  padding: var(--ds-space-1);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-sm);
  font-size: var(--ds-text-xs);
}

.ds-detection-type {
  font-weight: var(--ds-font-medium);
  color: var(--ds-primary);
}

.ds-detection-confidence {
  color: var(--ds-secondary);
}

.ds-detection-method {
  color: var(--ds-text-muted);
  font-style: italic;
}

.ds-debug-json {
  background: var(--ds-surface-secondary);
  padding: var(--ds-space-2);
  border-radius: var(--ds-radius-sm);
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-debug-info {
    font-size: var(--ds-text-2xs);
  }
  
  .ds-debug-content {
    grid-template-columns: 1fr;
  }
  
  .ds-detection-item {
    flex-direction: column;
    gap: var(--ds-space-1);
  }
}

/* === ANIMATIONS === */
.ds-progressive-content-renderer {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Content wrapper animations */
.ds-progressive-table-wrapper,
.ds-progressive-code-wrapper,
.ds-json-content,
.ds-diagram-content,
.ds-thinking-content,
.ds-tool-content,
.ds-search-content,
.ds-text-content {
  animation: slideInUp 0.4s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
