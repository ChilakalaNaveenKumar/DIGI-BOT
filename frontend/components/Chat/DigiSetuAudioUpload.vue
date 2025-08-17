<template>
  <div class="ds-audio-upload">
    <!-- Upload Button -->
    <div class="ds-upload-section">
      <input 
        type="file" 
        @change="handleAudioUpload" 
        accept="audio/*"
        ref="fileInput"
        class="ds-file-input"
      />
      <button 
        @click="$refs.fileInput.click()" 
        class="ds-upload-btn"
        :disabled="isProcessing"
      >
        <Icon name="mdi:microphone" class="ds-icon" />
        {{ isProcessing ? 'Processing...' : 'Upload Audio' }}
      </button>
    </div>
    
    <!-- Audio Preview -->
    <div v-if="uploadedAudio" class="ds-audio-preview">
      <div class="ds-preview-container">
        <div class="ds-audio-player">
          <audio 
            :src="uploadedAudio" 
            controls 
            class="ds-audio-element"
          ></audio>
        </div>
        <div class="ds-audio-info">
          <p class="ds-filename">{{ fileName }}</p>
          <p class="ds-filesize">{{ fileSize }}</p>
          <p v-if="audioDuration" class="ds-duration">Duration: {{ audioDuration }}</p>
        </div>
      </div>
      
      <!-- Processing Controls -->
      <div class="ds-processing-controls">
        <div class="ds-tabs">
          <button 
            @click="activeTab = 'transcribe'"
            :class="['ds-tab', { 'ds-tab-active': activeTab === 'transcribe' }]"
          >
            <Icon name="mdi:text" class="ds-tab-icon" />
            Transcribe
          </button>
          <button 
            @click="activeTab = 'analyze'"
            :class="['ds-tab', { 'ds-tab-active': activeTab === 'analyze' }]"
          >
            <Icon name="mdi:chart-line" class="ds-tab-icon" />
            Analyze
          </button>
        </div>
        
        <!-- Transcription Tab -->
        <div v-if="activeTab === 'transcribe'" class="ds-tab-content">
          <div class="ds-transcribe-options">
            <div class="ds-language-section">
              <label for="language" class="ds-label">Language:</label>
              <select 
                id="language" 
                v-model="selectedLanguage" 
                class="ds-select"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
                <option value="pt">Portuguese</option>
                <option value="ru">Russian</option>
                <option value="ja">Japanese</option>
                <option value="ko">Korean</option>
                <option value="zh">Chinese</option>
              </select>
            </div>
            
            <div class="ds-model-section">
              <label for="transcribeModel" class="ds-label">Model:</label>
              <select 
                id="transcribeModel" 
                v-model="selectedTranscribeModel" 
                class="ds-select"
              >
                <option value="whisper-1">Whisper v1</option>
              </select>
            </div>
            
            <button 
              @click="transcribeAudio" 
              class="ds-process-btn"
              :disabled="isProcessing"
            >
              <Icon name="mdi:text-to-speech" class="ds-icon" />
              {{ isProcessing ? 'Transcribing...' : 'Transcribe Audio' }}
            </button>
          </div>
        </div>
        
        <!-- Analysis Tab -->
        <div v-if="activeTab === 'analyze'" class="ds-tab-content">
          <div class="ds-analyze-options">
            <div class="ds-analysis-type-section">
              <label for="analysisType" class="ds-label">Analysis Type:</label>
              <select 
                id="analysisType" 
                v-model="selectedAnalysisType" 
                class="ds-select"
              >
                <option value="general">General Analysis</option>
                <option value="sentiment">Sentiment Analysis</option>
                <option value="topics">Topic Extraction</option>
                <option value="summary">Content Summary</option>
              </select>
            </div>
            
            <div class="ds-checkbox-section">
              <label class="ds-checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="includeTranscription"
                  class="ds-checkbox"
                />
                Include transcription in analysis
              </label>
            </div>
            
            <button 
              @click="analyzeAudio" 
              class="ds-process-btn"
              :disabled="isProcessing"
            >
              <Icon name="mdi:chart-box" class="ds-icon" />
              {{ isProcessing ? 'Analyzing...' : 'Analyze Audio' }}
            </button>
          </div>
        </div>
        
        <!-- Clear Button -->
        <div class="ds-clear-section">
          <button 
            @click="clearAudio" 
            class="ds-clear-btn"
            :disabled="isProcessing"
          >
            <Icon name="mdi:close" class="ds-icon" />
            Clear
          </button>
        </div>
      </div>
    </div>
    
    <!-- Transcription Result -->
    <div v-if="transcriptionResult" class="ds-result-section">
      <h4 class="ds-result-title">Transcription Result:</h4>
      <div class="ds-transcription-content">
        {{ transcriptionResult }}
      </div>
      <div class="ds-result-metadata">
        <span class="ds-metadata-item">Language: {{ resultMetadata.language }}</span>
        <span class="ds-metadata-item">Model: {{ resultMetadata.model }}</span>
        <span class="ds-metadata-item">Time: {{ resultMetadata.processingTime }}s</span>
      </div>
    </div>
    
    <!-- Analysis Result -->
    <div v-if="analysisResult" class="ds-result-section">
      <h4 class="ds-result-title">Analysis Result:</h4>
      <div class="ds-analysis-content">
        <!-- Transcription -->
        <div v-if="analysisResult.transcription" class="ds-analysis-section">
          <h5 class="ds-section-title">Transcription:</h5>
          <p class="ds-section-content">{{ analysisResult.transcription }}</p>
        </div>
        
        <!-- Sentiment -->
        <div v-if="analysisResult.sentiment" class="ds-analysis-section">
          <h5 class="ds-section-title">Sentiment Analysis:</h5>
          <div class="ds-sentiment-result">
            <span :class="['ds-sentiment-badge', `ds-sentiment-${analysisResult.sentiment.sentiment}`]">
              {{ analysisResult.sentiment.sentiment }}
            </span>
            <span class="ds-confidence">Confidence: {{ (analysisResult.sentiment.confidence * 100).toFixed(1) }}%</span>
            <p class="ds-sentiment-explanation">{{ analysisResult.sentiment.explanation }}</p>
          </div>
        </div>
        
        <!-- Topics -->
        <div v-if="analysisResult.topics" class="ds-analysis-section">
          <h5 class="ds-section-title">Main Topics:</h5>
          <div class="ds-topics-list">
            <span 
              v-for="topic in analysisResult.topics" 
              :key="topic"
              class="ds-topic-tag"
            >
              {{ topic }}
            </span>
          </div>
        </div>
        
        <!-- Summary -->
        <div v-if="analysisResult.summary" class="ds-analysis-section">
          <h5 class="ds-section-title">Summary:</h5>
          <p class="ds-section-content">{{ analysisResult.summary }}</p>
        </div>
        
        <!-- General Analysis -->
        <div v-if="analysisResult.word_count" class="ds-analysis-section">
          <h5 class="ds-section-title">Statistics:</h5>
          <div class="ds-stats-grid">
            <div class="ds-stat-item">
              <span class="ds-stat-label">Words:</span>
              <span class="ds-stat-value">{{ analysisResult.word_count }}</span>
            </div>
            <div class="ds-stat-item">
              <span class="ds-stat-label">Sentences:</span>
              <span class="ds-stat-value">{{ analysisResult.sentence_count }}</span>
            </div>
            <div class="ds-stat-item">
              <span class="ds-stat-label">Reading Time:</span>
              <span class="ds-stat-value">{{ Math.ceil(analysisResult.estimated_reading_time) }}min</span>
            </div>
          </div>
          <div v-if="analysisResult.ai_insights" class="ds-ai-insights">
            <h6 class="ds-insights-title">AI Insights:</h6>
            <p class="ds-insights-content">{{ analysisResult.ai_insights }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Error Display -->
    <div v-if="error" class="ds-error">
      <Icon name="mdi:alert-circle" class="ds-error-icon" />
      <span>{{ error }}</span>
      <button @click="error = null" class="ds-error-close">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props and Emits
const emit = defineEmits(['audioTranscribed', 'audioAnalyzed'])

// Reactive state
const uploadedAudio = ref(null)
const fileName = ref('')
const fileSize = ref('')
const audioDuration = ref('')
const activeTab = ref('transcribe')
const selectedLanguage = ref('en')
const selectedTranscribeModel = ref('whisper-1')
const selectedAnalysisType = ref('general')
const includeTranscription = ref(true)
const isProcessing = ref(false)
const transcriptionResult = ref('')
const analysisResult = ref(null)
const resultMetadata = ref({})
const error = ref(null)
const fileInput = ref(null)
const currentFile = ref(null)

// Handle audio upload
const handleAudioUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file type
  const allowedTypes = [
    'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/m4a', 
    'audio/ogg', 'audio/flac', 'audio/webm'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    error.value = 'Please select a valid audio file (MP3, WAV, M4A, OGG, FLAC, WEBM)'
    return
  }
  
  // Validate file size (max 25MB)
  if (file.size > 25 * 1024 * 1024) {
    error.value = 'Audio file too large (max 25MB)'
    return
  }
  
  currentFile.value = file
  fileName.value = file.name
  fileSize.value = formatFileSize(file.size)
  
  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedAudio.value = e.target.result
    error.value = null
    
    // Try to get audio duration
    const audio = new Audio(e.target.result)
    audio.addEventListener('loadedmetadata', () => {
      audioDuration.value = formatDuration(audio.duration)
    })
  }
  reader.readAsDataURL(file)
}

// Format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Format duration
const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Transcribe audio
const transcribeAudio = async () => {
  if (!currentFile.value) return
  
  try {
    isProcessing.value = true
    error.value = null
    transcriptionResult.value = ''
    
    const startTime = Date.now()
    
    const formData = new FormData()
    formData.append('file', currentFile.value)
    formData.append('language', selectedLanguage.value)
    formData.append('model', selectedTranscribeModel.value)
    
    const response = await fetch('/api/v1/audio/transcribe', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Transcription failed')
    }
    
    const result = await response.json()
    
    if (result.success) {
      transcriptionResult.value = result.transcription
      resultMetadata.value = {
        language: result.metadata.language,
        model: result.metadata.model,
        processingTime: ((Date.now() - startTime) / 1000).toFixed(2)
      }
      
      // Emit result to parent
      emit('audioTranscribed', {
        transcription: result.transcription,
        metadata: result.metadata,
        audio: uploadedAudio.value
      })
    } else {
      throw new Error(result.error || 'Transcription failed')
    }
    
  } catch (err) {
    error.value = err.message
    console.error('Audio transcription failed:', err)
  } finally {
    isProcessing.value = false
  }
}

// Analyze audio
const analyzeAudio = async () => {
  if (!currentFile.value) return
  
  try {
    isProcessing.value = true
    error.value = null
    analysisResult.value = null
    
    const formData = new FormData()
    formData.append('file', currentFile.value)
    formData.append('analysis_type', selectedAnalysisType.value)
    formData.append('include_transcription', includeTranscription.value.toString())
    
    const response = await fetch('/api/v1/audio/analyze', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Analysis failed')
    }
    
    const result = await response.json()
    
    if (result.success) {
      analysisResult.value = result.analysis
      
      // Emit result to parent
      emit('audioAnalyzed', {
        analysis: result.analysis,
        metadata: result.metadata,
        audio: uploadedAudio.value
      })
    } else {
      throw new Error(result.error || 'Analysis failed')
    }
    
  } catch (err) {
    error.value = err.message
    console.error('Audio analysis failed:', err)
  } finally {
    isProcessing.value = false
  }
}

// Clear audio
const clearAudio = () => {
  uploadedAudio.value = null
  fileName.value = ''
  fileSize.value = ''
  audioDuration.value = ''
  currentFile.value = null
  transcriptionResult.value = ''
  analysisResult.value = null
  resultMetadata.value = {}
  error.value = null
  isProcessing.value = false
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.ds-audio-upload {
  @apply space-y-4 p-4 border border-gray-200 rounded-lg bg-white;
}

.ds-upload-section {
  @apply flex justify-center;
}

.ds-file-input {
  @apply hidden;
}

.ds-upload-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.ds-icon {
  @apply w-5 h-5;
}

.ds-audio-preview {
  @apply space-y-4;
}

.ds-preview-container {
  @apply flex gap-4 items-start;
}

.ds-audio-player {
  @apply flex-shrink-0;
}

.ds-audio-element {
  @apply w-64;
}

.ds-audio-info {
  @apply flex-1 space-y-1;
}

.ds-filename {
  @apply font-medium text-gray-900 truncate;
}

.ds-filesize, .ds-duration {
  @apply text-sm text-gray-500;
}

.ds-processing-controls {
  @apply space-y-4 p-4 bg-gray-50 rounded-lg;
}

.ds-tabs {
  @apply flex border-b border-gray-200;
}

.ds-tab {
  @apply flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-500 border-b-2 border-transparent hover:text-gray-700 hover:border-gray-300 transition-colors;
}

.ds-tab-active {
  @apply text-blue-600 border-blue-600;
}

.ds-tab-icon {
  @apply w-4 h-4;
}

.ds-tab-content {
  @apply pt-4 space-y-4;
}

.ds-transcribe-options, .ds-analyze-options {
  @apply space-y-3;
}

.ds-language-section, .ds-model-section, .ds-analysis-type-section {
  @apply space-y-1;
}

.ds-label {
  @apply block text-sm font-medium text-gray-700;
}

.ds-select {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.ds-checkbox-section {
  @apply flex items-center;
}

.ds-checkbox-label {
  @apply flex items-center gap-2 text-sm text-gray-700 cursor-pointer;
}

.ds-checkbox {
  @apply w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500;
}

.ds-process-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.ds-clear-section {
  @apply pt-2 border-t border-gray-200;
}

.ds-clear-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.ds-result-section {
  @apply space-y-3 p-4 bg-blue-50 rounded-lg border border-blue-200;
}

.ds-result-title {
  @apply font-medium text-blue-900;
}

.ds-transcription-content {
  @apply text-gray-800 whitespace-pre-wrap p-3 bg-white rounded border;
}

.ds-result-metadata {
  @apply flex gap-2 flex-wrap text-xs text-blue-600;
}

.ds-metadata-item {
  @apply bg-blue-100 px-2 py-1 rounded;
}

.ds-analysis-content {
  @apply space-y-4;
}

.ds-analysis-section {
  @apply space-y-2;
}

.ds-section-title {
  @apply font-medium text-gray-900;
}

.ds-section-content {
  @apply text-gray-800 p-3 bg-white rounded border;
}

.ds-sentiment-result {
  @apply flex items-center gap-3 flex-wrap;
}

.ds-sentiment-badge {
  @apply px-3 py-1 rounded-full text-sm font-medium;
}

.ds-sentiment-positive {
  @apply bg-green-100 text-green-800;
}

.ds-sentiment-negative {
  @apply bg-red-100 text-red-800;
}

.ds-sentiment-neutral {
  @apply bg-gray-100 text-gray-800;
}

.ds-confidence {
  @apply text-sm text-gray-600;
}

.ds-sentiment-explanation {
  @apply w-full text-sm text-gray-700 mt-2;
}

.ds-topics-list {
  @apply flex gap-2 flex-wrap;
}

.ds-topic-tag {
  @apply px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm;
}

.ds-stats-grid {
  @apply grid grid-cols-3 gap-4 p-3 bg-white rounded border;
}

.ds-stat-item {
  @apply text-center;
}

.ds-stat-label {
  @apply block text-xs text-gray-500;
}

.ds-stat-value {
  @apply block text-lg font-semibold text-gray-900;
}

.ds-ai-insights {
  @apply mt-3 p-3 bg-white rounded border;
}

.ds-insights-title {
  @apply font-medium text-gray-900 mb-2;
}

.ds-insights-content {
  @apply text-gray-800 text-sm;
}

.ds-error {
  @apply flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800;
}

.ds-error-icon {
  @apply w-5 h-5 text-red-500;
}

.ds-error-close {
  @apply ml-auto text-red-500 hover:text-red-700 font-bold text-lg leading-none;
}
</style>

