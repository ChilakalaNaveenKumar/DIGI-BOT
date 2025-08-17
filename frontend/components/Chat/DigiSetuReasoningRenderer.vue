<template>
  <div class="ds-reasoning-renderer">
    <div class="ds-reasoning-header">
      <Icon name="mdi:brain" class="ds-reasoning-icon" />
      <h3 class="ds-reasoning-title">Chain-of-Thought Reasoning</h3>
      <div class="ds-reasoning-meta">
        <span class="ds-confidence">{{ Math.round(metadata.total_confidence * 100) }}% confidence</span>
        <span class="ds-time">{{ metadata.reasoning_time?.toFixed(2) }}s</span>
      </div>
    </div>

    <div class="ds-reasoning-content">
      <!-- Query -->
      <div class="ds-query-section">
        <h4 class="ds-section-title">Query</h4>
        <p class="ds-query-text">{{ metadata.query || 'Reasoning analysis' }}</p>
      </div>

      <!-- Reasoning Steps -->
      <div class="ds-steps-section">
        <h4 class="ds-section-title">Step-by-Step Analysis</h4>
        <div class="ds-reasoning-steps">
          <div 
            v-for="(step, index) in reasoningSteps" 
            :key="index"
            class="ds-reasoning-step"
          >
            <div class="ds-step-header">
              <div class="ds-step-number">{{ step.step_number }}</div>
              <div class="ds-step-info">
                <h5 class="ds-step-thought">{{ step.thought }}</h5>
                <div class="ds-step-confidence">
                  <Icon name="mdi:target" class="ds-confidence-icon" />
                  {{ Math.round(step.confidence * 100) }}%
                </div>
              </div>
            </div>
            
            <div class="ds-step-content">
              <div class="ds-reasoning-text">
                <strong>Reasoning:</strong> {{ step.reasoning }}
              </div>
              <div class="ds-conclusion-text">
                <strong>Conclusion:</strong> {{ step.conclusion }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Final Answer -->
      <div class="ds-final-section">
        <h4 class="ds-section-title">Final Answer</h4>
        <div class="ds-final-answer">
          <div class="ds-answer-content" v-html="formatContent(finalAnswer)"></div>
          <div class="ds-answer-meta">
            <div class="ds-overall-confidence">
              <Icon name="mdi:check-circle" class="ds-check-icon" />
              Overall Confidence: {{ Math.round(metadata.total_confidence * 100) }}%
            </div>
            <div class="ds-model-used">
              <Icon name="mdi:robot" class="ds-model-icon" />
              Model: {{ metadata.model_used || 'GPT-4' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  metadata: {
    type: Object,
    default: () => ({})
  }
})

// Parse reasoning steps from content or metadata
const reasoningSteps = computed(() => {
  // Try to get steps from metadata first
  if (props.metadata.steps && Array.isArray(props.metadata.steps)) {
    return props.metadata.steps
  }
  
  // If no steps in metadata, try to parse from content
  const steps = []
  const stepMatches = props.content.match(/\*\*Step \d+:\*\*(.*?)(?=\*\*Step \d+:|\*\*Final Answer:|$)/gs)
  
  if (stepMatches) {
    stepMatches.forEach((match, index) => {
      const stepContent = match.replace(/\*\*Step \d+:\*\*/, '').trim()
      const lines = stepContent.split('\n').filter(line => line.trim())
      
      steps.push({
        step_number: index + 1,
        thought: lines[0] || `Step ${index + 1}`,
        reasoning: lines.find(line => line.includes('Reasoning:'))?.replace('*Reasoning:*', '').trim() || stepContent,
        conclusion: lines.find(line => line.includes('Conclusion:'))?.replace('*Conclusion:*', '').trim() || '',
        confidence: 0.8 // Default confidence
      })
    })
  }
  
  // Fallback: create a single step from content
  if (steps.length === 0) {
    steps.push({
      step_number: 1,
      thought: 'Analysis',
      reasoning: props.content,
      conclusion: 'Analysis completed',
      confidence: 0.7
    })
  }
  
  return steps
})

// Extract final answer from content
const finalAnswer = computed(() => {
  const finalMatch = props.content.match(/\*\*Final Answer:\*\*(.*?)$/s)
  if (finalMatch) {
    return finalMatch[1].trim()
  }
  
  // If no explicit final answer, use the last part of content
  const lines = props.content.split('\n').filter(line => line.trim())
  return lines[lines.length - 1] || 'Analysis completed'
})

// Format content with basic markdown support
const formatContent = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
@reference "tailwindcss";
.ds-reasoning-renderer {
  @apply bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 space-y-6;
}

.ds-reasoning-header {
  @apply flex items-center justify-between flex-wrap gap-4;
}

.ds-reasoning-icon {
  @apply w-6 h-6 text-purple-600;
}

.ds-reasoning-title {
  @apply flex-1 text-lg font-semibold text-purple-900;
}

.ds-reasoning-meta {
  @apply flex items-center gap-4 text-sm text-purple-700;
}

.ds-confidence {
  @apply px-2 py-1 bg-purple-100 rounded font-medium;
}

.ds-time {
  @apply px-2 py-1 bg-blue-100 rounded font-medium text-blue-700;
}

.ds-reasoning-content {
  @apply space-y-6;
}

.ds-section-title {
  @apply font-semibold text-gray-900 mb-3 flex items-center gap-2;
}

.ds-query-section {
  @apply space-y-2;
}

.ds-query-text {
  @apply p-3 bg-white rounded border border-purple-200 text-gray-700;
}

.ds-steps-section {
  @apply space-y-4;
}

.ds-reasoning-steps {
  @apply space-y-4;
}

.ds-reasoning-step {
  @apply bg-white rounded-lg border border-purple-200 p-4 space-y-3;
}

.ds-step-header {
  @apply flex items-start gap-3;
}

.ds-step-number {
  @apply w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold text-sm;
}

.ds-step-info {
  @apply flex-1 space-y-1;
}

.ds-step-thought {
  @apply font-medium text-gray-900;
}

.ds-step-confidence {
  @apply flex items-center gap-1 text-sm text-purple-600;
}

.ds-confidence-icon {
  @apply w-4 h-4;
}

.ds-step-content {
  @apply ml-11 space-y-2 text-sm text-gray-700;
}

.ds-reasoning-text, .ds-conclusion-text {
  @apply p-2 bg-gray-50 rounded;
}

.ds-final-section {
  @apply space-y-3;
}

.ds-final-answer {
  @apply bg-white rounded-lg border-2 border-green-200 p-4 space-y-3;
}

.ds-answer-content {
  @apply text-gray-800 leading-relaxed;
}

.ds-answer-meta {
  @apply flex items-center justify-between flex-wrap gap-4 pt-3 border-t border-green-200;
}

.ds-overall-confidence {
  @apply flex items-center gap-2 text-green-700 font-medium;
}

.ds-check-icon {
  @apply w-5 h-5;
}

.ds-model-used {
  @apply flex items-center gap-2 text-gray-600 text-sm;
}

.ds-model-icon {
  @apply w-4 h-4;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .ds-reasoning-renderer {
    @apply from-purple-900/20 to-blue-900/20 border-purple-700;
  }
  
  .ds-reasoning-title {
    @apply text-purple-100;
  }
  
  .ds-query-text, .ds-reasoning-step, .ds-final-answer {
    @apply bg-gray-800 border-gray-700;
  }
  
  .ds-step-thought {
    @apply text-gray-100;
  }
  
  .ds-reasoning-text, .ds-conclusion-text {
    @apply bg-gray-700 text-gray-200;
  }
  
  .ds-answer-content {
    @apply text-gray-200;
  }
}
</style>

