<template>
  <div class="ds-image-container">
    <div v-if="isLoading" class="ds-image-loading">
      <div class="ds-loading-spinner"></div>
      <span>Loading image...</span>
    </div>
    <div v-else class="ds-image-wrapper" :class="{ 'ds-zoomable': zoomable }">
      <img 
        :src="src" 
        :alt="alt"
        class="ds-image"
        :class="{ 'ds-image-error': hasError }"
        @load="handleLoad"
        @error="handleError"
        @click="zoomable && handleZoom()"
      />
      <div v-if="caption" class="ds-image-caption">
        {{ caption }}
      </div>
    </div>
    <div v-if="hasError" class="ds-image-error-state">
      <ImageIcon class="w-6 h-6" />
      <span>Failed to load image</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ImageIcon } from 'lucide-vue-next'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: 'Image'
  },
  caption: {
    type: String,
    default: null
  },
  zoomable: {
    type: Boolean,
    default: false
  }
})

const isLoading = ref(true)
const hasError = ref(false)

const handleLoad = () => {
  isLoading.value = false
  hasError.value = false
}

const handleError = () => {
  isLoading.value = false
  hasError.value = true
}

const handleZoom = () => {
  // TODO: Implement zoom functionality
  console.log('Zoom image:', props.src)
}

onMounted(() => {
  // Start loading
  isLoading.value = true
})
</script>

<style scoped>
.ds-image-container {
  margin: var(--ds-space-4) 0;
  text-align: center;
}

.ds-image-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-6);
  color: var(--ds-text-secondary);
}

.ds-loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--ds-border-primary);
  border-top: 2px solid var(--ds-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.ds-image-wrapper {
  display: inline-block;
  max-width: 100%;
}

.ds-image {
  max-width: 100%;
  height: auto;
  border-radius: var(--ds-radius-lg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform var(--ds-transition-normal);
}

.ds-zoomable .ds-image {
  cursor: zoom-in;
}

.ds-zoomable .ds-image:hover {
  transform: scale(1.02);
}

.ds-image-caption {
  margin-top: var(--ds-space-2);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  font-style: italic;
}

.ds-image-error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-6);
  color: var(--ds-text-muted);
  background: var(--ds-surface-secondary);
  border: 1px dashed var(--ds-border-secondary);
  border-radius: var(--ds-radius-lg);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
