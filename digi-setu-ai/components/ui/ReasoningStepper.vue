<template>
  <div class="reasoning-stepper">
    <div class="reasoning-accordion">
      <div class="stepper-line" />
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
                :class="{ 
                  'thinking-dot--active': step.status === 'active',
                  'thinking-dot--completed': step.status === 'completed'
                }"
              />
            </div>
            
            <div class="step-content">
              <span class="step-text">{{ getStepPreview(step) }}</span>
              <UiIcon 
                :name="expandedSteps.has(index) ? 'chevron-up' : 'chevron-down'" 
                :size="12" 
                class="step-arrow"
              />
            </div>
          </div>
          
          <!-- Expanded content directly under the step -->
          <div v-if="expandedSteps.has(index) && step.result" class="step-expanded-content">
            <UiStreamingMarkdown
              :key="`step-${index}-result`"
              :content="String(step.result || '')"
              :is-streaming="false"
              :show-cursor="false"
              mode="static"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Only show thinking indicator inside reasoning stepper -->
    <div v-if="isStreaming && showStreamingIndicator" class="thinking-indicator">
      <div class="thinking-dots">
        <span /><span /><span />
      </div>
      <span class="thinking-text">Thinking...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ReasoningStep } from '~/types'

interface Props {
  steps: ReasoningStep[]
  initialExpanded?: boolean
  isStreaming?: boolean
  showStreamingIndicator?: boolean
  showCursor?: boolean
}

const _props = withDefaults(defineProps<Props>(), {
  initialExpanded: false,
  isStreaming: false,
  showStreamingIndicator: true,
  showCursor: false
})

const expandedSteps = ref(new Set<number>())

const getStepPreview = (step: ReasoningStep) => {
  // Strip markdown formatting for preview
  const preview = step.content
    .replace(/^##?\s*/, '') // Remove ## or # headers
    .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold **text**
    .replace(/\*(.*?)\*/g, '$1') // Remove italic *text*
    .replace(/- /g, '') // Remove list markers
    .replace(/\n/g, ' ') // Replace newlines with spaces
    .trim()
  
  return preview.length > 60 
    ? preview.substring(0, 60) + '...'
    : preview
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
    'codebase_search': 'lucide:book-open',
    'read_file': 'lucide:file-text', 
    'search_replace': 'lucide:edit-3',
    'write': 'lucide:plus',
    'run_terminal_cmd': 'lucide:terminal',
    'grep': 'lucide:search',
    'list_dir': 'lucide:folder',
    'web_search': 'lucide:globe',
    'delete_file': 'lucide:trash-2',
    'multi_edit': 'lucide:edit-3',
    'create_diagram': 'lucide:sparkles',
    'chart_tools': 'lucide:bar-chart-3'
  }
  return iconMap[toolName || ''] || 'lucide:settings'
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
  top: 22px;
  bottom: 22px;
  width: 2px;
  background: var(--border-primary);
  border-radius: 1px;
  z-index: 1;
}

.accordion-steps {
  position: relative;
  z-index: 2;
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
  transition: transform 0.2s ease;
}

.step-arrow--rotated {
  transform: rotate(180deg);
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

/* Thinking indicator */
.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  color: var(--text-secondary);
  font-size: 14px;
  font-style: italic;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-primary);
}

.thinking-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.thinking-dots {
  display: flex;
  gap: 3px;
}

.thinking-dots span {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out;
}

.thinking-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dots span:nth-child(3) {
  animation-delay: 0.4s;
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

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 🎨 MARKDOWN STYLING FOR REASONING STEPPER */
.step-expanded-content :deep(h1),
.step-expanded-content :deep(h2),
.step-expanded-content :deep(h3),
.step-expanded-content :deep(h4),
.step-expanded-content :deep(h5),
.step-expanded-content :deep(h6) {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 8px 0 4px 0;
  padding: 0;
  border: none;
}

.step-expanded-content :deep(p) {
  margin: 6px 0;
  line-height: 1.5;
}

.step-expanded-content :deep(strong) {
  font-weight: 600;
  color: var(--text-primary);
}

.step-expanded-content :deep(em) {
  font-style: italic;
}

.step-expanded-content :deep(code) {
  background: var(--bg-primary);
  color: var(--accent-primary);
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  border: 1px solid var(--border-primary);
}

.step-expanded-content :deep(pre) {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  padding: 8px;
  margin: 8px 0;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 11px;
  line-height: 1.4;
}

.step-expanded-content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-primary);
}

.step-expanded-content :deep(ul), 
.step-expanded-content :deep(ol) {
  margin: 6px 0;
  padding-left: 16px;
}

.step-expanded-content :deep(li) {
  margin: 2px 0;
  line-height: 1.4;
}

.step-expanded-content :deep(ul li) {
  list-style: disc;
}

.step-expanded-content :deep(ol li) {
  list-style: decimal;
}

.step-expanded-content :deep(blockquote) {
  background: var(--bg-primary);
  border-left: 3px solid var(--accent-primary);
  padding: 6px 8px;
  margin: 8px 0;
  border-radius: 0 4px 4px 0;
}

.step-expanded-content :deep(blockquote p) {
  margin: 0;
  color: var(--text-secondary);
  font-style: italic;
}

.step-expanded-content :deep(a) {
  color: var(--accent-primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.2s ease;
}

.step-expanded-content :deep(a:hover) {
  border-bottom-color: var(--accent-primary);
}
</style>
