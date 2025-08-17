<template>
  <div class="ds-vision-renderer">
    <!-- Header -->
    <div class="ds-vision-header">
      <div class="ds-header-info">
        <Icon name="mdi:image-search" class="ds-header-icon" />
        <h3 class="ds-header-title">Image Analysis</h3>
        <span class="ds-model-badge">{{ visionData.model }}</span>
      </div>
      <div class="ds-header-actions">
        <button 
          @click="toggleImageView" 
          class="ds-action-btn"
          v-if="visionData.image"
        >
          <Icon :name="showImage ? 'mdi:eye-off' : 'mdi:eye'" class="ds-action-icon" />
          {{ showImage ? 'Hide' : 'Show' }} Image
        </button>
        <button @click="copyAnalysis" class="ds-action-btn">
          <Icon name="mdi:content-copy" class="ds-action-icon" />
          Copy
        </button>
      </div>
    </div>
    
    <!-- Image Display -->
    <div v-if="visionData.image && showImage" class="ds-image-section">
      <div class="ds-image-container">
        <img 
          :src="visionData.image" 
          alt="Analyzed image" 
          class="ds-analyzed-image"
          @click="openImageModal"
        />
        <div class="ds-image-overlay">
          <button @click="openImageModal" class="ds-zoom-btn">
            <Icon name="mdi:magnify-plus" class="ds-zoom-icon" />
          </button>
        </div>
      </div>
      <div class="ds-image-info">
        <p class="ds-prompt-text">
          <strong>Prompt:</strong> {{ visionData.prompt }}
        </p>
      </div>
    </div>
    
    <!-- Analysis Content -->
    <div class="ds-analysis-section">
      <div class="ds-analysis-content">
        <div class="ds-content-text" v-html="formattedAnalysis"></div>
      </div>
      
      <!-- Analysis Metadata -->
      <div class="ds-analysis-metadata">
        <div class="ds-metadata-grid">
          <div class="ds-metadata-item">
            <Icon name="mdi:brain" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Model:</span>
            <span class="ds-metadata-value">{{ visionData.model }}</span>
          </div>
          <div class="ds-metadata-item" v-if="analysisTime">
            <Icon name="mdi:clock" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Time:</span>
            <span class="ds-metadata-value">{{ analysisTime }}s</span>
          </div>
          <div class="ds-metadata-item" v-if="wordCount">
            <Icon name="mdi:text" class="ds-metadata-icon" />
            <span class="ds-metadata-label">Words:</span>
            <span class="ds-metadata-value">{{ wordCount }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Image Modal -->
    <div v-if="showModal" class="ds-modal-overlay" @click="closeImageModal">
      <div class="ds-modal-content" @click.stop>
        <div class="ds-modal-header">
          <h3 class="ds-modal-title">Analyzed Image</h3>
          <button @click="closeImageModal" class="ds-modal-close">
            <Icon name="mdi:close" class="ds-close-icon" />
          </button>
        </div>
        <div class="ds-modal-body">
          <img 
            :src="visionData.image" 
            alt="Analyzed image (full size)" 
            class="ds-modal-image"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  content: {
    type: [String, Object],
    required: true
  },
  metadata: {
    type: Object,
    default: () => ({})
  }
})

// Reactive state
const showImage = ref(true)
const showModal = ref(false)

// Computed properties
const visionData = computed(() => {
  if (typeof props.content === 'object') {
    return {
      analysis: props.content.analysis || '',
      image: props.content.image || props.metadata.image || null,
      model: props.content.model || props.metadata.model || 'Unknown',
      prompt: props.content.prompt || props.metadata.prompt || 'Image analysis'
    }
  }
  
  return {
    analysis: props.content,
    image: props.metadata.image || null,
    model: props.metadata.model || 'Unknown',
    prompt: props.metadata.prompt || 'Image analysis'
  }
})

const formattedAnalysis = computed(() => {
  if (!visionData.value.analysis) return ''
  
  // Convert markdown-like formatting to HTML
  let formatted = visionData.value.analysis
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
  
  return `<p>${formatted}</p>`
})

const analysisTime = computed(() => {
  return props.metadata.analysis_time || props.metadata.processingTime || null
})

const wordCount = computed(() => {
  if (!visionData.value.analysis) return 0
  return visionData.value.analysis.split(/\s+/).length
})

// Methods
const toggleImageView = () => {
  showImage.value = !showImage.value
}

const openImageModal = () => {
  showModal.value = true
}

const closeImageModal = () => {
  showModal.value = false
}

const copyAnalysis = async () => {
  try {
    await navigator.clipboard.writeText(visionData.value.analysis)
    // You could add a toast notification here
    console.log('Analysis copied to clipboard')
  } catch (err) {
    console.error('Failed to copy analysis:', err)
  }
}

// Lifecycle
onMounted(() => {
  // Auto-hide image if no image is provided
  if (!visionData.value.image) {
    showImage.value = false
  }
})
</script>

<style scoped>
@reference "tailwindcss";
.ds-vision-renderer {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-4);
  padding: var(--ds-space-4);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  background: var(--ds-surface-secondary);
}

.ds-vision-header {
  @apply flex justify-between items-center;
}

.ds-header-info {
  @apply flex items-center gap-3;
}

.ds-header-icon {
  @apply w-6 h-6 text-blue-600;
}

.ds-header-title {
  @apply text-lg font-semibold text-blue-900;
}

.ds-model-badge {
  @apply px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full;
}

.ds-header-actions {
  @apply flex gap-2;
}

.ds-action-btn {
  @apply flex items-center gap-2 px-3 py-1.5 bg-white text-blue-700 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors text-sm;
}

.ds-action-icon {
  @apply w-4 h-4;
}

.ds-image-section {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-3);
}

.ds-image-container {
  @apply relative inline-block;
}

.ds-analyzed-image {
  @apply max-w-md max-h-64 object-contain rounded-lg border border-gray-300 cursor-pointer hover:shadow-lg transition-shadow;
}

.ds-image-overlay {
  @apply absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity bg-black rounded-lg;
}

.ds-zoom-btn {
  @apply p-2 bg-white rounded-full transition-all;
}

.ds-zoom-icon {
  @apply w-5 h-5 text-gray-700;
}

.ds-image-info {
  @apply p-3 bg-white rounded-lg;
}

.ds-prompt-text {
  @apply text-sm text-gray-700;
}

.ds-analysis-section {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-4);
}

.ds-analysis-content {
  @apply p-4 bg-white rounded-lg border border-gray-200;
}

.ds-content-text {
  @apply text-gray-800 leading-relaxed;
}

.ds-content-text :deep(p) {
  @apply mb-3 last:mb-0;
}

.ds-content-text :deep(strong) {
  @apply font-semibold text-gray-900;
}

.ds-content-text :deep(em) {
  @apply italic text-gray-700;
}

.ds-analysis-metadata {
  @apply p-3 bg-white rounded-lg;
}

.ds-metadata-grid {
  @apply grid grid-cols-1 sm:grid-cols-3 gap-3;
}

.ds-metadata-item {
  @apply flex items-center gap-2 text-sm;
}

.ds-metadata-icon {
  @apply w-4 h-4 text-blue-600;
}

.ds-metadata-label {
  @apply font-medium text-gray-700;
}

.ds-metadata-value {
  @apply text-gray-900;
}

/* Modal Styles */
.ds-modal-overlay {
  @apply fixed inset-0 bg-black flex items-center justify-center z-50 p-4;
}

.ds-modal-content {
  @apply bg-white rounded-lg max-w-4xl max-h-full overflow-hidden;
}

.ds-modal-header {
  @apply flex justify-between items-center p-4 border-b border-gray-200;
}

.ds-modal-title {
  @apply text-lg font-semibold text-gray-900;
}

.ds-modal-close {
  @apply p-1 hover:bg-gray-100 rounded transition-colors;
}

.ds-close-icon {
  @apply w-5 h-5 text-gray-500;
}

.ds-modal-body {
  @apply p-4 max-h-96 overflow-auto;
}

.ds-modal-image {
  @apply w-full h-auto max-h-full object-contain;
}
</style>
