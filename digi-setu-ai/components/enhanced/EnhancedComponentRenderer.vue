<template>
  <div class="enhanced-component-renderer" :class="`component-${componentType}`">
    <!-- Chart Components -->
    <EnhancedChartRenderer
      v-if="isChart"
      :type="chartType"
      :data="componentData"
      :title="componentTitle"
      :options="chartOptions"
    />
    
    <!-- Data Table -->
    <EnhancedDataTable
      v-else-if="isTable"
      :data="componentData"
      :title="componentTitle"
      :headers="tableHeaders"
      :page-size="tablePageSize"
    />
    
    <!-- Progress Bar -->
    <div v-else-if="componentType === 'progress-bar'" class="progress-component">
      <h4 v-if="componentTitle" class="component-title">{{ componentTitle }}</h4>
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: `${progressValue}%` }">
          <span class="progress-text">{{ progressValue }}%</span>
        </div>
      </div>
    </div>
    
    <!-- Metric Cards -->
    <div v-else-if="componentType === 'metric-cards'" class="metrics-grid">
      <h4 v-if="componentTitle" class="component-title">{{ componentTitle }}</h4>
      <div class="metrics-container">
        <div v-for="(metric, index) in metricsData" :key="index" class="metric-card">
          <div class="metric-value">{{ formatMetricValue(metric.value) }}</div>
          <div class="metric-label">{{ metric.label }}</div>
          <div v-if="metric.change" class="metric-change" :class="getChangeClass(metric.change)">
            {{ formatChange(metric.change) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Timeline -->
    <div v-else-if="componentType === 'timeline'" class="timeline-component">
      <h4 v-if="componentTitle" class="component-title">{{ componentTitle }}</h4>
      <div class="timeline-container">
        <div v-for="(item, index) in timelineData" :key="index" class="timeline-item">
          <div class="timeline-marker"></div>
          <div class="timeline-content">
            <div class="timeline-date">{{ formatDate(item.date) }}</div>
            <div class="timeline-title">{{ item.title }}</div>
            <div class="timeline-description">{{ item.description }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Status Badge -->
    <div v-else-if="componentType === 'status-badge'" class="status-component">
      <div class="status-badge" :class="getStatusClass(statusValue)">
        <div class="status-indicator" :class="getStatusIndicatorClass(statusValue)"></div>
        {{ statusLabel }}
      </div>
    </div>
    
    <!-- Alert/Notification -->
    <div v-else-if="componentType === 'alert'" class="alert-component">
      <div class="alert-box" :class="getAlertClass(alertType)">
        <div class="alert-icon">
          <Icon :name="getAlertIcon(alertType)" />
        </div>
        <div class="alert-content">
          <div class="alert-title">{{ alertTitle }}</div>
          <div class="alert-message">{{ alertMessage }}</div>
        </div>
      </div>
    </div>
    
    <!-- Code Block -->
    <div v-else-if="componentType === 'code-block'" class="code-component">
      <div class="code-container">
        <div class="code-header">
          <span>{{ codeLanguage || 'Code' }}</span>
          <button @click="copyCode" class="copy-button">
            <Icon name="lucide:copy" />
          </button>
        </div>
        <pre class="code-content"><code>{{ codeContent }}</code></pre>
      </div>
    </div>
    
    <!-- Fallback for unknown component types -->
    <div v-else class="fallback-component">
      <div class="fallback-content">
        <div class="fallback-header">
          <Icon name="lucide:help-circle" />
          <span>Unknown Component: {{ componentType }}</span>
        </div>
        <pre class="fallback-data">{{ JSON.stringify(componentData, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  componentType: string
  markdown?: string
  title?: string
}

const props = defineProps<Props>()

// Parse component data from markdown
const componentData = computed(() => {
  if (!props.markdown) return {}
  
  try {
    // Extract data from markdown content
    const lines = props.markdown.split('\n')
    const data: Record<string, any> = {}
    
    for (const line of lines) {
      if (line.includes(':')) {
        const [key, ...valueParts] = line.split(':')
        const value = valueParts.join(':').trim()
        
        if (key && value) {
          const cleanKey = key.trim().toLowerCase().replace(/[^a-z0-9]/g, '_')
          
          // Try to parse as JSON, number, or keep as string
          try {
            data[cleanKey] = JSON.parse(value)
          } catch {
            if (!isNaN(Number(value))) {
              data[cleanKey] = Number(value)
            } else {
              data[cleanKey] = value
            }
          }
        }
      }
    }
    
    return data
  } catch (error) {
    console.error('Error parsing component data:', error)
    return {}
  }
})

// Component type checks
const isChart = computed(() => {
  return ['pie-chart', 'bar-chart', 'line-chart', 'area-chart', 'scatter-chart'].includes(props.componentType)
})

const isTable = computed(() => {
  return props.componentType === 'data-table'
})

// Component-specific computed properties
const componentTitle = computed(() => props.title || componentData.value.title || '')

const chartType = computed(() => {
  return props.componentType.replace('-chart', '')
})

const chartOptions = computed(() => componentData.value.options || {})

const tableHeaders = computed(() => componentData.value.headers || [])
const tablePageSize = computed(() => componentData.value.page_size || 10)

const progressValue = computed(() => componentData.value.value || componentData.value.progress || 0)

const metricsData = computed(() => {
  if (componentData.value.metrics) return componentData.value.metrics
  if (Array.isArray(componentData.value.data)) return componentData.value.data
  return []
})

const timelineData = computed(() => {
  if (componentData.value.timeline) return componentData.value.timeline
  if (Array.isArray(componentData.value.data)) return componentData.value.data
  return []
})

const statusValue = computed(() => componentData.value.status || componentData.value.value || 'unknown')
const statusLabel = computed(() => componentData.value.label || statusValue.value)

const alertType = computed(() => componentData.value.type || 'info')
const alertTitle = computed(() => componentData.value.title || '')
const alertMessage = computed(() => componentData.value.message || componentData.value.content || '')

const codeLanguage = computed(() => componentData.value.language || componentData.value.lang || '')
const codeContent = computed(() => componentData.value.code || componentData.value.content || '')

// Helper methods
const formatMetricValue = (value: any) => {
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return String(value)
}

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change}%`
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'change-positive'
  if (change < 0) return 'change-negative'
  return 'change-neutral'
}

const formatDate = (date: string | Date) => {
  try {
    return new Date(date).toLocaleDateString()
  } catch {
    return String(date)
  }
}

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    'success': 'status-success',
    'warning': 'status-warning',
    'error': 'status-error',
    'danger': 'status-error',
    'info': 'status-info'
  }
  return statusMap[status.toLowerCase()] || 'status-default'
}

const getStatusIndicatorClass = (status: string) => {
  const statusMap: Record<string, string> = {
    'success': 'indicator-success',
    'warning': 'indicator-warning',
    'error': 'indicator-error',
    'danger': 'indicator-error',
    'info': 'indicator-info'
  }
  return statusMap[status.toLowerCase()] || 'indicator-default'
}

const getAlertClass = (type: string) => {
  const typeMap: Record<string, string> = {
    'info': 'alert-info',
    'warning': 'alert-warning',
    'error': 'alert-error',
    'success': 'alert-success'
  }
  return typeMap[type.toLowerCase()] || 'alert-info'
}

const getAlertIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    'info': 'lucide:info',
    'warning': 'lucide:alert-triangle',
    'error': 'lucide:alert-circle',
    'success': 'lucide:check-circle'
  }
  return iconMap[type.toLowerCase()] || 'lucide:info'
}

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(codeContent.value)
  } catch (error) {
    console.error('Failed to copy code:', error)
  }
}
</script>

<style scoped>
.enhanced-component-renderer {
  margin: 1rem 0;
  border-radius: 0.5rem;
  border: 1px solid var(--border-primary);
  background: var(--bg-primary);
  overflow: hidden;
}

.component-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

/* Progress Bar */
.progress-component {
  padding: 1rem;
}

.progress-container {
  width: 100%;
  background: var(--bg-tertiary);
  border-radius: 9999px;
  height: 1.5rem;
  position: relative;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--accent-primary);
  border-radius: 9999px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}

/* Metrics Grid */
.metrics-grid {
  padding: 1rem;
}

.metrics-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric-card {
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.metric-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.metric-change {
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 0.5rem;
}

.change-positive {
  color: var(--success-color, #22c55e);
}

.change-negative {
  color: var(--error-color, #ef4444);
}

.change-neutral {
  color: var(--text-tertiary);
}

/* Timeline */
.timeline-component {
  padding: 1rem;
}

.timeline-container {
  position: relative;
}

.timeline-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  padding-bottom: 1.5rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  width: 0.75rem;
  height: 0.75rem;
  background: var(--accent-primary);
  border-radius: 50%;
  margin-right: 1rem;
  margin-top: 0.25rem;
  flex-shrink: 0;
  position: relative;
}

.timeline-marker::after {
  content: '';
  position: absolute;
  top: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 1.5rem;
  background: var(--border-primary);
}

.timeline-item:last-child .timeline-marker::after {
  display: none;
}

.timeline-content {
  flex: 1;
}

.timeline-date {
  font-size: 0.875rem;
  color: var(--text-tertiary);
}

.timeline-title {
  font-weight: 500;
  color: var(--text-primary);
}

.timeline-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* Status Badge */
.status-component {
  padding: 1rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-success {
  background: var(--success-bg, #dcfce7);
  color: var(--success-text, #166534);
}

.status-warning {
  background: var(--warning-bg, #fef3cd);
  color: var(--warning-text, #92400e);
}

.status-error {
  background: var(--error-bg, #fee2e2);
  color: var(--error-text, #991b1b);
}

.status-info {
  background: var(--info-bg, #dbeafe);
  color: var(--info-text, #1e40af);
}

.status-default {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.status-indicator {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.indicator-success {
  background: var(--success-color, #22c55e);
}

.indicator-warning {
  background: var(--warning-color, #f59e0b);
}

.indicator-error {
  background: var(--error-color, #ef4444);
}

.indicator-info {
  background: var(--info-color, #3b82f6);
}

.indicator-default {
  background: var(--text-tertiary);
}

/* Alert */
.alert-component {
  padding: 1rem;
}

.alert-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 0.5rem;
}

.alert-info {
  background: var(--info-bg, #dbeafe);
  color: var(--info-text, #1e40af);
}

.alert-warning {
  background: var(--warning-bg, #fef3cd);
  color: var(--warning-text, #92400e);
}

.alert-error {
  background: var(--error-bg, #fee2e2);
  color: var(--error-text, #991b1b);
}

.alert-success {
  background: var(--success-bg, #dcfce7);
  color: var(--success-text, #166534);
}

.alert-icon {
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.alert-message {
  font-size: 0.875rem;
}

/* Code Block */
.code-component {
  padding: 1rem;
}

.code-container {
  background: var(--bg-code, #1f2937);
  border-radius: 0.5rem;
  overflow: hidden;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: var(--bg-code-header, #374151);
  color: var(--text-code-header, #d1d5db);
  font-size: 0.875rem;
}

.copy-button {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
}

.copy-button:hover {
  background: var(--bg-hover, rgba(255, 255, 255, 0.1));
}

.code-content {
  padding: 1rem;
  overflow-x: auto;
  font-size: 0.875rem;
  margin: 0;
  background: none;
  color: var(--text-code, #f9fafb);
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
}

/* Fallback */
.fallback-component {
  padding: 1rem;
}

.fallback-content {
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
}

.fallback-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.fallback-data {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-family: monospace;
  background: var(--bg-tertiary);
  padding: 0.75rem;
  border-radius: 0.25rem;
  margin: 0;
  overflow-x: auto;
}
</style>