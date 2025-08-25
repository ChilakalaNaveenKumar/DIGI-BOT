<template>
  <div ref="messagesArea" class="chat-container">
    <!-- Welcome Screen (When no messages) -->
    <div v-if="messages.length === 0" class="welcome-section">
      <div class="welcome-content">
        <!-- Welcome Message -->
        <div class="welcome-message">
          <div class="avatar-container">
            <Icon name="lucide:sparkles" :size="24" class="sparkle-icon" />
          </div>
          <h1 class="welcome-title">Transform learning with AI</h1>
          <p class="welcome-subtitle">Transform static content into interactive learning experiences with AI</p>
        </div>
        
        <!-- Main Input (Digi Setu Style) -->
        <div class="main-input">
          <UiDigiSetuInput
            :loading="isLoading || isStreaming || isProcessingComponents"
            placeholder="Ask me anything or describe what you want to create..."
            @send="handleSend"
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
      <!-- Conversation Header -->
      <div v-if="conversationTitle" class="conversation-header">
        <h2 class="conversation-title">{{ conversationTitle }}</h2>
        <button @click="startNewConversation" class="new-chat-btn">
          <Icon name="lucide:plus" :size="16" />
          New Chat
        </button>
      </div>
      
      <div class="chat-messages">
        <div class="messages-list">
          <ChatMessage
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
          <UiDigiSetuInput
            :loading="isLoading || isStreaming || isProcessingComponents"
            placeholder="Reply to Digi Setu..."
            @send="handleSend"
          />
          
          <!-- Analysis Status Indicator -->
          <div v-if="isAnalyzing || isProcessingComponents" class="analysis-status">
            <Icon name="lucide:bar-chart-3" :size="12" class="analysis-icon" />
            <span class="analysis-text">
              {{ isProcessingComponents ? 'Processing components...' : 'Analyzing for components...' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Message type imported by useStreamingChat composable

interface ExamplePrompt {
  id: string
  text: string
  icon: string
}

// Use streaming chat composable
const { 
  messages, 
  isLoading, 
  isStreaming, 
  conversationId,
  conversationTitle,
  isProcessingComponents,
  sendMessage, 
  startNewConversation,
  regenerateMessage 
} = useStreamingChat()

const isAnalyzing = ref(false)

const messagesArea = ref()

const examplePrompts: ExamplePrompt[] = [
  {
    id: '1',
    text: 'Create an interactive lesson',
    icon: 'lucide:graduation-cap'
  },
  {
    id: '2', 
    text: 'Generate a quiz',
    icon: 'lucide:help-circle'
  },
  {
    id: '3',
    text: 'Build a data visualization',
    icon: 'lucide:bar-chart-3'
  },
  {
    id: '4',
    text: 'Design a component',
    icon: 'lucide:code-2'
  }
]

const handleSend = async (content: string) => {
  if (!content.trim()) return
  
  console.log('ChatContainer: handleSend called with:', content) // Debug log
  
  // Use the streaming composable
  await sendMessage(content.trim())
}

// Removed simulateAIResponse - now using real streaming via useStreamingChat()

const handleExampleClick = (text: string) => {
  handleSend(text)
}

const handleCopyMessage = (content: string) => {
  navigator.clipboard.writeText(content)
  // TODO: Show toast notification
}

const handleRegenerateMessage = async (messageId: string) => {
  await regenerateMessage(messageId)
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

.welcome-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
  max-width: 600px;
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

.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgb(var(--color-border));
  background: rgb(var(--color-surface));
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.conversation-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgb(var(--color-primary));
  color: rgb(var(--color-primary-foreground));
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  background: rgb(var(--color-primary-hover));
  transform: translateY(-1px);
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

.chat-input-area-fixed :deep(.digi-setu-input-wrapper) {
  max-width: 800px; /* Match messages container width */
  margin: 0 auto;
  padding: 0 24px; /* Match messages-list padding */
  width: 100%;
  box-sizing: border-box;
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

/* Responsive */
@media (max-width: 1024px) {
  .chat-input-area-fixed {
    left: 260px; /* Keep sidebar offset */
    right: 0;
    padding: 16px 0;
  }
  
  .chat-input-area-fixed :deep(.digi-setu-input-wrapper) {
    max-width: calc(100vw - 260px - 48px); /* Viewport width minus sidebar width minus padding */
    padding: 0 24px;
    margin: 0 auto;
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
  
  .chat-input-area-fixed :deep(.digi-setu-input-wrapper) {
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
  
  .chat-input-area-fixed :deep(.digi-setu-input-wrapper) {
    max-width: calc(100vw - 260px - 24px); /* Account for sidebar width minus padding */
    padding: 0;
  }
  
  .messages-list {
    padding: 12px;
  }
}
</style>