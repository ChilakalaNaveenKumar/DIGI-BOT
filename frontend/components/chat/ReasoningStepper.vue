<template>
  <div class="reasoning-stepper">
    <div class="reasoning-accordion">
      <div class="stepper-line"></div>
      <div class="accordion-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          class="accordion-step"
        >
          <div 
            class="step-header step-header--clickable"
            @click="toggleStep(index)"
          >
            <div class="step-indicator">
              <UiIcon 
                v-if="step.type === 'tool_call'"
                :name="getToolIcon(step.tool_name)" 
                :size="14" 
                class="step-icon"
              />
              <div 
                v-else
                class="thinking-dot"
                :class="{ 'thinking-dot--active': step.status === 'active' }"
              ></div>
            </div>
            
            <div class="step-content">
              <span class="step-text">{{ getStepPreview(step) }}</span>
              <UiIcon 
                :name="expandedSteps.has(index) ? 'chevron-up' : 'chevron-down'" 
                :size="12" 
                class="step-arrow"
                :class="{ 'step-arrow--rotated': expandedSteps.has(index) }"
              />
            </div>
          </div>
          
          <!-- Expanded content directly under the step -->
          <p v-if="expandedSteps.has(index) && step.result" class="step-expanded-content">
            {{ step.result }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ReasoningStep {
  type: 'thinking' | 'tool_call' | 'conclusion'
  content: string
  status?: 'active' | 'completed' | 'error'
  tool_name?: string
  result?: any
  preview?: string
}

interface Props {
  steps: ReasoningStep[]
  initialExpanded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialExpanded: false
})

const expandedSteps = ref(new Set<number>())

const getStepPreview = (step: ReasoningStep) => {
  return step.content.length > 60 
    ? step.content.substring(0, 60) + '...'
    : step.content
}

const toggleStep = (index: number) => {
  if (expandedSteps.value.has(index)) {
    // Close this step
    expandedSteps.value.delete(index)
  } else {
    // Close all other steps and open this one (accordion behavior)
    expandedSteps.value.clear()
    expandedSteps.value.add(index)
  }
}

const getToolIcon = (toolName?: string) => {
  const iconMap: Record<string, string> = {
    'codebase_search': 'book-open',
    'read_file': 'book-open', 
    'search_replace': 'edit-3',
    'write': 'plus',
    'run_terminal_cmd': 'hard-drive',
    'grep': 'code-2',
    'list_dir': 'hard-drive',
    'web_search': 'globe',
    'delete_file': 'alert-circle',
    'multi_edit': 'edit-3',
    'create_diagram': 'sparkles'
  }
  return iconMap[toolName || ''] || 'settings'
}

const getStatusVariant = (status?: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'error': return 'error'
    default: return 'warning'
  }
}

const formatResult = (result: any) => {
  if (typeof result === 'string') {
    return result.length > 200 ? result.substring(0, 200) + '...' : result
  }
  return JSON.stringify(result, null, 2)
}
</script>

<style scoped>
.reasoning-stepper {
  margin-bottom: 16px;
}

.reasoning-accordion {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.stepper-line {
  position: absolute;
  left: 25px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border-primary);
  border-radius: 1px;
  z-index: 1;
}

.accordion-steps {
  position: relative;
  z-index: 2;
}

.accordion-step {
  /* No border between steps */
}

.preview-steps {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.preview-step {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
  padding: 4px 0;
  border-radius: 4px;
  transition: background 0.2s ease;
  margin-left: 0;
}

.preview-step--clickable {
  cursor: pointer;
}

.preview-step--clickable:hover {
  background: var(--bg-hover);
}

.step-indicator {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
}

.step-icon {
  color: var(--text-secondary);
}

.thinking-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  transition: all 0.3s ease;
  border: 2px solid var(--bg-primary);
}

.thinking-dot--active {
  background: var(--primary);
  animation: pulse 2s infinite;
}

.thinking-dot--completed {
  background: var(--success);
}

.step-content {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.step-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.step-arrow {
  color: var(--text-primary);
  flex-shrink: 0;
  margin-left: 8px;
  opacity: 0.7;
}

.expand-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.step-count {
  font-size: 12px;
  color: var(--text-tertiary);
}

.expand-icon {
  color: var(--text-tertiary);
  transition: transform 0.2s ease;
}

/* Expanded State */
.reasoning-expanded {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  overflow: hidden;
  max-width: 700px;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: background 0.2s ease;
}



.collapse-icon {
  margin-left: auto;
  transition: transform 0.2s ease;
}

.reasoning-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
}

.stepper-container {
  position: relative;
}

.stepper-line--full {
  position: absolute;
  left: 24px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border-primary);
  border-radius: 1px;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reasoning-step {
  display: flex;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.reasoning-step .step-indicator {
  width: 24px;
  height: 24px;
}

.reasoning-step .step-icon {
  color: var(--text-primary);
}

.step-body {
  flex: 1;
  min-width: 0;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.step-header--clickable:hover {
  background: var(--bg-hover);
}

.step-expanded-content {
  padding: 12px 16px 12px 48px;
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-primary);
}

.step-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tool-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.step-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.step-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-step-icon {
  color: var(--text-tertiary);
  transition: transform 0.2s ease;
}

.step-result {
  margin-top: 8px;
  margin-left: 8px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-left: 3px solid var(--border-primary);
  border-radius: 0 6px 6px 0;
}

.result-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

/* Scrollbar Styling */
.reasoning-content::-webkit-scrollbar {
  width: 6px;
}

.reasoning-content::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.reasoning-content::-webkit-scrollbar-thumb {
  background: var(--border-primary);
  border-radius: 3px;
}

</style>
