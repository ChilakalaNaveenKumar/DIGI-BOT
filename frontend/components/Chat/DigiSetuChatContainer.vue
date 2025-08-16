<template>
  <div class="ds-chat-container">
    <!-- Welcome State -->
    <div v-if="messages.length === 0" class="ds-welcome-state">
      <div class="ds-welcome-content">
        <!-- Digi Setu Logo -->
        <div class="ds-welcome-logo">
          <div class="ds-logo-circle">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="48" height="48" rx="12" fill="var(--ds-primary)"/>
              <path d="M12 18h24v3H12v-3zm0 6h24v3H12v-3zm0 6h18v3H12v-3z" fill="white"/>
              <circle cx="30" cy="30" r="4" fill="var(--ds-secondary)"/>
            </svg>
          </div>
          <div class="ds-status-pulse"></div>
        </div>

        <!-- Welcome Text -->
        <div class="ds-welcome-text">
          <h2 class="ds-welcome-title">Welcome to Digi Setu AI</h2>
          <p class="ds-welcome-description">
            Your intelligent AI assistant powered by multiple AI models. 
            Ask questions, upload documents, or request interactive content.
          </p>
        </div>

        <!-- Feature Cards -->
        <div class="ds-feature-grid">
          <div class="ds-feature-card">
            <div class="ds-feature-icon ds-feature-reasoning">
              <Brain class="w-5 h-5" />
            </div>
            <h3 class="ds-feature-title">AI Reasoning</h3>
            <p class="ds-feature-description">See how AI thinks through problems step by step</p>
          </div>
          
          <div class="ds-feature-card">
            <div class="ds-feature-icon ds-feature-orchestration">
              <Zap class="w-5 h-5" />
            </div>
            <h3 class="ds-feature-title">Multi-AI Orchestration</h3>
            <p class="ds-feature-description">Automatically selects the best AI model for each task</p>
          </div>
          
          <div class="ds-feature-card">
            <div class="ds-feature-icon ds-feature-content">
              <FileText class="w-5 h-5" />
            </div>
            <h3 class="ds-feature-title">Rich Content</h3>
            <p class="ds-feature-description">Interactive tables, code blocks, images, and more</p>
          </div>
        </div>

        <!-- Quick Start Prompts -->
        <div class="ds-quick-prompts">
          <h3 class="ds-prompts-title">Try asking:</h3>
          <div class="ds-prompt-buttons">
            <button 
              v-for="prompt in quickPrompts" 
              :key="prompt.id"
              class="ds-prompt-btn"
              @click="sendQuickPrompt(prompt.text)"
            >
              <component :is="prompt.icon" class="w-4 h-4" />
              <span>{{ prompt.text }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages Area -->
    <div v-else class="ds-messages-area" ref="messagesContainer">
      <div class="ds-messages-list">
        <DigiSetuMessage
          v-for="(message, index) in messages"
          :key="message.id || index"
          :message="message"
          :is-loading="isLoading && index === messages.length - 1"
          :current-activity="currentActivity"
          @regenerate="$emit('regenerate-message', message.id)"
          @copy="handleCopyMessage"
          @like="handleLikeMessage"
        />
      </div>
    </div>

    <!-- Input Area -->
    <div class="ds-input-area">
      <DigiSetuInput
        v-model="inputValue"
        :is-loading="isLoading"
        :placeholder="inputPlaceholder"
        @send="handleSendMessage"
        @file-upload="handleFileUpload"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted } from 'vue'
import { Brain, Zap, FileText, Lightbulb, Code, Image, HelpCircle } from 'lucide-vue-next'

// Import components with explicit .vue extension
import DigiSetuMessage from './DigiSetuMessage.vue'
import DigiSetuInput from './DigiSetuInput.vue'

const props = defineProps({
  conversation: {
    type: Object,
    default: null
  },
  messages: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  currentActivity: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'send-message',
  'regenerate-message'
])

// Reactive state
const inputValue = ref('')
const messagesContainer = ref(null)

// Quick start prompts
const quickPrompts = ref([
  {
    id: 1,
    text: "Explain quantum computing",
    icon: Lightbulb
  },
  {
    id: 2,
    text: "Create a Python function",
    icon: Code
  },
  {
    id: 3,
    text: "Generate an image",
    icon: Image
  },
  {
    id: 4,
    text: "Help me learn something new",
    icon: HelpCircle
  }
])

// Computed properties
const inputPlaceholder = computed(() => {
  if (props.isLoading) {
    return 'AI is processing...'
  }
  return 'Ask me anything, upload files, or request interactive content...'
})

// Methods
const handleSendMessage = (messageData) => {
  // Handle both string content (from quick prompts) and object data (from input component)
  let content, files
  
  if (typeof messageData === 'string') {
    content = messageData
    files = null
  } else if (messageData && typeof messageData === 'object') {
    content = messageData.text || messageData.content || ''
    files = messageData.files || null
  } else {
    return
  }
  
  if (!content || typeof content !== 'string' || !content.trim() || props.isLoading) return
  
  emit('send-message', { content: content.trim(), files })
  inputValue.value = ''
  
  // Scroll to bottom after sending
  nextTick(() => {
    scrollToBottom()
  })
}

const sendQuickPrompt = (promptText) => {
  handleSendMessage(promptText)
}

const handleFileUpload = (files) => {
  console.log('Files uploaded:', files)
  // Handle file upload logic here
}

const handleCopyMessage = (message) => {
  // Extract text content from message
  let textContent = ''
  if (message.parts) {
    textContent = message.parts
      .filter(part => part.type === 'text')
      .map(part => part.text)
      .join('')
  } else {
    textContent = message.content || ''
  }
  
  // Copy to clipboard
  navigator.clipboard.writeText(textContent).then(() => {
    console.log('Message copied to clipboard')
    // Could show a toast notification here
  }).catch(err => {
    console.error('Failed to copy message:', err)
  })
}

const handleLikeMessage = (message) => {
  console.log('Message liked:', message.id)
  // Handle like functionality
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

// Watch for new messages and scroll to bottom
watch(() => props.messages.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// Watch for loading state changes
watch(() => props.isLoading, (newLoading) => {
  if (newLoading) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})

// Auto-scroll when activity changes
watch(() => props.currentActivity, () => {
  if (props.currentActivity) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})

onMounted(() => {
  // Initial scroll to bottom if there are messages
  if (props.messages.length > 0) {
    scrollToBottom()
  }
})
</script>

<style scoped>
.ds-chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--ds-bg-secondary);
}

/* === WELCOME STATE === */
.ds-welcome-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-8);
  overflow-y: auto;
}

.ds-welcome-content {
  max-width: 600px;
  text-align: center;
  animation: ds-fade-in 0.6s ease-out;
}

.ds-welcome-logo {
  position: relative;
  display: inline-block;
  margin-bottom: var(--ds-space-8);
}

.ds-logo-circle {
  position: relative;
  z-index: 2;
}

.ds-status-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border: 2px solid var(--ds-primary);
  border-radius: 50%;
  opacity: 0.3;
  animation: ds-pulse 2s ease-in-out infinite;
}

@keyframes ds-pulse {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.7;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.3;
  }
  100% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.7;
  }
}

.ds-welcome-text {
  margin-bottom: var(--ds-space-8);
}

.ds-welcome-title {
  font-size: var(--ds-text-3xl);
  font-weight: var(--ds-font-bold);
  color: var(--ds-text-primary);
  margin: 0 0 var(--ds-space-4) 0;
  line-height: 1.2;
}

.ds-welcome-description {
  font-size: var(--ds-text-lg);
  color: var(--ds-text-secondary);
  line-height: var(--ds-leading-relaxed);
  margin: 0;
}

/* === FEATURE GRID === */
.ds-feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--ds-space-4);
  margin-bottom: var(--ds-space-8);
}

.ds-feature-card {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-xl);
  padding: var(--ds-space-6);
  text-align: center;
  transition: all var(--ds-transition-normal);
}

.ds-feature-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--ds-shadow-lg);
}

.ds-feature-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--ds-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--ds-space-3) auto;
  color: white;
}

.ds-feature-reasoning {
  background: var(--ds-primary);
}

.ds-feature-orchestration {
  background: var(--ds-secondary);
}

.ds-feature-content {
  background: var(--ds-accent);
}

.ds-feature-title {
  font-size: var(--ds-text-base);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  margin: 0 0 var(--ds-space-2) 0;
}

.ds-feature-description {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  line-height: var(--ds-leading-relaxed);
  margin: 0;
}

/* === QUICK PROMPTS === */
.ds-quick-prompts {
  text-align: left;
}

.ds-prompts-title {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  margin: 0 0 var(--ds-space-4) 0;
  text-align: center;
}

.ds-prompt-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--ds-space-3);
}

.ds-prompt-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  padding: var(--ds-space-3) var(--ds-space-4);
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
  text-align: left;
}

.ds-prompt-btn:hover {
  background: var(--ds-surface-hover);
  border-color: var(--ds-primary);
  transform: translateY(-1px);
  box-shadow: var(--ds-shadow-md);
}

.ds-prompt-btn:active {
  transform: translateY(0);
}

/* === MESSAGES AREA === */
.ds-messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--ds-space-6) 0;
}

.ds-messages-list {
  margin: 0 auto;
  padding: 0 var(--ds-space-6);
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-6);
}

/* === INPUT AREA === */
.ds-input-area {
  flex-shrink: 0;
  background: var(--ds-surface-primary);
  border-top: 1px solid var(--ds-border-primary);
  padding: var(--ds-space-6);
}

/* === SCROLLBAR STYLING === */
.ds-messages-area::-webkit-scrollbar {
  width: 6px;
}

.ds-messages-area::-webkit-scrollbar-track {
  background: transparent;
}

.ds-messages-area::-webkit-scrollbar-thumb {
  background: var(--ds-border-secondary);
  border-radius: var(--ds-radius-full);
}

.ds-messages-area::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-welcome-state {
    padding: var(--ds-space-6) var(--ds-space-4);
  }
  
  .ds-welcome-title {
    font-size: var(--ds-text-2xl);
  }
  
  .ds-welcome-description {
    font-size: var(--ds-text-base);
  }
  
  .ds-feature-grid {
    grid-template-columns: 1fr;
    gap: var(--ds-space-3);
  }
  
  .ds-prompt-buttons {
    grid-template-columns: 1fr;
  }
  
  .ds-messages-list {
    padding: 0 var(--ds-space-4);
  }
  
  .ds-input-area {
    padding: var(--ds-space-4);
  }
}

@media (max-width: 480px) {
  .ds-welcome-state {
    padding: var(--ds-space-4) var(--ds-space-3);
  }
  
  .ds-feature-card {
    padding: var(--ds-space-4);
  }
  
  .ds-messages-list {
    padding: 0 var(--ds-space-3);
  }
  
  .ds-input-area {
    padding: var(--ds-space-3);
  }
}

/* === ACCESSIBILITY === */
.ds-prompt-btn:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === ANIMATIONS === */
.ds-feature-card {
  animation: ds-slide-up 0.4s ease-out;
  animation-fill-mode: both;
}

.ds-feature-card:nth-child(1) {
  animation-delay: 0.1s;
}

.ds-feature-card:nth-child(2) {
  animation-delay: 0.2s;
}

.ds-feature-card:nth-child(3) {
  animation-delay: 0.3s;
}

.ds-prompt-btn {
  animation: ds-slide-up 0.4s ease-out;
  animation-fill-mode: both;
}

.ds-prompt-btn:nth-child(1) {
  animation-delay: 0.4s;
}

.ds-prompt-btn:nth-child(2) {
  animation-delay: 0.5s;
}

.ds-prompt-btn:nth-child(3) {
  animation-delay: 0.6s;
}

.ds-prompt-btn:nth-child(4) {
  animation-delay: 0.7s;
}

/* === HIGH CONTRAST MODE === */
@media (prefers-contrast: high) {
  .ds-feature-card {
    border-width: 2px;
  }
  
  .ds-prompt-btn {
    border-width: 2px;
  }
}

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) {
  .ds-status-pulse {
    animation: none;
  }
  
  .ds-feature-card,
  .ds-prompt-btn {
    animation: none;
  }
  
  .ds-feature-card:hover,
  .ds-prompt-btn:hover {
    transform: none;
  }
}
</style>
