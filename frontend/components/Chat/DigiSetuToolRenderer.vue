<template>
  <div class="ds-tool-renderer">
    <!-- Single Tool Result -->
    <div v-if="isSingleTool" class="ds-single-tool">
      <!-- Header -->
      <div class="ds-tool-header">
        <div class="ds-header-info">
          <Icon name="mdi:tools" class="ds-header-icon" />
          <h3 class="ds-header-title">Tool Execution</h3>
          <span class="ds-tool-badge">{{ toolData.tool_name }}</span>
        </div>
        <div class="ds-header-actions">
          <button @click="copyResult" class="ds-action-btn">
            <Icon name="mdi:content-copy" class="ds-action-icon" />
            Copy
          </button>
          <button @click="toggleDetails" class="ds-action-btn">
            <Icon :name="showDetails ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="ds-action-icon" />
            {{ showDetails ? 'Hide' : 'Show' }} Details
          </button>
        </div>
      </div>
      
      <!-- Tool Result -->
      <div class="ds-tool-result">
        <div class="ds-result-content">
          <component 
            :is="getResultComponent(toolData.result)" 
            :result="toolData.result"
            :tool-name="toolData.tool_name"
          />
        </div>
      </div>
      
      <!-- Tool Details -->
      <div v-if="showDetails" class="ds-tool-details">
        <div class="ds-details-grid">
          <div class="ds-detail-item">
            <Icon name="mdi:function" class="ds-detail-icon" />
            <span class="ds-detail-label">Function:</span>
            <span class="ds-detail-value">{{ toolData.tool_name }}</span>
          </div>
          <div class="ds-detail-item" v-if="toolData.execution_time">
            <Icon name="mdi:clock" class="ds-detail-icon" />
            <span class="ds-detail-label">Execution Time:</span>
            <span class="ds-detail-value">{{ toolData.execution_time.toFixed(3) }}s</span>
          </div>
          <div class="ds-detail-item" v-if="hasParameters">
            <Icon name="mdi:cog" class="ds-detail-icon" />
            <span class="ds-detail-label">Parameters:</span>
            <span class="ds-detail-value">{{ parameterCount }} parameter(s)</span>
          </div>
        </div>
        
        <!-- Parameters -->
        <div v-if="hasParameters && showDetails" class="ds-parameters-section">
          <h4 class="ds-parameters-title">Parameters:</h4>
          <div class="ds-parameters-list">
            <div 
              v-for="(value, key) in toolData.parameters" 
              :key="key"
              class="ds-parameter-item"
            >
              <span class="ds-parameter-key">{{ key }}:</span>
              <span class="ds-parameter-value">{{ formatParameterValue(value) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Batch Tool Results -->
    <div v-if="isBatchTools" class="ds-batch-tools">
      <!-- Header -->
      <div class="ds-batch-header">
        <div class="ds-header-info">
          <Icon name="mdi:format-list-bulleted" class="ds-header-icon" />
          <h3 class="ds-header-title">Batch Tool Execution</h3>
          <span class="ds-batch-badge">{{ batchData.total_count }} tools</span>
        </div>
        <div class="ds-header-actions">
          <button @click="copyAllResults" class="ds-action-btn">
            <Icon name="mdi:content-copy" class="ds-action-icon" />
            Copy All
          </button>
        </div>
      </div>
      
      <!-- Tool Results List -->
      <div class="ds-batch-results">
        <div 
          v-for="(result, index) in batchData.results" 
          :key="index"
          class="ds-batch-item"
          :class="{ 'ds-batch-error': !result.success }"
        >
          <div class="ds-batch-item-header">
            <div class="ds-batch-item-info">
              <Icon 
                :name="result.success ? 'mdi:check-circle' : 'mdi:alert-circle'" 
                :class="['ds-batch-status-icon', result.success ? 'ds-success' : 'ds-error']"
              />
              <span class="ds-batch-tool-name">{{ result.tool_name }}</span>
              <span v-if="result.execution_time" class="ds-batch-time">
                {{ result.execution_time.toFixed(3) }}s
              </span>
            </div>
            <button 
              @click="toggleBatchItem(index)" 
              class="ds-batch-toggle"
            >
              <Icon 
                :name="expandedItems.has(index) ? 'mdi:chevron-up' : 'mdi:chevron-down'" 
                class="ds-toggle-icon" 
              />
            </button>
          </div>
          
          <!-- Batch Item Content -->
          <div v-if="expandedItems.has(index)" class="ds-batch-item-content">
            <div v-if="result.success" class="ds-batch-result">
              <component 
                :is="getResultComponent(result.result)" 
                :result="result.result"
                :tool-name="result.tool_name"
              />
            </div>
            <div v-else class="ds-batch-error-content">
              <Icon name="mdi:alert" class="ds-error-icon" />
              <span class="ds-error-message">{{ result.error }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  content: {
    type: [String, Object],
    required: true
  },
  metadata: {
    type: Object,
    default: () => ({})
  }
})

// Reactive state
const showDetails = ref(false)
const expandedItems = ref(new Set())

// Computed properties
const isSingleTool = computed(() => {
  return props.metadata.type === 'tool_result' || 
         (typeof props.content === 'object' && props.content.tool_name)
})

const isBatchTools = computed(() => {
  return props.metadata.type === 'batch_tool_results' || 
         (typeof props.content === 'object' && props.content.results)
})

const toolData = computed(() => {
  if (typeof props.content === 'object' && props.content.tool_name) {
    return props.content
  }
  
  return {
    result: props.content,
    tool_name: props.metadata.tool_name || 'Unknown Tool',
    parameters: props.metadata.parameters || {},
    execution_time: props.metadata.execution_time || 0
  }
})

const batchData = computed(() => {
  if (typeof props.content === 'object' && props.content.results) {
    return props.content
  }
  
  return {
    results: Array.isArray(props.content) ? props.content : [props.content],
    total_count: props.metadata.count || 1,
    executed_tools: props.metadata.executed_tools || []
  }
})

const hasParameters = computed(() => {
  return toolData.value.parameters && Object.keys(toolData.value.parameters).length > 0
})

const parameterCount = computed(() => {
  return Object.keys(toolData.value.parameters || {}).length
})

// Methods
const getResultComponent = (result) => {
  // Return appropriate component based on result type
  if (typeof result === 'object') {
    return 'ObjectResult'
  }
  return 'TextResult'
}

const formatParameterValue = (value) => {
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  return String(value)
}

const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

const toggleBatchItem = (index) => {
  if (expandedItems.value.has(index)) {
    expandedItems.value.delete(index)
  } else {
    expandedItems.value.add(index)
  }
}

const copyResult = async () => {
  try {
    let textToCopy = ''
    
    if (typeof toolData.value.result === 'object') {
      textToCopy = JSON.stringify(toolData.value.result, null, 2)
    } else {
      textToCopy = String(toolData.value.result)
    }
    
    await navigator.clipboard.writeText(textToCopy)
    console.log('Tool result copied to clipboard')
  } catch (err) {
    console.error('Failed to copy tool result:', err)
  }
}

const copyAllResults = async () => {
  try {
    const results = batchData.value.results.map(result => {
      if (result.success) {
        return `${result.tool_name}: ${JSON.stringify(result.result, null, 2)}`
      } else {
        return `${result.tool_name}: ERROR - ${result.error}`
      }
    }).join('\n\n')
    
    await navigator.clipboard.writeText(results)
    console.log('All batch results copied to clipboard')
  } catch (err) {
    console.error('Failed to copy batch results:', err)
  }
}
</script>

<script>
// Result Components
const TextResult = {
  props: ['result', 'toolName'],
  template: `
    <div class="ds-text-result">
      <pre class="ds-result-text">{{ result }}</pre>
    </div>
  `
}

const ObjectResult = {
  props: ['result', 'toolName'],
  computed: {
    formattedResult() {
      return JSON.stringify(this.result, null, 2)
    }
  },
  template: `
    <div class="ds-object-result">
      <pre class="ds-result-json">{{ formattedResult }}</pre>
    </div>
  `
}

export default {
  components: {
    TextResult,
    ObjectResult
  }
}
</script>

<style scoped>
@reference "tailwindcss";

.ds-tool-renderer {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-4);
  padding: var(--ds-space-4);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  background: var(--ds-surface-secondary);
}

.ds-single-tool, .ds-batch-tools {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-4);
}

.ds-tool-header, .ds-batch-header {
  @apply flex justify-between items-center;
}

.ds-header-info {
  @apply flex items-center gap-3;
}

.ds-header-icon {
  @apply w-6 h-6 text-green-600;
}

.ds-header-title {
  @apply text-lg font-semibold text-green-900;
}

.ds-tool-badge, .ds-batch-badge {
  @apply px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full;
}

.ds-header-actions {
  @apply flex gap-2;
}

.ds-action-btn {
  @apply flex items-center gap-2 px-3 py-1.5 bg-white text-green-700 border border-green-300 rounded-lg hover:bg-green-50 transition-colors text-sm;
}

.ds-action-icon {
  @apply w-4 h-4;
}

.ds-tool-result {
  @apply p-4 bg-white rounded-lg border border-gray-200;
}

.ds-result-content {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-2);
}

.ds-tool-details {
  @apply space-y-3 p-4 bg-white rounded-lg;
}

.ds-details-grid {
  @apply grid grid-cols-1 sm:grid-cols-3 gap-3;
}

.ds-detail-item {
  @apply flex items-center gap-2 text-sm;
}

.ds-detail-icon {
  @apply w-4 h-4 text-green-600;
}

.ds-detail-label {
  @apply font-medium text-gray-700;
}

.ds-detail-value {
  @apply text-gray-900;
}

.ds-parameters-section {
  @apply space-y-2;
}

.ds-parameters-title {
  @apply font-medium text-gray-900;
}

.ds-parameters-list {
  @apply space-y-1;
}

.ds-parameter-item {
  @apply flex gap-2 text-sm;
}

.ds-parameter-key {
  @apply font-medium text-gray-700 min-w-0 flex-shrink-0;
}

.ds-parameter-value {
  @apply text-gray-900 break-all;
}

.ds-batch-results {
  @apply space-y-3;
}

.ds-batch-item {
  @apply p-3 bg-white rounded-lg border border-gray-200;
}

.ds-batch-item.ds-batch-error {
  @apply border-red-200 bg-red-50;
}

.ds-batch-item-header {
  @apply flex justify-between items-center;
}

.ds-batch-item-info {
  @apply flex items-center gap-3;
}

.ds-batch-status-icon {
  @apply w-5 h-5;
}

.ds-batch-status-icon.ds-success {
  @apply text-green-600;
}

.ds-batch-status-icon.ds-error {
  @apply text-red-600;
}

.ds-batch-tool-name {
  @apply font-medium text-gray-900;
}

.ds-batch-time {
  @apply text-sm text-gray-500;
}

.ds-batch-toggle {
  @apply p-1 hover:bg-gray-100 rounded transition-colors;
}

.ds-toggle-icon {
  @apply w-4 h-4 text-gray-500;
}

.ds-batch-item-content {
  @apply mt-3 pt-3 border-t border-gray-200;
}

.ds-batch-result {
  @apply space-y-2;
}

.ds-batch-error-content {
  @apply flex items-center gap-2 text-red-700;
}

.ds-error-icon {
  @apply w-4 h-4;
}

.ds-error-message {
  @apply text-sm;
}

/* Result Component Styles */
.ds-text-result, .ds-object-result {
  @apply w-full;
}

.ds-result-text, .ds-result-json {
  @apply w-full p-3 bg-gray-50 rounded border text-sm font-mono whitespace-pre-wrap overflow-x-auto;
}

.ds-result-json {
  @apply text-blue-800;
}
</style>
