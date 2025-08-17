<template>
  <div class="message-bubble" :class="[`message--${message.role}`]">
    <Avatar 
      v-if="message.role === 'assistant'"
      icon="cpu"
      variant="primary"
      size="md"
    />
    <Avatar 
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
        <LoadingDots v-if="message.isLoading" size="sm" />
        <div v-else v-html="formatMessage(message.content)"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
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

/* Loading dots styles handled by LoadingDots component */
</style>
