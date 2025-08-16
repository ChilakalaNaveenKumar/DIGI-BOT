<template>
  <div class="ds-activity-stream">
    <div class="ds-activity-content">
      <!-- Activity Icon -->
      <div class="ds-activity-icon" :class="activityIconClass">
        <component :is="activityIcon" class="w-4 h-4" />
      </div>

      <!-- Activity Text -->
      <div class="ds-activity-text">
        <span class="ds-activity-message">{{ displayMessage }}</span>
        <div v-if="showProgress" class="ds-activity-progress">
          <div class="ds-progress-bar">
            <div class="ds-progress-fill" :style="{ width: `${progress}%` }"></div>
          </div>
          <span class="ds-progress-text">{{ progress }}%</span>
        </div>
      </div>

      <!-- Provider Badge -->
      <div v-if="provider" class="ds-activity-provider">
        <component :is="getProviderIcon(provider)" class="w-3 h-3" />
        <span>{{ getProviderName(provider) }}</span>
      </div>

      <!-- Elapsed Time -->
      <div class="ds-activity-time">
        {{ elapsedTime }}s
      </div>
    </div>

    <!-- Activity Details (Expandable) -->
    <div v-if="showDetails && activityDetails" class="ds-activity-details">
      <button class="ds-details-toggle" @click="toggleDetails">
        <ChevronDown class="w-3 h-3" :class="{ 'rotated': detailsExpanded }" />
        <span>{{ detailsExpanded ? 'Hide' : 'Show' }} details</span>
      </button>
      
      <div v-if="detailsExpanded" class="ds-details-content">
        <div v-for="(detail, index) in activityDetails" :key="index" class="ds-detail-item">
          <div class="ds-detail-timestamp">{{ formatTimestamp(detail.timestamp) }}</div>
          <div class="ds-detail-message">{{ detail.message }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Loader2, Brain, Search, Image, FileText, Code, 
  Database, Globe, Zap, ChevronDown, Clock
} from 'lucide-vue-next'

const props = defineProps({
  activity: {
    type: String,
    required: true
  },
  provider: {
    type: String,
    default: null
  },
  progress: {
    type: Number,
    default: null
  },
  details: {
    type: Array,
    default: () => []
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})

// Reactive state
const startTime = ref(Date.now())
const elapsedTime = ref(0)
const detailsExpanded = ref(false)
const timer = ref(null)

// Activity message mapping with privacy-aware, user-friendly messages
const activityMessages = {
  // General activities
  'thinking': 'Analyzing your request...',
  'processing': 'Processing information...',
  'analyzing': 'Analyzing the content...',
  'generating': 'Generating response...',
  'finalizing': 'Finalizing answer...',
  
  // Search and retrieval
  'searching': 'Searching for information...',
  'retrieving': 'Retrieving relevant data...',
  'indexing': 'Indexing content...',
  'querying': 'Querying knowledge base...',
  
  // Content processing
  'reading_document': 'Reading your document...',
  'parsing_content': 'Understanding the content...',
  'extracting_data': 'Extracting key information...',
  'summarizing': 'Creating summary...',
  
  // Code-related
  'analyzing_code': 'Analyzing the code...',
  'generating_code': 'Writing code...',
  'testing_code': 'Validating solution...',
  'optimizing': 'Optimizing approach...',
  
  // Image processing
  'processing_image': 'Processing your image...',
  'analyzing_image': 'Analyzing visual content...',
  'generating_image': 'Creating image...',
  'enhancing_image': 'Enhancing image quality...',
  
  // AI orchestration
  'selecting_model': 'Choosing best AI model...',
  'routing_request': 'Routing to specialist AI...',
  'coordinating': 'Coordinating AI responses...',
  'validating_response': 'Validating answer quality...',
  
  // Tool execution
  'executing_tool': 'Running specialized tool...',
  'calling_api': 'Accessing external service...',
  'processing_results': 'Processing results...',
  'formatting_output': 'Formatting response...'
}

// Activity icons mapping
const activityIcons = {
  'thinking': Brain,
  'processing': Loader2,
  'analyzing': Brain,
  'generating': Loader2,
  'searching': Search,
  'retrieving': Database,
  'reading_document': FileText,
  'analyzing_code': Code,
  'processing_image': Image,
  'selecting_model': Zap,
  'executing_tool': Loader2,
  'default': Loader2
}

// Computed properties
const displayMessage = computed(() => {
  return activityMessages[props.activity] || 
         activityMessages[props.activity.toLowerCase()] || 
         'Working on your request...'
})

const activityIcon = computed(() => {
  return activityIcons[props.activity] || 
         activityIcons[props.activity.toLowerCase()] || 
         activityIcons.default
})

const activityIconClass = computed(() => {
  const baseClass = 'ds-activity-spinning'
  
  // Different animation styles for different activities
  if (['thinking', 'analyzing', 'processing'].includes(props.activity)) {
    return `${baseClass} ds-activity-pulse`
  } else if (['searching', 'retrieving', 'querying'].includes(props.activity)) {
    return `${baseClass} ds-activity-bounce`
  } else {
    return baseClass
  }
})

const activityDetails = computed(() => {
  return props.details.length > 0 ? props.details : null
})

// Provider utilities
const getProviderIcon = (provider) => {
  const iconMap = {
    'openai': Brain,
    'anthropic': Zap,
    'grok': Globe
  }
  return iconMap[provider] || Brain
}

const getProviderName = (provider) => {
  const nameMap = {
    'openai': 'GPT-5',
    'anthropic': 'Claude-4',
    'grok': 'Grok-4'
  }
  return nameMap[provider] || provider
}

// Methods
const toggleDetails = () => {
  detailsExpanded.value = !detailsExpanded.value
}

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

const updateElapsedTime = () => {
  elapsedTime.value = Math.floor((Date.now() - startTime.value) / 1000)
}

// Lifecycle
onMounted(() => {
  // Update elapsed time every second
  timer.value = setInterval(updateElapsedTime, 1000)
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped>
.ds-activity-stream {
  background: color-mix(in srgb, var(--ds-primary) 5%, transparent);
  border: 1px solid color-mix(in srgb, var(--ds-primary) 20%, transparent);
  border-radius: var(--ds-radius-xl);
  padding: var(--ds-space-4);
  margin-bottom: var(--ds-space-4);
  animation: ds-fade-in 0.3s ease-out;
}

/* === ACTIVITY CONTENT === */
.ds-activity-content {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-activity-icon {
  color: var(--ds-primary);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ds-activity-spinning {
  animation: ds-spin 2s linear infinite;
}

.ds-activity-pulse {
  animation: ds-pulse 1.5s ease-in-out infinite;
}

.ds-activity-bounce {
  animation: ds-bounce 1s ease-in-out infinite;
}

@keyframes ds-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes ds-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes ds-bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

.ds-activity-text {
  flex: 1;
  min-width: 0;
}

.ds-activity-message {
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-activity-progress {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-top: var(--ds-space-2);
}

.ds-progress-bar {
  flex: 1;
  height: 4px;
  background: var(--ds-surface-primary);
  border-radius: var(--ds-radius-full);
  overflow: hidden;
}

.ds-progress-fill {
  height: 100%;
  background: var(--ds-primary);
  border-radius: var(--ds-radius-full);
  transition: width var(--ds-transition-normal);
  animation: ds-progress-shimmer 2s ease-in-out infinite;
}

@keyframes ds-progress-shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

.ds-progress-text {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  font-weight: var(--ds-font-medium);
  min-width: 35px;
  text-align: right;
}

/* === PROVIDER BADGE === */
.ds-activity-provider {
  display: flex;
  align-items: center;
  gap: var(--ds-space-1);
  padding: var(--ds-space-1) var(--ds-space-2);
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
  color: var(--ds-primary);
  border-radius: var(--ds-radius-full);
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-medium);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

/* === ELAPSED TIME === */
.ds-activity-time {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  font-family: var(--ds-font-mono);
  background: var(--ds-surface-primary);
  padding: var(--ds-space-1) var(--ds-space-2);
  border-radius: var(--ds-radius-sm);
  flex-shrink: 0;
}

/* === ACTIVITY DETAILS === */
.ds-activity-details {
  margin-top: var(--ds-space-4);
  border-top: 1px solid color-mix(in srgb, var(--ds-primary) 20%, transparent);
  padding-top: var(--ds-space-3);
}

.ds-details-toggle {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  background: none;
  border: none;
  color: var(--ds-text-muted);
  font-size: var(--ds-text-xs);
  cursor: pointer;
  padding: var(--ds-space-1) 0;
  transition: all var(--ds-transition-fast);
}

.ds-details-toggle:hover {
  color: var(--ds-text-primary);
}

.ds-details-toggle .rotated {
  transform: rotate(180deg);
}

.ds-details-content {
  margin-top: var(--ds-space-3);
  max-height: 200px;
  overflow-y: auto;
  animation: ds-slide-down 0.2s ease-out;
}

.ds-detail-item {
  display: flex;
  gap: var(--ds-space-3);
  padding: var(--ds-space-2) 0;
  border-bottom: 1px solid var(--ds-border-primary);
  font-size: var(--ds-text-xs);
}

.ds-detail-item:last-child {
  border-bottom: none;
}

.ds-detail-timestamp {
  color: var(--ds-text-muted);
  font-family: var(--ds-font-mono);
  flex-shrink: 0;
  width: 60px;
}

.ds-detail-message {
  color: var(--ds-text-secondary);
  flex: 1;
}

/* === SCROLLBAR STYLING === */
.ds-details-content::-webkit-scrollbar {
  width: 4px;
}

.ds-details-content::-webkit-scrollbar-track {
  background: transparent;
}

.ds-details-content::-webkit-scrollbar-thumb {
  background: var(--ds-border-secondary);
  border-radius: var(--ds-radius-full);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-activity-content {
    flex-wrap: wrap;
    gap: var(--ds-space-2);
  }
  
  .ds-activity-provider {
    order: -1;
    margin-left: auto;
  }
  
  .ds-activity-time {
    order: -1;
  }
  
  .ds-activity-progress {
    flex-direction: column;
    align-items: stretch;
    gap: var(--ds-space-1);
  }
  
  .ds-progress-text {
    text-align: center;
    min-width: auto;
  }
}

/* === ACCESSIBILITY === */
.ds-details-toggle:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
  border-radius: var(--ds-radius-sm);
}

/* === ANIMATIONS === */
@keyframes ds-fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes ds-slide-down {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 200px;
  }
}

/* === HIGH CONTRAST MODE === */
@media (prefers-contrast: high) {
  .ds-activity-stream {
    border-width: 2px;
  }
  
  .ds-progress-bar {
    border: 1px solid var(--ds-border-primary);
  }
}

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) {
  .ds-activity-spinning,
  .ds-activity-pulse,
  .ds-activity-bounce {
    animation: none;
  }
  
  .ds-progress-fill {
    animation: none;
  }
  
  .ds-activity-stream,
  .ds-details-content {
    animation: none;
  }
}

/* === DARK MODE ADJUSTMENTS === */
.dark .ds-activity-stream {
  background: color-mix(in srgb, var(--ds-primary) 8%, transparent);
  border-color: color-mix(in srgb, var(--ds-primary) 25%, transparent);
}

.dark .ds-progress-bar {
  background: var(--ds-surface-secondary);
}

.dark .ds-activity-time {
  background: var(--ds-surface-secondary);
}
</style>
