<template>
  <div class="message-bubble" :class="[`message--${message.role}`]">
    <UiAvatar 
      v-if="message.role === 'assistant'"
      icon="lucide:cpu"
      variant="primary"
      size="md"
    />
    <UiAvatar 
      v-else
      initials="NK"
      variant="secondary"
      size="md"
    />
    
    <div class="message-content">
      <div class="message-header">
        <span class="message-author">
          {{ message.role === 'assistant' ? 'Claude' : 'You' }}
        </span>
        <span class="message-time">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>
      
      <div class="message-text">
        <UiLoadingDots v-if="message.isLoading" size="sm" />
        <div v-else>
          <!-- Reasoning section -->
          <div v-if="message.reasoning" class="reasoning-section">
            <div class="reasoning-header">
                          <UiIcon name="lucide:cpu" :size="14" />
            <span>Thinking...</span>
            </div>
            <div class="reasoning-content" v-html="formatMessage(message.reasoning)"></div>
          </div>
          
          <!-- Tool calls section -->
          <div v-if="message.toolCalls && message.toolCalls.length > 0" class="tools-section">
            <div v-for="toolCall in message.toolCalls" :key="toolCall.id" class="tool-call">
              <div class="tool-header">
                <UiIcon name="lucide:cpu" :size="14" />
                <span class="tool-name">{{ toolCall.name }}</span>
                <UiBadge 
                  :variant="toolCall.status === 'completed' ? 'success' : toolCall.status === 'error' ? 'error' : 'warning'"
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
          
          <!-- Main content -->
          <div v-if="message.content" v-html="formatMessage(message.content)"></div>
          
          <!-- Error display -->
          <div v-if="message.error" class="error-message">
            <UiIcon name="lucide:alert-circle" :size="14" />
            <span>{{ message.error }}</span>
          </div>
        </div>
        
        <!-- Message Actions (for assistant messages) -->
        <div v-if="message.role === 'assistant' && message.content" class="message-actions">
          <UiButton variant="ghost" size="sm" class="action-btn" @click="copyMessage">
            <UiIcon name="lucide:copy" :size="12" />
            Copy
          </UiButton>
          <UiButton variant="ghost" size="sm" class="action-btn" @click="regenerateMessage">
            <UiIcon name="lucide:refresh-cw" :size="12" />
            Regenerate
          </UiButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Message {
  id?: number
  content: string
  role: 'user' | 'assistant'
  timestamp?: Date
  isLoading?: boolean
}

interface Props {
  message: Message
}

const props = defineProps<Props>()

const formatTime = (timestamp?: Date) => {
  if (!timestamp) return ''
  return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content: string) => {
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    // Could show a toast notification here
    console.log('Message copied to clipboard')
  } catch (err) {
    console.error('Failed to copy message:', err)
  }
}

const regenerateMessage = () => {
  // This would trigger message regeneration
  console.log('Regenerate message:', props.message.id)
  // Could emit an event to parent component
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 12px;
  max-width: 100%;
  margin-bottom: 16px;
}

/* Avatar styles handled by Avatar component */

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
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

.message-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

.message-text :deep(code) {
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(em) {
  font-style: italic;
}

/* Enhanced sections styling */
.reasoning-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.reasoning-content {
  font-size: 13px;
  color: var(--text-secondary);
  font-style: italic;
}

.tools-section {
  margin-bottom: 12px;
}

.tool-call {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.tool-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.tool-result {
  background: var(--bg-primary);
  border-radius: 4px;
  padding: 8px;
  overflow-x: auto;
}

.tool-result pre {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
  color: var(--text-secondary);
  margin: 0;
  white-space: pre-wrap;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 8px;
}

.message-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message-bubble:hover .message-actions {
  opacity: 1;
}

.action-btn {
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
  color: var(--text-secondary);
}

.action-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

/* Loading dots styles handled by LoadingDots component */
</style>
