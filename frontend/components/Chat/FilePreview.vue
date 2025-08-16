<template>
  <div class="file-preview">
    <!-- Image files -->
    <div v-if="isImage" class="image-preview">
      <img 
        :src="fileUrl" 
        :alt="file.name || 'Image'"
        class="max-w-full max-h-64 rounded-lg shadow-sm"
        @error="handleImageError"
      />
    </div>
    
    <!-- Audio files -->
    <div v-else-if="isAudio" class="audio-preview">
      <audio 
        :src="fileUrl" 
        controls 
        class="w-full max-w-md"
      >
        Your browser does not support the audio element.
      </audio>
    </div>
    
    <!-- Video files -->
    <div v-else-if="isVideo" class="video-preview">
      <video 
        :src="fileUrl" 
        controls 
        class="max-w-full max-h-64 rounded-lg shadow-sm"
      >
        Your browser does not support the video element.
      </video>
    </div>
    
    <!-- PDF files -->
    <div v-else-if="isPdf" class="pdf-preview">
      <div class="flex items-center space-x-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-700">
        <div class="w-8 h-8 bg-red-500 rounded flex items-center justify-center">
          <span class="text-white text-xs font-bold">PDF</span>
        </div>
        <div class="flex-1">
          <div class="font-medium text-red-700 dark:text-red-300">{{ file.name || 'PDF Document' }}</div>
          <div class="text-sm text-red-600 dark:text-red-400">{{ formatFileSize(file.size) }}</div>
        </div>
      </div>
    </div>
    
    <!-- Code files -->
    <div v-else-if="isCode" class="code-preview">
      <div class="mb-2">
        <div class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
          <div class="w-2 h-2 bg-green-500 rounded-full"></div>
          <span>{{ getLanguageFromExtension(file.name) }} File</span>
        </div>
      </div>
      
      <CodeBlock 
        v-if="fileContent"
        :code="fileContent" 
        :language="getLanguageFromExtension(file.name)"
        :show-copy="true"
        :show-header="false"
      />
      
      <div v-else class="text-sm text-gray-500 dark:text-gray-400">
        Loading file content...
      </div>
    </div>
    
    <!-- Text files -->
    <div v-else-if="isText" class="text-preview">
      <div class="bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <pre class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ fileContent || 'Loading...' }}</pre>
      </div>
    </div>
    
    <!-- JSON files -->
    <div v-else-if="isJson" class="json-preview">
      <JsonViewer 
        v-if="fileContent"
        :data="fileContent"
        :initially-expanded="false"
      />
      
      <div v-else class="text-sm text-gray-500 dark:text-gray-400">
        Loading JSON content...
      </div>
    </div>
    
    <!-- Generic file -->
    <div v-else class="generic-file">
      <div class="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div class="w-8 h-8 bg-gray-500 rounded flex items-center justify-center">
          <span class="text-white text-xs font-bold">{{ getFileExtension(file.name).toUpperCase() }}</span>
        </div>
        <div class="flex-1">
          <div class="font-medium text-gray-700 dark:text-gray-300">{{ file.name || 'Unknown File' }}</div>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            {{ file.type || 'Unknown type' }} • {{ formatFileSize(file.size) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Download button -->
    <div v-if="showDownload && fileUrl" class="mt-3">
      <a 
        :href="fileUrl" 
        :download="file.name"
        class="inline-flex items-center space-x-2 px-3 py-1 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
      >
        <Download class="w-4 h-4" />
        <span>Download</span>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Download } from 'lucide-vue-next'
import CodeBlock from './CodeBlock.vue'
import JsonViewer from './JsonViewer.vue'

interface Props {
  file: {
    name?: string
    type?: string
    size?: number
    url?: string
    data?: string
    content?: string
  }
  showDownload?: boolean
  maxPreviewSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  showDownload: true,
  maxPreviewSize: 1024 * 1024 // 1MB
})

const fileContent = ref<string>('')
const imageError = ref(false)

// File URL (could be data URL, blob URL, or regular URL)
const fileUrl = computed(() => {
  return props.file.url || props.file.data
})

// File type detection
const isImage = computed(() => {
  const imageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
  
  return imageTypes.includes(props.file.type || '') || 
         imageExtensions.some(ext => props.file.name?.toLowerCase().endsWith(ext)) ||
         (props.file.url && imageExtensions.some(ext => props.file.url!.toLowerCase().includes(ext)))
})

const isAudio = computed(() => {
  const audioTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3']
  const audioExtensions = ['.mp3', '.wav', '.ogg', '.m4a']
  
  return audioTypes.includes(props.file.type || '') || 
         audioExtensions.some(ext => props.file.name?.toLowerCase().endsWith(ext))
})

const isVideo = computed(() => {
  const videoTypes = ['video/mp4', 'video/webm', 'video/ogg']
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.avi', '.mov']
  
  return videoTypes.includes(props.file.type || '') || 
         videoExtensions.some(ext => props.file.name?.toLowerCase().endsWith(ext))
})

const isPdf = computed(() => {
  return props.file.type === 'application/pdf' || 
         props.file.name?.toLowerCase().endsWith('.pdf')
})

const isCode = computed(() => {
  const codeExtensions = ['.js', '.ts', '.jsx', '.tsx', '.vue', '.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.sql', '.sh', '.bash', '.ps1', '.yaml', '.yml', '.toml', '.ini', '.conf']
  
  return codeExtensions.some(ext => props.file.name?.toLowerCase().endsWith(ext))
})

const isText = computed(() => {
  const textTypes = ['text/plain', 'text/markdown']
  const textExtensions = ['.txt', '.md', '.readme', '.log']
  
  return textTypes.includes(props.file.type || '') || 
         textExtensions.some(ext => props.file.name?.toLowerCase().endsWith(ext))
})

const isJson = computed(() => {
  return props.file.type === 'application/json' || 
         props.file.name?.toLowerCase().endsWith('.json')
})

// Get file extension
const getFileExtension = (filename?: string): string => {
  if (!filename) return ''
  const parts = filename.split('.')
  return parts.length > 1 ? parts.pop() || '' : ''
}

// Get programming language from file extension
const getLanguageFromExtension = (filename?: string): string => {
  if (!filename) return 'text'
  
  const ext = getFileExtension(filename).toLowerCase()
  const languageMap: Record<string, string> = {
    'js': 'javascript',
    'jsx': 'javascript',
    'ts': 'typescript',
    'tsx': 'typescript',
    'vue': 'vue',
    'py': 'python',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'cs': 'csharp',
    'php': 'php',
    'rb': 'ruby',
    'go': 'go',
    'rs': 'rust',
    'swift': 'swift',
    'kt': 'kotlin',
    'scala': 'scala',
    'r': 'r',
    'sql': 'sql',
    'sh': 'bash',
    'bash': 'bash',
    'ps1': 'powershell',
    'yaml': 'yaml',
    'yml': 'yaml',
    'toml': 'toml',
    'ini': 'ini',
    'conf': 'conf',
    'json': 'json',
    'html': 'html',
    'css': 'css',
    'scss': 'scss',
    'sass': 'sass',
    'xml': 'xml'
  }
  
  return languageMap[ext] || ext
}

// Format file size
const formatFileSize = (bytes?: number): string => {
  if (!bytes) return 'Unknown size'
  
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

// Handle image loading error
const handleImageError = () => {
  imageError.value = true
}

// Load file content for text-based files
const loadFileContent = async () => {
  if (!fileUrl.value || (!isCode.value && !isText.value && !isJson.value)) return
  
  try {
    if (props.file.content) {
      fileContent.value = props.file.content
      return
    }
    
    if (props.file.data && props.file.data.startsWith('data:')) {
      // Handle data URLs
      const base64Data = props.file.data.split(',')[1]
      const decodedData = atob(base64Data)
      fileContent.value = decodedData
      return
    }
    
    if (fileUrl.value.startsWith('http')) {
      // Fetch remote file (be careful with CORS)
      const response = await fetch(fileUrl.value)
      const text = await response.text()
      fileContent.value = text
    }
  } catch (error) {
    console.error('Failed to load file content:', error)
    fileContent.value = 'Failed to load file content'
  }
}

onMounted(() => {
  loadFileContent()
})
</script>

<style scoped>
.file-preview {
  @apply w-full;
}

.image-preview img {
  @apply border border-gray-200 dark:border-gray-700;
}

.audio-preview audio {
  @apply bg-gray-100 dark:bg-gray-800 rounded;
}

.video-preview video {
  @apply border border-gray-200 dark:border-gray-700;
}
</style>

