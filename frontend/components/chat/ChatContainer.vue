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
    <div v-else class="chat-mode">
      <div class="chat-messages">
        <div class="messages-list">
          <Message
            v-for="message in messages" 
            :key="message.id"
            :message="message"
            @copy="handleCopyMessage"
            @regenerate="handleRegenerateMessage"
          />
        </div>
      </div>
      
      <!-- Fixed Input at bottom when in chat mode -->
      <div class="chat-input-area-fixed">
        <div class="input-with-status">
          <UiClaudeInput
            :loading="isLoading || isStreaming"
            placeholder="Reply to Claude..."
            @send="handleSend"
            @add="handleAdd"
            @options="handleOptions"
            @research="handleResearch"
            @upload="handleUpload"
            @model-select="handleModelSelect"
          />
          
          <!-- Analysis Status Indicator -->
          <div v-if="isAnalyzing" class="analysis-status">
            <UiIcon name="lucide:bar-chart-3" :size="12" class="analysis-icon" />
            <span class="analysis-text">Analyzing for components...</span>
          </div>
        </div>
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

const { messages, isLoading, isStreaming, isAnalyzing, sendMessage } = useSmartStreamingChat()
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
  overflow: visible;
  padding: 0;
  min-height: 100%;
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

/* Chat Mode Layout */
.chat-mode {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  overflow: visible;
}

.chat-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  overflow: visible;
  padding-bottom: 140px; /* Extra space for message actions visibility */
}

.messages-list {
  padding: 24px;
}

/* Fixed Input Area */
.chat-input-area-fixed {
  position: fixed;
  bottom: 0;
  left: 260px; /* Account for sidebar width */
  right: 0;
  background: transparent; /* Remove background to blend with chat */
  z-index: 100;
  padding: 16px 0;
}

.chat-input-area-fixed .claude-input-wrapper {
  max-width: 800px; /* Match messages container width */
  margin: 0 auto;
  padding: 0 24px; /* Match messages-list padding */
  width: 100%;
  box-sizing: border-box;
}

/* Responsive */
@media (max-width: 1024px) {
  .chat-input-area-fixed {
    left: 260px; /* Keep sidebar offset */
    right: 0;
    padding: 16px 0;
  }
  
  .chat-input-area-fixed .claude-input-wrapper {
    max-width: calc(100vw - 260px - 48px); /* Viewport width minus sidebar width minus padding */
    padding: 0 24px;
    margin: 0 auto;
  }
}

/* Analysis Status */
.input-with-status {
  position: relative;
}

.analysis-status {
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  backdrop-filter: blur(8px);
  z-index: 10;
}

.analysis-icon {
  color: var(--accent-primary);
  animation: pulse 2s infinite;
}

.analysis-text {
  white-space: nowrap;
}

@keyframes pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

/* Medium screens - better transition */
@media (min-width: 768px) and (max-width: 1024px) {
  .chat-input-area-fixed .claude-input-wrapper {
    max-width: min(800px, calc(100vw - 260px - 48px)); /* Account for sidebar + padding, capped at 800px */
    padding: 0 24px;
  }
}

/* Mobile screens */
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
  
  .chat-messages {
    padding-bottom: 160px; /* Extra space for message actions on mobile */
  }
  
  .chat-input-area-fixed {
    left: 260px; /* Keep sidebar offset */
    right: 0;
    padding: 0px; /* Match chat message container */
  }
  
  .chat-input-area-fixed .claude-input-wrapper {
    max-width: calc(100vw - 260px - 32px); /* Account for sidebar width minus padding */
    padding: 0; /* Match mobile messages padding */
    margin: 0 auto;
  }
  
  .messages-list {
    padding: 16px;
  }
}

/* Very small screens */
@media (max-width: 480px) {
  .chat-input-area-fixed {
    left: 260px; /* Keep sidebar offset */
    padding: 0px; /* Match chat message container */
  }
  
  .chat-input-area-fixed .claude-input-wrapper {
    max-width: calc(100vw - 260px - 24px); /* Account for sidebar width minus padding */
    padding: 0;
  }
  
  .messages-list {
    padding: 12px;
  }
}
</style>