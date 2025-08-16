<template>
  <div class="ds-code-block" :class="codeBlockClasses">
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
      
      <div class="ds-code-actions">
        <button 
          class="ds-code-action-btn"
          @click="copyCode"
          :title="copyButtonText"
        >
          <component :is="copyIcon" class="w-4 h-4" />
        </button>
        
        <button 
          v-if="isPreviewable"
          class="ds-code-action-btn"
          @click="togglePreview"
          :title="previewButtonText"
        >
          <component :is="previewIcon" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Code Content -->
    <div class="ds-code-content">
      <pre v-if="showLineNumbers" class="ds-code-pre ds-with-line-numbers"><code 
        class="ds-code-element" 
        :class="languageClass"
        v-html="highlightedCode"
      ></code></pre>
      
      <pre v-else class="ds-code-pre"><code 
        class="ds-code-element" 
        :class="languageClass"
        v-html="highlightedCode"
      ></code></pre>
      
      <!-- Line Numbers -->
      <div v-if="showLineNumbers" class="ds-line-numbers">
        <span 
          v-for="lineNumber in lineCount" 
          :key="lineNumber"
          class="ds-line-number"
        >
          {{ lineNumber }}
        </span>
      </div>
    </div>

    <!-- Live Preview -->
    <div v-if="showPreview && isPreviewable" class="ds-code-preview">
      <div class="ds-preview-header">
        <Eye class="w-4 h-4" />
        <span>Live Preview</span>
      </div>
      <div class="ds-preview-content">
        <iframe 
          v-if="language === 'html' || language === 'xml'"
          :srcdoc="previewContent"
          class="ds-preview-iframe"
          sandbox="allow-scripts"
        ></iframe>
        <div v-else-if="language === 'css'" class="ds-css-preview">
          <div class="ds-css-demo" :style="cssPreviewStyle">
            CSS Preview
          </div>
        </div>
        <div v-else class="ds-preview-placeholder">
          Preview not available for {{ language }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  FileText, Copy, Check, Eye, EyeOff, Code, 
  FileCode, Braces, Terminal, Database
} from 'lucide-vue-next'

const props = defineProps({
  code: {
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
  showLineNumbers: {
    type: Boolean,
    default: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  maxHeight: {
    type: String,
    default: '400px'
  }
})

// Reactive state
const copied = ref(false)
const showPreview = ref(false)
const highlightedCode = ref('')

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
  
  return languageNames[props.language.toLowerCase()] || 
         props.language.charAt(0).toUpperCase() + props.language.slice(1)
})

const languageIcon = computed(() => {
  return languageIcons[props.language.toLowerCase()] || languageIcons.default
})

const languageClass = computed(() => {
  return `language-${props.language.toLowerCase()}`
})

const lineCount = computed(() => {
  return props.code.split('\n').length
})

const codeBlockClasses = computed(() => {
  return {
    'ds-code-with-preview': showPreview.value,
    'ds-code-scrollable': lineCount.value > 20
  }
})

const copyIcon = computed(() => {
  return copied.value ? Check : Copy
})

const copyButtonText = computed(() => {
  return copied.value ? 'Copied!' : 'Copy code'
})

const previewIcon = computed(() => {
  return showPreview.value ? EyeOff : Eye
})

const previewButtonText = computed(() => {
  return showPreview.value ? 'Hide preview' : 'Show preview'
})

const isPreviewable = computed(() => {
  const previewableLanguages = ['html', 'css', 'xml']
  return previewableLanguages.includes(props.language.toLowerCase())
})

const previewContent = computed(() => {
  if (props.language.toLowerCase() === 'html' || props.language.toLowerCase() === 'xml') {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { 
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
              margin: 16px; 
              line-height: 1.5; 
            }
          </style>
        </head>
        <body>
          ${props.code}
        </body>
      </html>
    `
  }
  return props.code
})

const cssPreviewStyle = computed(() => {
  if (props.language.toLowerCase() === 'css') {
    return props.code
  }
  return ''
})

// Methods
const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy code:', error)
  }
}

const togglePreview = () => {
  showPreview.value = !showPreview.value
}

const highlightCode = () => {
  // Basic syntax highlighting without external dependencies
  let highlighted = props.code
  
  // Escape HTML
  highlighted = highlighted
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
  
  // Apply basic highlighting based on language
  switch (props.language.toLowerCase()) {
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
  
  highlightedCode.value = highlighted
}

const highlightJavaScript = (code) => {
  // Keywords
  const keywords = /\b(const|let|var|function|if|else|for|while|return|class|import|export|from|async|await|try|catch|finally)\b/g
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
  const keywords = /\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|finally|with|lambda|and|or|not|in|is)\b/g
  code = code.replace(keywords, '<span class="ds-keyword">$1</span>')
  
  // Strings
  const strings = /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g
  code = code.replace(strings, '<span class="ds-string">$1$2$1</span>')
  
  // Comments
  const comments = /#.*$/gm
  code = code.replace(comments, '<span class="ds-comment">$&</span>')
  
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

// Lifecycle
onMounted(() => {
  highlightCode()
})
</script>

<style scoped>
.ds-code-block {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  line-height: 1.5;
}

/* === CODE HEADER === */
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

.ds-code-actions {
  display: flex;
  align-items: center;
  gap: var(--ds-space-1);
}

.ds-code-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-2);
  background: none;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  border-radius: var(--ds-radius-md);
  transition: all var(--ds-transition-fast);
}

.ds-code-action-btn:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

/* === CODE CONTENT === */
.ds-code-content {
  position: relative;
  overflow-x: auto;
  max-height: v-bind(maxHeight);
  overflow-y: auto;
}

.ds-code-pre {
  margin: 0;
  padding: var(--ds-space-4);
  background: transparent;
  overflow: visible;
}

.ds-with-line-numbers {
  padding-left: calc(var(--ds-space-4) + 40px);
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

/* === LINE NUMBERS === */
.ds-line-numbers {
  position: absolute;
  top: 0;
  left: 0;
  padding: var(--ds-space-4) var(--ds-space-2);
  background: var(--ds-surface-secondary);
  border-right: 1px solid var(--ds-border-primary);
  color: var(--ds-text-muted);
  font-size: var(--ds-text-sm);
  line-height: 1.5;
  user-select: none;
  width: 40px;
  text-align: right;
}

.ds-line-number {
  display: block;
  line-height: 1.5;
}

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

/* === LIVE PREVIEW === */
.ds-code-preview {
  border-top: 1px solid var(--ds-border-primary);
  background: var(--ds-surface-secondary);
}

.ds-preview-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-3) var(--ds-space-4);
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-preview-content {
  background: white;
  min-height: 200px;
}

.ds-preview-iframe {
  width: 100%;
  height: 200px;
  border: none;
  background: white;
}

.ds-css-preview {
  padding: var(--ds-space-4);
  background: white;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ds-css-demo {
  padding: var(--ds-space-4);
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f9f9f9;
  color: #333;
}

.ds-preview-placeholder {
  padding: var(--ds-space-4);
  text-align: center;
  color: var(--ds-text-muted);
  font-style: italic;
}

/* === SCROLLBAR STYLING === */
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
  .ds-code-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--ds-space-2);
  }
  
  .ds-code-actions {
    align-self: flex-end;
  }
  
  .ds-code-pre {
    padding: var(--ds-space-3);
  }
  
  .ds-with-line-numbers {
    padding-left: calc(var(--ds-space-3) + 35px);
  }
  
  .ds-line-numbers {
    width: 35px;
    padding: var(--ds-space-3) var(--ds-space-1);
  }
}

/* === ACCESSIBILITY === */
.ds-code-action-btn:focus-visible {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}

/* === HIGH CONTRAST MODE === */
@media (prefers-contrast: high) {
  .ds-code-block {
    border-width: 2px;
  }
  
  .ds-line-numbers {
    border-right-width: 2px;
  }
}

/* === PRINT STYLES === */
@media print {
  .ds-code-header {
    background: transparent;
    border-bottom: 1px solid #000;
  }
  
  .ds-code-actions {
    display: none;
  }
  
  .ds-code-preview {
    display: none;
  }
  
  .ds-code-element {
    color: #000;
  }
  
  .ds-code-element :deep(.ds-keyword),
  .ds-code-element :deep(.ds-string),
  .ds-code-element :deep(.ds-comment),
  .ds-code-element :deep(.ds-number) {
    color: #000;
  }
}
</style>
