<template>
  <div class="ds-audio-container">
    <div class="ds-audio-header" v-if="title">
      <VolumeX class="w-5 h-5" />
      <h4 class="ds-audio-title">{{ title }}</h4>
    </div>
    
    <div class="ds-audio-player">
      <audio 
        ref="audioElement"
        :src="src"
        controls
        preload="metadata"
        class="ds-audio-controls"
        @loadedmetadata="handleLoadedMetadata"
        @error="handleError"
      >
        Your browser does not support the audio element.
      </audio>
    </div>

    <div v-if="transcript" class="ds-audio-transcript">
      <div class="ds-transcript-header">
        <FileText class="w-4 h-4" />
        <span>Transcript</span>
      </div>
      <div class="ds-transcript-content">
        {{ transcript }}
      </div>
    </div>

    <div v-if="hasError" class="ds-audio-error">
      <AlertCircle class="w-5 h-5" />
      <span>Unable to load audio file</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { VolumeX, FileText, AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: null
  },
  transcript: {
    type: String,
    default: null
  }
})

const audioElement = ref(null)
const hasError = ref(false)
const duration = ref(0)

const handleLoadedMetadata = () => {
  hasError.value = false
  if (audioElement.value) {
    duration.value = audioElement.value.duration
  }
}

const handleError = () => {
  hasError.value = true
}
</script>

<style scoped>
.ds-audio-container {
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  padding: var(--ds-space-4);
  margin: var(--ds-space-3) 0;
}

.ds-audio-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-3);
}

.ds-audio-title {
  font-size: var(--ds-text-base);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  margin: 0;
}

.ds-audio-player {
  margin-bottom: var(--ds-space-3);
}

.ds-audio-controls {
  width: 100%;
  height: 40px;
  background: var(--ds-surface-primary);
  border-radius: var(--ds-radius-md);
}

.ds-audio-transcript {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-secondary);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-3);
  margin-top: var(--ds-space-3);
}

.ds-transcript-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-2);
  font-size: var(--ds-text-sm);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-secondary);
}

.ds-transcript-content {
  font-size: var(--ds-text-sm);
  line-height: var(--ds-leading-relaxed);
  color: var(--ds-text-primary);
}

.ds-audio-error {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-danger);
  font-size: var(--ds-text-sm);
  margin-top: var(--ds-space-2);
}
</style>
