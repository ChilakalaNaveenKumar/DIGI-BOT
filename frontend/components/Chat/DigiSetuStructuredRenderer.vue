<template>
  <div class="ds-structured-renderer">
    <div class="ds-structured-header">
      <Icon name="mdi:code-json" class="ds-structured-icon" />
      <h3 class="ds-structured-title">Structured Output</h3>
      <div class="ds-structured-meta">
        <span :class="['ds-validation-badge', validationPassed ? 'ds-validation-passed' : 'ds-validation-failed']">
          <Icon :name="validationPassed ? 'mdi:check-circle' : 'mdi:alert-circle'" class="ds-validation-icon" />
          {{ validationPassed ? 'Validated' : 'Best Effort' }}
        </span>
        <span class="ds-generation-time">{{ metadata.generation_time?.toFixed(2) }}s</span>
      </div>
    </div>

    <div class="ds-structured-content">
      <!-- Schema Information -->
      <div class="ds-schema-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:file-tree" class="ds-section-icon" />
          Schema Details
        </h4>
        <div class="ds-schema-info">
          <div class="ds-schema-item">
            <span class="ds-schema-label">Type:</span>
            <span class="ds-schema-value">{{ metadata.schema_type || 'Custom' }}</span>
          </div>
          <div class="ds-schema-item">
            <span class="ds-schema-label">Format:</span>
            <span class="ds-schema-value">Pydantic Model</span>
          </div>
          <div class="ds-schema-item">
            <span class="ds-schema-label">Model:</span>
            <span class="ds-schema-value">{{ metadata.model_used || 'GPT-4' }}</span>
          </div>
        </div>
      </div>

      <!-- Data Preview -->
      <div class="ds-data-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:database" class="ds-section-icon" />
          Structured Data
          <button @click="toggleView" class="ds-view-toggle">
            <Icon :name="viewMode === 'formatted' ? 'mdi:code-braces' : 'mdi:format-list-bulleted'" class="ds-toggle-icon" />
            {{ viewMode === 'formatted' ? 'Raw JSON' : 'Formatted' }}
          </button>
        </h4>
        
        <!-- Formatted View -->
        <div v-if="viewMode === 'formatted'" class="ds-formatted-view">
          <div class="ds-data-cards">
            <div 
              v-for="(value, key) in structuredData" 
              :key="key"
              class="ds-data-card"
            >
              <div class="ds-card-header">
                <Icon :name="getFieldIcon(key)" class="ds-field-icon" />
                <span class="ds-field-name">{{ formatFieldName(key) }}</span>
                <span class="ds-field-type">{{ getFieldType(value) }}</span>
              </div>
              <div class="ds-card-content">
                <div v-if="Array.isArray(value)" class="ds-array-content">
                  <div 
                    v-for="(item, index) in value" 
                    :key="index"
                    class="ds-array-item"
                  >
                    {{ item }}
                  </div>
                </div>
                <div v-else-if="typeof value === 'object'" class="ds-object-content">
                  <pre class="ds-object-preview">{{ JSON.stringify(value, null, 2) }}</pre>
                </div>
                <div v-else class="ds-simple-content">
                  {{ value }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Raw JSON View -->
        <div v-else class="ds-raw-view">
          <div class="ds-json-container">
            <pre class="ds-json-content">{{ formattedJson }}</pre>
            <button @click="copyJson" class="ds-copy-btn">
              <Icon name="mdi:content-copy" class="ds-copy-icon" />
              Copy JSON
            </button>
          </div>
        </div>
      </div>

      <!-- Validation Details -->
      <div v-if="!validationPassed" class="ds-validation-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:alert-triangle" class="ds-section-icon" />
          Validation Notes
        </h4>
        <div class="ds-validation-warning">
          <p>This output was generated using best-effort parsing. Some fields may not match the expected schema exactly.</p>
          <p>For production use, consider refining the prompt or adjusting the schema requirements.</p>
        </div>
      </div>

      <!-- Usage Example -->
      <div class="ds-usage-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:code-tags" class="ds-section-icon" />
          Usage Example
        </h4>
        <div class="ds-usage-example">
          <pre class="ds-code-block">{{ usageExample }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  metadata: {
    type: Object,
    default: () => ({})
  }
})

// Local state
const viewMode = ref('formatted')

// Computed properties
const validationPassed = computed(() => {
  return props.metadata.validation_passed ?? true
})

const structuredData = computed(() => {
  if (props.metadata.data && typeof props.metadata.data === 'object') {
    return props.metadata.data
  }
  
  // Try to parse JSON from content
  try {
    const jsonMatch = props.content.match(/```json\n(.*?)\n```/s)
    if (jsonMatch) {
      return JSON.parse(jsonMatch[1])
    }
    
    // Try to find JSON in content
    const jsonStart = props.content.indexOf('{')
    const jsonEnd = props.content.lastIndexOf('}') + 1
    if (jsonStart >= 0 && jsonEnd > jsonStart) {
      return JSON.parse(props.content.slice(jsonStart, jsonEnd))
    }
  } catch (e) {
    console.warn('Failed to parse structured data:', e)
  }
  
  return { result: 'No structured data available' }
})

const formattedJson = computed(() => {
  return JSON.stringify(structuredData.value, null, 2)
})

const usageExample = computed(() => {
  const schemaType = props.metadata.schema_type || 'data'
  return `# Python usage example
import json

# Parse the structured data
${schemaType}_data = json.loads('''${formattedJson.value}''')

# Access fields
${Object.keys(structuredData.value).slice(0, 3).map(key => 
  `print(f"${formatFieldName(key)}: {${schemaType}_data['${key}']}")`
).join('\n')}

# Use with Pydantic model
from pydantic import BaseModel

class ${formatFieldName(schemaType)}Schema(BaseModel):
${Object.entries(structuredData.value).slice(0, 3).map(([key, value]) => 
  `    ${key}: ${getPythonType(value)}`
).join('\n')}

# Validate data
validated_${schemaType} = ${formatFieldName(schemaType)}Schema(**${schemaType}_data)`
})

// Methods
const toggleView = () => {
  viewMode.value = viewMode.value === 'formatted' ? 'raw' : 'formatted'
}

const copyJson = async () => {
  try {
    await navigator.clipboard.writeText(formattedJson.value)
    // Could add a toast notification here
  } catch (err) {
    console.error('Failed to copy JSON:', err)
  }
}

const formatFieldName = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getFieldType = (value) => {
  if (Array.isArray(value)) {
    return `Array[${value.length}]`
  }
  if (value === null) {
    return 'null'
  }
  if (typeof value === 'object') {
    return 'Object'
  }
  return typeof value
}

const getPythonType = (value) => {
  if (Array.isArray(value)) {
    return 'List[str]'
  }
  if (typeof value === 'string') {
    return 'str'
  }
  if (typeof value === 'number') {
    return Number.isInteger(value) ? 'int' : 'float'
  }
  if (typeof value === 'boolean') {
    return 'bool'
  }
  return 'Any'
}

const getFieldIcon = (key) => {
  const keyLower = key.toLowerCase()
  if (keyLower.includes('name')) return 'mdi:account'
  if (keyLower.includes('email')) return 'mdi:email'
  if (keyLower.includes('age')) return 'mdi:calendar'
  if (keyLower.includes('price')) return 'mdi:currency-usd'
  if (keyLower.includes('date')) return 'mdi:calendar-clock'
  if (keyLower.includes('url') || keyLower.includes('link')) return 'mdi:link'
  if (keyLower.includes('phone')) return 'mdi:phone'
  if (keyLower.includes('address')) return 'mdi:map-marker'
  if (keyLower.includes('skill') || keyLower.includes('tag')) return 'mdi:tag'
  if (keyLower.includes('rating') || keyLower.includes('score')) return 'mdi:star'
  return 'mdi:text'
}
</script>

<style scoped>
@reference "tailwindcss";
.ds-structured-renderer {
  @apply bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6 space-y-6;
}

.ds-structured-header {
  @apply flex items-center justify-between flex-wrap gap-4;
}

.ds-structured-icon {
  @apply w-6 h-6 text-green-600;
}

.ds-structured-title {
  @apply flex-1 text-lg font-semibold text-green-900;
}

.ds-structured-meta {
  @apply flex items-center gap-3;
}

.ds-validation-badge {
  @apply px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1;
}

.ds-validation-passed {
  @apply bg-green-100 text-green-800;
}

.ds-validation-failed {
  @apply bg-yellow-100 text-yellow-800;
}

.ds-validation-icon {
  @apply w-4 h-4;
}

.ds-generation-time {
  @apply px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium;
}

.ds-structured-content {
  @apply space-y-6;
}

.ds-section-title {
  @apply flex items-center justify-between font-semibold text-gray-900 mb-3;
}

.ds-section-icon {
  @apply w-5 h-5 text-gray-600 mr-2;
}

.ds-view-toggle {
  @apply flex items-center gap-1 px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors;
}

.ds-toggle-icon {
  @apply w-4 h-4;
}

.ds-schema-section {
  @apply space-y-3;
}

.ds-schema-info {
  @apply grid grid-cols-1 md:grid-cols-3 gap-4;
}

.ds-schema-item {
  @apply flex flex-col space-y-1 p-3 bg-white rounded border border-green-200;
}

.ds-schema-label {
  @apply text-sm font-medium text-gray-600;
}

.ds-schema-value {
  @apply text-gray-900 font-medium;
}

.ds-data-section {
  @apply space-y-4;
}

.ds-formatted-view {
  @apply space-y-4;
}

.ds-data-cards {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.ds-data-card {
  @apply bg-white rounded-lg border border-green-200 overflow-hidden;
}

.ds-card-header {
  @apply flex items-center gap-2 p-3 bg-green-50 border-b border-green-200;
}

.ds-field-icon {
  @apply w-4 h-4 text-green-600;
}

.ds-field-name {
  @apply flex-1 font-medium text-gray-900;
}

.ds-field-type {
  @apply text-xs px-2 py-1 bg-green-100 text-green-700 rounded;
}

.ds-card-content {
  @apply p-3;
}

.ds-array-content {
  @apply space-y-1;
}

.ds-array-item {
  @apply px-2 py-1 bg-gray-100 rounded text-sm;
}

.ds-object-content {
  @apply space-y-2;
}

.ds-object-preview {
  @apply text-xs bg-gray-100 p-2 rounded overflow-x-auto;
}

.ds-simple-content {
  @apply text-gray-800;
}

.ds-raw-view {
  @apply space-y-3;
}

.ds-json-container {
  @apply relative bg-white rounded-lg border border-green-200 overflow-hidden;
}

.ds-json-content {
  @apply p-4 text-sm bg-gray-900 text-green-400 overflow-x-auto;
}

.ds-copy-btn {
  @apply absolute top-2 right-2 flex items-center gap-1 px-2 py-1 bg-gray-800 text-white rounded text-xs hover:bg-gray-700 transition-colors;
}

.ds-copy-icon {
  @apply w-3 h-3;
}

.ds-validation-section {
  @apply space-y-3;
}

.ds-validation-warning {
  @apply p-4 bg-yellow-50 border border-yellow-200 rounded-lg space-y-2 text-sm text-yellow-800;
}

.ds-usage-section {
  @apply space-y-3;
}

.ds-usage-example {
  @apply bg-white rounded-lg border border-green-200 overflow-hidden;
}

.ds-code-block {
  @apply p-4 text-sm bg-gray-900 text-gray-100 overflow-x-auto;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .ds-structured-renderer {
    @apply from-green-900/20 to-emerald-900/20 border-green-700;
  }
  
  .ds-structured-title {
    @apply text-green-100;
  }
  
  .ds-data-card, .ds-schema-item, .ds-json-container, .ds-usage-example {
    @apply bg-gray-800 border-gray-700;
  }
  
  .ds-card-header {
    @apply bg-green-900/30 border-green-700;
  }
  
  .ds-field-name {
    @apply text-gray-100;
  }
  
  .ds-simple-content {
    @apply text-gray-200;
  }
}
</style>

