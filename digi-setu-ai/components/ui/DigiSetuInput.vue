<template>
  <div class="digi-setu-input-wrapper">
    <!-- Main Input Field -->
    <div class="digi-setu-input" :class="{ 'digi-setu-input--focused': isFocused }">
      <textarea
        ref="textareaRef"
        v-model="inputValue"
        class="input-field"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        @focus="handleFocus"
        @blur="handleBlur"
        @input="handleInput"
        @keydown="handleKeydown"
      />
      
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <button class="toolbar-btn toolbar-btn--icon" @click="$emit('add')">
            <Icon name="lucide:plus" :size="16" />
          </button>
          
          <!-- File Upload Button Only -->
          <UiFileUpload 
            ref="fileUploadRef"
            @files-uploaded="handleFilesUploaded"
            @files-changed="handleFilesChanged"
          />
          
          <button 
            class="toolbar-btn toolbar-btn--thinking" 
            :class="{ 'toolbar-btn--thinking-active': thinkingMode }"
            @click="toggleThinkingMode"
            title="Toggle thinking mode (shows Claude's reasoning process)"
          >
            <Icon name="lucide:brain" :size="16" />
            <span>{{ thinkingMode ? 'Thinking On' : 'Thinking' }}</span>
          </button>
        </div>
        
        <div class="toolbar-right">
          <div class="model-selector" @click="$emit('model-select')">
            <span>Digi Setu AI</span>
            <Icon name="lucide:chevron-down" :size="16" />
          </div>
          
          <button 
            class="toolbar-btn toolbar-btn--audio"
            :class="{ 'toolbar-btn--audio-active': isRecording, 'toolbar-btn--voice-mode': isVoiceMode }"
            @click="toggleRecording"
            :disabled="loading"
            :title="isRecording ? (isVoiceMode ? 'Stop voice conversation' : 'Stop recording') : 'Start voice conversation'"
          >
            <div v-if="isRecording && isVoiceMode" class="waveform-container">
              <div class="waveform">
                <div class="wave-bar" v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.1}s` }"></div>
              </div>
            </div>
            <Icon 
              v-else-if="isRecording"
              name="lucide:square" 
              :size="16"
              class="audio-icon audio-icon--stop"
            />
            <Icon 
              v-else
              name="lucide:mic" 
              :size="16"
              class="audio-icon"
            />
          </button>
          
          <button 
            class="send-btn"
            :disabled="!canSend"
            :class="{ 'send-btn--disabled': !canSend }"
            @click="handleSend"
          >
            <Icon 
              v-if="loading"
              name="lucide:loader" 
              :size="16"
              class="send-icon send-icon--loading"
            />
            <Icon 
              v-else
              name="lucide:arrow-up" 
              :size="16"
              class="send-icon"
            />
          </button>
        </div>
      </div>
      
      <!-- File Grid Below Toolbar -->
      <div v-if="attachedFiles.length > 0" class="attached-files-section">
        <div class="attached-files-grid">
          <div 
            v-for="file in attachedFiles" 
            :key="file.id"
            class="attached-file-card"
            :class="{ 
              'attached-file-card--uploading': file.status === 'uploading', 
              'attached-file-card--error': file.status === 'error',
              'attached-file-card--uploaded': file.status === 'uploaded'
            }"
          >
            <div class="attached-file-header">
              <Icon :name="getFileIcon(file.name)" :size="16" class="attached-file-icon" />
              <button 
                class="attached-file-remove-btn"
                @click="removeAttachedFile(file.id)"
                title="Remove file"
              >
                <Icon name="lucide:x" :size="10" />
              </button>
            </div>
            
            <div class="attached-file-content">
              <div class="attached-file-name" :title="file.name">{{ file.name }}</div>
              <div class="attached-file-size">{{ formatFileSize(file.size) }}</div>
            </div>
            
            <div class="attached-file-status">
              <div v-if="file.status === 'uploading'" class="status-indicator status-uploading">
                <Icon name="lucide:loader" :size="10" class="status-icon" />
              </div>
              <div v-else-if="file.status === 'uploaded'" class="status-indicator status-uploaded">
                <Icon name="lucide:check" :size="10" class="status-icon" />
              </div>
              <div v-else-if="file.status === 'error'" class="status-indicator status-error">
                <Icon name="lucide:x" :size="10" class="status-icon" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watchEffect, watch } from 'vue'

interface Props {
  modelValue?: string
  disabled?: boolean
  loading?: boolean
  placeholder?: string
}

interface FileItem {
  id: string
  name: string
  size: number
  file: File
  status: 'pending' | 'uploading' | 'uploaded' | 'error'
  vectorStoreFileId?: string
  error?: string
}

interface Emits {
  (e: 'update:modelValue' | 'send', value: string): void
  (e: 'add' | 'options' | 'upload' | 'model-select' | 'focus' | 'blur'): void
  (e: 'thinking-mode-changed', value: boolean): void
  (e: 'files-uploaded' | 'files-changed', files: FileItem[]): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  disabled: false,
  loading: false,
  placeholder: 'How can I help you today?'
})

const emit = defineEmits<Emits>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const fileUploadRef = ref()
const isFocused = ref(false)
const inputValue = ref(props.modelValue || '')
const attachedFiles = ref<FileItem[]>([])

// Thinking mode state
const thinkingMode = ref(false)

// Audio recording state
const isRecording = ref(false)
const speechTimeout = ref<NodeJS.Timeout | null>(null)
const isVoiceMode = ref(false)
const lastTranscript = ref('')

// Real-time speech recognition
const { 
  startListening: startDeepgram, 
  stopListening: stopDeepgram, 
  fullTranscript: deepgramTranscript,
  hasApiKey: hasDeepgramKey
} = useRealtimeSpeech()

const { 
  startListening: startWebSpeech, 
  stopListening: stopWebSpeech, 
  fullTranscript: webSpeechTranscript
} = useWebSpeechFallback()

const canSend = computed(() => {
  return inputValue.value.trim().length > 0 && !props.disabled && !props.loading
})

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  if (newValue !== undefined) {
    inputValue.value = newValue
  }
})

// Emit changes to parent
watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue)
})

const handleFocus = () => {
  isFocused.value = true
  emit('focus')
}

const handleBlur = () => {
  isFocused.value = false
  emit('blur')
}

const handleInput = () => {
  autoResize()
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

const handleSend = () => {
  const content = inputValue.value.trim()
  if (content && !props.disabled && !props.loading) {

    emit('send', content)
    inputValue.value = ''
    nextTick(() => {
      autoResize()
    })
  }
}

const autoResize = () => {
  if (process.client) {
    nextTick(() => {
      if (textareaRef.value) {
        textareaRef.value.style.height = 'auto'
        const newHeight = Math.min(textareaRef.value.scrollHeight, 120)
        textareaRef.value.style.height = newHeight + 'px'
      }
    })
  }
}

const focus = () => {
  textareaRef.value?.focus()
}

// File upload handlers
const handleFilesUploaded = (files: FileItem[]) => {
  attachedFiles.value = [...attachedFiles.value, ...files]
  emit('files-uploaded', files)
}

const handleFilesChanged = (files: FileItem[]) => {
  attachedFiles.value = files
  emit('files-changed', files)
}

const removeAttachedFile = (fileId: string) => {
  attachedFiles.value = attachedFiles.value.filter(f => f.id !== fileId)
  emit('files-changed', [...attachedFiles.value])
}

const getFileIcon = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase()
  
  switch (ext) {
    case 'pdf': return 'lucide:file-text'
    case 'docx': case 'doc': return 'lucide:file-text'
    case 'txt': case 'md': return 'lucide:file-text'
    case 'csv': case 'xlsx': case 'xls': return 'lucide:table'
    case 'json': case 'yaml': case 'yml': return 'lucide:braces'
    case 'py': case 'js': case 'ts': case 'html': case 'css': return 'lucide:code'
    case 'png': case 'jpg': case 'jpeg': case 'webp': return 'lucide:image'
    default: return 'lucide:file'
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Thinking mode toggle
const toggleThinkingMode = () => {
  thinkingMode.value = !thinkingMode.value
  // Emit thinking mode change to parent
  emit('thinking-mode-changed', thinkingMode.value)
}

// Audio recording methods
const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}



const startRecording = async () => {
  try {
    // Reset transcript tracking
    lastTranscript.value = ''
    inputValue.value = '' // Clear input for new recording
    
    // Try Deepgram first if API key is available
    if (hasDeepgramKey.value) {
      console.log('Starting Deepgram real-time transcription')
      const success = await startDeepgram()
      if (success) {
        isRecording.value = true
        isVoiceMode.value = true
        
        // Watch for Deepgram transcripts
        const stopWatcher = watch(deepgramTranscript, (newTranscript) => {
          if (newTranscript && newTranscript.trim()) {
            console.log('Deepgram transcript updated:', newTranscript)
            inputValue.value = newTranscript
            autoResize()
            
            // Auto-send after 2 seconds of no new transcription
            if (speechTimeout.value) {
              clearTimeout(speechTimeout.value)
            }
            speechTimeout.value = setTimeout(() => {
              if (inputValue.value.trim() && isVoiceMode.value) {
                console.log(`Auto-sending Deepgram message: "${inputValue.value.trim()}"`)
                handleSend()
                stopWatcher() // Stop watching after sending
              }
            }, 2000)
          }
        }, { immediate: true })
        
        return
      } else {
        console.log('Deepgram failed, falling back to Web Speech API')
      }
    }
    
    // Fallback to Web Speech API
    console.log('Starting Web Speech API transcription')
    const success = await startWebSpeech()
    if (success) {
      isRecording.value = true
      isVoiceMode.value = true
      
              // Watch for Web Speech transcripts
        const stopWatcher = watch(webSpeechTranscript, (newTranscript) => {
          if (newTranscript && newTranscript.trim()) {
            console.log('Web Speech transcript updated:', newTranscript)
            inputValue.value = newTranscript
            autoResize()
            
            // Auto-send after 2 seconds of no new transcription
            if (speechTimeout.value) {
              clearTimeout(speechTimeout.value)
            }
            speechTimeout.value = setTimeout(() => {
              if (inputValue.value.trim() && isVoiceMode.value) {
                console.log(`Auto-sending Web Speech message: "${inputValue.value.trim()}"`)
                handleSend()
                stopWatcher() // Stop watching after sending
              }
            }, 2000)
          }
        }, { immediate: true })
    } else {
      console.error('Both Deepgram and Web Speech API failed')
      alert('Speech recognition is not available. Please check your microphone permissions.')
    }
    
  } catch (error) {
    console.error('Error starting recording:', error)
    alert('Could not access microphone. Please check permissions.')
  }
}

const stopRecording = () => {
  // Stop Deepgram if it's running
  stopDeepgram()
  
  // Stop Web Speech API if it's running
  stopWebSpeech()
  
  // Clear timeout
  if (speechTimeout.value) {
    clearTimeout(speechTimeout.value)
    speechTimeout.value = null
  }
  
  isRecording.value = false
  isVoiceMode.value = false
  
  console.log('Stopped all speech recognition')
}



defineExpose({ 
  focus,
  attachedFiles: readonly(attachedFiles),
  isVoiceMode: readonly(isVoiceMode),
  clearFiles: () => {
    attachedFiles.value = []
    if (fileUploadRef.value?.clearFiles) {
      fileUploadRef.value.clearFiles()
    }
  }
})
</script>

<style scoped>
.digi-setu-input-wrapper {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.digi-setu-input {
  background: var(--bg-secondary);
  border: 1.5px solid var(--border-primary);
  border-radius: 16px;
  padding: 0;
  transition: all 0.2s ease;
  overflow: hidden;
}

.digi-setu-input--focused {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.input-field {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  padding: 20px 24px 16px;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-primary);
  resize: none;
  min-height: 24px;
  max-height: 120px;
}

.input-field::placeholder {
  color: var(--text-tertiary);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border-primary);
  background: var(--bg-tertiary);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.toolbar-btn:hover:not(:disabled) {
  color: var(--text-primary);
  background: var(--bg-hover);
  border-color: var(--border-secondary);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn--icon {
  padding: 8px;
  min-width: 36px;
  height: 36px;
  justify-content: center;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.toolbar-btn--icon:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.toolbar-btn--thinking {
  padding: 8px 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.toolbar-btn--thinking:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.toolbar-btn--thinking-active {
  background: var(--accent-primary) !important;
  color: white !important;
  border-color: var(--accent-primary) !important;
}

.toolbar-btn--audio {
  padding: 8px;
  min-width: 36px;
  height: 36px;
  justify-content: center;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.toolbar-btn--audio:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.toolbar-btn--audio-active {
  background: #ef4444 !important;
  color: white !important;
  border-color: #ef4444 !important;
  animation: pulse 2s infinite;
}

.toolbar-btn--voice-mode {
  background: var(--accent-primary) !important;
  color: white !important;
  border-color: var(--accent-primary) !important;
  position: relative;
  overflow: hidden;
}

/* Waveform Container */
.waveform-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.waveform {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  height: 16px;
}

.wave-bar {
  width: 2px;
  background: white;
  border-radius: 1px;
  animation: waveAnimation 1.2s ease-in-out infinite;
  transform-origin: center;
}

.wave-bar:nth-child(1) { animation-delay: 0s; }
.wave-bar:nth-child(2) { animation-delay: 0.1s; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; }
.wave-bar:nth-child(5) { animation-delay: 0.4s; }

@keyframes waveAnimation {
  0%, 100% {
    height: 4px;
    opacity: 0.4;
  }
  50% {
    height: 16px;
    opacity: 1;
  }
}

/* Glowing border effect for voice mode */
.toolbar-btn--voice-mode::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 10px;
  background: linear-gradient(45deg, var(--accent-primary), #ff8a50, var(--accent-primary));
  z-index: -1;
  animation: borderGlow 2s ease-in-out infinite;
}

@keyframes borderGlow {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.audio-icon {
  transition: all 0.2s ease;
}

.audio-icon--stop {
  color: white;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 4px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.model-selector:hover {
  color: var(--text-primary);
}

.send-btn {
  background: var(--accent-primary);
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.send-btn .send-icon {
  color: white !important;
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: scale(1.05);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-btn--disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.send-icon--loading {
  animation: spin 1s linear infinite;
}

/* Attached Files Section */
.attached-files-section {
  padding: 8px 16px 12px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-primary);
}

.attached-files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 6px;
  max-height: 120px;
  overflow-y: auto;
}

.attached-file-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 4px;
  padding: 6px;
  transition: all 0.2s ease;
  position: relative;
  min-height: 60px;
  display: flex;
  flex-direction: column;
}

.attached-file-card:hover {
  border-color: var(--border-secondary);
  background: var(--bg-hover);
}

.attached-file-card--uploading {
  background: var(--bg-secondary);
  border-color: var(--accent-primary);
}

.attached-file-card--error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.attached-file-card--uploaded {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.attached-file-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.attached-file-icon {
  color: var(--text-secondary);
  flex-shrink: 0;
}

.attached-file-card--uploaded .attached-file-icon {
  color: #10b981;
}

.attached-file-card--error .attached-file-icon {
  color: #ef4444;
}

.attached-file-card--uploading .attached-file-icon {
  color: var(--accent-primary);
}

.attached-file-remove-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 1px;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0.7;
}

.attached-file-remove-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  opacity: 1;
}

.attached-file-content {
  flex: 1;
  margin-bottom: 4px;
}

.attached-file-name {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 1px;
  line-height: 1.2;
}

.attached-file-size {
  font-size: 9px;
  color: var(--text-tertiary);
}

.attached-file-status {
  margin-top: auto;
  display: flex;
  justify-content: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 2px;
}

.status-uploading {
  color: var(--accent-primary);
}

.status-uploading .status-icon {
  animation: spin 1s linear infinite;
}

.status-uploaded {
  color: #10b981;
}

.status-error {
  color: #ef4444;
}

/* Responsive adjustments for attached files */
@media (max-width: 600px) {
  .attached-files-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
  
  .attached-file-card {
    min-height: 50px;
    padding: 4px;
  }
  
  .attached-file-name {
    font-size: 9px;
  }
  
  .attached-file-size {
    font-size: 8px;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
