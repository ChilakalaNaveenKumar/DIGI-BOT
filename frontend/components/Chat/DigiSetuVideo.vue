<template>
  <div class="ds-video-container">
    <div class="ds-video-header" v-if="title">
      <Play class="w-5 h-5" />
      <h4 class="ds-video-title">{{ title }}</h4>
    </div>
    
    <div class="ds-video-player">
      <video 
        ref="videoElement"
        :src="src"
        :poster="poster"
        controls
        preload="metadata"
        class="ds-video-element"
        @loadedmetadata="handleLoadedMetadata"
        @error="handleError"
      >
        <!-- Captions track -->
        <track 
          v-if="captions"
          kind="captions" 
          :src="captions" 
          srclang="en" 
          label="English"
          default
        />
        Your browser does not support the video element.
      </video>
    </div>

    <div v-if="hasError" class="ds-video-error">
      <AlertCircle class="w-5 h-5" />
      <span>Unable to load video file</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Play, AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: null
  },
  poster: {
    type: String,
    default: null
  },
  captions: {
    type: String,
    default: null
  }
})

const videoElement = ref(null)
const hasError = ref(false)
const duration = ref(0)

const handleLoadedMetadata = () => {
  hasError.value = false
  if (videoElement.value) {
    duration.value = videoElement.value.duration
  }
}

const handleError = () => {
  hasError.value = true
}
</script>

<style scoped>
.ds-video-container {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
  margin: var(--ds-space-4) 0;
}

.ds-video-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-3) var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-secondary);
}

.ds-video-title {
  font-size: var(--ds-text-base);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  margin: 0;
}

.ds-video-player {
  position: relative;
  width: 100%;
  background: #000;
}

.ds-video-element {
  width: 100%;
  height: auto;
  max-height: 500px;
  display: block;
}

.ds-video-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--ds-space-2);
  color: var(--ds-danger);
  font-size: var(--ds-text-sm);
  padding: var(--ds-space-6);
  background: var(--ds-surface-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .ds-video-element {
    max-height: 300px;
  }
}
</style>
