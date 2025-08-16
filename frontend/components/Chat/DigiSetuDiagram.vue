<template>
  <div class="ds-diagram-container">
    <div class="ds-diagram-header">
      <span class="ds-diagram-title">{{ diagramTitle }}</span>
    </div>
    <div ref="diagramRef" class="ds-diagram-content" :id="diagramId"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'mermaid'
  }
})

const diagramRef = ref(null)
const diagramId = ref(`diagram-${Math.random().toString(36).substr(2, 9)}`)

const diagramTitle = computed(() => {
  const typeMap = {
    'mermaid': 'Mermaid Diagram',
    'flowchart': 'Flowchart',
    'sequence': 'Sequence Diagram',
    'class': 'Class Diagram',
    'state': 'State Diagram',
    'pie': 'Pie Chart',
    'gantt': 'Gantt Chart'
  }
  return typeMap[props.type] || 'Diagram'
})

const renderMermaidDiagram = async () => {
  if (typeof window === 'undefined') return
  
  try {
    // Dynamically import mermaid
    const mermaid = await import('mermaid')
    
    // Initialize mermaid with configuration
    mermaid.default.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      themeVariables: {
        primaryColor: '#3b82f6',
        primaryTextColor: '#1f2937',
        primaryBorderColor: '#e5e7eb',
        lineColor: '#6b7280',
        secondaryColor: '#f3f4f6',
        tertiaryColor: '#ffffff'
      }
    })
    
    // Clear previous content
    if (diagramRef.value) {
      diagramRef.value.innerHTML = ''
    }
    
    // Render the diagram
    const { svg } = await mermaid.default.render(diagramId.value, props.content)
    
    if (diagramRef.value) {
      diagramRef.value.innerHTML = svg
    }
  } catch (error) {
    console.error('Mermaid rendering error:', error)
    if (diagramRef.value) {
      diagramRef.value.innerHTML = `
        <div class="ds-diagram-error">
          <p>Failed to render diagram</p>
          <pre>${props.content}</pre>
        </div>
      `
    }
  }
}

onMounted(async () => {
  await nextTick()
  if (props.type === 'mermaid') {
    await renderMermaidDiagram()
  }
})

// Re-render when content changes
watch(() => props.content, async () => {
  await nextTick()
  if (props.type === 'mermaid') {
    await renderMermaidDiagram()
  }
})
</script>

<style scoped>
.ds-diagram-container {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
  margin: var(--ds-space-3) 0;
}

.ds-diagram-header {
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-diagram-title {
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.ds-diagram-content {
  padding: var(--ds-space-4);
  text-align: center;
  overflow-x: auto;
  background: var(--ds-surface-primary);
}

.ds-diagram-content :deep(svg) {
  max-width: 100%;
  height: auto;
}

.ds-diagram-error {
  color: var(--ds-danger);
  text-align: left;
}

.ds-diagram-error p {
  margin-bottom: var(--ds-space-2);
  font-weight: var(--ds-font-medium);
}

.ds-diagram-error pre {
  background: var(--ds-surface-secondary);
  padding: var(--ds-space-3);
  border-radius: var(--ds-radius-md);
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  overflow-x: auto;
  white-space: pre-wrap;
}

/* Scrollbar styling */
.ds-diagram-content::-webkit-scrollbar {
  height: 6px;
}

.ds-diagram-content::-webkit-scrollbar-track {
  background: var(--ds-surface-primary);
}

.ds-diagram-content::-webkit-scrollbar-thumb {
  background: var(--ds-border-primary);
  border-radius: 3px;
}

.ds-diagram-content::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .ds-diagram-content {
    padding: var(--ds-space-3);
  }
}
</style>
