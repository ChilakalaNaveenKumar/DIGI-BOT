<template>
  <div class="message" :class="[`message--${message.role}`]">
    <div class="message-avatar">
      <UiAvatar 
        v-if="message.role === 'assistant'"
        icon="lucide:cpu"
        variant="primary"
        size="md"
      />
      <UiAvatar 
        v-else
        :initials="userInitials"
        variant="secondary"
        size="md"
      />
    </div>
    
    <div class="message-content">
      <div class="message-header">
        <span class="message-author">
          {{ message.role === 'assistant' ? 'Claude' : 'You' }}
        </span>
        <span class="message-time">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>
      
      <div class="message-body">
        <!-- Loading State -->
        <UiLoadingDots v-if="message.isLoading" size="sm" />
        
        <div v-else>
          <!-- Reasoning Section -->
          <ReasoningStepper 
            v-if="message.reasoningSteps && message.reasoningSteps.length > 0 && showReasoning"
            :steps="message.reasoningSteps"
            :initial-expanded="false"
          />
          
          <!-- Fallback for old reasoning format -->
          <div v-else-if="message.reasoning && showReasoning" class="reasoning-section">
            <div class="reasoning-header" @click="toggleReasoning">
              <UiIcon name="lucide:cpu" :size="14" />
              <span>Thought process</span>
              <UiIcon 
                name="lucide:chevron-down" 
                :size="14" 
                class="reasoning-chevron"
                :class="{ 'reasoning-chevron--expanded': reasoningExpanded }"
              />
            </div>
            <div v-if="reasoningExpanded" class="reasoning-content">
              <UiStreamingMarkdown
                :key="`reasoning-${message.id}`"
                :content="message.reasoning || ''"
                :is-streaming="false"
                :show-cursor="false"
                mode="static"
              />
            </div>
          </div>
          
          <!-- Main Content -->
          <div v-if="message.content" class="message-text">
            <UiStreamingMarkdown
              :key="`content-${message.id}`"
              :content="message.content"
              :is-streaming="message.isStreaming || false"
              :show-cursor="message.isStreaming || false"
              :show-streaming-indicator="message.isStreaming || false"
              :mode="message.isStreaming ? 'streaming' : 'static'"
              :auto-scroll="true"
              @content-updated="handleContentUpdate"
              @streaming-complete="handleStreamingComplete"
              @block-completed="handleBlockCompleted"
            />
          </div>
          
          <!-- Generated Components -->
          <div v-if="message.components && message.components.length > 0" class="components-section">
            <div class="components-header">
              <UiIcon name="lucide:bar-chart-3" :size="14" />
              <span>Generated Components ({{ message.components.length }})</span>
            </div>
            <div class="components-list">
              <div
                v-for="(component, index) in message.components"
                :key="`component-${index}`"
                class="generated-component"
              >
                <div class="component-info">
                  <div class="component-meta">
                    <UiBadge variant="secondary" size="sm">
                      {{ component.type }}
                    </UiBadge>
                    <span class="component-confidence">
                      {{ (component.confidence * 100).toFixed(1) }}% confidence
                    </span>
                  </div>
                </div>
                <div class="component-preview">
                  <EnhancedComponentRenderer
                    :component-type="component.type"
                    :markdown="component.markdown"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Tool Calls -->
          <div v-if="message.toolCalls && message.toolCalls.length > 0" class="tools-section">
            <div v-for="toolCall in message.toolCalls" :key="toolCall.id" class="tool-call">
              <div class="tool-header">
                <UiIcon name="lucide:cpu" :size="14" />
                <span class="tool-name">{{ toolCall.name }}</span>
                <UiBadge 
                  :variant="getToolStatus(toolCall.status)"
                  size="sm"
                >
                  {{ toolCall.status || 'running' }}
                </UiBadge>
              </div>
              <div v-if="toolCall.result" class="tool-result">
                <pre>{{ JSON.stringify(toolCall.result, null, 2) }}</pre>
              </div>
            </div>
          </div>
          
          <!-- Error Display -->
          <div v-if="message.error" class="error-message">
            <UiIcon name="lucide:alert-circle" :size="14" />
            <span>{{ message.error }}</span>
          </div>
        </div>
      </div>
      
      <!-- Message Actions -->
      <div v-if="message.role === 'assistant' && message.content && !message.isLoading" class="message-actions">
        <UiButton variant="ghost" size="sm" class="action-button" @click="copyMessage">
          <UiIcon name="lucide:copy" :size="12" />
          Copy
        </UiButton>
        <UiButton variant="ghost" size="sm" class="action-button" @click="regenerateMessage">
          <UiIcon name="lucide:refresh-cw" :size="12" />
          Regenerate
        </UiButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '~/types'

interface Props {
  message: Message
  userInitials?: string
  showReasoning?: boolean
}

interface Emits {
  (e: 'copy', content: string): void
  (e: 'regenerate', messageId: string | number): void
  (e: 'content-updated' | 'streaming-complete'): void
}

const props = withDefaults(defineProps<Props>(), {
  userInitials: 'NK',
  showReasoning: true
})

const emit = defineEmits<Emits>()

const reasoningExpanded = ref(false)

// Event handlers for StreamingMarkdown
const handleContentUpdate = () => {
  emit('content-updated')
}

const handleStreamingComplete = () => {
  emit('streaming-complete')
}

const handleBlockCompleted = (block: unknown) => {
  console.log('Block completed:', block)
}

const formatTime = (timestamp?: Date) => {
  if (!timestamp) return ''
  return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const toggleReasoning = () => {
  reasoningExpanded.value = !reasoningExpanded.value
}

const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    emit('copy', props.message.content)
  } catch (err) {
    console.error('Failed to copy message:', err)
  }
}

const regenerateMessage = () => {
  if (props.message.id) {
    emit('regenerate', props.message.id)
  }
}

const getToolStatus = (status?: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'error'
    case 'running': return 'warning'
    default: return 'secondary'
  }
}
</script>

<style scoped>
.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 100%;
  margin-bottom: 16px;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.message-author {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-body {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

/* Reasoning section */
.reasoning-section {
  margin-bottom: 12px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.reasoning-header:hover {
  background: var(--bg-tertiary);
}

.reasoning-chevron {
  margin-left: auto;
  transition: transform 0.2s ease;
}

.reasoning-chevron--expanded {
  transform: rotate(180deg);
}

.reasoning-content {
  padding: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.message-text {
  margin-bottom: 8px;
}

/* Generated Components */
.components-section {
  margin: 12px 0;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.components-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-tertiary);
}

.components-list {
  padding: 8px;
}

.generated-component {
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  margin-bottom: 8px;
  overflow: hidden;
}

.generated-component:last-child {
  margin-bottom: 0;
}

.component-info {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-secondary);
}

.component-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.component-confidence {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: monospace;
}

.component-preview {
  background: var(--bg-code);
}

.component-markdown {
  padding: 12px;
}

.component-code {
  margin: 0;
  font-size: 11px;
  line-height: 1.4;
  color: var(--text-code);
  background: none;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}

/* Tool calls */
.tools-section {
  margin: 12px 0;
}

.tool-call {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  margin-bottom: 8px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-primary);
}

.tool-name {
  flex: 1;
  font-family: monospace;
}

.tool-result {
  padding: 12px;
}

.tool-result pre {
  margin: 0;
  font-size: 11px;
  line-height: 1.4;
  color: var(--text-secondary);
  background: none;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Error message */
.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--error-bg, #fef2f2);
  color: #dc2626;
  border-radius: 8px;
  margin-top: 8px;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  margin-bottom: 24px;
  padding: 8px 0 16px 0;
  opacity: 0;
  transition: opacity 0.2s ease;
  background: var(--bg-primary);
  border-radius: 8px;
}

.message:hover .message-actions,
.message:last-child .message-actions {
  opacity: 1;
}

.action-button {
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
}

.message--user .message-content {
  align-items: flex-end;
}

.message--user .message-header {
  justify-content: flex-end;
}

.message--user .message-actions {
  justify-content: flex-end;
}
</style>

