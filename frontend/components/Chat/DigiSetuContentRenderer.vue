<template>
  <div class="ds-content-renderer" :class="contentTypeClass">
    <!-- Text Content -->
    <div v-if="contentType === 'text'" class="ds-text-content" v-html="processedContent"></div>

    <!-- Markdown Content -->
    <div v-else-if="contentType === 'markdown'" class="ds-markdown-content">
      <DigiSetuMarkdown :content="content" />
    </div>

    <!-- Code Content -->
    <div v-else-if="contentType === 'code'" class="ds-code-content">
      <DigiSetuCodeBlock 
        :code="content" 
        :language="metadata?.language || 'text'"
        :filename="metadata?.filename"
        :show-line-numbers="metadata?.showLineNumbers !== false"
      />
    </div>

    <!-- JSON Content -->
    <div v-else-if="contentType === 'json'" class="ds-json-content">
      <DigiSetuJsonViewer 
        :data="parsedJsonContent" 
        :collapsed="metadata?.collapsed !== false"
      />
    </div>

    <!-- Table Content -->
    <div v-else-if="contentType === 'table'" class="ds-table-content">
      <DigiSetuTable 
        :data="parsedTableContent"
        :headers="metadata?.headers"
        :sortable="metadata?.sortable !== false"
        :searchable="metadata?.searchable !== false"
      />
    </div>

    <!-- Diagram Content -->
    <div v-else-if="contentType === 'diagram'" class="ds-diagram-content">
      <DigiSetuDiagram 
        :content="content"
        :type="metadata?.diagramType || 'mermaid'"
      />
    </div>

    <!-- Image Content -->
    <div v-else-if="contentType === 'image'" class="ds-image-content">
      <DigiSetuImage 
        :src="content"
        :alt="metadata?.alt || 'Generated image'"
        :caption="metadata?.caption"
        :zoomable="metadata?.zoomable !== false"
      />
    </div>

    <!-- Audio Content -->
    <div v-else-if="contentType === 'audio'" class="ds-audio-content">
      <DigiSetuAudio 
        :src="content"
        :title="metadata?.title"
        :transcript="metadata?.transcript"
      />
    </div>

    <!-- Video Content -->
    <div v-else-if="contentType === 'video'" class="ds-video-content">
      <DigiSetuVideo 
        :src="content"
        :title="metadata?.title"
        :poster="metadata?.poster"
        :captions="metadata?.captions"
      />
    </div>

    <!-- File Content -->
    <div v-else-if="contentType === 'file'" class="ds-file-content">
      <DigiSetuFile 
        :file="parsedFileContent"
        :preview="metadata?.preview !== false"
      />
    </div>

    <!-- Vision/Image Analysis Content -->
    <div v-else-if="contentType === 'vision'" class="ds-vision-content">
      <DigiSetuVisionRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Audio Transcription Content -->
    <div v-else-if="contentType === 'audio_transcription'" class="ds-audio-transcription-content">
      <DigiSetuAudioRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Audio Analysis Content -->
    <div v-else-if="contentType === 'audio_analysis'" class="ds-audio-analysis-content">
      <DigiSetuAudioRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Tool Result Content -->
    <div v-else-if="contentType === 'tool'" class="ds-tool-content">
      <DigiSetuToolRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Batch Tools Content -->
    <div v-else-if="contentType === 'batch_tools'" class="ds-batch-tools-content">
      <DigiSetuToolRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Search Results Content -->
    <div v-else-if="contentType === 'search'" class="ds-search-content">
      <DigiSetuSearchRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- News Search Content -->
    <div v-else-if="contentType === 'news'" class="ds-news-content">
      <DigiSetuSearchRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Reasoning Chain-of-Thought -->
    <div v-else-if="contentType === 'reasoning'" class="ds-reasoning-content">
      <DigiSetuReasoningRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Structured Output -->
    <div v-else-if="contentType === 'structured_output'" class="ds-structured-content">
      <DigiSetuStructuredRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Live Search -->
    <div v-else-if="contentType === 'live_search'" class="ds-live-search-content">
      <DigiSetuLiveSearchRenderer 
        :content="content"
        :metadata="metadata"
      />
    </div>

    <!-- Interactive Content -->
    <div v-else-if="contentType === 'interactive'" class="ds-interactive-content">
      <component 
        :is="getInteractiveComponent()" 
        v-bind="interactiveProps"
      />
    </div>

    <!-- Error/Fallback Content -->
    <div v-else class="ds-fallback-content">
      <div class="ds-fallback-header">
        <AlertCircle class="w-4 h-4" />
        <span>Unsupported content type: {{ contentType }}</span>
      </div>
      <div class="ds-fallback-raw">
        <pre>{{ content }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { AlertCircle } from 'lucide-vue-next'

// Import all the content renderer components
import DigiSetuMarkdown from './DigiSetuMarkdown.vue'
import DigiSetuCodeBlock from './DigiSetuCodeBlock.vue'
import DigiSetuJsonViewer from './DigiSetuJsonViewer.vue'
import DigiSetuTable from './DigiSetuTable.vue'
import DigiSetuDiagram from './DigiSetuDiagram.vue'
import DigiSetuImage from './DigiSetuImage.vue'
import DigiSetuAudio from './DigiSetuAudio.vue'
import DigiSetuVideo from './DigiSetuVideo.vue'
import DigiSetuFile from './DigiSetuFile.vue'
// Import new multimodal renderer components
import DigiSetuVisionRenderer from './DigiSetuVisionRenderer.vue'
import DigiSetuAudioRenderer from './DigiSetuAudioRenderer.vue'
import DigiSetuToolRenderer from './DigiSetuToolRenderer.vue'
import DigiSetuSearchRenderer from './DigiSetuSearchRenderer.vue'
// Import advanced feature renderers
import DigiSetuReasoningRenderer from './DigiSetuReasoningRenderer.vue'
import DigiSetuStructuredRenderer from './DigiSetuStructuredRenderer.vue'
import DigiSetuLiveSearchRenderer from './DigiSetuLiveSearchRenderer.vue'

const props = defineProps({
  content: {
    type: [String, Object, Array],
    required: true
  },
  contentType: {
    type: String,
    default: 'text'
  },
  metadata: {
    type: Object,
    default: () => ({})
  },
  provider: {
    type: String,
    default: null
  }
})

// Computed properties
const contentTypeClass = computed(() => {
  return `ds-content-${props.contentType}`
})

const processedContent = computed(() => {
  if (props.contentType !== 'text') return props.content
  
  // Basic text processing - convert URLs to links, etc.
  let processed = String(props.content)
  
  // Convert URLs to clickable links
  const urlRegex = /(https?:\/\/[^\s]+)/g
  processed = processed.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="ds-link">$1</a>')
  
  // Convert line breaks to <br> tags
  processed = processed.replace(/\n/g, '<br>')
  
  return processed
})

const parsedJsonContent = computed(() => {
  if (props.contentType !== 'json') return null
  
  try {
    if (typeof props.content === 'string') {
      return JSON.parse(props.content)
    }
    return props.content
  } catch (error) {
    console.error('Failed to parse JSON content:', error)
    return { error: 'Invalid JSON content' }
  }
})

const parsedTableContent = computed(() => {
  if (props.contentType !== 'table') return null
  
  try {
    if (typeof props.content === 'string') {
      // Try to parse CSV or other table formats
      const lines = props.content.split('\n')
      const headers = lines[0]?.split(',') || []
      const rows = lines.slice(1).map(line => line.split(','))
      return { headers, rows }
    }
    return props.content
  } catch (error) {
    console.error('Failed to parse table content:', error)
    return { headers: [], rows: [] }
  }
})

const parsedFileContent = computed(() => {
  if (props.contentType !== 'file') return null
  
  if (typeof props.content === 'string') {
    // Assume it's a file URL or path
    return {
      url: props.content,
      name: props.metadata?.filename || 'file',
      type: props.metadata?.mimeType || 'application/octet-stream',
      size: props.metadata?.size || 0
    }
  }
  
  return props.content
})

const interactiveProps = computed(() => {
  if (props.contentType !== 'interactive') return {}
  
  return {
    ...props.metadata,
    content: props.content,
    provider: props.provider
  }
})

// Methods
const getInteractiveComponent = () => {
  const interactiveType = props.metadata?.interactiveType || 'default'
  
  const componentMap = {
    'quiz': 'DigiSetuQuiz',
    'poll': 'DigiSetuPoll', 
    'chart': 'DigiSetuChart',
    'calculator': 'DigiSetuCalculator',
    'form': 'DigiSetuForm',
    'game': 'DigiSetuGame',
    'default': 'DigiSetuInteractiveDefault'
  }
  
  return componentMap[interactiveType] || componentMap.default
}
</script>

<style scoped>
.ds-content-renderer {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

/* === TEXT CONTENT === */
.ds-text-content {
  color: var(--ds-text-primary);
  line-height: var(--ds-leading-relaxed);
  word-wrap: break-word;
  overflow-wrap: break-word;
  /* Ensure line breaks are preserved while allowing normal wrapping */
  white-space: pre-line;
}

.ds-text-content :deep(.ds-link) {
  color: var(--ds-primary);
  text-decoration: underline;
  text-decoration-color: color-mix(in srgb, var(--ds-primary) 50%, transparent);
  transition: all var(--ds-transition-fast);
}

.ds-text-content :deep(.ds-link:hover) {
  text-decoration-color: var(--ds-primary);
  background: color-mix(in srgb, var(--ds-primary) 5%, transparent);
  padding: 2px 4px;
  border-radius: var(--ds-radius-sm);
  margin: -2px -4px;
}

/* === MARKDOWN CONTENT === */
.ds-markdown-content {
  /* Styles will be handled by DigiSetuMarkdown component */
}

/* === CODE CONTENT === */
.ds-code-content {
  margin: var(--ds-space-3) 0;
}

/* === JSON CONTENT === */
.ds-json-content {
  margin: var(--ds-space-3) 0;
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
}

/* === TABLE CONTENT === */
.ds-table-content {
  margin: var(--ds-space-3) 0;
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
}

/* === DIAGRAM CONTENT === */
.ds-diagram-content {
  margin: var(--ds-space-4) 0;
  text-align: center;
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  padding: var(--ds-space-4);
}

/* === IMAGE CONTENT === */
.ds-image-content {
  margin: var(--ds-space-4) 0;
  text-align: center;
}

/* === AUDIO CONTENT === */
.ds-audio-content {
  margin: var(--ds-space-3) 0;
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  padding: var(--ds-space-4);
}

/* === VIDEO CONTENT === */
.ds-video-content {
  margin: var(--ds-space-4) 0;
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
}

/* === FILE CONTENT === */
.ds-file-content {
  margin: var(--ds-space-3) 0;
}

/* === MULTIMODAL CONTENT === */
.ds-vision-content {
  margin: var(--ds-space-4) 0;
}

.ds-audio-transcription-content,
.ds-audio-analysis-content {
  margin: var(--ds-space-4) 0;
}

.ds-tool-content,
.ds-batch-tools-content {
  margin: var(--ds-space-4) 0;
}

.ds-search-content,
.ds-news-content {
  margin: var(--ds-space-4) 0;
}

/* === INTERACTIVE CONTENT === */
.ds-interactive-content {
  margin: var(--ds-space-4) 0;
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
}

/* === FALLBACK CONTENT === */
.ds-fallback-content {
  margin: var(--ds-space-3) 0;
  background: color-mix(in srgb, var(--ds-danger) 5%, transparent);
  border: 1px solid color-mix(in srgb, var(--ds-danger) 20%, transparent);
  border-radius: var(--ds-radius-lg);
  padding: var(--ds-space-4);
}

.ds-fallback-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-danger);
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  margin-bottom: var(--ds-space-3);
}

.ds-fallback-raw {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-3);
  overflow-x: auto;
}

.ds-fallback-raw pre {
  margin: 0;
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* === CONTENT TYPE SPECIFIC STYLES === */

/* Text content variations */
.ds-content-text.ds-content-large {
  font-size: var(--ds-text-lg);
  line-height: var(--ds-leading-relaxed);
}

.ds-content-text.ds-content-small {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
}

/* Code content variations */
.ds-content-code.ds-content-inline {
  display: inline;
  margin: 0;
}

.ds-content-code.ds-content-inline :deep(.ds-code-block) {
  display: inline;
  padding: 2px var(--ds-space-1);
  border-radius: var(--ds-radius-sm);
  font-size: 0.9em;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .ds-diagram-content,
  .ds-image-content,
  .ds-video-content,
  .ds-interactive-content {
    margin: var(--ds-space-3) 0;
    padding: var(--ds-space-3);
  }
  
  .ds-fallback-raw {
    font-size: var(--ds-text-xs);
  }
}

/* === ACCESSIBILITY === */
.ds-text-content :deep(.ds-link:focus-visible) {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === HIGH CONTRAST MODE === */
@media (prefers-contrast: high) {
  .ds-json-content,
  .ds-table-content,
  .ds-diagram-content,
  .ds-audio-content,
  .ds-video-content,
  .ds-interactive-content {
    border-width: 2px;
  }
  
  .ds-fallback-content {
    border-width: 2px;
  }
}

/* === PRINT STYLES === */
@media print {
  .ds-interactive-content,
  .ds-audio-content,
  .ds-video-content {
    display: none;
  }
  
  .ds-text-content :deep(.ds-link) {
    color: inherit;
    text-decoration: underline;
  }
  
  .ds-text-content :deep(.ds-link::after) {
    content: " (" attr(href) ")";
    font-size: 0.8em;
    color: var(--ds-text-muted);
  }
}
</style>
