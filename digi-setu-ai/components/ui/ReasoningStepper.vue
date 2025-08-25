<template>
  <div class="reasoning-stepper">
    <div class="reasoning-accordion">
      <div class="stepper-line" />
      <div class="accordion-steps">
        <div 
          v-for="(step, index) in _props.steps" 
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
                :size="16" 
                class="step-icon"
                :class="{ 
                  'step-icon--active': index === currentlyRunningStepIndex,
                  'step-icon--completed': step.status === 'completed'
                }"
              />
              <UiIcon 
                v-else
                name="brain-circuit"
                :size="16"
                class="thinking-icon"
                :class="{ 
                  'thinking-icon--active': index === currentlyRunningStepIndex,
                  'thinking-icon--completed': step.status === 'completed'
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
          <div v-if="expandedSteps.has(index)" class="step-expanded-content">
            <UiStreamingMarkdown
              :key="`step-${index}-content`"
              :content="step.content || ''"
              :is-streaming="false"
              :show-cursor="false"
              mode="static"
            />
            
            <!-- Show tool results if available -->
            <div v-if="step.result && step.type === 'tool_call'" class="tool-result-section">

              <div class="tool-result-content">
                <UiStreamingMarkdown
                  :key="`tool-result-${step.id}`"
                  :content="formatToolResultAsMarkdown(step)"
                  :is-streaming="false"
                  :show-cursor="false"
                  mode="static"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Only show thinking indicator inside reasoning stepper -->
    <div v-if="_props.isStreaming && _props.showStreamingIndicator" class="thinking-indicator">
      <div class="thinking-dots">
        <span /><span /><span />
      </div>
      <span class="thinking-text">Thinking...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
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

// Find the currently running step (last active step)
const currentlyRunningStepIndex = computed(() => {
  if (!_props.steps) return -1
  for (let i = _props.steps.length - 1; i >= 0; i--) {
    if (_props.steps[i]?.status === 'active') {
      return i
    }
  }
  return -1
})

const getStepPreview = (step: ReasoningStep) => {
  if (step.type === 'thinking') {
    return 'Thinking'
  }
  
  if (step.type === 'tool_call') {
    // For web search, show the query from the inputJson or content
    if (step.tool_name === 'web_search') {
      // Try to extract query from inputJson first
      try {
        const inputJson = (step as ReasoningStep & { inputJson?: string }).inputJson
        if (inputJson) {
          const parsed = JSON.parse(inputJson)
          if (parsed.query) {
            return `Searching: ${parsed.query}`
          }
        }
      } catch {
        // Fall back to content parsing
      }
      
      // Fallback: extract from content
      const queryMatch = step.content.match(/Searching:\s*(.+)/)
      if (queryMatch) {
        return step.content
      }
      return 'Web Search'
    }
    
    // For other tools, show tool name
    const toolNames: Record<string, string> = {
      'web_search': 'Web Search',
      'code_execution': 'Code Execution',
      'file_read': 'File Read',
      'chart_tools': 'Chart Generation'
    }
    return toolNames[step.tool_name || ''] || 'Tool Call'
  }
  
  // Fallback to content preview
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
    'codebase_search': 'book-open',
    'read_file': 'book-open', 
    'search_replace': 'edit-3',
    'write': 'plus',
    'run_terminal_cmd': 'settings',
    'grep': 'settings',
    'list_dir': 'settings',
    'web_search': 'book-open',
    'delete_file': 'settings',
    'multi_edit': 'edit-3',
    'create_diagram': 'sparkles',
    'chart_tools': 'settings'
  }
  return iconMap[toolName || ''] || 'settings'
}

const formatToolResultAsMarkdown = (step: ReasoningStep) => {
  if (!step.result) return ''
  
  if (step.tool_name === 'web_search' && Array.isArray(step.result)) {
    // Format web search results as rich cards
    let markdown = ''
    
    step.result.forEach((result: { title: string; url: string }, idx: number) => {
      let domain = 'unknown'
      try {
        domain = new URL(result.url).hostname.replace('www.', '')
      } catch {
        // Fallback for invalid URLs
        domain = result.url.split('/')[2] || 'unknown'
      }
      
      markdown += `<div class="search-result-card">\n`
      markdown += `  <div class="search-result-header">\n`
      markdown += `    <span class="search-result-domain">${domain}</span>\n`
      markdown += `  </div>\n`
      markdown += `  <h4 class="search-result-title">\n`
      markdown += `    <a href="${result.url}" target="_blank" rel="noopener noreferrer">${result.title}</a>\n`
      markdown += `  </h4>\n`
      markdown += `  <p class="search-result-url">${result.url}</p>\n`
      markdown += `</div>\n\n`
    })
    
    return markdown
  }
  
  // For other tools, format as code block
  if (typeof step.result === 'string') {
    return `\`\`\`\n${step.result}\n\`\`\``
  }
  
  // For objects, format as JSON
  return `\`\`\`json\n${JSON.stringify(step.result, null, 2)}\n\`\`\``
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
  left: 29px;
  top: 24px;
  bottom: 24px;
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
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
}

.step-icon {
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.step-icon--active {
  color: #ff8c00 !important; /* Orange for currently running tools */
  animation: pulse-icon 2s infinite;
}

.step-icon--completed {
  color: var(--text-secondary); /* Normal color for completed */
}

.thinking-icon {
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.thinking-icon--active {
  color: #ff8c00 !important; /* Orange for currently running thinking */
  animation: pulse-icon 2s infinite;
}

.thinking-icon--completed {
  color: var(--text-secondary); /* Normal color for completed */
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
  transition: all 0.2s ease;
  border-radius: 6px;
}

.step-header--clickable:hover {
  background: var(--bg-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.step-header--clickable:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
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

@keyframes pulse-orange {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 8px rgba(255, 140, 0, 0.4);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.2);
    box-shadow: 0 0 12px rgba(255, 140, 0, 0.6);
  }
}

@keyframes pulse-icon {
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

/* Tool Results Styling */
.tool-result-section {
  margin-top: 12px;
  border-top: 1px solid var(--border-primary);
  padding-top: 12px;
}

.tool-result-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.tool-result-content {
  font-size: 13px;
  color: var(--text-primary);
  max-height: 400px;
  overflow-y: auto;
  border-radius: 8px;
  border: 1px solid var(--border-primary);
  padding: 8px;
  margin-top: 8px;
  background: var(--bg-primary);
}

.tool-result-content::-webkit-scrollbar {
  width: 6px;
}

.tool-result-content::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.tool-result-content::-webkit-scrollbar-thumb {
  background: var(--border-primary);
  border-radius: 3px;
}

.tool-result-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}

/* Enhanced link styling for tool results */
.tool-result-content :deep(a) {
  color: var(--accent-primary) !important;
  text-decoration: none !important;
  font-weight: 500 !important;
  border-bottom: 1px solid transparent !important;
  transition: all 0.2s ease !important;
  padding: 2px 0 !important;
}

.tool-result-content :deep(a:hover) {
  color: var(--accent-primary) !important;
  border-bottom-color: var(--accent-primary) !important;
  background: rgba(59, 130, 246, 0.1) !important;
  border-radius: 3px !important;
  padding: 2px 4px !important;
  margin: 0 -4px !important;
}

.tool-result-content :deep(strong) {
  color: var(--text-primary) !important;
  font-weight: 600 !important;
  margin-bottom: 4px !important;
  display: block !important;
}

.tool-result-content :deep(p) {
  margin: 8px 0 !important;
  line-height: 1.5 !important;
}

/* 🔍 SEARCH RESULT CARDS */
.tool-result-content :deep(.search-result-card) {
  background: var(--bg-secondary) !important;
  border: 1px solid var(--border-primary) !important;
  border-radius: 8px !important;
  padding: 16px !important;
  margin: 12px 0 !important;
  transition: all 0.2s ease !important;
  position: relative !important;
  animation: slideInUp 0.3s ease-out !important;
  animation-fill-mode: both !important;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tool-result-content :deep(.search-result-card:hover) {
  border-color: var(--accent-primary) !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
  transform: translateY(-1px) !important;
}

.tool-result-content :deep(.search-result-header) {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-end !important;
  margin-bottom: 8px !important;
}



.tool-result-content :deep(.search-result-domain) {
  background: var(--bg-tertiary) !important;
  color: var(--text-tertiary) !important;
  padding: 4px 8px !important;
  border-radius: 12px !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}

.tool-result-content :deep(.search-result-title) {
  margin: 8px 0 6px 0 !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  line-height: 1.4 !important;
}

.tool-result-content :deep(.search-result-title a) {
  color: var(--text-primary) !important;
  text-decoration: none !important;
  border-bottom: none !important;
  padding: 0 !important;
  margin: 0 !important;
  background: none !important;
  border-radius: 0 !important;
}

.tool-result-content :deep(.search-result-title a:hover) {
  color: var(--accent-primary) !important;
  background: none !important;
  border-bottom: 1px solid var(--accent-primary) !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 0 !important;
}

.tool-result-content :deep(.search-result-url) {
  color: var(--text-tertiary) !important;
  font-size: 12px !important;
  margin: 0 !important;
  word-break: break-all !important;
  opacity: 0.8 !important;
}

/* Tool result content is now handled by StreamingMarkdown component */

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
