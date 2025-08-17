<template>
  <div class="ds-enhanced-chat">
    <!-- Chat Header -->
    <div class="ds-chat-header">
      <div class="ds-header-info">
        <Icon name="mdi:robot" class="ds-chat-icon" />
        <div class="ds-header-text">
          <h2 class="ds-chat-title">Digi Setu AI Assistant</h2>
          <p class="ds-chat-subtitle">Enhanced with multimodal capabilities</p>
        </div>
      </div>
      
      <div class="ds-header-actions">
        <button @click="showCapabilities = !showCapabilities" class="ds-header-btn">
          <Icon name="mdi:information" class="ds-btn-icon" />
          Capabilities
        </button>
        <button @click="clearConversation" class="ds-header-btn">
          <Icon name="mdi:refresh" class="ds-btn-icon" />
          Clear
        </button>
        <button @click="exportConversation" class="ds-header-btn">
          <Icon name="mdi:download" class="ds-btn-icon" />
          Export
        </button>
      </div>
    </div>

    <!-- Capabilities Panel -->
    <div v-if="showCapabilities" class="ds-capabilities-panel">
      <div class="ds-capabilities-header">
        <h3 class="ds-capabilities-title">Available Capabilities</h3>
        <button @click="showCapabilities = false" class="ds-close-btn">
          <Icon name="mdi:close" class="ds-close-icon" />
        </button>
      </div>
      
      <div v-if="capabilities" class="ds-capabilities-grid">
        <div 
          v-for="(capability, key) in capabilities.capabilities" 
          :key="key"
          class="ds-capability-card"
        >
          <div class="ds-capability-header">
            <Icon :name="getCapabilityIcon(key)" class="ds-capability-icon" />
            <h4 class="ds-capability-name">{{ formatCapabilityName(key) }}</h4>
          </div>
          <p class="ds-capability-description">{{ capability.description }}</p>
          
          <!-- Show supported formats/features -->
          <div v-if="capability.supported_formats" class="ds-capability-details">
            <span class="ds-detail-label">Formats:</span>
            <div class="ds-format-tags">
              <span 
                v-for="format in capability.supported_formats.slice(0, 3)" 
                :key="format"
                class="ds-format-tag"
              >
                {{ format }}
              </span>
              <span v-if="capability.supported_formats.length > 3" class="ds-more-tag">
                +{{ capability.supported_formats.length - 3 }} more
              </span>
            </div>
          </div>
          
          <div v-if="capability.available_tools" class="ds-capability-details">
            <span class="ds-detail-label">Tools:</span>
            <div class="ds-tool-count">{{ capability.available_tools.length }} available</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Conversation Stats -->
    <div v-if="conversationStats.totalMessages > 0" class="ds-conversation-stats">
      <div class="ds-stats-grid">
        <div class="ds-stat-item">
          <Icon name="mdi:message" class="ds-stat-icon" />
          <span class="ds-stat-value">{{ conversationStats.totalMessages }}</span>
          <span class="ds-stat-label">Messages</span>
        </div>
        <div class="ds-stat-item">
          <Icon name="mdi:tools" class="ds-stat-icon" />
          <span class="ds-stat-value">{{ conversationStats.toolCalls }}</span>
          <span class="ds-stat-label">Tool Calls</span>
        </div>
      </div>
    </div>

    <!-- Messages Container -->
    <div class="ds-messages-container" ref="messagesContainer">
      <div v-if="messages.length === 0" class="ds-welcome-message">
        <div class="ds-welcome-content">
          <Icon name="mdi:robot-excited" class="ds-welcome-icon" />
          <h3 class="ds-welcome-title">Welcome to Enhanced AI Chat!</h3>
          <p class="ds-welcome-text">
            I can help you with calculations, weather, code generation, web search, 
            image analysis, audio processing, and much more. Just ask me anything!
          </p>
          
          <!-- Example prompts -->
          <div class="ds-example-prompts">
            <h4 class="ds-examples-title">Try these examples:</h4>
            <div class="ds-examples-grid">
              <button 
                v-for="example in examplePrompts" 
                :key="example.text"
                @click="sendExampleMessage(example.text)"
                class="ds-example-btn"
                :disabled="isLoading"
              >
                <Icon :name="example.icon" class="ds-example-icon" />
                {{ example.text }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Message List -->
      <div v-for="(message, index) in messages" :key="index" class="ds-message-wrapper">
        <div :class="['ds-message', `ds-message-${message.role}`]">
          <!-- Message Header -->
          <div class="ds-message-header">
            <div class="ds-message-avatar">
              <Icon 
                :name="message.role === 'user' ? 'mdi:account' : 'mdi:robot'" 
                class="ds-avatar-icon" 
              />
            </div>
            <div class="ds-message-meta">
              <span class="ds-message-role">
                {{ message.role === 'user' ? 'You' : 'AI Assistant' }}
              </span>
              <span class="ds-message-time">
                {{ formatTime(message.timestamp) }}
              </span>
            </div>
            
            <!-- Content Type Badge -->
            <div v-if="message.role === 'assistant'" class="ds-content-type-badge">
              <Icon :name="formatMessage(message).icon" class="ds-badge-icon" />
              {{ formatMessage(message).displayName }}
            </div>
          </div>

          <!-- Message Content -->
          <div class="ds-message-content">
            <!-- Use appropriate renderer based on content type -->
            <component 
              :is="getMessageRenderer(message)"
              :content="getMessageContent(message)"
              :metadata="message.metadata"
            />
          </div>

          <!-- Tool Calls Display -->
          <div v-if="hasToolCalls(message)" class="ds-tool-calls-section">
            <div class="ds-tool-calls-header">
              <Icon name="mdi:tools" class="ds-tools-icon" />
              <span class="ds-tools-title">Tool Calls ({{ getToolCalls(message).length }})</span>
            </div>
            <div class="ds-tool-calls-list">
              <div 
                v-for="(toolCall, toolIndex) in getToolCalls(message)" 
                :key="toolIndex"
                class="ds-tool-call-item"
              >
                <Icon name="mdi:function" class="ds-tool-call-icon" />
                <span class="ds-tool-call-name">{{ toolCall.tool }}</span>
                <div class="ds-tool-call-params">
                  {{ Object.keys(toolCall.parameters || {}).join(', ') }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="ds-loading-message">
        <div class="ds-loading-content">
          <div class="ds-loading-spinner"></div>
          <span class="ds-loading-text">AI is thinking...</span>
        </div>
      </div>
    </div>

    <!-- Input Section -->
    <div class="ds-input-section">
      <!-- Error Display -->
      <div v-if="error" class="ds-error-banner">
        <Icon name="mdi:alert-circle" class="ds-error-icon" />
        <span class="ds-error-text">{{ error }}</span>
        <button @click="error = null" class="ds-error-close">×</button>
      </div>

      <!-- Chat Input -->
      <div class="ds-chat-input">
        <div class="ds-input-wrapper">
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="handleEnterKey"
            @input="handleInput"
            placeholder="Ask me anything... I can help with calculations, weather, code, search, and more!"
            class="ds-input-field"
            rows="1"
            :disabled="isLoading"
          ></textarea>
          
          <div class="ds-input-actions">
            <!-- Intent Preview -->
            <div v-if="detectedIntent" class="ds-intent-preview">
              <Icon :name="getIntentIcon(detectedIntent)" class="ds-intent-icon" />
              <span class="ds-intent-text">{{ formatIntentName(detectedIntent) }}</span>
            </div>
            
            <button 
              @click="sendMessage"
              :disabled="!inputMessage.trim() || isLoading"
              class="ds-send-btn"
            >
              <Icon name="mdi:send" class="ds-send-icon" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useMultimodalChat } from '../../composables/useMultimodalChat.ts'

// Import renderer components
import DigiSetuContentRenderer from './DigiSetuContentRenderer.vue'
import DigiSetuVisionRenderer from './DigiSetuVisionRenderer.vue'
import DigiSetuAudioRenderer from './DigiSetuAudioRenderer.vue'
import DigiSetuToolRenderer from './DigiSetuToolRenderer.vue'
import DigiSetuSearchRenderer from './DigiSetuSearchRenderer.vue'

// Use multimodal chat composable
const {
  messages,
  isLoading,
  error,
  lastAssistantMessage,
  conversationStats,
  sendMessage: sendChatMessage,
  getCapabilities,
  testIntent,
  clearConversation: clearChat,
  formatMessage,
  hasToolCalls,
  getToolCalls,
  exportConversation: exportChat
} = useMultimodalChat()

// Local state
const inputMessage = ref('')
const showCapabilities = ref(false)
const capabilities = ref(null)
const detectedIntent = ref(null)
const messagesContainer = ref(null)

// Example prompts
const examplePrompts = [
  { text: 'generate audio explaining bubble sorting', icon: 'mdi:volume-high' },
  { text: 'what is 25 * 4 + 12', icon: 'mdi:calculator' },
  { text: 'weather in Paris', icon: 'mdi:weather-cloudy' },
  { text: 'search for latest AI news', icon: 'mdi:web' },
  { text: 'generate Python code for fibonacci', icon: 'mdi:code-braces' },
  { text: 'analyze this data: [1,2,3,4,5]', icon: 'mdi:chart-line' }
]

// Methods
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  detectedIntent.value = null
  
  await sendChatMessage(message)
  scrollToBottom()
}

const sendExampleMessage = async (message) => {
  inputMessage.value = message
  await sendMessage()
}

const handleEnterKey = (event) => {
  if (event.shiftKey) {
    // Allow new line with Shift+Enter
    return
  }
  sendMessage()
}

const handleInput = async () => {
  // Auto-resize textarea
  const textarea = event.target
  textarea.style.height = 'auto'
  textarea.style.height = textarea.scrollHeight + 'px'
  
  // Detect intent for preview
  if (inputMessage.value.trim().length > 10) {
    const intentResult = await testIntent(inputMessage.value)
    detectedIntent.value = intentResult?.detected_intent || null
  } else {
    detectedIntent.value = null
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const getMessageRenderer = (message) => {
  if (message.role === 'user') {
    return DigiSetuContentRenderer
  }
  
  const contentType = message.metadata?.content_type || 'text'
  
  switch (contentType) {
    case 'vision':
      return DigiSetuVisionRenderer
    case 'audio_transcription':
    case 'audio_analysis':
      return DigiSetuAudioRenderer
    case 'tool':
    case 'batch_tools':
      return DigiSetuToolRenderer
    case 'search':
    case 'news':
      return DigiSetuSearchRenderer
    default:
      return DigiSetuContentRenderer
  }
}

const getMessageContent = (message) => {
  if (message.role === 'user') {
    return message.content
  }
  
  // For assistant messages, always return the content as string
  // The metadata will be handled by the appropriate renderer
  return message.content || ''
}

const clearConversation = () => {
  clearChat()
  detectedIntent.value = null
  inputMessage.value = ''
}

const exportConversation = () => {
  exportChat()
}

// Utility functions
const getCapabilityIcon = (capability) => {
  const icons = {
    vision: 'mdi:eye',
    audio: 'mdi:microphone',
    tools: 'mdi:tools',
    search: 'mdi:web',
    intent_detection: 'mdi:brain'
  }
  return icons[capability] || 'mdi:help-circle'
}

const formatCapabilityName = (capability) => {
  return capability.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getIntentIcon = (intent) => {
  const icons = {
    audio_generation: 'mdi:volume-high',
    calculation: 'mdi:calculator',
    weather: 'mdi:weather-cloudy',
    code_generation: 'mdi:code-braces',
    web_search: 'mdi:web',
    data_analysis: 'mdi:chart-line'
  }
  return icons[intent] || 'mdi:lightbulb'
}

const formatIntentName = (intent) => {
  return intent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

// Lifecycle
onMounted(async () => {
  capabilities.value = await getCapabilities()
})

// Watch for new messages and scroll
watch(messages, () => {
  scrollToBottom()
}, { deep: true })
</script>

<style scoped>
@reference "tailwindcss";
.ds-enhanced-chat {
  @apply flex flex-col h-full max-h-screen bg-gray-50;
}

.ds-chat-header {
  @apply flex justify-between items-center p-4 bg-white border-b border-gray-200;
}

.ds-header-info {
  @apply flex items-center gap-3;
}

.ds-chat-icon {
  @apply w-8 h-8 text-blue-600;
}

.ds-chat-title {
  @apply text-lg font-semibold text-gray-900;
}

.ds-chat-subtitle {
  @apply text-sm text-gray-500;
}

.ds-header-actions {
  @apply flex gap-2;
}

.ds-header-btn {
  @apply flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors;
}

.ds-btn-icon {
  @apply w-4 h-4;
}

.ds-capabilities-panel {
  @apply p-4 bg-blue-50 border-b border-blue-200;
}

.ds-capabilities-header {
  @apply flex justify-between items-center mb-4;
}

.ds-capabilities-title {
  @apply font-semibold text-blue-900;
}

.ds-close-btn {
  @apply p-1 text-blue-600 hover:text-blue-800 rounded;
}

.ds-close-icon {
  @apply w-5 h-5;
}

.ds-capabilities-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.ds-capability-card {
  @apply p-3 bg-white rounded-lg border border-blue-200;
}

.ds-capability-header {
  @apply flex items-center gap-2 mb-2;
}

.ds-capability-icon {
  @apply w-5 h-5 text-blue-600;
}

.ds-capability-name {
  @apply font-medium text-gray-900;
}

.ds-capability-description {
  @apply text-sm text-gray-600 mb-2;
}

.ds-capability-details {
  @apply flex items-center gap-2 text-xs;
}

.ds-detail-label {
  @apply font-medium text-gray-500;
}

.ds-format-tags {
  @apply flex gap-1 flex-wrap;
}

.ds-format-tag, .ds-more-tag {
  @apply px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs;
}

.ds-tool-count {
  @apply text-blue-600 font-medium;
}

.ds-conversation-stats {
  @apply p-3 bg-white border-b border-gray-200;
}

.ds-stats-grid {
  @apply flex gap-6;
}

.ds-stat-item {
  @apply flex items-center gap-2;
}

.ds-stat-icon {
  @apply w-4 h-4 text-gray-500;
}

.ds-stat-value {
  @apply font-semibold text-gray-900;
}

.ds-stat-label {
  @apply text-sm text-gray-500;
}

.ds-messages-container {
  @apply flex-1 overflow-y-auto p-4 space-y-4;
}

.ds-welcome-message {
  @apply flex justify-center items-center min-h-96;
}

.ds-welcome-content {
  @apply text-center max-w-2xl;
}

.ds-welcome-icon {
  @apply w-16 h-16 mx-auto mb-4 text-blue-600;
}

.ds-welcome-title {
  @apply text-xl font-semibold text-gray-900 mb-2;
}

.ds-welcome-text {
  @apply text-gray-600 mb-6;
}

.ds-example-prompts {
  @apply space-y-3;
}

.ds-examples-title {
  @apply font-medium text-gray-900 mb-3;
}

.ds-examples-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-2;
}

.ds-example-btn {
  @apply flex items-center gap-2 p-3 text-left text-sm text-gray-700 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors disabled:opacity-50;
}

.ds-example-icon {
  @apply w-4 h-4 text-blue-600;
}

.ds-message-wrapper {
  @apply space-y-2;
}

.ds-message {
  @apply bg-white rounded-lg border border-gray-200 p-4;
}

.ds-message-user {
  @apply bg-blue-50 border-blue-200;
}

.ds-message-header {
  @apply flex items-center gap-3 mb-3;
}

.ds-message-avatar {
  @apply w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center;
}

.ds-avatar-icon {
  @apply w-5 h-5 text-gray-600;
}

.ds-message-meta {
  @apply flex-1;
}

.ds-message-role {
  @apply font-medium text-gray-900;
}

.ds-message-time {
  @apply text-xs text-gray-500 ml-2;
}

.ds-content-type-badge {
  @apply flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs;
}

.ds-badge-icon {
  @apply w-3 h-3;
}

.ds-message-content {
  @apply space-y-2;
}

.ds-tool-calls-section {
  @apply mt-3 pt-3 border-t border-gray-200;
}

.ds-tool-calls-header {
  @apply flex items-center gap-2 mb-2;
}

.ds-tools-icon {
  @apply w-4 h-4 text-green-600;
}

.ds-tools-title {
  @apply text-sm font-medium text-gray-700;
}

.ds-tool-calls-list {
  @apply space-y-1;
}

.ds-tool-call-item {
  @apply flex items-center gap-2 p-2 bg-green-50 rounded text-sm;
}

.ds-tool-call-icon {
  @apply w-3 h-3 text-green-600;
}

.ds-tool-call-name {
  @apply font-medium text-green-800;
}

.ds-tool-call-params {
  @apply text-green-600 text-xs;
}

.ds-loading-message {
  @apply flex justify-center;
}

.ds-loading-content {
  @apply flex items-center gap-3 p-4 bg-white rounded-lg border border-gray-200;
}

.ds-loading-spinner {
  @apply w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin;
}

.ds-loading-text {
  @apply text-gray-600;
}

.ds-input-section {
  @apply p-4 bg-white border-t border-gray-200;
}

.ds-error-banner {
  @apply flex items-center gap-2 p-3 mb-3 bg-red-50 border border-red-200 rounded-lg text-red-800;
}

.ds-error-icon {
  @apply w-5 h-5 text-red-500;
}

.ds-error-text {
  @apply flex-1;
}

.ds-error-close {
  @apply text-red-500 hover:text-red-700 font-bold text-lg;
}

.ds-chat-input {
  @apply space-y-2;
}

.ds-input-wrapper {
  @apply flex gap-2 items-end;
}

.ds-input-field {
  @apply flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none min-h-12 max-h-32;
}

.ds-input-actions {
  @apply flex flex-col gap-2;
}

.ds-intent-preview {
  @apply flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs;
}

.ds-intent-icon {
  @apply w-3 h-3;
}

.ds-intent-text {
  @apply font-medium;
}

.ds-send-btn {
  @apply p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.ds-send-icon {
  @apply w-5 h-5;
}
</style>
