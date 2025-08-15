<template>
  <div class="diagram-viewer">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-2">
        <div class="p-1.5 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
          <GitBranch class="w-4 h-4 text-orange-600 dark:text-orange-400" />
        </div>
        <span class="text-sm font-medium text-orange-700 dark:text-orange-300">{{ diagramType }}</span>
        <UBadge color="orange" variant="soft" size="xs">{{ format }}</UBadge>
      </div>
      <div class="flex items-center space-x-2">
        <UButton @click="toggleFullscreen" size="xs" variant="ghost" icon="i-lucide-maximize-2" />
        <UButton @click="copyDiagram" size="xs" variant="ghost" icon="i-lucide-copy" />
        <UButton @click="downloadDiagram" size="xs" variant="ghost" icon="i-lucide-download" />
      </div>
    </div>
    
    <div 
      :class="[
        'diagram-container',
        'font-mono text-sm bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700',
        'overflow-x-auto whitespace-pre',
        fullscreen ? 'fixed inset-4 z-50 p-8 max-w-none max-h-none' : ''
      ]"
    >
      <div v-if="fullscreen" class="flex justify-end mb-4">
        <UButton @click="toggleFullscreen" size="sm" variant="ghost" icon="i-lucide-minimize-2" />
      </div>
      
      <!-- ASCII Art Diagram -->
      <div v-if="format === 'ascii_art'" class="ascii-diagram" v-html="enhancedDiagram"></div>
      
      <!-- Mermaid Diagram (if supported) -->
      <div v-else-if="format === 'mermaid'" class="mermaid-diagram">
        <div ref="mermaidContainer" class="mermaid" v-html="content"></div>
      </div>
      
      <!-- Flowchart Text -->
      <div v-else-if="format === 'flowchart'" class="flowchart-text">{{ content }}</div>
      
      <!-- Generic Diagram -->
      <div v-else class="generic-diagram">{{ content }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { GitBranch } from 'lucide-vue-next'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  format: {
    type: String,
    default: 'ascii_art'
  },
  metadata: {
    type: Object,
    default: () => ({})
  }
})

const fullscreen = ref(false)
const mermaidContainer = ref(null)

// Detect diagram type from content
const diagramType = computed(() => {
  const content = props.content.toLowerCase()
  
  if (content.includes('flowchart') || content.includes('graph')) return 'Flowchart'
  if (content.includes('┌') || content.includes('┐') || content.includes('└') || content.includes('┘')) return 'Box Diagram'
  if (content.includes('→') || content.includes('←') || content.includes('↑') || content.includes('↓')) return 'Flow Diagram'
  if (content.includes('├') || content.includes('┤') || content.includes('┬') || content.includes('┴')) return 'Tree Diagram'
  if (props.format === 'mermaid') return 'Mermaid Diagram'
  
  return 'Diagram'
})

// Enhanced ASCII art with better formatting
const enhancedDiagram = computed(() => {
  return props.content
    .replace(/([┌┐└┘├┤┬┴│─])/g, '<span class="text-blue-600 dark:text-blue-400 font-bold">$1</span>')
    .replace(/(→|←|↑|↓|⟶|⟵|⟷)/g, '<span class="text-green-600 dark:text-green-400 font-bold">$1</span>')
    .replace(/([{}[\]()])/g, '<span class="text-purple-600 dark:text-purple-400 font-bold">$1</span>')
    .replace(/(\b[A-Z][A-Za-z\s]+\b)/g, '<span class="text-orange-600 dark:text-orange-400 font-semibold">$1</span>')
})

const toggleFullscreen = () => {
  fullscreen.value = !fullscreen.value
  
  if (fullscreen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

const copyDiagram = async () => {
  try {
    await navigator.clipboard.writeText(props.content)
    console.log('Diagram copied to clipboard')
  } catch (error) {
    console.error('Failed to copy diagram:', error)
  }
}

const downloadDiagram = () => {
  const blob = new Blob([props.content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `diagram-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

// Initialize Mermaid if needed
onMounted(async () => {
  if (props.format === 'mermaid' && mermaidContainer.value) {
    try {
      // Dynamically import Mermaid
      const mermaidModule = await import('mermaid')
      const mermaid = mermaidModule.default
      
      // Initialize Mermaid with proper configuration
      mermaid.initialize({ 
        startOnLoad: false, 
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'inherit'
      })
      
      await nextTick()
      
      // Render the diagram
      const { svg } = await mermaid.render('mermaid-diagram-' + Date.now(), props.content)
      if (mermaidContainer.value) {
        mermaidContainer.value.innerHTML = svg
      }
      
    } catch (error) {
      console.log('Mermaid rendering failed, displaying as text:', error)
      // Fallback to text display with monospace font
      if (mermaidContainer.value) {
        mermaidContainer.value.innerHTML = `<pre style="font-family: monospace; white-space: pre-wrap;">${props.content}</pre>`
      }
    }
  }
})
</script>

<style scoped>
.diagram-container {
  transition: all 0.3s ease;
  line-height: 1.2;
}

.ascii-diagram {
  font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
  line-height: 1.1;
  letter-spacing: 0.05em;
}

.mermaid-diagram {
  text-align: center;
}

.flowchart-text {
  font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
  white-space: pre-wrap;
}

.generic-diagram {
  font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
  white-space: pre-wrap;
}

/* Fullscreen overlay */
.diagram-container.fixed {
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
}

.dark .diagram-container.fixed {
  background: rgba(0, 0, 0, 0.98);
}
</style>
