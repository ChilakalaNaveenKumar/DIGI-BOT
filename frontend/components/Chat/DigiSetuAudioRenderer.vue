<template>
  <div class="ds-audio-renderer">
    <!-- Header -->
    <div class="ds-audio-header">
      <div class="ds-header-info">
        <Icon :name="headerIcon" class="ds-header-icon" />
        <h3 class="ds-header-title">{{ headerTitle }}</h3>
        <span class="ds-type-badge">{{ typeBadge }}</span>
      </div>
      <div class="ds-header-actions">
        <button @click="copyContent" class="ds-action-btn">
          <Icon name="mdi:content-copy" class="ds-action-icon" />
          Copy
        </button>
        <button @click="toggleExpanded" class="ds-action-btn" v-if="hasExpandableContent">
          <Icon :name="isExpanded ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="ds-action-icon" />
          {{ isExpanded ? 'Collapse' : 'Expand' }}
        </button>
      </div>
    </div>
    
    <!-- Audio Transcription Content -->
    <div v-if="isTranscription" class="ds-transcription-section">
      <div class="ds-transcription-content">
        <div class="ds-transcription-text">
          {{ audioData.transcription }}
        </div>
      </div>
      
      <!-- Transcription Metadata -->
      <div class="ds-transcription-metadata">
        <div class="ds-metadata-grid">
          <div class="ds-metadata-item">
            <Icon name="mdi:translate" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Language:</span>
            <span class="ds-metadata-value">{{ getLanguageName(audioData.language) }}</span>
          </div>
          <div class="ds-metadata-item">
            <Icon name="mdi:brain" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Model:</span>
            <span class="ds-metadata-value">{{ audioData.model }}</span>
          </div>
          <div class="ds-metadata-item" v-if="audioData.filename">
            <Icon name="mdi:file-music" class="ds-metadata-icon" />
            <span class="ds-metadata-label">File:</span>
            <span class="ds-metadata-value">{{ audioData.filename }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Audio Generation Content -->
    <div v-else-if="isGeneration" class="ds-generation-section">
      <!-- Audio Player -->
      <div v-if="audioData.audio_base64" class="ds-audio-player">
        <audio 
          :src="audioSrc" 
          controls 
          class="ds-audio-element"
          @loadedmetadata="onAudioLoaded"
        >
          Your browser does not support the audio element.
        </audio>
        
        <!-- Audio Info -->
        <div class="ds-audio-info">
          <div class="ds-audio-details">
            <Icon name="mdi:music" class="ds-audio-icon" />
            <div class="ds-audio-text">
              <span class="ds-audio-title">Generated Audio</span>
              <span class="ds-audio-subtitle">{{ audioData.voice || 'Default Voice' }} • {{ audioData.model || 'TTS-1' }}</span>
            </div>
          </div>
          <div class="ds-audio-actions">
            <button @click="downloadAudio" class="ds-audio-action" title="Download">
              <Icon name="mdi:download" class="ds-action-icon" />
            </button>
            <button @click="shareAudio" class="ds-audio-action" title="Share">
              <Icon name="mdi:share" class="ds-action-icon" />
            </button>
          </div>
        </div>
      </div>

      <!-- Original Text -->
      <div class="ds-original-text">
        <div class="ds-text-header">
          <Icon name="mdi:text" class="ds-text-icon" />
          <span class="ds-text-label">Original Text</span>
        </div>
        <div class="ds-text-content">
          {{ audioData.text || content }}
        </div>
      </div>

      <!-- Generation Metadata -->
      <div class="ds-generation-metadata">
        <div class="ds-metadata-grid">
          <div class="ds-metadata-item">
            <Icon name="mdi:account-voice" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Voice:</span>
            <span class="ds-metadata-value">{{ audioData.voice || 'alloy' }}</span>
          </div>
          <div class="ds-metadata-item">
            <Icon name="mdi:speedometer" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Speed:</span>
            <span class="ds-metadata-value">{{ audioData.speed || '1.0' }}x</span>
          </div>
          <div class="ds-metadata-item">
            <Icon name="mdi:brain" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Model:</span>
            <span class="ds-metadata-value">{{ audioData.model || 'tts-1' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Audio Analysis Content -->
    <div v-else-if="isAnalysis" class="ds-analysis-section">
      <div class="ds-analysis-content">
        <div class="ds-analysis-text">
          {{ audioData.analysis }}
        </div>
      </div>
      
      <!-- Analysis Metadata -->
      <div class="ds-analysis-metadata">
        <div class="ds-metadata-grid">
          <div class="ds-metadata-item">
            <Icon name="mdi:brain" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Model:</span>
            <span class="ds-metadata-value">{{ audioData.model }}</span>
          </div>
          <div class="ds-metadata-item" v-if="audioData.filename">
            <Icon name="mdi:file-music" class="ds-metadata-icon" />
            <span class="ds-metadata-label">File:</span>
            <span class="ds-metadata-value">{{ audioData.filename }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Fallback Content -->
    <div v-else class="ds-fallback-content">
      <div class="ds-fallback-text">
        {{ content }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  metadata: {
    type: Object,
    default: () => ({})
  }
})

// Component state
const isExpanded = ref(false)

// Parse audio data
const audioData = computed(() => {
  try {
    return typeof props.content === 'string' ? JSON.parse(props.content) : props.content
  } catch {
    return { text: props.content }
  }
})

// Content type detection
const isTranscription = computed(() => {
  return audioData.value.transcription || audioData.value.type === 'transcription'
})

const isGeneration = computed(() => {
  return audioData.value.audio_base64 || audioData.value.type === 'generation'
})

const isAnalysis = computed(() => {
  return audioData.value.analysis || audioData.value.type === 'analysis'
})

// Header properties
const headerIcon = computed(() => {
  if (isTranscription.value) return 'mdi:microphone-message'
  if (isGeneration.value) return 'mdi:volume-high'
  if (isAnalysis.value) return 'mdi:waveform'
  return 'mdi:music'
})

const headerTitle = computed(() => {
  if (isTranscription.value) return 'Audio Transcription'
  if (isGeneration.value) return 'Audio Generation'
  if (isAnalysis.value) return 'Audio Analysis'
  return 'Audio Content'
})

const typeBadge = computed(() => {
  if (isTranscription.value) return 'Transcription'
  if (isGeneration.value) return 'Generated'
  if (isAnalysis.value) return 'Analysis'
  return 'Audio'
})

// Audio source for player
const audioSrc = computed(() => {
  if (audioData.value.audio_base64) {
    return `data:audio/mpeg;base64,${audioData.value.audio_base64}`
  }
  return null
})

// Expandable content check
const hasExpandableContent = computed(() => {
  return audioData.value.transcription?.length > 200 || 
         audioData.value.analysis?.length > 200
})

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const copyContent = async () => {
  try {
    let textToCopy = ''
    if (isTranscription.value) {
      textToCopy = audioData.value.transcription
    } else if (isAnalysis.value) {
      textToCopy = audioData.value.analysis
    } else if (isGeneration.value) {
      textToCopy = audioData.value.text || props.content
    } else {
      textToCopy = props.content
    }
    
    await navigator.clipboard.writeText(textToCopy)
    // Could add toast notification here
  } catch (error) {
    console.error('Failed to copy:', error)
  }
}

const downloadAudio = () => {
  if (audioSrc.value) {
    const link = document.createElement('a')
    link.href = audioSrc.value
    link.download = 'generated-audio.mp3'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const shareAudio = async () => {
  if (navigator.share && audioSrc.value) {
    try {
      // Convert base64 to blob for sharing
      const response = await fetch(audioSrc.value)
      const blob = await response.blob()
      const file = new File([blob], 'generated-audio.mp3', { type: 'audio/mpeg' })
      
      await navigator.share({
        title: 'Generated Audio',
        text: audioData.value.text || 'Generated audio file',
        files: [file]
      })
    } catch (error) {
      console.error('Failed to share:', error)
      // Fallback to download
      downloadAudio()
    }
  } else {
    downloadAudio()
  }
}

const onAudioLoaded = (event) => {
  // Could add duration info or other metadata here
  console.log('Audio loaded:', event.target.duration)
}

const getLanguageName = (code) => {
  const languages = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese'
  }
  return languages[code] || code || 'Unknown'
}
</script>

<style scoped>
@reference "tailwindcss";
.ds-audio-renderer {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);   
  border-radius: var(--ds-radius-lg);
  padding: var(--ds-space-6);
  margin: var(--ds-space-4) 0;
}

.ds-audio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--ds-space-4);
  padding-bottom: var(--ds-space-4);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-header-info {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--ds-primary);
}

.ds-header-title {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  margin: 0;
}

.ds-type-badge {
  background: var(--ds-secondary);
  color: white;
  padding: var(--ds-space-1) var(--ds-space-3);
  border-radius: var(--ds-radius-full);
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-medium);
}

.ds-header-actions {
  display: flex;
  gap: var(--ds-space-2);
}

.ds-action-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  color: var(--ds-text-secondary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.ds-action-btn:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

.ds-transcription-section,
.ds-generation-section,
.ds-analysis-section {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-4);
}

.ds-transcription-content,
.ds-analysis-content {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
  border-left: 4px solid var(--ds-primary);
}

.ds-transcription-text,
.ds-analysis-text {
  color: var(--ds-text-primary);
  line-height: var(--ds-leading-relaxed);
  font-size: var(--ds-text-base);
}

.ds-audio-player {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
  border: 1px solid var(--ds-border-primary);
}

.ds-audio-element {
  width: 100%;
  margin-bottom: var(--ds-space-3);
}

.ds-audio-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ds-audio-details {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-audio-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--ds-primary);
}

.ds-audio-text {
  display: flex;
  flex-direction: column;
}

.ds-audio-title {
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-audio-subtitle {
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
}

.ds-audio-actions {
  display: flex;
  gap: var(--ds-space-2);
}

.ds-audio-action {
  padding: var(--ds-space-2);
  background: transparent;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  border-radius: var(--ds-radius-sm);
  transition: all 0.2s ease;
}

.ds-audio-action:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-primary);
}

.ds-original-text {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
}

.ds-text-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-3);
}

.ds-text-icon {
  width: 1rem;
  height: 1rem;
  color: var(--ds-text-muted);
}

.ds-text-label {
  font-size: var(--ds-text-sm);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-secondary);
}

.ds-text-content {
  color: var(--ds-text-primary);
  line-height: var(--ds-leading-relaxed);
  font-size: var(--ds-text-sm);
}

.ds-transcription-metadata,
.ds-generation-metadata,
.ds-analysis-metadata {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
}

.ds-metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--ds-space-3);
}

.ds-metadata-item {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
}

.ds-metadata-icon {
  width: 1rem;
  height: 1rem;
  color: var(--ds-primary);
}

.ds-metadata-label {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
  font-weight: var(--ds-font-medium);
}

.ds-metadata-value {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
  font-weight: var(--ds-font-semibold);
}

.ds-fallback-content {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
}

.ds-fallback-text {
  color: var(--ds-text-primary);
  line-height: var(--ds-leading-relaxed);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .ds-audio-renderer {
    background: var(--ds-dark-surface-primary);
    border-color: var(--ds-dark-border-primary);
  }
  
  .ds-header-title {
    color: var(--ds-dark-text-primary);
  }
  
  .ds-action-btn {
    background: var(--ds-dark-surface-secondary);
    border-color: var(--ds-dark-border-primary);
    color: var(--ds-dark-text-secondary);
  }
  
  .ds-action-btn:hover {
    background: var(--ds-dark-surface-hover);
    color: var(--ds-dark-text-primary);
  }
}
</style>