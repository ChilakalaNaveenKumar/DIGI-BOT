<template>
  <div class="ds-progressive-json-container" :class="containerClasses">
    <!-- JSON Controls -->
    <div v-if="showControls" class="ds-json-controls">
      <div class="ds-control-group">
        <button 
          @click="toggleAnimation" 
          class="ds-control-btn"
          :class="{ 'active': animationsEnabled }"
        >
          <Zap class="w-4 h-4" />
          {{ animationsEnabled ? 'Live' : 'Static' }}
        </button>
        
        <button 
          @click="completeRendering" 
          class="ds-control-btn"
          v-if="isRendering"
        >
          <FastForward class="w-4 h-4" />
          Complete
        </button>
        
        <button 
          @click="toggleCollapse" 
          class="ds-control-btn"
        >
          <component :is="collapseIcon" class="w-4 h-4" />
          {{ allCollapsed ? 'Expand' : 'Collapse' }}
        </button>
        
        <button 
          @click="copyJson" 
          class="ds-control-btn"
          :title="copyButtonText"
        >
          <component :is="copyIcon" class="w-4 h-4" />
        </button>
      </div>
      
      <div class="ds-progress-indicator" v-if="isRendering">
        <div class="ds-progress-bar">
          <div 
            class="ds-progress-fill" 
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
        <span class="ds-progress-text">
          {{ itemsRendered }}/{{ totalItems }} {{ jsonType === 'array' ? 'items' : 'keys' }}
        </span>
      </div>
    </div>

    <!-- JSON Header -->
    <div v-if="showHeader" class="ds-json-header">
      <div class="ds-json-info">
        <div class="ds-json-type">
          <component :is="jsonTypeIcon" class="w-4 h-4" />
          <span>{{ jsonTypeDisplay }}</span>
        </div>
        <div v-if="isValidJson" class="ds-json-size">
          <Hash class="w-3 h-3" />
          <span>{{ jsonSize }} {{ jsonType === 'array' ? 'items' : 'keys' }}</span>
        </div>
      </div>
      
      <div class="ds-typing-indicator" v-if="isStreaming && animationsEnabled">
        <div class="ds-typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="ds-typing-text">Parsing JSON...</span>
      </div>
    </div>

    <!-- JSON Content -->
    <div class="ds-json-content" :style="{ maxHeight: maxHeight }">
      <!-- Loading State -->
      <div v-if="!hasContent" class="ds-json-loading">
        <div class="ds-loading-skeleton">
          <div class="ds-skeleton-brace">{</div>
          <div class="ds-skeleton-entry" v-for="n in 4" :key="n"></div>
          <div class="ds-skeleton-brace">}</div>
        </div>
      </div>

      <!-- Progressive JSON -->
      <div v-else-if="canRender && isValidJson" class="ds-json-wrapper">
        <!-- JSON Object -->
        <div v-if="jsonType === 'object'" class="ds-json-object">
          <div class="ds-json-brace ds-open-brace">{</div>
          
          <!-- Rendered Entries -->
          <div class="ds-json-entries">
            <div
              v-for="(entry, index) in visibleEntries"
              :key="entry.id || `entry-${index}`"
              class="ds-json-entry"
              :class="getEntryClasses(entry, index)"
              :style="getEntryAnimationStyle(index)"
            >
              <span class="ds-json-key">"{{ entry.key }}"</span>
              <span class="ds-json-colon">:</span>
              <span class="ds-json-value" :class="getValueClasses(entry.value)">
                {{ formatJsonValue(entry.value) }}
              </span>
              <span v-if="index < visibleEntries.length - 1 || isStreaming" class="ds-json-comma">,</span>
            </div>

            <!-- Current entry being painted -->
            <div v-if="isStreaming && currentPaintingEntry" class="ds-json-entry ds-painting-entry">
              <span class="ds-json-key ds-painting-content">"{{ currentPaintingEntry.key }}"</span>
              <span class="ds-json-colon">:</span>
              <span class="ds-json-value ds-painting-content" :class="getValueClasses(currentPaintingEntry.value)">
                {{ formatJsonValue(currentPaintingEntry.value) }}
              </span>
              <span class="ds-typing-cursor" v-if="animationsEnabled">█</span>
              <span class="ds-json-comma">,</span>
            </div>

            <!-- Placeholder for more entries -->
            <div v-if="isStreaming && hasMoreEntries" class="ds-json-entry ds-placeholder-entry">
              <div class="ds-painting-indicator">
                <div class="ds-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="ds-json-brace ds-close-brace">}</div>
        </div>

        <!-- JSON Array -->
        <div v-else-if="jsonType === 'array'" class="ds-json-array">
          <div class="ds-json-brace ds-open-brace">[</div>
          
          <!-- Rendered Items -->
          <div class="ds-json-items">
            <div
              v-for="(item, index) in visibleItems"
              :key="item.id || `item-${index}`"
              class="ds-json-item"
              :class="getItemClasses(item, index)"
              :style="getItemAnimationStyle(index)"
            >
              <span class="ds-json-value" :class="getValueClasses(item.value)">
                {{ formatJsonValue(item.value) }}
              </span>
              <span v-if="index < visibleItems.length - 1 || isStreaming" class="ds-json-comma">,</span>
            </div>

            <!-- Current item being painted -->
            <div v-if="isStreaming && currentPaintingItem" class="ds-json-item ds-painting-item">
              <span class="ds-json-value ds-painting-content" :class="getValueClasses(currentPaintingItem.value)">
                {{ formatJsonValue(currentPaintingItem.value) }}
              </span>
              <span class="ds-typing-cursor" v-if="animationsEnabled">█</span>
              <span class="ds-json-comma">,</span>
            </div>

            <!-- Placeholder for more items -->
            <div v-if="isStreaming && hasMoreItems" class="ds-json-item ds-placeholder-item">
              <div class="ds-painting-indicator">
                <div class="ds-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="ds-json-brace ds-close-brace">]</div>
        </div>
      </div>

      <!-- Partial JSON (streaming incomplete JSON) -->
      <div v-else-if="isStreaming && !isValidJson" class="ds-partial-json">
        <div class="ds-partial-header">
          <AlertCircle class="w-4 h-4" />
          <span>Parsing JSON...</span>
        </div>
        <pre class="ds-partial-content">{{ cleanContent }}</pre>
        <div class="ds-typing-cursor" v-if="animationsEnabled">█</div>
      </div>

      <!-- Fallback Content -->
      <div v-else-if="renderingError" class="ds-fallback-content">
        <div class="ds-fallback-header">
          <AlertTriangle class="w-4 h-4" />
          <span>Invalid JSON - Displaying raw content</span>
        </div>
        <pre class="ds-raw-content">{{ rawContent }}</pre>
      </div>

      <!-- Empty State -->
      <div v-else class="ds-empty-state">
        <Braces class="w-8 h-8 text-gray-400" />
        <p>No JSON data available</p>
      </div>
    </div>

    <!-- JSON Stats -->
    <div v-if="hasContent && showStats" class="ds-json-stats">
      <span v-if="isValidJson">{{ totalItems }} {{ jsonType === 'array' ? 'items' : 'keys' }}</span>
      <span v-if="jsonType">{{ jsonTypeDisplay }}</span>
      <span v-if="characterCount">{{ characterCount }} chars</span>
      <span v-if="!isValidJson" class="ds-invalid">Invalid JSON</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { 
  Braces, 
  Hash,
  Copy, 
  Check, 
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  AlertCircle,
  Zap,
  FastForward
} from 'lucide-vue-next'
import { useProgressiveRenderer } from '@/composables/useProgressiveRenderer'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  showControls: {
    type: Boolean,
    default: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showStats: {
    type: Boolean,
    default: true
  },
  maxHeight: {
    type: String,
    default: '500px'
  },
  animationDelay: {
    type: Number,
    default: 80
  },
  chunkSize: {
    type: Number,
    default: 3
  }
})

// Progressive renderer
const { createProgressiveRenderer } = useProgressiveRenderer()
const renderer = createProgressiveRenderer('json', {
  chunkSize: props.chunkSize,
  renderDelay: props.animationDelay,
  enableAnimations: true,
  fallbackMode: 'graceful'
})

// Destructure renderer state and methods
const {
  rawContent,
  parsedContent,
  visibleItems,
  renderProgress,
  isRendering,
  renderingError,
  hasContent,
  canRender,
  progressPercentage,
  itemsRendered,
  totalItems,
  updateContent,
  completeRendering: rendererCompleteRendering,
  stopRendering
} = renderer

// Local state
const copied = ref(false)
const animationsEnabled = ref(true)
const allCollapsed = ref(false)

// Computed properties
const isValidJson = computed(() => {
  return parsedContent.value && !renderingError.value
})

const jsonType = computed(() => {
  if (!parsedContent.value) return null
  return parsedContent.value.type === 'json-array' ? 'array' : 'object'
})

const jsonTypeDisplay = computed(() => {
  return jsonType.value === 'array' ? 'JSON Array' : 'JSON Object'
})

const jsonTypeIcon = computed(() => {
  return Braces // Could use different icons for array vs object
})

const jsonSize = computed(() => {
  if (!parsedContent.value) return 0
  return jsonType.value === 'array' 
    ? parsedContent.value.items?.length || 0
    : parsedContent.value.entries?.length || 0
})

const containerClasses = computed(() => {
  return {
    'ds-json-streaming': props.isStreaming,
    'ds-json-animated': animationsEnabled.value,
    'ds-json-valid': isValidJson.value,
    'ds-json-invalid': !isValidJson.value && hasContent.value,
    'ds-json-array': jsonType.value === 'array',
    'ds-json-object': jsonType.value === 'object'
  }
})

const visibleEntries = computed(() => {
  if (jsonType.value !== 'object') return []
  return visibleItems.value || []
})

const visibleItemsArray = computed(() => {
  if (jsonType.value !== 'array') return []
  return visibleItems.value || []
})

const currentPaintingEntry = computed(() => {
  if (!props.isStreaming || jsonType.value !== 'object' || !parsedContent.value) return null
  
  const allEntries = parsedContent.value.entries || []
  const visibleCount = visibleItems.value.length
  
  if (visibleCount < allEntries.length) {
    return allEntries[visibleCount] || null
  }
  
  return null
})

const currentPaintingItem = computed(() => {
  if (!props.isStreaming || jsonType.value !== 'array' || !parsedContent.value) return null
  
  const allItems = parsedContent.value.items || []
  const visibleCount = visibleItems.value.length
  
  if (visibleCount < allItems.length) {
    return allItems[visibleCount] || null
  }
  
  return null
})

const hasMoreEntries = computed(() => {
  if (jsonType.value !== 'object' || !parsedContent.value) return false
  const allEntries = parsedContent.value.entries || []
  return visibleItems.value.length < allEntries.length
})

const hasMoreItems = computed(() => {
  if (jsonType.value !== 'array' || !parsedContent.value) return false
  const allItems = parsedContent.value.items || []
  return visibleItems.value.length < allItems.length
})

const cleanContent = computed(() => {
  return rawContent.value.replace(/DIGI_JSON_START\n?/g, '').trim()
})

const characterCount = computed(() => {
  return rawContent.value.length
})

const copyIcon = computed(() => {
  return copied.value ? Check : Copy
})

const copyButtonText = computed(() => {
  return copied.value ? 'Copied!' : 'Copy JSON'
})

const collapseIcon = computed(() => {
  return allCollapsed.value ? ChevronDown : ChevronUp
})

// Methods
const copyJson = async () => {
  try {
    const contentToCopy = isValidJson.value 
      ? JSON.stringify(getParsedData(), null, 2)
      : cleanContent.value
    
    await navigator.clipboard.writeText(contentToCopy)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy JSON:', error)
  }
}

const toggleAnimation = () => {
  animationsEnabled.value = !animationsEnabled.value
}

const toggleCollapse = () => {
  allCollapsed.value = !allCollapsed.value
}

const completeRendering = () => {
  rendererCompleteRendering()
}

const getParsedData = () => {
  if (!parsedContent.value) return null
  
  if (jsonType.value === 'array') {
    return parsedContent.value.items?.map(item => item.value) || []
  } else {
    const obj = {}
    parsedContent.value.entries?.forEach(entry => {
      obj[entry.key] = entry.value
    })
    return obj
  }
}

const formatJsonValue = (value) => {
  if (value === null) return 'null'
  if (value === undefined) return 'undefined'
  if (typeof value === 'string') return `"${value}"`
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const getValueClasses = (value) => {
  const type = typeof value
  return {
    'ds-value-string': type === 'string',
    'ds-value-number': type === 'number',
    'ds-value-boolean': type === 'boolean',
    'ds-value-null': value === null,
    'ds-value-object': type === 'object' && value !== null,
    'ds-value-array': Array.isArray(value)
  }
}

const getEntryClasses = (entry, index) => {
  return {
    'ds-entry-even': index % 2 === 0,
    'ds-entry-odd': index % 2 === 1,
    'ds-entry-new': animationsEnabled.value && isRendering.value
  }
}

const getItemClasses = (item, index) => {
  return {
    'ds-item-even': index % 2 === 0,
    'ds-item-odd': index % 2 === 1,
    'ds-item-new': animationsEnabled.value && isRendering.value
  }
}

const getEntryAnimationStyle = (index) => {
  if (!animationsEnabled.value || !isRendering.value) return {}
  
  return {
    animationDelay: `${index * 60}ms`,
    animationDuration: '0.4s'
  }
}

const getItemAnimationStyle = (index) => {
  if (!animationsEnabled.value || !isRendering.value) return {}
  
  return {
    animationDelay: `${index * 60}ms`,
    animationDuration: '0.4s'
  }
}

// Watch for content changes
watch(() => props.content, (newContent) => {
  updateContent(newContent, props.isStreaming)
}, { immediate: true })

watch(() => props.isStreaming, (streaming) => {
  if (streaming) {
    updateContent(props.content, true)
  } else {
    // Complete rendering when streaming stops
    setTimeout(() => {
      completeRendering()
    }, 300)
  }
})

// Lifecycle
onMounted(() => {
  updateContent(props.content, props.isStreaming)
})
</script>

<style scoped>
.ds-progressive-json-container {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  line-height: 1.6;
}

/* === CONTROLS === */
.ds-json-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-control-group {
  display: flex;
  gap: var(--ds-space-2);
}

.ds-control-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-control-btn:hover {
  background: var(--ds-surface-hover);
}

.ds-control-btn.active {
  background: var(--ds-primary);
  color: white;
  border-color: var(--ds-primary);
}

.ds-progress-indicator {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-progress-bar {
  width: 120px;
  height: 4px;
  background: var(--ds-border-primary);
  border-radius: var(--ds-radius-full);
  overflow: hidden;
}

.ds-progress-fill {
  height: 100%;
  background: var(--ds-primary);
  transition: width var(--ds-transition-fast);
}

.ds-progress-text {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
  min-width: 100px;
}

/* === HEADER === */
.ds-json-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-3) var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-json-info {
  display: flex;
  align-items: center;
  gap: var(--ds-space-4);
}

.ds-json-type {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
}

.ds-json-size {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-text-muted);
  font-size: var(--ds-text-sm);
}

.ds-typing-indicator {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-primary);
}

.ds-typing-dots {
  display: flex;
  gap: 4px;
}

.ds-typing-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--ds-primary);
  animation: dotPulse 1.4s infinite ease-in-out;
}

.ds-typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.ds-typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.ds-typing-text {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
}

/* === CONTENT === */
.ds-json-content {
  overflow-x: auto;
  overflow-y: auto;
  padding: var(--ds-space-4);
}

.ds-json-wrapper {
  position: relative;
}

/* === JSON STRUCTURE === */
.ds-json-brace {
  font-weight: var(--ds-font-bold);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-lg);
}

.ds-json-entries,
.ds-json-items {
  padding-left: var(--ds-space-6);
  margin: var(--ds-space-2) 0;
}

.ds-json-entry,
.ds-json-item {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-1) 0;
  line-height: 1.6;
}

.ds-json-key {
  color: var(--ds-primary);
  font-weight: var(--ds-font-medium);
}

.ds-json-colon {
  color: var(--ds-text-muted);
}

.ds-json-comma {
  color: var(--ds-text-muted);
}

/* === VALUE TYPES === */
.ds-json-value.ds-value-string {
  color: var(--ds-secondary);
}

.ds-json-value.ds-value-number {
  color: var(--ds-accent);
}

.ds-json-value.ds-value-boolean {
  color: var(--ds-info);
  font-weight: var(--ds-font-medium);
}

.ds-json-value.ds-value-null {
  color: var(--ds-text-muted);
  font-style: italic;
}

.ds-json-value.ds-value-object,
.ds-json-value.ds-value-array {
  color: var(--ds-warning);
}

/* === PROGRESSIVE RENDERING === */
.ds-json-animated .ds-json-entry,
.ds-json-animated .ds-json-item {
  animation: fadeInLeft 0.4s ease-out forwards;
  opacity: 0;
  transform: translateX(-15px);
}

@keyframes fadeInLeft {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.ds-painting-entry,
.ds-painting-item {
  background: color-mix(in srgb, var(--ds-primary) 5%, transparent);
  border-radius: var(--ds-radius-sm);
  padding: var(--ds-space-1) var(--ds-space-2);
  margin: 0 calc(-1 * var(--ds-space-2));
}

.ds-painting-content {
  display: inline;
}

.ds-typing-cursor {
  color: var(--ds-primary);
  animation: blink 1s infinite;
  margin-left: 4px;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.ds-placeholder-entry,
.ds-placeholder-item {
  opacity: 0.5;
}

.ds-painting-indicator {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: var(--ds-space-2);
}

.ds-dots {
  display: flex;
  gap: 4px;
}

.ds-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--ds-primary);
  animation: dotPulse 1.4s infinite ease-in-out;
}

/* === LOADING === */
.ds-json-loading {
  padding: var(--ds-space-4);
}

.ds-loading-skeleton {
  animation: pulse 2s infinite;
}

.ds-skeleton-brace {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-bold);
  color: var(--ds-text-muted);
  margin: var(--ds-space-1) 0;
}

.ds-skeleton-entry {
  height: 24px;
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-sm);
  margin: var(--ds-space-2) 0 var(--ds-space-2) var(--ds-space-6);
}

.ds-skeleton-entry:nth-child(2) { width: 80%; }
.ds-skeleton-entry:nth-child(3) { width: 60%; }
.ds-skeleton-entry:nth-child(4) { width: 90%; }
.ds-skeleton-entry:nth-child(5) { width: 70%; }

/* === PARTIAL JSON === */
.ds-partial-json {
  position: relative;
}

.ds-partial-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-3);
  color: var(--ds-warning);
  font-weight: var(--ds-font-medium);
}

.ds-partial-content {
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-3);
  white-space: pre-wrap;
  overflow-x: auto;
  position: relative;
}

/* === FALLBACK === */
.ds-fallback-content {
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-4);
}

.ds-fallback-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-3);
  color: var(--ds-danger);
  font-weight: var(--ds-font-medium);
}

.ds-raw-content {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-3);
  white-space: pre-wrap;
  overflow-x: auto;
}

/* === EMPTY STATE === */
.ds-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-6);
  color: var(--ds-text-muted);
}

/* === STATS === */
.ds-json-stats {
  display: flex;
  gap: var(--ds-space-4);
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-top: 1px solid var(--ds-border-primary);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
}

.ds-invalid {
  color: var(--ds-danger);
  font-weight: var(--ds-font-medium);
}

/* === SCROLLBAR === */
.ds-json-content::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.ds-json-content::-webkit-scrollbar-track {
  background: var(--ds-surface-secondary);
}

.ds-json-content::-webkit-scrollbar-thumb {
  background: var(--ds-border-secondary);
  border-radius: var(--ds-radius-full);
}

.ds-json-content::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-json-controls {
    flex-direction: column;
    gap: var(--ds-space-3);
    align-items: stretch;
  }
  
  .ds-progress-indicator {
    justify-content: space-between;
  }
  
  .ds-json-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--ds-space-2);
  }
  
  .ds-json-entries,
  .ds-json-items {
    padding-left: var(--ds-space-4);
  }
  
  .ds-json-entry,
  .ds-json-item {
    flex-wrap: wrap;
    gap: var(--ds-space-1);
  }
}
</style>
