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
          {{ message.role === 'assistant' ? 'Digi Setu AI' : 'You' }}
        </span>
        <span class="message-time">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>
      
      <div class="message-body">
        <!-- Loading State -->
        <UiLoadingDots v-if="message.isLoading" size="sm" />
        
        <div v-else>
          <!-- Reasoning Stepper (for assistant messages with reasoning) -->
          <div v-if="message.role === 'assistant' && message.reasoningSteps && message.reasoningSteps.length > 0" class="reasoning-section">
            <UiReasoningStepper
              :steps="message.reasoningSteps"
              :is-streaming="false"
              :show-streaming-indicator="false"
            />
          </div>
          
          <!-- Streaming indicator for response generation (below reasoning) -->
          <div v-if="message.role === 'assistant' && message.isStreaming && !message.content.trim()" class="response-streaming-indicator">
            <div class="streaming-dots">
              <span /><span /><span />
            </div>
            <span class="streaming-text">Generating response...</span>
          </div>
          
          <!-- Component processing indicator -->
          <div v-if="message.role === 'assistant' && message.isProcessingComponents" class="component-processing-indicator">
            <div class="processing-dots">
              <span /><span /><span />
            </div>
            <span class="processing-text">Analyzing for interactive components...</span>
          </div>
          
          <!-- Main Content -->
          <div v-if="message.content.trim()" class="message-text">
            <UiStreamingMarkdown
              :key="`content-${message.id}`"
              :content="message.content"
              :is-streaming="message.isStreaming || false"
              :show-cursor="message.isStreaming || false"
              :mode="message.isStreaming ? 'streaming' : 'static'"
              :enable-component-matching="true"
            />
          </div>
          

          
          <!-- Error Display -->
          <div v-if="message.error" class="error-message">
            <Icon name="lucide:alert-circle" :size="14" />
            <span>{{ message.error }}</span>
          </div>
        </div>
      </div>
      
      <!-- Message Actions -->
      <div v-if="message.role === 'assistant' && message.content && !message.isLoading" class="message-actions">
        <button class="action-button" @click="copyMessage">
          <Icon name="lucide:copy" :size="12" />
          Copy
        </button>
        <button class="action-button" @click="regenerateMessage">
          <Icon name="lucide:refresh-cw" :size="12" />
          Regenerate
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import type { Message } from '~/types'

interface Props {
  message: Message
  userInitials?: string
}

interface Emits {
  (e: 'copy' | 'regenerate', data: string): void
}

const props = withDefaults(defineProps<Props>(), {
  userInitials: 'NK'
})

const emit = defineEmits<Emits>()



const formatTime = (timestamp?: Date | string | number) => {
  if (!timestamp) return ''
  
  // Convert to Date object if it's not already
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp)
  
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    console.warn('Invalid timestamp:', timestamp)
    return ''
  }
  
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
    emit('regenerate', String(props.message.id))
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
  margin-bottom: 15px;
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

.reasoning-section {
  margin-bottom: 12px;
}

.response-streaming-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  color: var(--text-secondary);
  font-size: 14px;
  font-style: italic;
  margin-bottom: 8px;
}

.streaming-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.streaming-dots {
  display: flex;
  gap: 3px;
}

.streaming-dots span {
  width: 6px;
  height: 6px;
  background: var(--accent-primary);
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out;
}

.streaming-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.streaming-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.component-processing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: var(--text-secondary);
  font-size: 14px;
  font-style: italic;
  margin-bottom: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.processing-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.processing-dots {
  display: flex;
  gap: 3px;
}

.processing-dots span {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out;
}

.processing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.processing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.message-text {
  margin-bottom: 8px;
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
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
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

.component-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 500;
  border-radius: 12px;
  background: var(--primary);
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.component-confidence {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: monospace;
}

.component-preview {
  background: var(--bg-code);
  padding: 12px;
}

.component-markdown {
  margin: 0;
  font-size: 11px;
  line-height: 1.4;
  color: var(--text-secondary);
  background: none;
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
</style>
