<template>
  <div class="file-attachment" :class="{ 'file-attachment--compact': compact }">
    <div class="attachment-icon">
      <Icon :name="getFileIcon(filename)" :size="compact ? 14 : 16" />
    </div>
    
    <div class="attachment-info">
      <span class="attachment-name">{{ filename }}</span>
      <span v-if="!compact && size" class="attachment-size">{{ formatFileSize(size) }}</span>
    </div>
    
    <div v-if="status && !compact" class="attachment-status">
      <Icon 
        v-if="status === 'uploading'"
        name="lucide:loader" 
        :size="12" 
        class="status-icon status-icon--loading"
      />
      <Icon 
        v-else-if="status === 'uploaded'"
        name="lucide:check" 
        :size="12" 
        class="status-icon status-icon--success"
      />
      <Icon 
        v-else-if="status === 'error'"
        name="lucide:x" 
        :size="12" 
        class="status-icon status-icon--error"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  filename: string
  size?: number
  status?: 'uploading' | 'uploaded' | 'error'
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false
})

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
</script>

<style scoped>
.file-attachment {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 8px 12px;
  margin: 2px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.file-attachment--compact {
  padding: 4px 8px;
  font-size: 12px;
  gap: 6px;
}

.file-attachment:hover {
  background: var(--bg-hover);
  border-color: var(--border-secondary);
}

.attachment-icon {
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.attachment-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.attachment-name {
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.attachment-size {
  font-size: 11px;
  color: var(--text-tertiary);
}

.attachment-status {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.status-icon--loading {
  color: var(--accent-primary);
  animation: spin 1s linear infinite;
}

.status-icon--success {
  color: #10b981;
}

.status-icon--error {
  color: #ef4444;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
