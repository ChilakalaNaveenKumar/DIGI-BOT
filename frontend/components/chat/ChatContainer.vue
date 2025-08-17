<template>
  <div class="chat-container">
    <div class="messages-area" ref="messagesArea">
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-content">
          <h2>Coffee and Claude time? ☕</h2>
          <p>Ready to help with your coding tasks. What would you like to work on today?</p>
        </div>
      </div>
      
      <div v-for="message in messages" :key="message.id" class="message-wrapper">
        <MessageBubble :message="message" />
      </div>
      
      <div v-if="isLoading" class="loading-message">
        <MessageBubble :message="{ role: 'assistant', content: 'Thinking...', isLoading: true }" />
      </div>
    </div>
    
    <InputArea 
      v-model="input"
      :loading="isLoading"
      @send="handleSend"
    />
  </div>
</template>

<script setup>
const { messages, isLoading, input, sendMessage } = useChat()
const messagesArea = ref()

const handleSend = (content: string) => {
  sendMessage(content)
  
  // Scroll to bottom after sending
  nextTick(() => {
    if (messagesArea.value) {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight
    }
  })
}

// Auto-scroll when new messages arrive
watch(messages, () => {
  nextTick(() => {
    if (messagesArea.value) {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight
    }
  })
}, { deep: true })
</script>

<style scoped>
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.welcome-content {
  text-align: center;
  max-width: 400px;
}

.welcome-content h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.welcome-content p {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
}

.loading-message {
  opacity: 0.7;
}
</style>
