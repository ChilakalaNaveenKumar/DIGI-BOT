<template>
  <div class="enhanced-components-demo">
    <div class="demo-header">
      <h1 class="demo-title">Enhanced Components Demo</h1>
      <p class="demo-description">
        Test the enhanced component system with position-based insertion and dynamic rendering.
      </p>
    </div>

    <div class="demo-content">
      <!-- Test Controls -->
      <div class="test-controls">
        <h2>Test Controls</h2>
        <div class="control-group">
          <button @click="testBasicComponents" class="test-btn">
            Test Basic Components
          </button>
          <button @click="testPositionInsertion" class="test-btn">
            Test Position Insertion
          </button>
          <button @click="testStreamingWithComponents" class="test-btn">
            Test Streaming + Components
          </button>
          <button @click="clearDemo" class="test-btn secondary">
            Clear Demo
          </button>
        </div>
      </div>

      <!-- Demo Output -->
      <div class="demo-output">
        <h2>Demo Output</h2>
        <div class="output-container">
          <UiEnhancedStreamingMarkdown
            :content="demoContent"
            :is-streaming="isStreaming"
            :mode="streamingMode"
            :enable-component-matching="true"
            @content-updated="onContentUpdated"
            @streaming-complete="onStreamingComplete"
            @component-processed="onComponentProcessed"
            @components-ready="onComponentsReady"
          />
        </div>
      </div>

      <!-- Component Analysis -->
      <div class="component-analysis">
        <h2>Component Analysis</h2>
        <div class="analysis-grid">
          <div class="analysis-card">
            <h3>Detected Components</h3>
            <div class="component-list">
              <div v-for="component in detectedComponents" :key="component.id" class="component-item">
                <div class="component-header">
                  <span class="component-type">{{ component.type }}</span>
                  <span class="component-position">Position: {{ component.position }}</span>
                </div>
                <div class="component-title">{{ component.title }}</div>
                <div class="component-action">Action: {{ component.action }}</div>
              </div>
            </div>
          </div>

          <div class="analysis-card">
            <h3>Content Blocks</h3>
            <div class="block-list">
              <div v-for="(block, index) in contentBlocks" :key="block.id" class="block-item">
                <div class="block-header">
                  <span class="block-type">{{ block.type }}</span>
                  <span class="block-index">#{{ index + 1 }}</span>
                </div>
                <div class="block-content">
                  {{ block.type === 'text' ? block.content.substring(0, 100) + '...' : 'Component Block' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Raw Content Inspector -->
      <div class="content-inspector">
        <h2>Content Inspector</h2>
        <div class="inspector-tabs">
          <button 
            @click="activeTab = 'raw'" 
            :class="['tab-btn', { active: activeTab === 'raw' }]"
          >
            Raw Content
          </button>
          <button 
            @click="activeTab = 'processed'" 
            :class="['tab-btn', { active: activeTab === 'processed' }]"
          >
            Processed Content
          </button>
          <button 
            @click="activeTab = 'components'" 
            :class="['tab-btn', { active: activeTab === 'components' }]"
          >
            Components JSON
          </button>
        </div>
        
        <div class="inspector-content">
          <pre v-if="activeTab === 'raw'" class="inspector-code">{{ demoContent }}</pre>
          <pre v-else-if="activeTab === 'processed'" class="inspector-code">{{ processedContent }}</pre>
          <pre v-else class="inspector-code">{{ JSON.stringify(detectedComponents, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useEnhancedStreaming } from '~/composables/useEnhancedStreaming'

// Demo state
const demoContent = ref('')
const isStreaming = ref(false)
const streamingMode = ref<'streaming' | 'static' | 'dynamic'>('static')
const activeTab = ref('raw')

// Enhanced streaming composable
const {
  streamingContent,
  renderedBlocks,
  processStreamingText,
  startStreaming,
  stopStreaming
} = useEnhancedStreaming()

// Computed properties
const detectedComponents = computed(() => streamingContent.value.components)
const contentBlocks = computed(() => streamingContent.value.blocks)
const processedContent = computed(() => {
  return contentBlocks.value.map(block => ({
    type: block.type,
    position: block.position,
    content: block.type === 'text' ? block.content : `[${block.component?.type} Component]`
  }))
})

// Test data
const sampleComponents = {
  pieChart: `:::pie-chart
title: Market Share Distribution
position: 150
action: insert
data: [
  {"label": "Product A", "value": 45},
  {"label": "Product B", "value": 30},
  {"label": "Product C", "value": 15},
  {"label": "Product D", "value": 10}
]
:::`,

  dataTable: `:::data-table
title: Sales Performance Q4
position: 300
action: insert
data: [
  {"Region": "North America", "Sales": 125000, "Growth": 12.5},
  {"Region": "Europe", "Sales": 98000, "Growth": 8.3},
  {"Region": "Asia Pacific", "Sales": 156000, "Growth": 15.7},
  {"Region": "Latin America", "Sales": 67000, "Growth": 5.2}
]
:::`,

  metrics: `:::metric-cards
title: Key Performance Indicators
position: 450
action: insert
data: [
  {"label": "Revenue", "value": 2450000, "change": 12.5},
  {"label": "Users", "value": 45600, "change": -2.3},
  {"label": "Conversion", "value": 3.2, "change": 8.7}
]
:::`,

  alert: `:::alert
title: Important Notice
position: 600
action: insert
data: {
  "type": "warning",
  "message": "System maintenance scheduled for tonight at 2 AM EST."
}
:::`
}

// Test methods
const testBasicComponents = () => {
  const content = `# Component Demo

This is a demonstration of our enhanced component system. Let me show you some charts and data visualizations.

${sampleComponents.pieChart}

As you can see from the chart above, Product A dominates the market with 45% share. Now let's look at regional performance:

${sampleComponents.dataTable}

The data shows strong growth in Asia Pacific region. Here are our key metrics:

${sampleComponents.metrics}

${sampleComponents.alert}

This completes our component demonstration.`

  demoContent.value = content
  processStreamingText(content)
}

const testPositionInsertion = () => {
  // Test precise position insertion
  const baseText = "The quarterly results show significant growth across all regions. Our revenue increased by 15% compared to last quarter, with particularly strong performance in the technology sector."
  
  const chartComponent = `:::bar-chart
title: Quarterly Growth by Region
position: 85
action: insert
data: [
  {"label": "Q1", "value": 85000},
  {"label": "Q2", "value": 92000},
  {"label": "Q3", "value": 98000},
  {"label": "Q4", "value": 112000}
]
:::`

  demoContent.value = baseText + '\n\n' + chartComponent
  processStreamingText(demoContent.value)
}

const testStreamingWithComponents = async () => {
  streamingMode.value = 'streaming'
  isStreaming.value = true
  startStreaming()
  
  const fullContent = `# Streaming Demo with Components

Let me analyze the data step by step...

First, let's look at the overall trends:

${sampleComponents.pieChart}

Now, examining the detailed breakdown:

${sampleComponents.dataTable}

Finally, here are the key takeaways:

${sampleComponents.metrics}`

  // Simulate streaming
  let currentContent = ''
  const words = fullContent.split(' ')
  
  for (let i = 0; i < words.length; i++) {
    currentContent += (i > 0 ? ' ' : '') + words[i]
    demoContent.value = currentContent
    processStreamingText(currentContent)
    
    // Add delay to simulate streaming
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  
  isStreaming.value = false
  stopStreaming()
  streamingMode.value = 'static'
}

const clearDemo = () => {
  demoContent.value = ''
  isStreaming.value = false
  streamingMode.value = 'static'
  processStreamingText('')
}

// Event handlers
const onContentUpdated = (content: string) => {
  console.log('Content updated:', content.length, 'characters')
}

const onStreamingComplete = () => {
  console.log('Streaming complete')
}

const onComponentProcessed = (component: any) => {
  console.log('Component processed:', component)
}

const onComponentsReady = (components: any[]) => {
  console.log('Components ready:', components.length)
}

// Set page meta
definePageMeta({
  layout: 'default',
  title: 'Enhanced Components Demo'
})
</script>

<style scoped>
.enhanced-components-demo {
  max-width: 72rem;
  margin: 0 auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.demo-header {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.demo-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
}

.demo-description {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 42rem;
  margin: 0 auto;
}

.demo-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.test-controls {
  background: var(--bg-primary);
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-primary);
}

.test-controls h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.control-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.test-btn {
  padding: 0.5rem 1rem;
  background: var(--accent-primary);
  color: white;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.test-btn:hover {
  background: var(--accent-hover);
}

.test-btn.secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.test-btn.secondary:hover {
  background: var(--bg-hover);
}

.demo-output {
  background: var(--bg-primary);
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-primary);
}

.demo-output h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.output-container {
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
  min-height: 200px;
}

.component-analysis {
  background: var(--bg-primary);
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-primary);
}

.component-analysis h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .analysis-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.analysis-card {
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
}

.analysis-card h3 {
  font-size: 1.125rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.component-list, .block-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.component-item, .block-item {
  background: var(--bg-primary);
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid var(--border-primary);
}

.component-header, .block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.component-type, .block-type {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--accent-primary);
}

.component-position, .block-index {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.component-title, .component-action, .block-content {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.content-inspector {
  background: var(--bg-primary);
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-primary);
}

.content-inspector h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.inspector-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);
  background: transparent;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent-bg);
  color: var(--accent-primary);
}

.inspector-content {
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
}

.inspector-code {
  font-size: 0.875rem;
  font-family: monospace;
  color: var(--text-secondary);
  white-space: pre-wrap;
}
</style>
