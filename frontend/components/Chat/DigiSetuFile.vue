<template>
  <div class="ds-file-container">
    <div class="ds-file-info">
      <div class="ds-file-icon">
        <FileIcon class="w-6 h-6" />
      </div>
      <div class="ds-file-details">
        <div class="ds-file-name">{{ file.name || 'Unknown file' }}</div>
        <div class="ds-file-meta">
          <span v-if="file.size" class="ds-file-size">{{ formatFileSize(file.size) }}</span>
          <span v-if="file.type" class="ds-file-type">{{ file.type }}</span>
        </div>
      </div>
      <div class="ds-file-actions">
        <button 
          v-if="file.url" 
          @click="downloadFile"
          class="ds-file-download"
          :disabled="isDownloading"
        >
          <Download class="w-4 h-4" />
          <span v-if="isDownloading">Downloading...</span>
          <span v-else>Download</span>
        </button>
      </div>
    </div>

    <!-- File preview if supported and enabled -->
    <div v-if="preview && canPreview" class="ds-file-preview">
      <div class="ds-preview-header">
        <Eye class="w-4 h-4" />
        <span>Preview</span>
      </div>
      <div class="ds-preview-content">
        <!-- Text file preview -->
        <pre v-if="isTextFile" class="ds-text-preview">{{ previewContent }}</pre>
        
        <!-- Image preview -->
        <img 
          v-else-if="isImageFile" 
          :src="file.url" 
          :alt="file.name"
          class="ds-image-preview"
        />
        
        <!-- Unsupported preview -->
        <div v-else class="ds-preview-unsupported">
          <FileX class="w-8 h-8" />
          <span>Preview not available for this file type</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FileIcon, Download, Eye, FileX } from 'lucide-vue-next'

const props = defineProps({
  file: {
    type: Object,
    required: true
  },
  preview: {
    type: Boolean,
    default: false
  }
})

const isDownloading = ref(false)
const previewContent = ref('')

const canPreview = computed(() => {
  return props.file.url && (isTextFile.value || isImageFile.value)
})

const isTextFile = computed(() => {
  const textTypes = ['text/', 'application/json', 'application/xml']
  return textTypes.some(type => props.file.type?.startsWith(type))
})

const isImageFile = computed(() => {
  return props.file.type?.startsWith('image/')
})

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const downloadFile = async () => {
  if (!props.file.url) return
  
  isDownloading.value = true
  try {
    const link = document.createElement('a')
    link.href = props.file.url
    link.download = props.file.name || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Download failed:', error)
  } finally {
    isDownloading.value = false
  }
}

const loadPreview = async () => {
  if (!props.preview || !canPreview.value || !isTextFile.value) return
  
  try {
    const response = await fetch(props.file.url)
    const text = await response.text()
    previewContent.value = text.substring(0, 1000) // Limit preview size
  } catch (error) {
    console.error('Failed to load preview:', error)
  }
}

onMounted(() => {
  if (props.preview) {
    loadPreview()
  }
})
</script>

<style scoped>
.ds-file-container {
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  margin: var(--ds-space-3) 0;
  overflow: hidden;
}

.ds-file-info {
  display: flex;
  align-items: center;
  padding: var(--ds-space-4);
  gap: var(--ds-space-3);
}

.ds-file-icon {
  flex-shrink: 0;
  color: var(--ds-text-secondary);
}

.ds-file-details {
  flex: 1;
  min-width: 0;
}

.ds-file-name {
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  word-break: break-all;
}

.ds-file-meta {
  display: flex;
  gap: var(--ds-space-2);
  margin-top: var(--ds-space-1);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
}

.ds-file-size::after {
  content: "•";
  margin-left: var(--ds-space-2);
}

.ds-file-actions {
  flex-shrink: 0;
}

.ds-file-download {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-primary);
  color: white;
  border: none;
  border-radius: var(--ds-radius-md);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: background var(--ds-transition-fast);
}

.ds-file-download:hover:not(:disabled) {
  background: color-mix(in srgb, var(--ds-primary) 90%, black);
}

.ds-file-download:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ds-file-preview {
  border-top: 1px solid var(--ds-border-secondary);
  background: var(--ds-surface-primary);
}

.ds-preview-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-3) var(--ds-space-4);
  background: var(--ds-surface-secondary);
  font-size: var(--ds-text-sm);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-secondary);
}

.ds-preview-content {
  padding: var(--ds-space-4);
  max-height: 300px;
  overflow: auto;
}

.ds-text-preview {
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  line-height: var(--ds-leading-relaxed);
  color: var(--ds-text-primary);
  background: var(--ds-surface-secondary);
  padding: var(--ds-space-3);
  border-radius: var(--ds-radius-md);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.ds-image-preview {
  max-width: 100%;
  height: auto;
  border-radius: var(--ds-radius-md);
}

.ds-preview-unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-text-muted);
  padding: var(--ds-space-6);
}
</style>
