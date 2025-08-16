<template>
  <div class="ds-tool-stepper">
    <div class="ds-stepper-header" @click="toggleExpanded">
      <div class="ds-stepper-icon">
        <Settings class="w-4 h-4" />
      </div>
      <div class="ds-stepper-title">
        <span class="ds-stepper-label">Tool Execution</span>
        <span class="ds-stepper-count">{{ completedSteps }}/{{ totalSteps }} steps</span>
      </div>
      <div class="ds-stepper-status" :class="stepperStatusClass">
        <component :is="statusIcon" class="w-4 h-4" />
        <span>{{ stepperStatusText }}</span>
      </div>
      <button class="ds-stepper-toggle" :class="{ 'expanded': isExpanded }">
        <ChevronDown class="w-4 h-4" />
      </button>
    </div>

    <!-- Tool Steps -->
    <div v-if="isExpanded" class="ds-stepper-content">
      <div class="ds-steps-container">
        <div 
          v-for="(step, index) in toolSteps" 
          :key="step.id || index"
          class="ds-step"
          :class="getStepClasses(step)"
        >
          <!-- Step Timeline -->
          <div class="ds-step-timeline">
            <div class="ds-step-marker" :class="getStepMarkerClass(step)">
              <component :is="getStepIcon(step)" class="w-3 h-3" />
            </div>
            <div v-if="index < toolSteps.length - 1" class="ds-step-connector"></div>
          </div>

          <!-- Step Content -->
          <div class="ds-step-content">
            <!-- Step Header -->
            <div class="ds-step-header">
              <div class="ds-step-info">
                <h4 class="ds-step-title">{{ step.title || getStepTitle(step) }}</h4>
                <p class="ds-step-description">{{ step.description || getStepDescription(step) }}</p>
              </div>
              <div class="ds-step-meta">
                <span v-if="step.duration" class="ds-step-duration">
                  {{ formatDuration(step.duration) }}
                </span>
                <span v-if="step.provider" class="ds-step-provider">
                  {{ step.provider }}
                </span>
              </div>
            </div>

            <!-- Step Details (Expandable) -->
            <div v-if="step.status !== 'pending'" class="ds-step-details">
              <button 
                v-if="hasStepDetails(step)"
                class="ds-details-toggle"
                @click="toggleStepDetails(step.id)"
                :class="{ 'expanded': expandedSteps.has(step.id) }"
              >
                <ChevronRight class="w-3 h-3" />
                <span>{{ expandedSteps.has(step.id) ? 'Hide' : 'Show' }} details</span>
              </button>

              <!-- Tool Input -->
              <div v-if="expandedSteps.has(step.id) && step.input" class="ds-step-input">
                <h5 class="ds-detail-title">Input</h5>
                <div class="ds-detail-content">
                  <DigiSetuCodeBlock 
                    v-if="isJsonContent(step.input)"
                    :code="formatJson(step.input)"
                    language="json"
                    :show-header="false"
                    :show-line-numbers="false"
                  />
                  <pre v-else class="ds-detail-text">{{ step.input }}</pre>
                </div>
              </div>

              <!-- Tool Output -->
              <div v-if="expandedSteps.has(step.id) && step.output" class="ds-step-output">
                <h5 class="ds-detail-title">Output</h5>
                <div class="ds-detail-content">
                  <DigiSetuContentRenderer 
                    :content="step.output"
                    :content-type="step.output_type || 'text'"
                    :provider="step.provider"
                  />
                </div>
              </div>

              <!-- Tool Error -->
              <div v-if="expandedSteps.has(step.id) && step.error" class="ds-step-error">
                <h5 class="ds-detail-title">Error</h5>
                <div class="ds-detail-content ds-error-content">
                  <AlertCircle class="w-4 h-4" />
                  <span>{{ step.error }}</span>
                </div>
              </div>

              <!-- Step Progress -->
              <div v-if="step.status === 'executing' && step.progress" class="ds-step-progress">
                <div class="ds-progress-bar">
                  <div 
                    class="ds-progress-fill" 
                    :style="{ width: `${step.progress}%` }"
                  ></div>
                </div>
                <span class="ds-progress-text">{{ step.progress }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tool Summary -->
      <div v-if="isCompleted" class="ds-stepper-summary">
        <div class="ds-summary-header">
          <CheckCircle class="w-4 h-4" />
          <span>Execution Summary</span>
        </div>
        <div class="ds-summary-stats">
          <div class="ds-stat">
            <span class="ds-stat-label">Total Steps</span>
            <span class="ds-stat-value">{{ totalSteps }}</span>
          </div>
          <div class="ds-stat">
            <span class="ds-stat-label">Success Rate</span>
            <span class="ds-stat-value">{{ successRate }}%</span>
          </div>
          <div class="ds-stat">
            <span class="ds-stat-label">Total Time</span>
            <span class="ds-stat-value">{{ totalDuration }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { 
  Settings, ChevronDown, ChevronRight, Clock, CheckCircle, 
  XCircle, AlertCircle, Loader2, Play, Search, Image, 
  FileText, Database, Globe
} from 'lucide-vue-next'

const props = defineProps({
  toolParts: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  autoExpand: {
    type: Boolean,
    default: true
  }
})

// Reactive state
const isExpanded = ref(props.autoExpand)
const expandedSteps = ref(new Set())

// Process tool parts into steps
const toolSteps = computed(() => {
  return props.toolParts.map((part, index) => {
    const step = {
      id: part.id || `step-${index}`,
      type: part.type,
      tool_name: part.tool_name,
      status: getStepStatus(part),
      input: part.tool_input,
      output: part.tool_output || part.content,
      output_type: part.content_type,
      error: part.tool_error || part.error,
      provider: part.provider,
      duration: part.duration,
      progress: part.progress,
      timestamp: part.timestamp || new Date().toISOString()
    }
    
    return step
  })
})

// Computed properties
const totalSteps = computed(() => toolSteps.value.length)

const completedSteps = computed(() => {
  return toolSteps.value.filter(step => 
    step.status === 'completed' || step.status === 'error'
  ).length
})

const successfulSteps = computed(() => {
  return toolSteps.value.filter(step => step.status === 'completed').length
})

const isCompleted = computed(() => {
  return totalSteps.value > 0 && completedSteps.value === totalSteps.value && !props.isLoading
})

const hasErrors = computed(() => {
  return toolSteps.value.some(step => step.status === 'error')
})

const stepperStatusClass = computed(() => {
  if (props.isLoading) return 'ds-status-executing'
  if (hasErrors.value) return 'ds-status-error'
  if (isCompleted.value) return 'ds-status-completed'
  return 'ds-status-pending'
})

const stepperStatusText = computed(() => {
  if (props.isLoading) return 'Executing...'
  if (hasErrors.value) return 'Completed with errors'
  if (isCompleted.value) return 'Completed successfully'
  return 'Ready'
})

const statusIcon = computed(() => {
  if (props.isLoading) return Loader2
  if (hasErrors.value) return AlertCircle
  if (isCompleted.value) return CheckCircle
  return Clock
})

const successRate = computed(() => {
  if (totalSteps.value === 0) return 0
  return Math.round((successfulSteps.value / totalSteps.value) * 100)
})

const totalDuration = computed(() => {
  const total = toolSteps.value.reduce((sum, step) => {
    return sum + (step.duration || 0)
  }, 0)
  return formatDuration(total)
})

// Methods
const getStepStatus = (part) => {
  if (part.type === 'tool_loading') return 'executing'
  if (part.type === 'tool_executing') return 'executing'
  if (part.type === 'tool_error') return 'error'
  if (part.type === 'tool_result') return 'completed'
  if (part.tool_error || part.error) return 'error'
  if (part.tool_output || part.content) return 'completed'
  return 'pending'
}

const getStepClasses = (step) => {
  return {
    'ds-step-pending': step.status === 'pending',
    'ds-step-executing': step.status === 'executing',
    'ds-step-completed': step.status === 'completed',
    'ds-step-error': step.status === 'error'
  }
}

const getStepMarkerClass = (step) => {
  return `ds-marker-${step.status}`
}

const getStepIcon = (step) => {
  if (step.status === 'executing') return Loader2
  if (step.status === 'completed') return CheckCircle
  if (step.status === 'error') return XCircle
  
  // Tool-specific icons
  const toolIcons = {
    'web_search': Search,
    'image_generation': Image,
    'file_processing': FileText,
    'database_query': Database,
    'api_call': Globe
  }
  
  return toolIcons[step.tool_name] || Play
}

const getStepTitle = (step) => {
  const titles = {
    'web_search': 'Web Search',
    'image_generation': 'Image Generation',
    'file_processing': 'File Processing',
    'database_query': 'Database Query',
    'api_call': 'API Call'
  }
  
  return titles[step.tool_name] || `Execute ${step.tool_name || 'Tool'}`
}

const getStepDescription = (step) => {
  const descriptions = {
    'web_search': 'Searching the web for relevant information',
    'image_generation': 'Generating image based on description',
    'file_processing': 'Processing uploaded file content',
    'database_query': 'Querying database for information',
    'api_call': 'Making external API request'
  }
  
  return descriptions[step.tool_name] || 'Executing tool operation'
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const toggleStepDetails = (stepId) => {
  if (expandedSteps.value.has(stepId)) {
    expandedSteps.value.delete(stepId)
  } else {
    expandedSteps.value.add(stepId)
  }
}

const hasStepDetails = (step) => {
  return step.input || step.output || step.error
}

const isJsonContent = (content) => {
  if (typeof content === 'object') return true
  if (typeof content === 'string') {
    try {
      JSON.parse(content)
      return true
    } catch {
      return false
    }
  }
  return false
}

const formatJson = (content) => {
  if (typeof content === 'object') {
    return JSON.stringify(content, null, 2)
  }
  try {
    return JSON.stringify(JSON.parse(content), null, 2)
  } catch {
    return content
  }
}

const formatDuration = (duration) => {
  if (!duration) return '0ms'
  
  if (duration < 1000) {
    return `${Math.round(duration)}ms`
  } else {
    return `${(duration / 1000).toFixed(1)}s`
  }
}

// Watch for new tool parts and auto-expand
watch(() => props.toolParts.length, (newLength, oldLength) => {
  if (newLength > oldLength && props.autoExpand) {
    isExpanded.value = true
  }
})

// Auto-expand when loading starts
watch(() => props.isLoading, (newLoading) => {
  if (newLoading && props.autoExpand) {
    isExpanded.value = true
  }
})
</script>

<style scoped>
.ds-tool-stepper {
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-xl);
  margin-bottom: var(--ds-space-4);
  overflow: hidden;
  transition: all var(--ds-transition-normal);
}

.ds-tool-stepper:hover {
  border-color: var(--ds-border-secondary);
}

/* === STEPPER HEADER === */
.ds-stepper-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-4);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
  user-select: none;
}

.ds-stepper-header:hover {
  background: var(--ds-surface-hover);
}

.ds-stepper-icon {
  color: var(--ds-primary);
  flex-shrink: 0;
}

.ds-stepper-title {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ds-stepper-label {
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-stepper-count {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-stepper-status {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  border-radius: var(--ds-radius-full);
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-medium);
}

.ds-status-pending {
  background: color-mix(in srgb, var(--ds-text-muted) 10%, transparent);
  color: var(--ds-text-muted);
}

.ds-status-executing {
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
  color: var(--ds-primary);
}

.ds-status-executing svg {
  animation: spin 1s linear infinite;
}

.ds-status-completed {
  background: color-mix(in srgb, var(--ds-secondary) 10%, transparent);
  color: var(--ds-secondary);
}

.ds-status-error {
  background: color-mix(in srgb, var(--ds-danger) 10%, transparent);
  color: var(--ds-danger);
}

.ds-stepper-toggle {
  background: none;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  padding: var(--ds-space-1);
  border-radius: var(--ds-radius-sm);
  transition: all var(--ds-transition-fast);
}

.ds-stepper-toggle:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

.ds-stepper-toggle.expanded {
  transform: rotate(180deg);
}

/* === STEPPER CONTENT === */
.ds-stepper-content {
  border-top: 1px solid var(--ds-border-primary);
  animation: ds-slide-down 0.3s ease-out;
}

.ds-steps-container {
  padding: var(--ds-space-4);
}

/* === STEP === */
.ds-step {
  display: flex;
  gap: var(--ds-space-4);
  position: relative;
  animation: ds-fade-in 0.4s ease-out;
}

.ds-step:not(:last-child) {
  margin-bottom: var(--ds-space-6);
}

/* === STEP TIMELINE === */
.ds-step-timeline {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.ds-step-marker {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  background: var(--ds-surface-primary);
  z-index: 1;
}

.ds-marker-pending {
  border-color: var(--ds-border-secondary);
  color: var(--ds-text-muted);
}

.ds-marker-executing {
  border-color: var(--ds-primary);
  color: var(--ds-primary);
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
}

.ds-marker-executing svg {
  animation: spin 1s linear infinite;
}

.ds-marker-completed {
  border-color: var(--ds-secondary);
  color: var(--ds-secondary);
  background: color-mix(in srgb, var(--ds-secondary) 10%, transparent);
}

.ds-marker-error {
  border-color: var(--ds-danger);
  color: var(--ds-danger);
  background: color-mix(in srgb, var(--ds-danger) 10%, transparent);
}

.ds-step-connector {
  width: 2px;
  height: 40px;
  background: var(--ds-border-primary);
  margin-top: var(--ds-space-2);
}

/* === STEP CONTENT === */
.ds-step-content {
  flex: 1;
  min-width: 0;
}

.ds-step-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--ds-space-3);
}

.ds-step-info {
  flex: 1;
  min-width: 0;
}

.ds-step-title {
  font-size: var(--ds-text-base);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  margin: 0 0 var(--ds-space-1) 0;
}

.ds-step-description {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  margin: 0;
  line-height: var(--ds-leading-relaxed);
}

.ds-step-meta {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-1);
  align-items: flex-end;
}

.ds-step-duration,
.ds-step-provider {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  background: var(--ds-surface-primary);
  padding: 2px var(--ds-space-2);
  border-radius: var(--ds-radius-sm);
}

/* === STEP DETAILS === */
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
  margin-bottom: var(--ds-space-3);
}

.ds-details-toggle:hover {
  color: var(--ds-text-primary);
}

.ds-details-toggle.expanded svg {
  transform: rotate(90deg);
}

.ds-step-input,
.ds-step-output,
.ds-step-error {
  margin-bottom: var(--ds-space-4);
}

.ds-detail-title {
  font-size: var(--ds-text-sm);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  margin: 0 0 var(--ds-space-2) 0;
}

.ds-detail-content {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  padding: var(--ds-space-3);
  overflow-x: auto;
}

.ds-detail-text {
  margin: 0;
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.ds-error-content {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-danger);
  background: color-mix(in srgb, var(--ds-danger) 5%, transparent);
  border-color: color-mix(in srgb, var(--ds-danger) 20%, transparent);
}

/* === STEP PROGRESS === */
.ds-step-progress {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  margin-top: var(--ds-space-3);
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
}

.ds-progress-text {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  font-weight: var(--ds-font-medium);
  min-width: 35px;
  text-align: right;
}

/* === STEPPER SUMMARY === */
.ds-stepper-summary {
  border-top: 1px solid var(--ds-border-primary);
  padding: var(--ds-space-4);
  background: var(--ds-surface-primary);
}

.ds-summary-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-4);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-summary-header svg {
  color: var(--ds-secondary);
}

.ds-summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: var(--ds-space-4);
}

.ds-stat {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-1);
}

.ds-stat-label {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.ds-stat-value {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
}

/* === ANIMATIONS === */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes ds-slide-down {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes ds-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-step-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--ds-space-2);
  }
  
  .ds-step-meta {
    align-items: flex-start;
    flex-direction: row;
    gap: var(--ds-space-3);
  }
  
  .ds-summary-stats {
    grid-template-columns: 1fr;
    gap: var(--ds-space-3);
  }
}

/* === ACCESSIBILITY === */
.ds-stepper-header:focus-visible,
.ds-details-toggle:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) {
  .ds-stepper-content,
  .ds-step {
    animation: none;
  }
  
  .ds-marker-executing svg,
  .ds-status-executing svg {
    animation: none;
  }
}
</style>
