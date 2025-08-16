<template>
  <div v-if="thoughtSteps.length > 0" class="ds-thought-process">
    <button 
      class="ds-thought-toggle"
      @click="isExpanded = !isExpanded"
      :aria-expanded="isExpanded"
    >
      <div class="ds-thought-header">
        <Brain class="w-4 h-4" />
        <span class="ds-thought-title">Thought process</span>
        <span v-if="!isExpanded && thoughtSteps.length > 0" class="ds-thought-count">
          {{ thoughtSteps.length }} steps
        </span>
      </div>
      <ChevronDown 
        class="w-4 h-4 ds-chevron" 
        :class="{ 'ds-chevron-expanded': isExpanded }"
      />
    </button>
    
    <Transition name="ds-thought-content">
      <div v-if="isExpanded" class="ds-thought-content">
        <div class="ds-thought-content-simple">
          <DigiSetuMarkdown 
            :content="getAllThoughtContent()"
            class="ds-thought-text"
          />
        </div>
        
        <!-- Simple loading indicator -->
        <div v-if="isThinking" class="ds-thinking-indicator">
          <div class="ds-thinking-text">Thinking...</div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Brain, ChevronDown } from 'lucide-vue-next'
import { useSimpleContentRouter } from '~/composables/useSimpleContentRouter'

// Import markdown renderer - AI already formats content properly
import DigiSetuMarkdown from './DigiSetuMarkdown.vue'

const { routeContent, cleanContent } = useSimpleContentRouter()

const props = defineProps({
  thoughtSteps: {
    type: Array,
    default: () => []
  },
  isThinking: {
    type: Boolean,
    default: false
  },
  autoExpand: {
    type: Boolean,
    default: false
  }
})

const isExpanded = ref(false) // Always start collapsed

// Auto-expand when new thoughts arrive (disabled by default)
watch(() => props.thoughtSteps.length, (newLength, oldLength) => {
  if (newLength > oldLength && props.autoExpand) {
    isExpanded.value = true
  }
})

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

// Combine all thought steps into one continuous markdown content
const getAllThoughtContent = () => {
  if (!props.thoughtSteps || props.thoughtSteps.length === 0) return ''
  
  return props.thoughtSteps
    .map(step => cleanContent(step.content || ''))
    .filter(content => content.trim())
    .join('\n\n')
}
</script>

<style scoped>
.ds-thought-process {
  margin: var(--ds-space-3) 0;
  border: 1px solid var(--ds-border-secondary);
  border-radius: var(--ds-radius-lg);
  background: var(--ds-surface-secondary);
  overflow: hidden;
}

.ds-thought-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-3) var(--ds-space-4);
  background: none;
  border: none;
  cursor: pointer;
  transition: all var(--ds-transition-fast);
  color: var(--ds-text-primary);
}

.ds-thought-toggle:hover {
  background: var(--ds-surface-hover);
}

.ds-thought-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
}

.ds-thought-title {
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
}

.ds-thought-count {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  background: var(--ds-surface-tertiary);
  padding: 2px var(--ds-space-2);
  border-radius: var(--ds-radius-full);
}

.ds-chevron {
  transition: transform var(--ds-transition-fast);
  color: var(--ds-text-muted);
}

.ds-chevron-expanded {
  transform: rotate(180deg);
}

.ds-thought-content {
  padding: 0 var(--ds-space-4) var(--ds-space-4);
  border-top: 1px solid var(--ds-border-tertiary);
  background: var(--ds-surface-primary);
}

.ds-thought-content-simple {
  padding: var(--ds-space-2) 0;
}

.ds-thought-text {
  color: var(--ds-color-text-secondary);
  line-height: 1.6;
  font-size: 0.9rem;
}

.ds-thinking-indicator {
  padding: var(--ds-space-2) 0;
  opacity: 0.7;
}

.ds-thinking-text {
  color: var(--ds-color-text-secondary);
  font-style: italic;
  font-size: 0.9rem;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.ds-step-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--ds-border-secondary);
  border-top: 2px solid var(--ds-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.ds-step-content {
  flex: 1;
  min-width: 0;
}

.ds-step-text {
  font-size: var(--ds-text-sm);
  line-height: var(--ds-leading-relaxed);
  color: var(--ds-text-primary);
}

/* Transition animations */
.ds-thought-content-enter-active,
.ds-thought-content-leave-active {
  transition: all var(--ds-transition-normal);
  overflow: hidden;
}

.ds-thought-content-enter-from,
.ds-thought-content-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.ds-thought-content-enter-to,
.ds-thought-content-leave-from {
  max-height: 500px;
  opacity: 1;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .ds-thought-toggle {
    padding: var(--ds-space-3);
  }
  
  .ds-thought-content {
    padding: 0 var(--ds-space-3) var(--ds-space-3);
  }
  
  .ds-thought-step {
    gap: var(--ds-space-2);
  }
}

/* Accessibility */
.ds-thought-toggle:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .ds-chevron,
  .ds-thought-content-enter-active,
  .ds-thought-content-leave-active {
    transition: none;
  }
  
  .ds-step-spinner {
    animation: none;
  }
}
</style>
