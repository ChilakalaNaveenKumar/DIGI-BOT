<template>
  <div class="ds-input-container">
    <div class="ds-input-wrapper" :class="{ 'ds-input-focused': isFocused, 'ds-input-disabled': isLoading }">
      <!-- File Attachments Preview -->
      <div v-if="attachedFiles.length > 0" class="ds-attachments-preview">
        <div 
          v-for="(file, index) in attachedFiles" 
          :key="index"
          class="ds-attachment-item"
        >
          <div class="ds-attachment-icon">
            <component :is="getFileIcon(file.type)" class="w-4 h-4" />
          </div>
          <div class="ds-attachment-info">
            <span class="ds-attachment-name">{{ file.name }}</span>
            <span class="ds-attachment-size">{{ formatFileSize(file.size) }}</span>
          </div>
          <button 
            class="ds-attachment-remove"
            @click="removeFile(index)"
            :disabled="isLoading"
          >
            <X class="w-3 h-3" />
          </button>
        </div>
      </div>

      <!-- Main Input Area -->
      <div class="ds-input-main">
        <!-- Text Input -->
        <div class="ds-input-field-wrapper">
          <textarea
            ref="textareaRef"
            v-model="inputValue"
            :placeholder="placeholder"
            :disabled="isLoading"
            class="ds-input-field"
            rows="1"
            @focus="handleFocus"
            @blur="handleBlur"
            @keydown="handleKeydown"
            @input="handleInput"
          />
          
          <!-- Input Actions -->
          <div class="ds-input-actions">
            <!-- File Upload -->
            <button 
              class="ds-input-action-btn"
              @click="triggerFileUpload"
              :disabled="isLoading"
              title="Attach files"
            >
              <Paperclip class="w-4 h-4" />
            </button>

            <!-- Voice Input -->
            <button 
              class="ds-input-action-btn"
              @click="toggleVoiceInput"
              :disabled="isLoading"
              :class="{ 'ds-recording': isRecording }"
              title="Voice input"
            >
              <Mic v-if="!isRecording" class="w-4 h-4" />
              <MicOff v-else class="w-4 h-4" />
            </button>

            <!-- Send Button -->
            <button 
              class="ds-send-btn"
              @click="handleSend"
              :disabled="!canSend"
              title="Send message"
            >
              <Send class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div v-if="showQuickActions" class="ds-quick-actions">
          <button 
            v-for="action in quickActions"
            :key="action.id"
            class="ds-quick-action-btn"
            @click="insertQuickAction(action)"
            :disabled="isLoading"
          >
            <component :is="action.icon" class="w-3 h-3" />
            <span>{{ action.label }}</span>
          </button>
        </div>
      </div>

      <!-- Input Footer -->
      <div class="ds-input-footer">
        <div class="ds-input-info">
          <span class="ds-character-count">{{ characterCount }}/{{ maxCharacters }}</span>
          <span v-if="isLoading" class="ds-loading-indicator">
            <Loader2 class="w-3 h-3 animate-spin" />
            AI is processing...
          </span>
        </div>
        
        <div class="ds-input-shortcuts">
          <span class="ds-shortcut">⏎ Send</span>
          <span class="ds-shortcut">⇧⏎ New line</span>
        </div>
      </div>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt,.md"
      class="ds-hidden-file-input"
      @change="handleFileSelect"
    />

    <!-- Voice Recording Modal -->
    <div v-if="isRecording" class="ds-voice-modal">
      <div class="ds-voice-content">
        <div class="ds-voice-animation">
          <div class="ds-voice-wave"></div>
          <div class="ds-voice-wave"></div>
          <div class="ds-voice-wave"></div>
        </div>
        <p class="ds-voice-text">Listening...</p>
        <div class="ds-voice-actions">
          <button class="ds-voice-cancel" @click="cancelVoiceInput">
            Cancel
          </button>
          <button class="ds-voice-stop" @click="stopVoiceInput">
            Stop
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { 
  Send, Paperclip, Mic, MicOff, X, Loader2,
  FileText, Image, Video, Music, File,
  Code, Calculator, Calendar, MapPin
} from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Ask me anything, upload files, or request interactive content...'
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  maxCharacters: {
    type: Number,
    default: 10000
  }
})

const emit = defineEmits([
  'update:modelValue',
  'send',
  'file-upload'
])

// Reactive state
const textareaRef = ref(null)
const fileInputRef = ref(null)
const isFocused = ref(false)
const isRecording = ref(false)
const attachedFiles = ref([])
const showQuickActions = ref(false)

// Input value with v-model support
const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Computed properties
const characterCount = computed(() => inputValue.value.length)

const canSend = computed(() => {
  return !props.isLoading && 
         (inputValue.value.trim().length > 0 || attachedFiles.value.length > 0) &&
         characterCount.value <= props.maxCharacters
})

// Quick actions
const quickActions = ref([
  { id: 'code', label: 'Code', icon: Code },
  { id: 'calculate', label: 'Calculate', icon: Calculator },
  { id: 'schedule', label: 'Schedule', icon: Calendar },
  { id: 'location', label: 'Location', icon: MapPin }
])

// Methods
const handleFocus = () => {
  isFocused.value = true
  showQuickActions.value = inputValue.value.length === 0
}

const handleBlur = () => {
  isFocused.value = false
  // Delay hiding quick actions to allow clicking
  setTimeout(() => {
    showQuickActions.value = false
  }, 200)
}

const handleInput = () => {
  // Auto-resize textarea
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 200) + 'px'
    }
  })
  
  // Show/hide quick actions
  showQuickActions.value = isFocused.value && inputValue.value.length === 0
}

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

const handleSend = () => {
  if (!canSend.value) return
  
  const messageData = {
    text: inputValue.value.trim(),
    files: attachedFiles.value.length > 0 ? [...attachedFiles.value] : null
  }
  
  emit('send', messageData)
  
  // Clear input
  inputValue.value = ''
  attachedFiles.value = []
  
  // Reset textarea height
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}

// File handling
const triggerFileUpload = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  
  // Validate files
  const validFiles = files.filter(file => {
    const maxSize = 50 * 1024 * 1024 // 50MB
    if (file.size > maxSize) {
      console.warn(`File ${file.name} is too large (max 50MB)`)
      return false
    }
    return true
  })
  
  attachedFiles.value.push(...validFiles)
  
  // Clear file input
  event.target.value = ''
  
  // Emit file upload event
  if (validFiles.length > 0) {
    emit('file-upload', validFiles)
  }
}

const removeFile = (index) => {
  attachedFiles.value.splice(index, 1)
}

const getFileIcon = (fileType) => {
  if (fileType.startsWith('image/')) return Image
  if (fileType.startsWith('video/')) return Video
  if (fileType.startsWith('audio/')) return Music
  if (fileType.includes('text') || fileType.includes('document')) return FileText
  return File
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Voice input
const toggleVoiceInput = () => {
  if (isRecording.value) {
    stopVoiceInput()
  } else {
    startVoiceInput()
  }
}

const startVoiceInput = () => {
  // Check for speech recognition support
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    console.warn('Speech recognition not supported')
    return
  }
  
  isRecording.value = true
  
  // Initialize speech recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  const recognition = new SpeechRecognition()
  
  recognition.continuous = true
  recognition.interimResults = true
  recognition.lang = 'en-US'
  
  recognition.onresult = (event) => {
    let transcript = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript
    }
    inputValue.value = transcript
  }
  
  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error)
    isRecording.value = false
  }
  
  recognition.onend = () => {
    isRecording.value = false
  }
  
  recognition.start()
}

const stopVoiceInput = () => {
  isRecording.value = false
}

const cancelVoiceInput = () => {
  isRecording.value = false
  inputValue.value = ''
}

// Quick actions
const insertQuickAction = (action) => {
  const templates = {
    code: 'Write a function that ',
    calculate: 'Calculate ',
    schedule: 'Schedule a meeting for ',
    location: 'Find information about '
  }
  
  inputValue.value = templates[action.id] || ''
  
  // Focus textarea
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.focus()
      textareaRef.value.setSelectionRange(inputValue.value.length, inputValue.value.length)
    }
  })
}

// Lifecycle
onMounted(() => {
  // Auto-focus on mount (optional)
  if (textareaRef.value) {
    textareaRef.value.focus()
  }
})

// Handle paste events for files
const handlePaste = (event) => {
  const items = event.clipboardData?.items
  if (!items) return
  
  const files = []
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.kind === 'file') {
      const file = item.getAsFile()
      if (file) files.push(file)
    }
  }
  
  if (files.length > 0) {
    attachedFiles.value.push(...files)
    emit('file-upload', files)
  }
}

onMounted(() => {
  document.addEventListener('paste', handlePaste)
})

onUnmounted(() => {
  document.removeEventListener('paste', handlePaste)
})
</script>

<style scoped>
.ds-input-container {
  position: relative;
}

.ds-input-wrapper {
  background: var(--ds-surface-primary);
  border: 2px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-2xl);
  transition: all var(--ds-transition-fast);
  overflow: hidden;
}

.ds-input-focused {
  border-color: var(--ds-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ds-primary) 10%, transparent);
}

.ds-input-disabled {
  opacity: 0.6;
  pointer-events: none;
}

/* === ATTACHMENTS PREVIEW === */
.ds-attachments-preview {
  padding: var(--ds-space-3) var(--ds-space-4) 0;
  border-bottom: 1px solid var(--ds-border-primary);
  display: flex;
  flex-wrap: wrap;
  gap: var(--ds-space-2);
}

.ds-attachment-item {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-lg);
  font-size: var(--ds-text-sm);
}

.ds-attachment-icon {
  color: var(--ds-text-muted);
}

.ds-attachment-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.ds-attachment-name {
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  truncate: true;
}

.ds-attachment-size {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-attachment-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-1);
  background: none;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  border-radius: var(--ds-radius-sm);
  transition: all var(--ds-transition-fast);
}

.ds-attachment-remove:hover {
  background: var(--ds-danger);
  color: white;
}

/* === MAIN INPUT === */
.ds-input-main {
  padding: var(--ds-space-4);
}

.ds-input-field-wrapper {
  display: flex;
  align-items: flex-end;
  gap: var(--ds-space-3);
}

.ds-input-field {
  flex: 1;
  min-height: 24px;
  max-height: 200px;
  padding: 0;
  border: none;
  outline: none;
  background: transparent;
  color: var(--ds-text-primary);
  font-family: inherit;
  font-size: var(--ds-text-base);
  line-height: var(--ds-leading-normal);
  resize: none;
  overflow-y: auto;
}

.ds-input-field::placeholder {
  color: var(--ds-text-muted);
}

.ds-input-field:disabled {
  opacity: 0.6;
}

/* === INPUT ACTIONS === */
.ds-input-actions {
  display: flex;
  align-items: center;
  gap: var(--ds-space-1);
}

.ds-input-action-btn {
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

.ds-input-action-btn:hover:not(:disabled) {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

.ds-input-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ds-recording {
  background: var(--ds-danger) !important;
  color: white !important;
  animation: ds-pulse 1s ease-in-out infinite;
}

.ds-send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-2);
  background: var(--ds-primary);
  color: white;
  border: none;
  border-radius: var(--ds-radius-lg);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-send-btn:hover:not(:disabled) {
  background: var(--ds-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--ds-shadow-md);
}

.ds-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* === QUICK ACTIONS === */
.ds-quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ds-space-2);
  margin-top: var(--ds-space-3);
  padding-top: var(--ds-space-3);
  border-top: 1px solid var(--ds-border-primary);
}

.ds-quick-action-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  color: var(--ds-text-secondary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-quick-action-btn:hover:not(:disabled) {
  background: var(--ds-surface-hover);
  border-color: var(--ds-primary);
  color: var(--ds-text-primary);
}

/* === INPUT FOOTER === */
.ds-input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-2) var(--ds-space-4);
  background: var(--ds-surface-secondary);
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-input-info {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-character-count {
  font-weight: var(--ds-font-medium);
}

.ds-loading-indicator {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-primary);
}

.ds-input-shortcuts {
  display: flex;
  gap: var(--ds-space-3);
}

.ds-shortcut {
  padding: 2px var(--ds-space-1);
  background: var(--ds-surface-primary);
  border-radius: var(--ds-radius-sm);
  font-family: var(--ds-font-mono);
}

/* === HIDDEN FILE INPUT === */
.ds-hidden-file-input {
  display: none;
}

/* === VOICE MODAL === */
.ds-voice-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--ds-z-modal);
}

.ds-voice-content {
  background: var(--ds-surface-primary);
  border-radius: var(--ds-radius-2xl);
  padding: var(--ds-space-8);
  text-align: center;
  box-shadow: var(--ds-shadow-xl);
  animation: ds-scale-in 0.2s ease-out;
}

.ds-voice-animation {
  display: flex;
  justify-content: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-4);
}

.ds-voice-wave {
  width: 4px;
  height: 20px;
  background: var(--ds-primary);
  border-radius: var(--ds-radius-full);
  animation: ds-voice-wave 1.5s ease-in-out infinite;
}

.ds-voice-wave:nth-child(2) {
  animation-delay: 0.2s;
}

.ds-voice-wave:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes ds-voice-wave {
  0%, 100% {
    height: 20px;
  }
  50% {
    height: 40px;
  }
}

.ds-voice-text {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  margin: 0 0 var(--ds-space-6) 0;
}

.ds-voice-actions {
  display: flex;
  gap: var(--ds-space-3);
  justify-content: center;
}

.ds-voice-cancel,
.ds-voice-stop {
  padding: var(--ds-space-3) var(--ds-space-6);
  border: none;
  border-radius: var(--ds-radius-lg);
  font-weight: var(--ds-font-medium);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-voice-cancel {
  background: var(--ds-surface-secondary);
  color: var(--ds-text-primary);
}

.ds-voice-cancel:hover {
  background: var(--ds-surface-hover);
}

.ds-voice-stop {
  background: var(--ds-primary);
  color: white;
}

.ds-voice-stop:hover {
  background: var(--ds-primary-dark);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-input-footer {
    flex-direction: column;
    gap: var(--ds-space-2);
    align-items: flex-start;
  }
  
  .ds-input-shortcuts {
    display: none;
  }
  
  .ds-quick-actions {
    flex-direction: column;
  }
  
  .ds-quick-action-btn {
    justify-content: center;
  }
}

/* === ACCESSIBILITY === */
.ds-input-action-btn:focus-visible,
.ds-send-btn:focus-visible,
.ds-quick-action-btn:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === ANIMATIONS === */
@keyframes ds-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) {
  .ds-recording {
    animation: none;
  }
  
  .ds-voice-wave {
    animation: none;
    height: 20px;
  }
}
</style>
