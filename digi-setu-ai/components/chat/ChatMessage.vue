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
          <!-- Main Content -->
          <div v-if="message.content || message.isStreaming" class="message-text">
            <UiStreamingMarkdown
              :key="`content-${message.id}`"
              :content="message.content"
              :is-streaming="message.isStreaming || false"
              :show-cursor="message.isStreaming || false"
              :mode="message.isStreaming ? 'streaming' : 'static'"
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

const formatTime = (timestamp?: Date) => {
  if (!timestamp) return ''
  return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
</style>
