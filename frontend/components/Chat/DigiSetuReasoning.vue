<template>
  <div class="ds-reasoning-container">
    <div class="ds-reasoning-header" @click="toggleExpanded">
      <div class="ds-reasoning-icon">
        <Brain class="w-4 h-4" />
      </div>
      <div class="ds-reasoning-title">
        <span class="ds-reasoning-label">Thinking</span>
        <span v-if="isLoading" class="ds-reasoning-status">
          <div class="ds-thinking-dots">
            <div class="ds-thinking-dot"></div>
            <div class="ds-thinking-dot"></div>
            <div class="ds-thinking-dot"></div>
          </div>
        </span>
        <span v-else class="ds-reasoning-count">{{ reasoningParts.length }} step{{ reasoningParts.length !== 1 ? 's' : '' }}</span>
      </div>
      <button class="ds-reasoning-toggle" :class="{ 'expanded': isExpanded }">
        <ChevronDown class="w-4 h-4" />
      </button>
    </div>

    <!-- Reasoning Content -->
    <div v-if="isExpanded" class="ds-reasoning-content">
      <div class="ds-reasoning-steps">
        <div 
          v-for="(step, index) in reasoningParts" 
          :key="index"
          class="ds-reasoning-step"
          :class="{ 'ds-step-loading': isLoading && index === reasoningParts.length - 1 }"
        >
          <!-- Step Header -->
          <div class="ds-step-header">
            <div class="ds-step-number">{{ index + 1 }}</div>
            <div class="ds-step-title">
              {{ getStepTitle(step, index) }}
            </div>
            <div v-if="step.duration" class="ds-step-duration">
              {{ formatDuration(step.duration) }}
            </div>
          </div>

          <!-- Step Content -->
          <div class="ds-step-content">
            <div class="ds-step-text">
              {{ step.text || step.content }}
            </div>
            
            <!-- Step Metadata -->
            <div v-if="step.metadata" class="ds-step-metadata">
              <div v-if="step.metadata.confidence" class="ds-confidence">
                <span class="ds-confidence-label">Confidence:</span>
                <div class="ds-confidence-bar">
                  <div 
                    class="ds-confidence-fill" 
                    :style="{ width: `${step.metadata.confidence}%` }"
                  ></div>
                </div>
                <span class="ds-confidence-value">{{ step.metadata.confidence }}%</span>
              </div>
              
              <div v-if="step.metadata.reasoning_type" class="ds-reasoning-type">
                <span class="ds-type-badge" :class="`ds-type-${step.metadata.reasoning_type}`">
                  {{ formatReasoningType(step.metadata.reasoning_type) }}
                </span>
              </div>
            </div>

            <!-- Sub-steps -->
            <div v-if="step.substeps && step.substeps.length > 0" class="ds-substeps">
              <div 
                v-for="(substep, subIndex) in step.substeps" 
                :key="subIndex"
                class="ds-substep"
              >
                <div class="ds-substep-marker">{{ String.fromCharCode(97 + subIndex) }}.</div>
                <div class="ds-substep-content">{{ substep.text || substep.content }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading Step -->
        <div v-if="isLoading" class="ds-reasoning-step ds-step-loading">
          <div class="ds-step-header">
            <div class="ds-step-number">
              <Loader2 class="w-3 h-3 animate-spin" />
            </div>
            <div class="ds-step-title">Processing...</div>
          </div>
          <div class="ds-step-content">
            <div class="ds-loading-placeholder">
              <div class="ds-loading-line"></div>
              <div class="ds-loading-line ds-loading-line-short"></div>
              <div class="ds-loading-line ds-loading-line-medium"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reasoning Summary -->
      <div v-if="!isLoading && reasoningParts.length > 1" class="ds-reasoning-summary">
        <div class="ds-summary-header">
          <Target class="w-4 h-4" />
          <span>Summary</span>
        </div>
        <div class="ds-summary-content">
          {{ generateSummary() }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Brain, ChevronDown, Target, Loader2 } from 'lucide-vue-next'

const props = defineProps({
  reasoningParts: {
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

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const getStepTitle = (step, index) => {
  if (step.title) return step.title
  
  // Generate title based on step content or type
  const titles = [
    'Analyzing the question',
    'Gathering relevant information', 
    'Evaluating options',
    'Forming response strategy',
    'Validating approach',
    'Finalizing answer'
  ]
  
  if (step.metadata?.reasoning_type) {
    const typeMap = {
      'analysis': 'Analyzing information',
      'synthesis': 'Synthesizing data',
      'evaluation': 'Evaluating options',
      'planning': 'Planning approach',
      'validation': 'Validating results',
      'conclusion': 'Drawing conclusions'
    }
    return typeMap[step.metadata.reasoning_type] || `Step ${index + 1}`
  }
  
  return titles[index] || `Step ${index + 1}`
}

const formatDuration = (duration) => {
  if (duration < 1000) {
    return `${duration}ms`
  } else {
    return `${(duration / 1000).toFixed(1)}s`
  }
}

const formatReasoningType = (type) => {
  const typeMap = {
    'analysis': 'Analysis',
    'synthesis': 'Synthesis', 
    'evaluation': 'Evaluation',
    'planning': 'Planning',
    'validation': 'Validation',
    'conclusion': 'Conclusion',
    'creative': 'Creative',
    'logical': 'Logical',
    'intuitive': 'Intuitive'
  }
  return typeMap[type] || type.charAt(0).toUpperCase() + type.slice(1)
}

const generateSummary = () => {
  if (props.reasoningParts.length === 0) return ''
  
  // Extract key points from reasoning steps
  const keyPoints = props.reasoningParts
    .map(step => step.text || step.content)
    .filter(text => text && text.length > 0)
  
  if (keyPoints.length === 0) return 'Completed reasoning process'
  
  // Generate a concise summary
  const firstStep = keyPoints[0].substring(0, 100)
  const lastStep = keyPoints[keyPoints.length - 1].substring(0, 100)
  
  return `Analyzed the problem through ${keyPoints.length} steps, from "${firstStep}..." to "${lastStep}..."`
}

// Watch for new reasoning parts and auto-expand if needed
watch(() => props.reasoningParts.length, (newLength, oldLength) => {
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
.ds-reasoning-container {
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-xl);
  margin-bottom: var(--ds-space-4);
  overflow: hidden;
  transition: all var(--ds-transition-normal);
}

.ds-reasoning-container:hover {
  border-color: var(--ds-border-secondary);
}

/* === REASONING HEADER === */
.ds-reasoning-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-4);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
  user-select: none;
}

.ds-reasoning-header:hover {
  background: var(--ds-surface-hover);
}

.ds-reasoning-icon {
  color: var(--ds-primary);
  flex-shrink: 0;
}

.ds-reasoning-title {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
}

.ds-reasoning-label {
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-reasoning-status {
  display: flex;
  align-items: center;
}

.ds-thinking-dots {
  display: flex;
  gap: 2px;
}

.ds-thinking-dot {
  width: 4px;
  height: 4px;
  background: var(--ds-primary);
  border-radius: 50%;
  animation: ds-thinking-dots 1.4s ease-in-out infinite both;
}

.ds-thinking-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.ds-thinking-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes ds-thinking-dots {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.ds-reasoning-count {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  background: var(--ds-surface-primary);
  padding: 2px var(--ds-space-2);
  border-radius: var(--ds-radius-full);
}

.ds-reasoning-toggle {
  background: none;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  padding: var(--ds-space-1);
  border-radius: var(--ds-radius-sm);
  transition: all var(--ds-transition-fast);
}

.ds-reasoning-toggle:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

.ds-reasoning-toggle.expanded {
  transform: rotate(180deg);
}

/* === REASONING CONTENT === */
.ds-reasoning-content {
  border-top: 1px solid var(--ds-border-primary);
  animation: ds-slide-down 0.3s ease-out;
}

.ds-reasoning-steps {
  padding: var(--ds-space-4);
}

/* === REASONING STEP === */
.ds-reasoning-step {
  position: relative;
  padding-left: var(--ds-space-8);
  margin-bottom: var(--ds-space-6);
  animation: ds-fade-in 0.4s ease-out;
}

.ds-reasoning-step:last-child {
  margin-bottom: 0;
}

.ds-reasoning-step::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 32px;
  bottom: -24px;
  width: 2px;
  background: var(--ds-border-primary);
}

.ds-reasoning-step:last-child::before {
  display: none;
}

.ds-step-loading::before {
  background: var(--ds-primary);
  animation: ds-pulse 1.5s ease-in-out infinite;
}

/* === STEP HEADER === */
.ds-step-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  margin-bottom: var(--ds-space-2);
}

.ds-step-number {
  position: absolute;
  left: 0;
  width: 24px;
  height: 24px;
  background: var(--ds-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-semibold);
  z-index: 1;
}

.ds-step-loading .ds-step-number {
  background: var(--ds-surface-primary);
  border: 2px solid var(--ds-primary);
  color: var(--ds-primary);
}

.ds-step-title {
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-step-duration {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  background: var(--ds-surface-primary);
  padding: 2px var(--ds-space-2);
  border-radius: var(--ds-radius-sm);
  margin-left: auto;
}

/* === STEP CONTENT === */
.ds-step-content {
  margin-left: var(--ds-space-6);
}

.ds-step-text {
  color: var(--ds-text-secondary);
  line-height: var(--ds-leading-relaxed);
  margin-bottom: var(--ds-space-3);
}

/* === STEP METADATA === */
.ds-step-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ds-space-3);
  margin-bottom: var(--ds-space-3);
}

.ds-confidence {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  font-size: var(--ds-text-xs);
}

.ds-confidence-label {
  color: var(--ds-text-muted);
}

.ds-confidence-bar {
  width: 60px;
  height: 4px;
  background: var(--ds-surface-primary);
  border-radius: var(--ds-radius-full);
  overflow: hidden;
}

.ds-confidence-fill {
  height: 100%;
  background: var(--ds-secondary);
  transition: width var(--ds-transition-normal);
}

.ds-confidence-value {
  color: var(--ds-text-primary);
  font-weight: var(--ds-font-medium);
}

.ds-reasoning-type {
  display: flex;
  align-items: center;
}

.ds-type-badge {
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-medium);
  padding: 2px var(--ds-space-2);
  border-radius: var(--ds-radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.ds-type-analysis {
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
  color: var(--ds-primary);
}

.ds-type-synthesis {
  background: color-mix(in srgb, var(--ds-secondary) 10%, transparent);
  color: var(--ds-secondary);
}

.ds-type-evaluation {
  background: color-mix(in srgb, var(--ds-accent) 10%, transparent);
  color: var(--ds-accent);
}

.ds-type-planning {
  background: color-mix(in srgb, var(--ds-info) 10%, transparent);
  color: var(--ds-info);
}

/* === SUBSTEPS === */
.ds-substeps {
  margin-top: var(--ds-space-3);
  padding-left: var(--ds-space-4);
  border-left: 2px solid var(--ds-border-primary);
}

.ds-substep {
  display: flex;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-2);
  font-size: var(--ds-text-sm);
}

.ds-substep:last-child {
  margin-bottom: 0;
}

.ds-substep-marker {
  color: var(--ds-text-muted);
  font-weight: var(--ds-font-medium);
  flex-shrink: 0;
}

.ds-substep-content {
  color: var(--ds-text-secondary);
  line-height: var(--ds-leading-relaxed);
}

/* === LOADING PLACEHOLDER === */
.ds-loading-placeholder {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-2);
}

.ds-loading-line {
  height: 12px;
  background: var(--ds-surface-primary);
  border-radius: var(--ds-radius-sm);
  animation: ds-shimmer 1.5s ease-in-out infinite;
}

.ds-loading-line-short {
  width: 60%;
}

.ds-loading-line-medium {
  width: 80%;
}

@keyframes ds-shimmer {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

/* === REASONING SUMMARY === */
.ds-reasoning-summary {
  border-top: 1px solid var(--ds-border-primary);
  padding: var(--ds-space-4);
  background: var(--ds-surface-primary);
}

.ds-summary-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-3);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-summary-header svg {
  color: var(--ds-secondary);
}

.ds-summary-content {
  color: var(--ds-text-secondary);
  font-size: var(--ds-text-sm);
  line-height: var(--ds-leading-relaxed);
  font-style: italic;
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-reasoning-step {
    padding-left: var(--ds-space-6);
  }
  
  .ds-step-content {
    margin-left: var(--ds-space-4);
  }
  
  .ds-step-metadata {
    flex-direction: column;
    gap: var(--ds-space-2);
  }
}

/* === ACCESSIBILITY === */
.ds-reasoning-header:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === ANIMATIONS === */
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

@keyframes ds-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) {
  .ds-reasoning-content,
  .ds-reasoning-step {
    animation: none;
  }
  
  .ds-thinking-dot {
    animation: none;
  }
  
  .ds-step-loading::before {
    animation: none;
  }
  
  .ds-loading-line {
    animation: none;
  }
}
</style>
