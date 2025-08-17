<template>
  <div ref="messagesArea" class="chat-container">
    <!-- Welcome Screen (When no messages) -->
    <div v-if="messages.length === 0" class="welcome-section">
      <div class="welcome-content">
        <!-- Welcome Message -->
        <div class="welcome-message">
          <div class="avatar-container">
            <UiIcon name="lucide:sparkles" :size="24" class="sparkle-icon" />
          </div>
          <h1 class="welcome-title">Coffee and Claude time?</h1>
        </div>
        
        <!-- Main Input (Claude Style) -->
        <div class="main-input">
          <UiClaudeInput
            :loading="isLoading"
            @send="handleSend"
            @add="handleAdd"
            @options="handleOptions"
            @research="handleResearch"
            @upload="handleUpload"
            @model-select="handleModelSelect"
          />
        </div>
        
        <!-- Example Prompts (Below input) -->
        <div class="example-prompts">
          <UiExamplePrompt
            v-for="prompt in examplePrompts" 
            :key="prompt.id"
            :text="prompt.text"
            :icon="prompt.icon"
            @click="handleExampleClick"
          />
        </div>
      </div>
    </div>
      
    <!-- Chat Messages (When messages exist) -->
    <div v-else class="chat-messages">
      <div class="messages-list">
        <Message
          v-for="message in messages" 
          :key="message.id"
          :message="message"
          @copy="handleCopyMessage"
          @regenerate="handleRegenerateMessage"
        />
        
        <Message
          v-if="isLoading"
          :message="{ id: Date.now() + 999, role: 'assistant', content: 'Thinking...', isLoading: true, timestamp: new Date() }"
        />
      </div>
      
      <!-- Input at bottom when in chat mode -->
      <div class="chat-input-area">
        <UiClaudeInput
          :loading="isLoading"
          placeholder="Reply to Claude..."
          @send="handleSend"
          @add="handleAdd"
          @options="handleOptions"
          @research="handleResearch"
          @upload="handleUpload"
          @model-select="handleModelSelect"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ExamplePrompt {
  id: string
  text: string
  icon: string
}

const { messages, isLoading, sendMessage } = useChat()
const messagesArea = ref()

const examplePrompts: ExamplePrompt[] = [
  {
    id: '1',
    text: 'Write',
    icon: 'lucide:pen-tool'
  },
  {
    id: '2', 
    text: 'Learn',
    icon: 'lucide:graduation-cap'
  },
  {
    id: '3',
    text: 'Code',
    icon: 'lucide:code-2'
  }
]

const handleSend = (content: string) => {
  sendMessage(content)
}

const handleExampleClick = (text: string) => {
  sendMessage(text)
}

const handleAdd = () => {
  console.log('Add clicked')
}

const handleOptions = () => {
  console.log('Options clicked')
}

const handleResearch = () => {
  console.log('Research clicked')
}

const handleUpload = () => {
  console.log('Upload clicked')
}

const handleModelSelect = () => {
  console.log('Model select clicked')
}

const handleCopyMessage = (content: string) => {
  console.log('Message copied:', content)
  // TODO: Show toast notification
}

const handleRegenerateMessage = (messageId: string | number) => {
  console.log('Regenerate message:', messageId)
  // TODO: Implement message regeneration
}

// Auto-scroll when new messages arrive
watch(messages, () => {
  nextTick(() => {
    if (messagesArea.value) {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 0;
}

/* Welcome Section */
.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 40px 24px;
}

.welcome-content {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
}

.avatar-container {
  width: 64px;
  height: 64px;
  background: var(--accent-primary);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sparkle-icon {
  color: white;
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.main-input {
  width: 100%;
  max-width: 800px;
}

.example-prompts {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  width: 100%;
  max-width: 600px;
}

/* Chat Messages */
.chat-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  min-height: 100vh;
}

.messages-list {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid var(--border-primary);
  background: var(--bg-primary);
}

/* Responsive */
@media (max-width: 768px) {
  .example-prompts {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-section {
    padding: 20px 16px;
  }
}
</style>