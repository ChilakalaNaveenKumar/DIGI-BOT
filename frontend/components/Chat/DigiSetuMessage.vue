<template>
  <div class="ds-message" :class="messageClasses">
    <!-- User Message -->
    <div v-if="message.role === 'user'" class="ds-user-message">
      <div class="ds-message-content">
        <div class="ds-message-text">{{ message.content }}</div>
        <div v-if="message.files && message.files.length > 0" class="ds-message-files">
          <div v-for="file in message.files" :key="file.id" class="ds-file-attachment">
            <Paperclip class="w-4 h-4" />
            <span>{{ file.name }}</span>
          </div>
        </div>
      </div>
      <div class="ds-message-avatar ds-user-avatar">
        <User class="w-4 h-4" />
      </div>
    </div>

    <!-- Assistant Message -->
    <div v-else class="ds-assistant-message">
      <div class="ds-message-avatar ds-assistant-avatar">
        <div class="ds-ai-logo">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="20" height="20" rx="4" fill="currentColor"/>
            <path d="M5 7h10v1H5V7zm0 2h10v1H5V9zm0 2h8v1H5v-1z" fill="white"/>
            <circle cx="13" cy="13" r="2" fill="var(--ds-secondary)"/>
          </svg>
        </div>
      </div>

      <div class="ds-message-content">
        <!-- Provider Badge -->
        <div v-if="message.provider" class="ds-provider-badge">
          <component :is="getProviderIcon(message.provider)" class="w-3 h-3" />
          <span>{{ getProviderName(message.provider) }}</span>
        </div>

        <!-- Activity Streaming -->
        <DigiSetuActivityStream 
          v-if="isLoading && currentActivity"
          :activity="currentActivity"
          :provider="message.provider"
        />

        <!-- Thought Process (Real AI Reasoning) -->
                <DigiSetuThoughtProcess
          v-if="thoughtSteps.length > 0 || isLoading"
          :thought-steps="thoughtSteps"
          :is-thinking="isLoading"
          :auto-expand="false"
        />

        <!-- Reasoning Display (Legacy) -->
        <DigiSetuReasoning 
          v-if="reasoningParts.length > 0"
          :reasoning-parts="reasoningParts"
          :is-loading="isLoading"
        />

        <!-- Tool Calling Stepper -->
        <DigiSetuToolStepper
          v-if="toolParts.length > 0"
          :tool-parts="toolParts"
          :is-loading="isLoading"
        />

        <!-- Message Content - Smart Content Detection -->
        <div v-if="message.content" class="ds-message-text-content">
          <DigiSetuContentRenderer
            :content="cleanMessageContent(message.content)"
            :content-type="contentType"
            :provider="message.provider"
          />
        </div>

        <!-- Multimodal Content -->
        <div v-if="multimodalParts.length > 0" class="ds-multimodal-content">
          <div
            v-for="(part, index) in multimodalParts"
            :key="`multimodal-${index}`"
            class="ds-multimodal-placeholder"
          >
            <div class="ds-placeholder-content">
              <Image class="w-6 h-6" />
              <span>{{ part.type || 'Multimodal Content' }}</span>
            </div>
          </div>
        </div>

        <!-- Message Actions -->
        <div v-if="!isLoading" class="ds-message-actions">
          <button class="ds-action-btn" @click="copyMessage" title="Copy message">
            <Copy class="w-4 h-4" />
          </button>
          <button class="ds-action-btn" @click="likeMessage" title="Like message">
            <ThumbsUp class="w-4 h-4" />
          </button>
          <button class="ds-action-btn" @click="regenerateMessage" title="Regenerate">
            <RotateCcw class="w-4 h-4" />
          </button>
          <button class="ds-action-btn" @click="shareMessage" title="Share">
            <Share class="w-4 h-4" />
          </button>
        </div>

        <!-- Message Metadata -->
        <div v-if="!isLoading" class="ds-message-meta">
          <span class="ds-message-time">{{ formatTime(message.timestamp) }}</span>
          <span v-if="message.model" class="ds-message-model">{{ message.model }}</span>
          <span v-if="message.tokens" class="ds-message-tokens">{{ message.tokens }} tokens</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  User, Paperclip, Copy, ThumbsUp, RotateCcw, Share,
  Brain, Zap, Globe, Image
} from 'lucide-vue-next'

// Import required components
import DigiSetuActivityStream from './DigiSetuActivityStream.vue'
import DigiSetuReasoning from './DigiSetuReasoning.vue'
import DigiSetuToolStepper from './DigiSetuToolStepper.vue'
import DigiSetuContentRenderer from './DigiSetuContentRenderer.vue'
import { useSimpleContentRouter } from '~/composables/useSimpleContentRouter'
import DigiSetuThoughtProcess from './DigiSetuThoughtProcess.vue'

const { cleanContent, detectContentType: detectContentTypeFromRouter } = useSimpleContentRouter()

const props = defineProps({
  message: {
    type: Object,
    required: true
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
  'copy',
  'like', 
  'regenerate',
  'share'
])

// Computed properties for message parts
const textParts = computed(() => {
  if (!props.message.parts) {
    // Fallback for simple content
    return props.message.content ? [{ text: props.message.content, type: 'text' }] : []
  }
  return props.message.parts.filter(part => part.type === 'text' || part.type === 'content')
})

const reasoningParts = computed(() => {
  if (!props.message.parts) return []
  return props.message.parts.filter(part => part.type === 'reasoning' || part.type === 'thinking')
})

const toolParts = computed(() => {
  if (!props.message.parts) return []
  return props.message.parts.filter(part => 
    part.type === 'tool_call' || 
    part.type === 'tool_result' || 
    part.type === 'tool_loading' ||
    part.type === 'tool_executing' ||
    part.type === 'tool_error'
  )
})

const multimodalParts = computed(() => {
  if (!props.message.parts) return []
  return props.message.parts.filter(part => 
    part.type === 'image' || 
    part.type === 'audio' || 
    part.type === 'video' ||
    part.type === 'file'
  )
})

const thoughtSteps = computed(() => {
  try {
    // Get thought steps from activities array (streaming format)
    const steps = []
    
    // From activities array (new streaming format) - most common case
    if (props.message?.activities && Array.isArray(props.message.activities)) {
      for (let i = 0; i < props.message.activities.length; i++) {
        const activity = props.message.activities[i]
        try {
          // Handle both string and object formats
          if (typeof activity === 'string' && activity.trim()) {
            steps.push({
              content: activity.trim(),
              timestamp: props.message.timestamp || new Date().toISOString(),
              isLoading: false
            })
          } else if (activity && typeof activity === 'object' && activity.content) {
            steps.push({
              content: String(activity.content || '').trim(),
              timestamp: activity.timestamp || props.message.timestamp || new Date().toISOString(),
              isLoading: Boolean(activity.isLoading)
            })
          }
        } catch (activityError) {
          // Skip problematic activities
          continue
        }
      }
    }
    
    // Fallback: From reasoning field (legacy format)
    if (steps.length === 0 && props.message?.reasoning) {
      try {
        const reasoningText = String(props.message.reasoning || '')
        if (reasoningText.trim()) {
          const lines = reasoningText.split('\n').filter(line => line.trim())
          for (const line of lines) {
            if (line.trim()) {
              steps.push({
                content: line.trim(),
                timestamp: props.message.timestamp || new Date().toISOString(),
                isLoading: false
              })
            }
          }
        }
      } catch (reasoningError) {
        // Skip reasoning if it causes issues
      }
    }
    
    // From message parts (if using parts structure)
    if (steps.length === 0 && props.message?.parts && Array.isArray(props.message.parts)) {
      try {
        const activityParts = props.message.parts.filter(part => 
          part && (part.type === 'activity' || part.type === 'thinking' || part.type === 'reasoning')
        )
        for (const part of activityParts) {
          if (part?.content && String(part.content).trim()) {
            steps.push({
              content: String(part.content).trim(),
              timestamp: part.timestamp || props.message.timestamp || new Date().toISOString(),
              isLoading: false
            })
          }
        }
      } catch (partsError) {
        // Skip parts if they cause issues
      }
    }
    
    return steps
  } catch (error) {
    console.error('Error in thoughtSteps computed:', error)
    return []
  }
})

// Clean message content by removing keywords but keeping AI formatting
const cleanMessageContent = (content) => {
  if (!content) return ''
  return cleanContent(content)
}

// Detect content type from accumulated content - cached to prevent excessive recalculation
const contentType = computed(() => {
  if (!props.message.content) return 'text'
  
  // Always try to detect keywords first, even during streaming
  const detection = detectContentTypeFromRouter(props.message.content)
  
  // Debug logging for content detection issues
  if (process.client && (props.message.content.includes('💻') || props.message.content.includes('📊') || props.message.content.includes('```'))) {
    console.log('Content detection:', {
      contentLength: props.message.content.length,
      hasCodeKeyword: props.message.content.includes('💻 DIGI_CODE_START'),
      hasDiagramKeyword: props.message.content.includes('📊 DIGI_DIAGRAM_START'),
      hasCodeBlock: props.message.content.includes('```'),
      detectedType: detection.type,
      confidence: detection.confidence,
      isStreaming: props.message.isStreaming
    })
  }
  
  // If we found a keyword-based detection, use it immediately
  if (detection.confidence >= 1.0) {
    return detection.type || 'text'
  }
  
  // For pattern-based detection, wait until we have more content during streaming
  if (props.message.isStreaming && props.message.content.length < 100) {
    // But still return the detection if we found something
    return detection.type || 'text'
  }
  
  return detection.type || 'text'
})

const messageClasses = computed(() => {
  return {
    'ds-message-user': props.message.role === 'user',
    'ds-message-assistant': props.message.role === 'assistant',
    'ds-message-loading': props.isLoading,
    'ds-message-error': props.message.error
  }
})

// Provider utilities
const getProviderIcon = (provider) => {
  const iconMap = {
    'openai': Brain,
    'anthropic': Zap,
    'grok': Globe
  }
  return iconMap[provider] || Brain
}

const getProviderName = (provider) => {
  const nameMap = {
    'openai': 'GPT-5',
    'anthropic': 'Claude-4',
    'grok': 'Grok-4'
  }
  return nameMap[provider] || provider
}

// Methods
const copyMessage = () => {
  emit('copy', props.message)
}

const likeMessage = () => {
  emit('like', props.message)
}

const regenerateMessage = () => {
  emit('regenerate', props.message)
}

const shareMessage = () => {
  emit('share', props.message)
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = (now - date) / (1000 * 60)
  
  if (diffInMinutes < 1) {
    return 'Just now'
  } else if (diffInMinutes < 60) {
    return `${Math.floor(diffInMinutes)}m ago`
  } else if (diffInMinutes < 1440) { // 24 hours
    return `${Math.floor(diffInMinutes / 60)}h ago`
  } else {
    return date.toLocaleDateString()
  }
}
</script>

<style scoped>
.ds-message {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-4);
  animation: ds-slide-up 0.3s ease-out;
}

/* === USER MESSAGE === */
.ds-user-message {
  display: flex;
  align-items: flex-start;
  gap: var(--ds-space-3);
  justify-content: flex-end;
}

.ds-user-message .ds-message-content {
  background: var(--ds-primary);
  color: white;
  padding: var(--ds-space-4) var(--ds-space-5);
  border-radius: var(--ds-radius-2xl) var(--ds-radius-2xl) var(--ds-radius-sm) var(--ds-radius-2xl);
  max-width: 70%;
  box-shadow: var(--ds-shadow-sm);
}

.ds-user-avatar {
  background: var(--ds-primary);
  color: white;
}

/* === ASSISTANT MESSAGE === */
.ds-assistant-message {
  display: flex;
  align-items: flex-start;
  gap: var(--ds-space-3);
}

.ds-assistant-message .ds-message-content {
  flex: 1;
  min-width: 0;
}

.ds-assistant-avatar {
  background: var(--ds-surface-secondary);
  color: var(--ds-primary);
  border: 1px solid var(--ds-border-primary);
}

/* === MESSAGE AVATAR === */
.ds-message-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--ds-radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--ds-transition-fast);
}

.ds-ai-logo {
  color: var(--ds-primary);
}

/* === PROVIDER BADGE === */
.ds-provider-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--ds-space-1);
  padding: var(--ds-space-1) var(--ds-space-2);
  background: color-mix(in srgb, var(--ds-primary) 10%, transparent);
  color: var(--ds-primary);
  border-radius: var(--ds-radius-full);
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-medium);
  margin-bottom: var(--ds-space-3);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

/* === MESSAGE TEXT === */
.ds-message-text {
  font-size: var(--ds-text-base);
  line-height: var(--ds-leading-relaxed);
  word-wrap: break-word;
}

.ds-message-text-content {
  margin-bottom: var(--ds-space-4);
}

/* === FILE ATTACHMENTS === */
.ds-message-files {
  margin-top: var(--ds-space-3);
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-2);
}

.ds-file-attachment {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--ds-radius-md);
  font-size: var(--ds-text-sm);
}

/* === MULTIMODAL CONTENT === */
.ds-multimodal-content {
  margin-bottom: var(--ds-space-4);
}

/* === MESSAGE ACTIONS === */
.ds-message-actions {
  display: flex;
  align-items: center;
  gap: var(--ds-space-1);
  margin-top: var(--ds-space-3);
  opacity: 0;
  transition: opacity var(--ds-transition-fast);
}

.ds-message:hover .ds-message-actions {
  opacity: 1;
}

.ds-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-2);
  background: none;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
}

.ds-action-btn:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

/* === MESSAGE METADATA === */
.ds-message-meta {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  margin-top: var(--ds-space-2);
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-message-time {
  font-weight: var(--ds-font-medium);
}

.ds-message-model,
.ds-message-tokens {
  padding: 2px var(--ds-space-2);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-sm);
}

/* === LOADING STATE === */
.ds-message-loading .ds-message-content {
  position: relative;
}

.ds-message-loading .ds-message-content::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    var(--ds-primary) 50%, 
    transparent 100%
  );
  animation: ds-loading-bar 2s ease-in-out infinite;
}

@keyframes ds-loading-bar {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* === ERROR STATE === */
.ds-message-error .ds-message-content {
  border-left: 3px solid var(--ds-danger);
  background: color-mix(in srgb, var(--ds-danger) 5%, transparent);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-user-message .ds-message-content {
    max-width: 85%;
  }
  
  .ds-message-actions {
    opacity: 1; /* Always show on mobile */
  }
  
  .ds-action-btn {
    padding: var(--ds-space-3);
  }
}

/* === ACCESSIBILITY === */
.ds-action-btn:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === HIGH CONTRAST MODE === */
@media (prefers-contrast: high) {
  .ds-user-message .ds-message-content {
    border: 2px solid var(--ds-primary-dark);
  }
  
  .ds-assistant-avatar {
    border-width: 2px;
  }
}

/* === MULTIMODAL PLACEHOLDER === */
.ds-multimodal-placeholder {
  padding: var(--ds-space-3);
  border: 1px dashed var(--ds-border-secondary);
  border-radius: var(--ds-radius-md);
  margin: var(--ds-space-2) 0;
}

.ds-placeholder-content {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-text-secondary);
  font-size: var(--ds-text-sm);
}

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) {
  .ds-message {
    animation: none;
  }
  
  .ds-message-loading .ds-message-content::after {
    animation: none;
  }
}
</style>
