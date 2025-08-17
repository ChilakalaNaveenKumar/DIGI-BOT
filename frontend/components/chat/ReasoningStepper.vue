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
                :class="{ 'thinking-dot--active': step.status === 'active' }"
              />
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
  </div>
</template>

<script setup lang="ts">
// Removed markdown-it imports - now using StreamingMarkdown component

interface ReasoningStep {
  type: 'thinking' | 'tool_call' | 'conclusion'
  content: string
  status?: 'active' | 'completed' | 'error'
  tool_name?: string
  result?: unknown
  preview?: string
}

interface Props {
  steps: ReasoningStep[]
  initialExpanded?: boolean
}

const _props = withDefaults(defineProps<Props>(), {
  initialExpanded: false
})

const expandedSteps = ref(new Set<number>())

// Markdown rendering now handled by StreamingMarkdown component

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

const _getStatusVariant = (status?: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'error': return 'error'
    default: return 'warning'
  }
}

const _formatResult = (result: unknown) => {
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

/* .accordion-step - No border between steps */

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

.reasoning-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}

/* 🎨 MARKDOWN STYLING FOR REASONING STEPPER */
.step-expanded-content.markdown-content {
  margin-top: 8px;
  margin-left: 8px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-left: 3px solid var(--border-primary);
  border-radius: 0 6px 6px 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-secondary);
  overflow-wrap: break-word;
}

/* Headers in reasoning */
.step-expanded-content.markdown-content :deep(h1),
.step-expanded-content.markdown-content :deep(h2),
.step-expanded-content.markdown-content :deep(h3),
.step-expanded-content.markdown-content :deep(h4),
.step-expanded-content.markdown-content :deep(h5),
.step-expanded-content.markdown-content :deep(h6) {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 8px 0 4px 0;
  padding: 0;
  border: none;
}

/* Paragraphs */
.step-expanded-content.markdown-content :deep(p) {
  margin: 6px 0;
  line-height: 1.5;
}

/* Text formatting */
.step-expanded-content.markdown-content :deep(strong) {
  font-weight: 600;
  color: var(--text-primary);
}

.step-expanded-content.markdown-content :deep(em) {
  font-style: italic;
}

.step-expanded-content.markdown-content :deep(del) {
  text-decoration: line-through;
  opacity: 0.7;
}

/* Inline code */
.step-expanded-content.markdown-content :deep(code) {
  background: var(--bg-primary);
  color: var(--accent-primary);
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  border: 1px solid var(--border-primary);
}

/* Code blocks */
.step-expanded-content.markdown-content :deep(pre) {
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

.step-expanded-content.markdown-content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-primary);
}

/* Lists */
.step-expanded-content.markdown-content :deep(ul), 
.step-expanded-content.markdown-content :deep(ol) {
  margin: 6px 0;
  padding-left: 16px;
}

.step-expanded-content.markdown-content :deep(li) {
  margin: 2px 0;
  line-height: 1.4;
}

.step-expanded-content.markdown-content :deep(ul li) {
  list-style: disc;
}

.step-expanded-content.markdown-content :deep(ol li) {
  list-style: decimal;
}

/* Blockquotes */
.step-expanded-content.markdown-content :deep(blockquote) {
  background: var(--bg-primary);
  border-left: 3px solid var(--accent-primary);
  padding: 6px 8px;
  margin: 8px 0;
  border-radius: 0 4px 4px 0;
}

.step-expanded-content.markdown-content :deep(blockquote p) {
  margin: 0;
  color: var(--text-secondary);
  font-style: italic;
}

/* Tables */
.step-expanded-content.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  background: var(--bg-primary);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border-primary);
  font-size: 12px;
}

.step-expanded-content.markdown-content :deep(th), 
.step-expanded-content.markdown-content :deep(td) {
  padding: 6px 8px;
  text-align: left;
  border-bottom: 1px solid var(--border-primary);
}

.step-expanded-content.markdown-content :deep(th) {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.step-expanded-content.markdown-content :deep(tr:last-child td) {
  border-bottom: none;
}

.step-expanded-content.markdown-content :deep(tr:nth-child(even)) {
  background: var(--bg-secondary);
}

/* Links */
.step-expanded-content.markdown-content :deep(a) {
  color: var(--accent-primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.2s ease;
}

.step-expanded-content.markdown-content :deep(a:hover) {
  border-bottom-color: var(--accent-primary);
}

/* Horizontal rules */
.step-expanded-content.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-primary);
  margin: 12px 0;
}

/* Syntax highlighting - Theme adaptive using data-theme */
.step-expanded-content.markdown-content :deep(.hljs) {
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  border-radius: 6px;
}

/* Light theme syntax colors for reasoning stepper */
:root .step-expanded-content.markdown-content :deep(.hljs-keyword) { 
  color: #d73a49; 
  font-weight: 600;
}

:root .step-expanded-content.markdown-content :deep(.hljs-string) { 
  color: #22863a; 
}

:root .step-expanded-content.markdown-content :deep(.hljs-comment) { 
  color: #6a737d; 
  font-style: italic;
}

:root .step-expanded-content.markdown-content :deep(.hljs-function) { 
  color: #6f42c1; 
  font-weight: 600;
}

:root .step-expanded-content.markdown-content :deep(.hljs-number) { 
  color: #005cc5; 
}

:root .step-expanded-content.markdown-content :deep(.hljs-variable) { 
  color: #e36209; 
}

:root .step-expanded-content.markdown-content :deep(.hljs-title) { 
  color: #6f42c1; 
  font-weight: 600;
}

:root .step-expanded-content.markdown-content :deep(.hljs-attr) { 
  color: #005cc5; 
}

:root .step-expanded-content.markdown-content :deep(.hljs-built_in) { 
  color: #d73a49; 
}

:root .step-expanded-content.markdown-content :deep(.hljs-literal) { 
  color: #005cc5; 
}

:root .step-expanded-content.markdown-content :deep(.hljs-meta) { 
  color: #6a737d; 
}

:root .step-expanded-content.markdown-content :deep(.hljs-tag) { 
  color: #22863a; 
}

/* Dark theme syntax colors for reasoning stepper */
[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-keyword) { 
  color: #ff6b6b; 
  font-weight: 600;
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-string) { 
  color: #51cf66; 
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-comment) { 
  color: #868e96; 
  font-style: italic;
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-function) { 
  color: #74c0fc; 
  font-weight: 600;
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-number) { 
  color: #ffd43b; 
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-variable) { 
  color: #ff8cc8; 
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-title) { 
  color: #74c0fc; 
  font-weight: 600;
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-attr) { 
  color: #ffd43b; 
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-built_in) { 
  color: #ff6b6b; 
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-literal) { 
  color: #ffd43b; 
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-meta) { 
  color: #868e96; 
}

[data-theme="dark"] .step-expanded-content.markdown-content :deep(.hljs-tag) { 
  color: #51cf66; 
}

/* Task Lists - Enhanced with proper styling */
.step-expanded-content.markdown-content :deep(.task-list-item) {
  list-style: none;
  margin: 2px 0;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding-left: 0;
}

.step-expanded-content.markdown-content :deep(.task-list-item-checkbox) {
  margin: 0;
  margin-top: 1px;
  width: 14px;
  height: 14px;
  accent-color: var(--accent-primary);
  cursor: pointer;
  flex-shrink: 0;
}

.step-expanded-content.markdown-content :deep(.task-list-item-checkbox:checked + .task-list-item-label) {
  text-decoration: line-through;
  opacity: 0.7;
  color: var(--text-secondary);
}

.step-expanded-content.markdown-content :deep(.task-list-item-label) {
  flex: 1;
  line-height: 1.4;
  cursor: pointer;
  font-size: 12px;
}

/* Task list container */
.step-expanded-content.markdown-content :deep(ul.contains-task-list) {
  padding-left: 0;
}

.step-expanded-content.markdown-content :deep(ul.contains-task-list li) {
  list-style: none;
}

/* Legacy support for basic checkbox syntax */
.step-expanded-content.markdown-content :deep(input[type="checkbox"]) {
  margin-right: 6px;
  accent-color: var(--accent-primary);
}

</style>
