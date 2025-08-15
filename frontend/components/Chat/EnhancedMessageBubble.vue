<template>
  <div class="message-bubble group relative animate-fade-in">
    <!-- Assistant Message -->
    <div v-if="message.role === 'assistant'" class="flex items-start space-x-4">
      <!-- AI Avatar with Provider Icon -->
      <div class="relative flex-shrink-0">
        <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-200">
          <ProviderIcon :provider="provider" :size="24" class="text-white" />
        </div>
        <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-900 animate-pulse"></div>
      </div>
      
      <!-- Message Content -->
      <div class="flex-1 max-w-4xl space-y-4">
        
        <!-- Reasoning Display -->
        <ReasoningDisplay
          v-if="hasReasoning"
          :reasoning="reasoningParts"
          :state="message.state || 'done'"
          :current-thinking="isStreaming ? currentThought : ''"
          :initial-expanded="isStreaming"
        />
        
        <!-- Main Content -->
        <div v-if="hasTextContent" class="content-card">
          <div class="p-6">
            <!-- Text Parts -->
            <div v-for="(part, index) in textParts" :key="`text-${index}`" class="mb-4 last:mb-0">
              <MarkdownRenderer :content="part.text" />
              
              <!-- Streaming indicator for active text part -->
              <div v-if="part.state === 'streaming'" class="flex items-center space-x-2 mt-2 text-blue-600 dark:text-blue-400">
                <Loader2 class="w-3 h-3 animate-spin" />
                <span class="text-xs">Generating response...</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Tool Calls and Results -->
        <div v-if="hasTools" class="space-y-3">
          <div 
            v-for="(toolPart, index) in toolParts" 
            :key="`tool-${index}`"
            class="tool-card"
          >
            <!-- Tool Call Header -->
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-2">
                <div class="p-1.5 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Wrench class="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </div>
                <span class="text-sm font-medium text-blue-700 dark:text-blue-300">
                  {{ getToolDisplayName(toolPart) }}
                </span>
                <UBadge 
                  :color="getToolStateColor(toolPart.state)" 
                  variant="soft" 
                  size="xs"
                >
                  {{ getToolStateLabel(toolPart.state) }}
                </UBadge>
              </div>
            </div>
            
            <!-- Tool Input (if available) -->
            <div v-if="toolPart.input && toolPart.state !== 'input-streaming'" class="mb-3">
              <details class="group/details">
                <summary class="cursor-pointer text-xs text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 flex items-center space-x-1">
                  <ChevronRight class="w-3 h-3 transition-transform group-open/details:rotate-90" />
                  <span>View Input Parameters</span>
                </summary>
                <div class="mt-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <pre class="text-xs text-gray-700 dark:text-gray-300 overflow-x-auto">{{ JSON.stringify(toolPart.input, null, 2) }}</pre>
                </div>
              </details>
            </div>
            
            <!-- Interactive Component Results -->
            <div v-if="toolPart.state === 'output-available' && toolPart.output">
              <!-- Table Component -->
              <InteractiveTable 
                v-if="isTableTool(toolPart)"
                :data="toolPart.output"
              />
              
              <!-- Quiz Component -->
              <InteractiveQuiz 
                v-else-if="isQuizTool(toolPart)"
                :quiz="toolPart.output"
              />
              
              <!-- Chart Component -->
              <InteractiveChart 
                v-else-if="isChartTool(toolPart)"
                :chart="toolPart.output"
              />
              
              <!-- Flashcards Component -->
              <InteractiveFlashcards 
                v-else-if="isFlashcardsTool(toolPart)"
                :flashcards="toolPart.output"
              />
              
              <!-- Generic Tool Result -->
              <div v-else class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700">
                <div class="text-sm text-green-800 dark:text-green-200">
                  <MarkdownRenderer :content="JSON.stringify(toolPart.output, null, 2)" />
                </div>
              </div>
            </div>
            
            <!-- Tool Error -->
            <div v-else-if="toolPart.state === 'output-error'" class="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-700">
              <div class="flex items-center space-x-2">
                <AlertCircle class="w-4 h-4 text-red-500" />
                <span class="text-sm font-medium text-red-700 dark:text-red-300">Tool Error</span>
              </div>
              <p class="text-sm text-red-600 dark:text-red-400 mt-1">{{ toolPart.errorText }}</p>
            </div>
            
            <!-- Tool Loading -->
            <div v-else-if="toolPart.state === 'input-streaming'" class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
              <div class="flex items-center space-x-2">
                <Loader2 class="w-4 h-4 text-blue-500 animate-spin" />
                <span class="text-sm text-blue-700 dark:text-blue-300">Executing tool...</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- File Attachments -->
        <div v-if="hasFiles" class="space-y-2">
          <div 
            v-for="(filePart, index) in fileParts" 
            :key="`file-${index}`"
            class="file-attachment"
          >
            <div class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <FileIcon :mediaType="filePart.mediaType" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {{ filePart.filename || 'Uploaded file' }}
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  {{ filePart.mediaType }}
                </p>
              </div>
              <UButton 
                @click="openFile(filePart.url)"
                size="xs" 
                variant="ghost"
                icon="i-lucide-external-link"
              />
            </div>
          </div>
        </div>
        
        <!-- Message Actions -->
        <div class="flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all duration-300">
          <div class="flex items-center space-x-2">
            <UButton @click="copyMessage" size="xs" variant="ghost" icon="i-lucide-copy" />
            <UButton @click="regenerateMessage" size="xs" variant="ghost" icon="i-lucide-refresh-cw" />
            <UButton v-if="isStreaming" @click="stopGeneration" size="xs" variant="ghost" color="red" icon="i-lucide-square" />
            <UButton @click="exportMessage" size="xs" variant="ghost" icon="i-lucide-download" />
            <UButton @click="likeMessage" size="xs" variant="ghost" icon="i-lucide-heart" />
          </div>
          
          <div class="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
            <Clock class="w-3 h-3" />
            <span>{{ formatTime(message.createdAt) }}</span>
            <span v-if="message.metadata?.model" class="text-blue-600 dark:text-blue-400">
              • {{ message.metadata.model }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User Message -->
    <div v-else class="flex items-start space-x-4 justify-end">
      <div class="max-w-2xl">
        <!-- Message Content -->
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl px-6 py-4 shadow-lg hover:shadow-xl transition-shadow">
          <div class="whitespace-pre-wrap leading-relaxed">
            {{ extractTextFromMessage(message) }}
          </div>
        </div>
        
        <!-- User Files -->
        <div v-if="hasFiles" class="mt-2 space-y-1">
          <div 
            v-for="(filePart, index) in fileParts" 
            :key="`user-file-${index}`"
            class="flex items-center space-x-2 text-xs text-blue-200"
          >
            <Paperclip class="w-3 h-3" />
            <span>{{ filePart.filename || 'Attached file' }}</span>
          </div>
        </div>
        
        <div class="text-xs text-gray-500 dark:text-gray-400 mt-2 text-right">
          {{ formatTime(message.createdAt) }}
        </div>
      </div>
      
      <!-- User Avatar -->
      <div class="w-12 h-12 bg-gradient-to-br from-gray-500 to-gray-600 rounded-2xl flex items-center justify-center shadow-lg">
        <User class="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Loader2, Wrench, ChevronRight, AlertCircle, Clock, 
  User, Paperclip, FileText, Image, File 
} from 'lucide-vue-next'
import { extractTextFromMessage, extractReasoningFromMessage, getToolCallsFromMessage } from '~/composables/useDigiSetuChatSSR'
import ReasoningDisplay from './ReasoningDisplay.vue'
import InteractiveTable from './InteractiveTable.vue'
import InteractiveQuiz from './InteractiveQuiz.vue'
import InteractiveChart from './InteractiveChart.vue'
import InteractiveFlashcards from './InteractiveFlashcards.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import ProviderIcon from '../UI/ProviderIcon.vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  provider: {
    type: String,
    default: 'openai'
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  currentThought: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['regenerate', 'copy', 'export', 'like', 'stop'])

// Message part analysis
const textParts = computed(() => {
  if (!props.message || !props.message.parts || !Array.isArray(props.message.parts)) return []
  return props.message.parts.filter(part => part && part.type === 'text')
})

const reasoningParts = computed(() => {
  if (!props.message || !props.message.parts || !Array.isArray(props.message.parts)) return []
  return props.message.parts.filter(part => part && part.type === 'reasoning')
})

const toolParts = computed(() => {
  if (!props.message || !props.message.parts || !Array.isArray(props.message.parts)) return []
  return props.message.parts.filter(part => part && (part.type?.startsWith('tool-') || part.type === 'dynamic-tool'))
})

const fileParts = computed(() => {
  if (!props.message || !props.message.parts || !Array.isArray(props.message.parts)) return []
  return props.message.parts.filter(part => part && part.type === 'file')
})

// Content checks
const hasTextContent = computed(() => textParts.value.length > 0)
const hasReasoning = computed(() => reasoningParts.value.length > 0)
const hasTools = computed(() => toolParts.value.length > 0)
const hasFiles = computed(() => fileParts.value.length > 0)

// Tool utilities
const getToolDisplayName = (toolPart) => {
  const name = toolPart.toolName || toolPart.type?.replace('tool-', '') || 'Unknown Tool'
  return name.charAt(0).toUpperCase() + name.slice(1).replace(/([A-Z])/g, ' $1')
}

const getToolStateColor = (state) => {
  const colors = {
    'input-streaming': 'blue',
    'input-available': 'yellow',
    'output-available': 'green',
    'output-error': 'red'
  }
  return colors[state] || 'gray'
}

const getToolStateLabel = (state) => {
  const labels = {
    'input-streaming': 'Processing',
    'input-available': 'Ready',
    'output-available': 'Complete',
    'output-error': 'Error'
  }
  return labels[state] || 'Unknown'
}

// Tool type checks
const isTableTool = (toolPart) => {
  return toolPart.toolName === 'createTable' || toolPart.type === 'tool-createTable'
}

const isQuizTool = (toolPart) => {
  return toolPart.toolName === 'createQuiz' || toolPart.type === 'tool-createQuiz'
}

const isChartTool = (toolPart) => {
  return toolPart.toolName === 'createChart' || toolPart.type === 'tool-createChart'
}

const isFlashcardsTool = (toolPart) => {
  return toolPart.toolName === 'createFlashcards' || toolPart.type === 'tool-createFlashcards'
}

// File utilities
const FileIcon = ({ mediaType }) => {
  if (mediaType?.startsWith('image/')) return Image
  if (mediaType?.includes('pdf')) return FileText
  return File
}

const openFile = (url) => {
  if (url.startsWith('data:') || url.startsWith('blob:')) {
    window.open(url, '_blank')
  }
}

// Message actions
const copyMessage = async () => {
  try {
    const textContent = extractTextFromMessage(props.message)
    await navigator.clipboard.writeText(textContent)
    console.log('Message copied to clipboard')
    emit('copy', props.message)
  } catch (error) {
    console.error('Failed to copy message:', error)
  }
}

const regenerateMessage = () => {
  emit('regenerate', props.message.id)
}

const stopGeneration = () => {
  emit('stop')
}

const exportMessage = () => {
  const exportData = {
    id: props.message.id,
    role: props.message.role,
    timestamp: props.message.createdAt,
    content: extractTextFromMessage(props.message),
    reasoning: extractReasoningFromMessage(props.message),
    tools: toolParts.value.map(tool => ({
      name: tool.toolName,
      state: tool.state,
      input: tool.input,
      output: tool.output
    })),
    provider: props.provider
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `message-${props.message.id}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  emit('export', props.message)
}

const likeMessage = () => {
  emit('like', props.message)
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format(new Date(timestamp))
}
</script>

<style scoped>
.message-bubble {
  margin-bottom: 2rem;
}

.content-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  overflow: hidden;
}

.content-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dark .content-card {
  background-color: #1f2937;
  border-color: #374151;
}

.tool-card {
  background: linear-gradient(to bottom right, #eff6ff, #e0e7ff);
  border: 1px solid rgba(59, 130, 246, 0.5);
  border-radius: 0.75rem;
  padding: 1rem;
}

.dark .tool-card {
  background: linear-gradient(to bottom right, rgba(30, 58, 138, 0.1), rgba(67, 56, 202, 0.1));
  border-color: rgba(59, 130, 246, 0.3);
}

.file-attachment {
  transition: all 0.2s;
}

.file-attachment:hover {
  transform: scale(1.02);
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
