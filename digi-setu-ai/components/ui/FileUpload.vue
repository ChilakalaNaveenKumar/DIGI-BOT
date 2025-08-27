<template>
  <div class="file-upload-container">
    <!-- File Upload Button -->
    <button 
      class="file-upload-btn"
      @click="triggerFileInput"
      :disabled="uploading || files.length >= 6"
      :title="files.length >= 6 ? 'Maximum 6 files allowed' : `Upload files (${6 - files.length} remaining)`"
    >
      <Icon 
        v-if="uploading"
        name="lucide:loader" 
        :size="16"
        class="upload-icon upload-icon--loading"
      />
      <Icon 
        v-else
        name="lucide:paperclip" 
        :size="16"
        class="upload-icon"
      />
      <span v-if="files.length > 0 && files.length < 6" class="file-count-badge">{{ files.length }}</span>
    </button>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      accept=".pdf,.docx,.txt,.md,.csv,.json,.py,.js,.ts,.html,.css,.png,.jpg,.jpeg,.webp"
      @change="handleFileSelect"
      class="hidden-file-input"
    />

    <!-- Drag and Drop Overlay -->
    <div 
      v-if="isDragOver"
      class="drag-overlay"
      @dragover.prevent
      @drop.prevent="handleDrop"
      @dragleave="handleDragLeave"
    >
      <div class="drag-content">
        <Icon name="lucide:upload" :size="32" class="drag-icon" />
        <p class="drag-text">Drop files here to upload</p>
        <p class="drag-subtext">Supports PDF, DOCX, TXT, MD, images and more</p>
      </div>
    </div>

    <!-- Error Message - Positioned at top-right -->
    <div v-if="errorMessage" class="error-toast">
      <div class="error-content">
        <Icon name="lucide:alert-circle" :size="16" class="error-icon" />
        <span class="error-text">{{ errorMessage }}</span>
        <button class="error-dismiss" @click="clearError">
          <Icon name="lucide:x" :size="14" />
        </button>
      </div>
    </div>

    <!-- File Grid Hidden - Files are displayed in parent component -->
  </div>
</template>

<script setup lang="ts">
import { ref, readonly, onMounted, onUnmounted, nextTick } from 'vue'

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
  (e: 'files-uploaded', files: FileItem[]): void
  (e: 'files-changed', files: FileItem[]): void
}

const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement | null>(null)
const files = ref<FileItem[]>([])
const uploading = ref(false)
const isDragOver = ref(false)
const errorMessage = ref('')

// Drag and drop handlers
const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  // Only hide overlay if leaving the container entirely
  if (!e.relatedTarget || !(e.currentTarget as Element).contains(e.relatedTarget as Node)) {
    isDragOver.value = false
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
  
  const droppedFiles = Array.from(e.dataTransfer?.files || [])
  if (droppedFiles.length > 0) {
    processFiles(droppedFiles)
  }
}

// File input handlers
const triggerFileInput = () => {
  if (files.value.length >= 6) {
    showError("I cannot process more than 6 files at a time. Please remove some files first.")
    return
  }
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  const selectedFiles = Array.from(target.files || [])
  if (selectedFiles.length > 0) {
    processFiles(selectedFiles)
  }
  // Reset input
  target.value = ''
}

// File processing
const processFiles = async (newFiles: File[]) => {
  try {
    // Clear any previous error
    clearError()
    
    // Check if adding these files would exceed the limit
    const remainingSlots = 6 - files.value.length
    
    if (newFiles.length > remainingSlots) {
      if (remainingSlots === 0) {
        showError("I cannot process more than 6 files at a time. Please remove some files first.")
      } else {
        showError(`I cannot process more than 6 files at a time. You can only add ${remainingSlots} more file${remainingSlots === 1 ? '' : 's'}.`)
      }
      return
    }

    const fileItems: FileItem[] = newFiles.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      size: file.size,
      file,
      status: 'pending' as const
    }))

    files.value.push(...fileItems)
    emit('files-changed', [...files.value])

    // Upload files
    await uploadFiles(fileItems)
  } catch (error) {
    // Handle any unexpected errors in file processing
    console.error('File processing error:', error)
    showError(`Failed to process files: ${error instanceof Error ? error.message : 'Unknown error'}`)
    
    // Ensure loading state is cleared
    uploading.value = false
  }
}

const uploadFiles = async (fileItems: FileItem[]) => {
  uploading.value = true

  // Set a timeout to prevent infinite loading (30 seconds max)
  const timeoutId = setTimeout(() => {
    if (uploading.value) {
      console.error('Upload timeout - forcing loading state to false')
      uploading.value = false
      showError('Upload timed out. Please try again.')
      
      // Mark any still-uploading files as error
      fileItems.forEach(item => {
        if (item.status === 'uploading') {
          item.status = 'error'
          item.error = 'Upload timed out'
        }
      })
      
      emit('files-changed', [...files.value])
    }
  }, 30000) // 30 second timeout

  try {
    for (const fileItem of fileItems) {
      try {
        fileItem.status = 'uploading'
        
        // Create form data
        const formData = new FormData()
        formData.append('file', fileItem.file)
        
        // Upload to chat-specific endpoint with timeout
        const controller = new AbortController()
        const uploadTimeout = setTimeout(() => controller.abort(), 15000) // 15 second per file timeout
        
        const response = await fetch('http://localhost:8000/api/files/upload-for-chat', {
          method: 'POST',
          credentials: 'include',
          body: formData,
          signal: controller.signal
        })

        clearTimeout(uploadTimeout)

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`)
        }

        const result = await response.json()
        
        if (result.success) {
          fileItem.status = 'uploaded'
          fileItem.vectorStoreFileId = result.file.id
        } else {
          throw new Error(result.error || 'Upload failed')
        }

      } catch (error) {
        console.error('File upload error:', error)
        fileItem.status = 'error'
        
        if (error.name === 'AbortError') {
          fileItem.error = 'Upload timed out'
          showError(`Upload of ${fileItem.name} timed out. Please try again.`)
        } else {
          fileItem.error = error instanceof Error ? error.message : 'Upload failed'
          showError(`Failed to upload ${fileItem.name}: ${error instanceof Error ? error.message : 'Upload failed'}`)
        }
      }
    }
  } catch (error) {
    // Handle any unexpected errors during the upload process
    console.error('Unexpected upload error:', error)
    showError(`Upload process failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
  } finally {
    // Clear timeout and loading state
    clearTimeout(timeoutId)
    uploading.value = false
  }
  
  // Emit uploaded files
  const uploadedFiles = files.value.filter(f => f.status === 'uploaded')
  if (uploadedFiles.length > 0) {
    emit('files-uploaded', uploadedFiles)
  }
  
  emit('files-changed', [...files.value])
}

const removeFile = (fileId: string) => {
  files.value = files.value.filter(f => f.id !== fileId)
  emit('files-changed', [...files.value])
  // Clear error when files are removed
  if (files.value.length < 6) {
    clearError()
  }
}

const showError = (message: string) => {
  errorMessage.value = message
  // Auto-clear error after 10 seconds (longer duration)
  setTimeout(() => {
    clearError()
  }, 10000)
}

const clearError = () => {
  errorMessage.value = ''
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

// Global drag handlers for the entire component area
onMounted(() => {
  const container = document.querySelector('.file-upload-container')
  if (container) {
    container.addEventListener('dragover', handleDragOver)
    container.addEventListener('dragleave', handleDragLeave)
    container.addEventListener('drop', handleDrop)
  }
})

onUnmounted(() => {
  const container = document.querySelector('.file-upload-container')
  if (container) {
    container.removeEventListener('dragover', handleDragOver)
    container.removeEventListener('dragleave', handleDragLeave)
    container.removeEventListener('drop', handleDrop)
  }
})

// Expose methods and state
defineExpose({
  files: readonly(files),
  uploading: readonly(uploading),
  clearFiles: () => {
    files.value = []
    clearError()
    emit('files-changed', [])
  }
})
</script>

<style scoped>
.file-upload-container {
  position: relative;
}

.file-upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  color: var(--text-primary);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  min-width: 36px;
  height: 36px;
  transition: all 0.2s ease;
}

.file-upload-btn:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.file-upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.file-upload-btn {
  position: relative;
}

.file-count-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--accent-primary);
  color: white;
  font-size: 10px;
  font-weight: 600;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
}

.upload-icon--loading {
  animation: spin 1s linear infinite;
}

.hidden-file-input {
  display: none;
}

/* Error Toast - Positioned at top-right */
.error-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
  min-width: 300px;
  animation: slideInFromRight 0.4s ease-out;
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  background: #ffffff;
  border: 2px solid #ef4444;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15), 0 4px 10px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.error-icon {
  color: #ef4444;
  flex-shrink: 0;
  margin-top: 1px;
}

.error-text {
  color: #1f2937;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  flex: 1;
}

.error-dismiss {
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-top: -2px;
}

.error-dismiss:hover {
  background: #f3f4f6;
  color: #374151;
  transform: scale(1.1);
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .error-content {
    background: #1f2937;
    border-color: #ef4444;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3), 0 4px 10px rgba(0, 0, 0, 0.2);
  }
  
  .error-text {
    color: #f9fafb;
  }
  
  .error-dismiss {
    color: #9ca3af;
  }
  
  .error-dismiss:hover {
    background: #374151;
    color: #d1d5db;
  }
}

@keyframes slideInFromRight {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* Mobile responsive */
@media (max-width: 640px) {
  .error-toast {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
    min-width: auto;
  }
  
  .error-content {
    padding: 12px 16px;
  }
  
  .error-text {
    font-size: 13px;
  }
}

.drag-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.drag-content {
  background: var(--bg-secondary);
  border: 2px dashed var(--accent-primary);
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  max-width: 400px;
}

.drag-icon {
  color: var(--accent-primary);
  margin-bottom: 16px;
}

.drag-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.drag-subtext {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* File Grid Layout */
.file-grid-container {
  margin-top: 12px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-secondary);
  padding: 8px;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
  max-width: 100%;
}

.file-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  padding: 8px;
  transition: all 0.2s ease;
  position: relative;
  min-height: 80px;
  display: flex;
  flex-direction: column;
}

.file-card:hover {
  border-color: var(--border-secondary);
  background: var(--bg-hover);
}

.file-card--uploading {
  background: var(--bg-tertiary);
  border-color: var(--accent-primary);
}

.file-card--error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.file-card--uploaded {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.file-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.file-icon {
  color: var(--text-secondary);
  flex-shrink: 0;
}

.file-card--uploaded .file-icon {
  color: #10b981;
}

.file-card--error .file-icon {
  color: #ef4444;
}

.file-card--uploading .file-icon {
  color: var(--accent-primary);
}

.file-remove-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0.7;
}

.file-remove-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  opacity: 1;
}

.file-card-content {
  flex: 1;
  margin-bottom: 6px;
}

.file-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
  line-height: 1.2;
}

.file-size {
  font-size: 10px;
  color: var(--text-tertiary);
}

.file-card-status {
  margin-top: auto;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 500;
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

.status-pending {
  color: var(--text-tertiary);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .file-grid {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
  
  .file-card {
    min-height: 70px;
    padding: 6px;
  }
  
  .file-name {
    font-size: 11px;
  }
  
  .file-size {
    font-size: 9px;
  }
  
  .status-indicator {
    font-size: 9px;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
