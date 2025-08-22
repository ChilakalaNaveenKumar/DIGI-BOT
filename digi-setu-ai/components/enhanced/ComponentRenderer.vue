<template>
  <div class="my-4">
    <!-- Chart Component -->
    <EnhancedChartRenderer
      v-if="isChart && parsedData"
      :type="chartType"
      :data="parsedData"
      :title="componentTitle"
    />
    
    <!-- Data Table -->
    <EnhancedDataTable
      v-else-if="isTable && parsedData"
      :data="parsedData"
      :title="componentTitle"
      :page-size="5"
    />
    
    <!-- Fallback -->
    <div v-else class="fallback-container">
      <pre class="fallback-text">{{ markdown }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  componentType: string
  markdown: string
  title?: string
}

const props = defineProps<Props>()

// Extract chart type
const chartType = computed(() => {
  return props.componentType.replace('-chart', '').replace('_chart', '')
})

const isChart = computed(() => {
  const types = ['pie', 'bar', 'line', 'doughnut', 'radar', 'polarArea', 'bubble', 'scatter']
  return types.includes(chartType.value)
})

const isTable = computed(() => {
  return props.componentType === 'data-table' || props.componentType === 'table'
})

const componentTitle = computed(() => {
  return props.title || extractTitle(props.markdown)
})

// Micro parser
const parsedData = computed(() => {
  try {
    // Extract data from markdown
    const dataMatch = props.markdown.match(/data:\s*(\[.*?\]|\{.*?\})/s)
    if (dataMatch && dataMatch[1]) {
      return JSON.parse(dataMatch[1])
    }
    
    // Try YAML-like format
    const yamlMatch = props.markdown.match(/```(?:yaml|json)?\n([\s\S]*?)\n```/)
    if (yamlMatch && yamlMatch[1]) {
      return JSON.parse(yamlMatch[1])
    }
    
    return null
  } catch {
    return null
  }
})

function extractTitle(markdown: string): string {
  const titleMatch = markdown.match(/title:\s*(.+)/)
  return titleMatch?.[1]?.trim() || 'Chart'
}
</script>

<style scoped>
.fallback-container {
  background: var(--bg-tertiary);
  border-radius: 0.375rem;
  padding: 0.5rem;
}

.fallback-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
  margin: 0;
  white-space: pre-wrap;
}
</style>

