<template>
  <div class="ds-progressive-code-container" :class="containerClasses">
    <!-- Code Controls -->
    <div v-if="showControls" class="ds-code-controls">
      <div class="ds-control-group">
        <button 
          @click="toggleAnimation" 
          class="ds-control-btn"
          :class="{ 'active': animationsEnabled }"
        >
          <Zap class="w-4 h-4" />
          {{ animationsEnabled ? 'Live' : 'Static' }}
        </button>
        
        <button 
          @click="completeRendering" 
          class="ds-control-btn"
          v-if="isRendering"
        >
          <FastForward class="w-4 h-4" />
          Complete
        </button>
        
        <button 
          @click="copyCode" 
          class="ds-control-btn"
          :title="copyButtonText"
        >
          <component :is="copyIcon" class="w-4 h-4" />
        </button>
      </div>
      
      <div class="ds-progress-indicator" v-if="isRendering">
        <div class="ds-progress-bar">
          <div 
            class="ds-progress-fill" 
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
        <span class="ds-progress-text">
          {{ itemsRendered }}/{{ totalItems }} lines
        </span>
      </div>
    </div>

    <!-- Code Header -->
    <div v-if="showHeader" class="ds-code-header">
      <div class="ds-code-info">
        <div class="ds-code-language">
          <component :is="languageIcon" class="w-4 h-4" />
          <span>{{ displayLanguage }}</span>
        </div>
        <div v-if="filename" class="ds-code-filename">
          <FileText class="w-3 h-3" />
          <span>{{ filename }}</span>
        </div>
      </div>
      
      <div class="ds-typing-indicator" v-if="isStreaming && animationsEnabled">
        <div class="ds-typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="ds-typing-text">Generating code...</span>
      </div>
    </div>

    <!-- Code Content -->
    <div class="ds-code-content" :style="{ maxHeight: maxHeight }">
      <!-- Loading State -->
      <div v-if="!hasContent" class="ds-code-loading">
        <div class="ds-loading-skeleton">
          <div class="ds-skeleton-line" v-for="n in 5" :key="n"></div>
        </div>
      </div>

      <!-- Progressive Code -->
      <div v-else class="ds-code-wrapper">
        <!-- Line Numbers -->
        <div v-if="showLineNumbers" class="ds-line-numbers">
          <span 
            v-for="(line, index) in visibleLines"
            :key="`line-num-${line.number || index + 1}`"
            class="ds-line-number"
            :class="getLineNumberClasses(line, index)"
          >
            {{ line.number || index + 1 }}
          </span>
          
          <!-- Current line being painted -->
          <span 
            v-if="isStreaming && currentPaintingLine"
            class="ds-line-number ds-painting-line-number"
          >
            {{ (visibleLines.length || 0) + 1 }}
          </span>
        </div>

        <!-- Code Lines -->
        <pre class="ds-code-pre" :class="{ 'ds-with-line-numbers': showLineNumbers }"><code 
          class="ds-code-element" 
          :class="languageClass"
        ><span
          v-for="(line, index) in visibleLines"
          :key="`line-${line.id || index}`"
          class="ds-code-line"
          :class="getLineClasses(line, index)"
          :style="getLineAnimationStyle(index)"
          v-html="highlightLine(line.content || '')"
        ></span><span
          v-if="isStreaming && currentPaintingLine"
          class="ds-code-line ds-painting-line"
        ><span 
          class="ds-painting-content"
          v-html="highlightLine(currentPaintingLine.content || '')"
        ></span><span 
          class="ds-typing-cursor"
          v-if="animationsEnabled"
        >█</span></span></code></pre>
      </div>

      <!-- Fallback Content -->
      <div v-if="renderingError && !canRender" class="ds-fallback-content">
        <div class="ds-fallback-header">
          <AlertTriangle class="w-4 h-4" />
          <span>Displaying raw content</span>
        </div>
        <pre class="ds-raw-content">{{ rawContent }}</pre>
      </div>
    </div>

    <!-- Code Stats -->
    <div v-if="hasContent && showStats" class="ds-code-stats">
      <span>{{ totalItems }} lines</span>
      <span v-if="detectedLanguage">{{ displayLanguage }}</span>
      <span v-if="characterCount">{{ characterCount }} chars</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { 
  FileText, 
  Copy, 
  Check, 
  Code, 
  FileCode, 
  Braces, 
  Terminal, 
  Database,
  AlertTriangle,
  Zap,
  FastForward
} from 'lucide-vue-next'
import { useProgressiveRenderer } from '@/composables/useProgressiveRenderer'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  language: {
    type: String,
    default: 'text'
  },
  filename: {
    type: String,
    default: null
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  showLineNumbers: {
    type: Boolean,
    default: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showControls: {
    type: Boolean,
    default: true
  },
  showStats: {
    type: Boolean,
    default: true
  },
  maxHeight: {
    type: String,
    default: '500px'
  },
  animationDelay: {
    type: Number,
    default: 50
  },
  chunkSize: {
    type: Number,
    default: 5
  }
})

// Progressive renderer
const { createProgressiveRenderer } = useProgressiveRenderer()
const renderer = createProgressiveRenderer('code', {
  chunkSize: props.chunkSize,
  renderDelay: props.animationDelay,
  enableAnimations: true,
  fallbackMode: 'graceful'
})

// Destructure renderer state and methods
const {
  rawContent,
  parsedContent,
  visibleItems,
  renderProgress,
  isRendering,
  renderingError,
  hasContent,
  canRender,
  progressPercentage,
  itemsRendered,
  totalItems,
  updateContent,
  completeRendering: rendererCompleteRendering,
  stopRendering
} = renderer

// Local state
const copied = ref(false)
const animationsEnabled = ref(true)

// Language icons mapping
const languageIcons = {
  javascript: Code,
  typescript: Code,
  python: FileCode,
  java: FileCode,
  cpp: FileCode,
  c: FileCode,
  html: Braces,
  xml: Braces,
  css: Braces,
  scss: Braces,
  json: Braces,
  yaml: FileText,
  sql: Database,
  bash: Terminal,
  shell: Terminal,
  powershell: Terminal,
  default: Code
}

// Computed properties
const detectedLanguage = computed(() => {
  return parsedContent.value?.language || props.language
})

const displayLanguage = computed(() => {
  const languageNames = {
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    python: 'Python',
    java: 'Java',
    cpp: 'C++',
    c: 'C',
    html: 'HTML',
    xml: 'XML',
    css: 'CSS',
    scss: 'SCSS',
    json: 'JSON',
    yaml: 'YAML',
    sql: 'SQL',
    bash: 'Bash',
    shell: 'Shell',
    powershell: 'PowerShell'
  }
  
  return languageNames[detectedLanguage.value.toLowerCase()] || 
         detectedLanguage.value.charAt(0).toUpperCase() + detectedLanguage.value.slice(1)
})

const languageIcon = computed(() => {
  return languageIcons[detectedLanguage.value.toLowerCase()] || languageIcons.default
})

const languageClass = computed(() => {
  return `language-${detectedLanguage.value.toLowerCase()}`
})

const containerClasses = computed(() => {
  return {
    'ds-code-streaming': props.isStreaming,
    'ds-code-animated': animationsEnabled.value,
    'ds-code-complete': !props.isStreaming && !isRendering.value
  }
})

const visibleLines = computed(() => {
  return visibleItems.value || []
})

const currentPaintingLine = computed(() => {
  if (!props.isStreaming || !parsedContent.value) return null
  
  // Get the line that's currently being painted
  const allLines = parsedContent.value.lines || []
  const visibleCount = visibleItems.value.length
  
  if (visibleCount < allLines.length) {
    return allLines[visibleCount] || null
  }
  
  return null
})

const copyIcon = computed(() => {
  return copied.value ? Check : Copy
})

const copyButtonText = computed(() => {
  return copied.value ? 'Copied!' : 'Copy code'
})

const characterCount = computed(() => {
  return rawContent.value.length
})

// Methods
const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(rawContent.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy code:', error)
  }
}

const toggleAnimation = () => {
  animationsEnabled.value = !animationsEnabled.value
}

const completeRendering = () => {
  rendererCompleteRendering()
}

const getLineClasses = (line, index) => {
  return {
    'ds-line-even': index % 2 === 0,
    'ds-line-odd': index % 2 === 1,
    'ds-line-new': animationsEnabled.value && isRendering.value
  }
}

const getLineNumberClasses = (line, index) => {
  return {
    'ds-line-number-even': index % 2 === 0,
    'ds-line-number-odd': index % 2 === 1
  }
}

const getLineAnimationStyle = (index) => {
  if (!animationsEnabled.value || !isRendering.value) return {}
  
  return {
    animationDelay: `${index * 30}ms`,
    animationDuration: '0.3s'
  }
}

const highlightLine = (content) => {
  if (!content) return ''
  
  // CRITICAL: Only apply highlighting when streaming is complete (END tag received)
  // This implements the user requirement: "showcase without highlighting until end and at the end highlight it"
  if (props.isStreaming) {
    // Show plain text during streaming - no highlighting
    return escapeHtml(content)
  }
  
  // Apply syntax highlighting only after streaming is complete
  let highlighted = escapeHtml(content)
  
  // Apply language-specific highlighting
  switch (detectedLanguage.value.toLowerCase()) {
    case 'javascript':
    case 'typescript':
      highlighted = highlightJavaScript(highlighted)
      break
    case 'python':
      highlighted = highlightPython(highlighted)
      break
    case 'html':
    case 'xml':
      highlighted = highlightHTML(highlighted)
      break
    case 'css':
    case 'scss':
      highlighted = highlightCSS(highlighted)
      break
    case 'json':
      highlighted = highlightJSON(highlighted)
      break
    default:
      // No highlighting for unknown languages
      break
  }
  
  return highlighted
}

const escapeHtml = (text) => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const highlightJavaScript = (code) => {
  // Keywords
  const keywords = /\b(const|let|var|function|if|else|for|while|return|class|import|export|from|async|await|try|catch|finally|this|new|typeof|instanceof)\b/g
  code = code.replace(keywords, '<span class="ds-keyword">$1</span>')
  
  // Strings
  const strings = /(["'`])((?:\\.|(?!\1)[^\\])*?)\1/g
  code = code.replace(strings, '<span class="ds-string">$1$2$1</span>')
  
  // Comments
  const comments = /(\/\/.*$|\/\*[\s\S]*?\*\/)/gm
  code = code.replace(comments, '<span class="ds-comment">$1</span>')
  
  // Numbers
  const numbers = /\b\d+\.?\d*\b/g
  code = code.replace(numbers, '<span class="ds-number">$&</span>')
  
  return code
}

const highlightPython = (code) => {
  // Keywords
  const keywords = /\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|finally|with|lambda|and|or|not|in|is|None|True|False)\b/g
  code = code.replace(keywords, '<span class="ds-keyword">$1</span>')
  
  // Strings
  const strings = /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g
  code = code.replace(strings, '<span class="ds-string">$1$2$1</span>')
  
  // Comments
  const comments = /#.*$/gm
  code = code.replace(comments, '<span class="ds-comment">$&</span>')
  
  // Numbers
  const numbers = /\b\d+\.?\d*\b/g
  code = code.replace(numbers, '<span class="ds-number">$&</span>')
  
  return code
}

const highlightHTML = (code) => {
  // Tags
  const tags = /(&lt;\/?)([a-zA-Z][a-zA-Z0-9]*)(.*?)(&gt;)/g
  code = code.replace(tags, '<span class="ds-tag">$1</span><span class="ds-tag-name">$2</span><span class="ds-attribute">$3</span><span class="ds-tag">$4</span>')
  
  return code
}

const highlightCSS = (code) => {
  // Selectors
  const selectors = /^([.#]?[a-zA-Z][a-zA-Z0-9-_]*)\s*{/gm
  code = code.replace(selectors, '<span class="ds-selector">$1</span> {')
  
  // Properties
  const properties = /([a-zA-Z-]+)(\s*:\s*)/g
  code = code.replace(properties, '<span class="ds-property">$1</span>$2')
  
  // Values
  const values = /:\s*([^;]+);/g
  code = code.replace(values, ': <span class="ds-value">$1</span>;')
  
  return code
}

const highlightJSON = (code) => {
  // Keys
  const keys = /"([^"]+)"(\s*:)/g
  code = code.replace(keys, '<span class="ds-json-key">"$1"</span>$2')
  
  // Strings
  const strings = /:\s*"([^"]+)"/g
  code = code.replace(strings, ': <span class="ds-string">"$1"</span>')
  
  // Numbers
  const numbers = /:\s*(\d+\.?\d*)/g
  code = code.replace(numbers, ': <span class="ds-number">$1</span>')
  
  // Booleans
  const booleans = /:\s*(true|false|null)/g
  code = code.replace(booleans, ': <span class="ds-boolean">$1</span>')
  
  return code
}

// Watch for content changes
watch(() => props.content, (newContent) => {
  updateContent(newContent, props.isStreaming)
}, { immediate: true })

watch(() => props.isStreaming, (streaming) => {
  if (streaming) {
    updateContent(props.content, true)
  } else {
    // Complete rendering when streaming stops
    setTimeout(() => {
      completeRendering()
    }, 300)
  }
})

// Lifecycle
onMounted(() => {
  updateContent(props.content, props.isStreaming)
})
</script>

<style scoped>
.ds-progressive-code-container {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  line-height: 1.5;
}

/* === CONTROLS === */
.ds-code-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-control-group {
  display: flex;
  gap: var(--ds-space-2);
}

.ds-control-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-control-btn:hover {
  background: var(--ds-surface-hover);
}

.ds-control-btn.active {
  background: var(--ds-primary);
  color: white;
  border-color: var(--ds-primary);
}

.ds-progress-indicator {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-progress-bar {
  width: 120px;
  height: 4px;
  background: var(--ds-border-primary);
  border-radius: var(--ds-radius-full);
  overflow: hidden;
}

.ds-progress-fill {
  height: 100%;
  background: var(--ds-primary);
  transition: width var(--ds-transition-fast);
}

.ds-progress-text {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
  min-width: 80px;
}

/* === HEADER === */
.ds-code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-3) var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-code-info {
  display: flex;
  align-items: center;
  gap: var(--ds-space-4);
}

.ds-code-language {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-code-filename {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-text-muted);
  font-size: var(--ds-text-sm);
}

.ds-typing-indicator {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  color: var(--ds-primary);
}

.ds-typing-dots {
  display: flex;
  gap: 4px;
}

.ds-typing-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--ds-primary);
  animation: dotPulse 1.4s infinite ease-in-out;
}

.ds-typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.ds-typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.ds-typing-text {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
}

/* === CONTENT === */
.ds-code-content {
  position: relative;
  overflow-x: auto;
  overflow-y: auto;
}

.ds-code-wrapper {
  display: flex;
  position: relative;
}

.ds-line-numbers {
  padding: var(--ds-space-4) var(--ds-space-2);
  background: var(--ds-surface-secondary);
  border-right: 1px solid var(--ds-border-primary);
  color: var(--ds-text-muted);
  font-size: var(--ds-text-sm);
  line-height: 1.5;
  user-select: none;
  min-width: 50px;
  text-align: right;
  flex-shrink: 0;
}

.ds-line-number {
  display: block;
  line-height: 1.5;
  transition: color var(--ds-transition-fast);
}

.ds-painting-line-number {
  color: var(--ds-primary);
  font-weight: var(--ds-font-medium);
}

.ds-code-pre {
  margin: 0;
  padding: var(--ds-space-4);
  background: transparent;
  overflow: visible;
  flex: 1;
}

.ds-code-element {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  color: var(--ds-text-primary);
  background: transparent;
  border: none;
  outline: none;
  white-space: pre;
  word-wrap: normal;
  overflow-wrap: normal;
}

.ds-code-line {
  display: block;
  line-height: 1.5;
}

/* === PROGRESSIVE RENDERING === */
.ds-code-animated .ds-code-line {
  animation: fadeInLeft 0.3s ease-out forwards;
  opacity: 0;
  transform: translateX(-10px);
}

@keyframes fadeInLeft {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.ds-painting-line {
  background: color-mix(in srgb, var(--ds-primary) 5%, transparent);
  position: relative;
}

.ds-painting-content {
  display: inline;
}

.ds-typing-cursor {
  display: inline;
  color: var(--ds-primary);
  animation: blink 1s infinite;
  margin-left: 2px;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* === LOADING === */
.ds-code-loading {
  padding: var(--ds-space-4);
}

.ds-loading-skeleton {
  animation: pulse 2s infinite;
}

.ds-skeleton-line {
  height: 20px;
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-sm);
  margin-bottom: var(--ds-space-2);
}

.ds-skeleton-line:nth-child(1) { width: 80%; }
.ds-skeleton-line:nth-child(2) { width: 60%; }
.ds-skeleton-line:nth-child(3) { width: 90%; }
.ds-skeleton-line:nth-child(4) { width: 70%; }
.ds-skeleton-line:nth-child(5) { width: 85%; }

/* === SYNTAX HIGHLIGHTING === */
.ds-code-element :deep(.ds-keyword) {
  color: var(--ds-primary);
  font-weight: var(--ds-font-medium);
}

.ds-code-element :deep(.ds-string) {
  color: var(--ds-secondary);
}

.ds-code-element :deep(.ds-comment) {
  color: var(--ds-text-muted);
  font-style: italic;
}

.ds-code-element :deep(.ds-number) {
  color: var(--ds-accent);
}

.ds-code-element :deep(.ds-tag) {
  color: var(--ds-primary);
}

.ds-code-element :deep(.ds-tag-name) {
  color: var(--ds-danger);
  font-weight: var(--ds-font-medium);
}

.ds-code-element :deep(.ds-attribute) {
  color: var(--ds-info);
}

.ds-code-element :deep(.ds-selector) {
  color: var(--ds-primary);
  font-weight: var(--ds-font-medium);
}

.ds-code-element :deep(.ds-property) {
  color: var(--ds-info);
}

.ds-code-element :deep(.ds-value) {
  color: var(--ds-secondary);
}

.ds-code-element :deep(.ds-json-key) {
  color: var(--ds-primary);
  font-weight: var(--ds-font-medium);
}

.ds-code-element :deep(.ds-boolean) {
  color: var(--ds-accent);
  font-weight: var(--ds-font-medium);
}

/* === FALLBACK === */
.ds-fallback-content {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
}

.ds-fallback-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-3);
  color: var(--ds-warning);
  font-weight: var(--ds-font-medium);
}

.ds-raw-content {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-3);
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  white-space: pre-wrap;
  overflow-x: auto;
}

/* === STATS === */
.ds-code-stats {
  display: flex;
  gap: var(--ds-space-4);
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-top: 1px solid var(--ds-border-primary);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
}

/* === SCROLLBAR === */
.ds-code-content::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.ds-code-content::-webkit-scrollbar-track {
  background: var(--ds-surface-secondary);
}

.ds-code-content::-webkit-scrollbar-thumb {
  background: var(--ds-border-secondary);
  border-radius: var(--ds-radius-full);
}

.ds-code-content::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-code-controls {
    flex-direction: column;
    gap: var(--ds-space-3);
    align-items: stretch;
  }
  
  .ds-progress-indicator {
    justify-content: space-between;
  }
  
  .ds-code-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--ds-space-2);
  }
  
  .ds-code-pre {
    padding: var(--ds-space-3);
  }
  
  .ds-line-numbers {
    min-width: 40px;
    padding: var(--ds-space-3) var(--ds-space-1);
  }
}
</style>
