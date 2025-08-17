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
          <div v-if="message.reasoning && showReasoning" class="reasoning-section">
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
              {{ message.reasoning }}
            </div>
          </div>
          
          <!-- Main Content -->
          <div v-if="message.content" class="message-text">{{ message.content }}</div>
          
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
}

const props = withDefaults(defineProps<Props>(), {
  userInitials: 'NK',
  showReasoning: true
})

const emit = defineEmits<Emits>()

const reasoningExpanded = ref(false)

const formatTime = (timestamp?: Date) => {
  if (!timestamp) return ''
  return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// const formatMessage = (content: string) => {
//   return content
//     .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//     .replace(/\*(.*?)\*/g, '<em>$1</em>')
//     .replace(/`(.*?)`/g, '<code>$1</code>')
//     .replace(/\n/g, '<br>')
// }

const getToolStatus = (status?: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'error': return 'error'
    default: return 'warning'
  }
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
  emit('regenerate', props.message.id)
}
</script>

<style scoped>
.message {
  display: flex;
  gap: 12px;
  padding: 16px 0;
}

.message--user {
  flex-direction: row-reverse;
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
  margin-bottom: 8px;
}

.message-author {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-body {
  color: var(--text-primary);
  line-height: 1.6;
}

.reasoning-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  cursor: pointer;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.reasoning-header:hover {
  background: var(--bg-hover);
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

.tools-section {
  margin: 16px 0;
}

.tool-call {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  margin-bottom: 8px;
  overflow: hidden;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.tool-name {
  font-weight: 500;
  color: var(--text-primary);
}

.tool-result {
  padding: 12px;
  background: var(--bg-primary);
}

.tool-result pre {
  font-size: 12px;
  color: var(--text-secondary);
  overflow-x: auto;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 8px;
  margin-top: 8px;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message:hover .message-actions {
  opacity: 1;
}

.action-button {
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
}

.message--user .message-content {
  text-align: right;
}

.message--user .message-header {
  justify-content: flex-end;
}

.message--user .message-actions {
  justify-content: flex-end;
}
</style>
