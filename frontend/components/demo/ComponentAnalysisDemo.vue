<template>
  <div class="component-analysis-demo p-6 max-w-4xl mx-auto">
    <div class="demo-header mb-8">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        Enhanced Component Analysis Demo
      </h2>
      <p class="text-gray-600 dark:text-gray-400">
        Test AI-powered content analysis and dynamic component generation
      </p>
    </div>

    <!-- Content Input -->
    <div class="content-input mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Content to Analyze
      </label>
      <textarea
        v-model="testContent"
        class="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        placeholder="Enter content that might contain data suitable for charts or tables..."
      />
      
      <div class="flex gap-2 mt-3">
        <UiButton 
          @click="analyzeContent"
          :disabled="isAnalyzing || !testContent.trim()"
          class="flex items-center gap-2"
        >
          <Icon v-if="isAnalyzing" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
          <Icon v-else name="lucide:search" class="w-4 h-4" />
          {{ isAnalyzing ? 'Analyzing...' : 'Analyze Content' }}
        </UiButton>
        
        <select
          v-model="selectedSampleId"
          class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
          @change="loadSpecificSample"
          :disabled="isAnalyzing"
        >
          <option value="">Choose Sample...</option>
          <option
            v-for="sample in availableMockResponses"
            :key="sample.id"
            :value="sample.id"
          >
            {{ sample.description }}
          </option>
        </select>
        
        <UiButton 
          variant="outline"
          @click="loadSampleContent"
          :disabled="isAnalyzing"
        >
          Random Sample
        </UiButton>
        
        <UiButton 
          variant="outline"
          @click="clearContent"
          :disabled="isAnalyzing"
        >
          Clear
        </UiButton>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-display mb-6">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
        <div class="flex items-center gap-2">
          <Icon name="lucide:alert-circle" class="w-5 h-5 text-red-600 dark:text-red-400" />
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Analysis Error</h3>
        </div>
        <p class="mt-1 text-sm text-red-700 dark:text-red-300">{{ error }}</p>
        <UiButton variant="outline" size="sm" @click="clearError" class="mt-2">
          Dismiss
        </UiButton>
      </div>
    </div>

    <!-- Analysis Results -->
    <div v-if="lastDecision" class="analysis-results mb-8">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Analysis Results
      </h3>
      
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="result-item">
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Decision
            </label>
            <div class="mt-1 flex items-center gap-2">
              <UiBadge :variant="lastDecision.decision === 'GENERATE_NOW' ? 'success' : 'secondary'">
                {{ lastDecision.decision }}
              </UiBadge>
            </div>
          </div>
          
          <div class="result-item">
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Component Type
            </label>
            <div class="mt-1">
              <span v-if="lastDecision.component_type" class="text-sm font-mono text-gray-900 dark:text-gray-100">
                {{ lastDecision.component_type }}
              </span>
              <span v-else class="text-sm text-gray-500 dark:text-gray-400">
                None
              </span>
            </div>
          </div>
          
          <div class="result-item">
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Confidence
            </label>
            <div class="mt-1">
              <span class="text-sm font-mono text-gray-900 dark:text-gray-100">
                {{ (lastDecision.confidence * 100).toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
        
        <div class="mt-4">
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
            Reasoning
          </label>
          <p class="text-sm text-gray-700 dark:text-gray-300">
            {{ lastDecision.reasoning }}
          </p>
        </div>
      </div>

      <!-- Generated Markdown -->
      <div v-if="lastDecision.markdown" class="generated-markdown">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Generated Component Markdown
        </label>
        <div class="bg-gray-900 dark:bg-gray-950 rounded-md p-4 overflow-x-auto">
          <pre class="text-sm text-green-400 font-mono whitespace-pre-wrap">{{ lastDecision.markdown }}</pre>
        </div>
      </div>
    </div>

    <!-- Component Preview -->
    <div v-if="lastDecision?.decision === 'GENERATE_NOW' && lastDecision.markdown" class="component-preview">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Component Preview
      </h3>
      
      <div class="preview-container bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <EnhancedComponentRenderer
          :component-type="lastDecision.component_type"
          :markdown="lastDecision.markdown"
        />
      </div>
    </div>

    <!-- Supported Components Info -->
    <div v-if="supportedComponents.length" class="supported-components mt-8">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Supported Components
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="component in supportedComponents"
          :key="component.type"
          class="component-card bg-gray-50 dark:bg-gray-800 rounded-lg p-4"
        >
          <div class="flex items-center gap-2 mb-2">
            <Icon name="lucide:component" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ component.name }}</h4>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {{ component.description }}
          </p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="use in component.best_for.slice(0, 3)"
              :key="use"
              class="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-2 py-1 rounded"
            >
              {{ use }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { complexMockResponses, getRandomMockResponse, type MockResponse } from '~/utils/complexMockData'

// Available mock responses for testing
const availableMockResponses = complexMockResponses

const { 
  isAnalyzing, 
  lastDecision, 
  supportedComponents, 
  error,
  analyzeContent: performAnalysis,
  clearError 
} = useComponentAnalysis()

const testContent = ref('')
const previewData = ref<any>(null)
const selectedSampleId = ref('')

const analyzeContent = async () => {
  if (!testContent.value.trim()) return
  
  await performAnalysis({
    content: testContent.value,
    context: 'Component analysis demo'
  })
}

// Preview data generation removed - now using AI's actual extracted data

const loadSampleContent = () => {
  const randomMockResponse = getRandomMockResponse()
  testContent.value = randomMockResponse.content
  selectedSampleId.value = randomMockResponse.id
  console.log(`🎯 Loaded sample: ${randomMockResponse.id}`)
  console.log(`📊 Expected components: ${randomMockResponse.expectedComponents.join(', ')}`)
}

const loadSpecificSample = () => {
  if (!selectedSampleId.value) return
  
  const mockResponse = availableMockResponses.find(r => r.id === selectedSampleId.value)
  if (mockResponse) {
    testContent.value = mockResponse.content
    console.log(`🎯 Loaded specific sample: ${mockResponse.id}`)
    console.log(`📊 Expected components: ${mockResponse.expectedComponents.join(', ')}`)
  }
}

const clearContent = () => {
  testContent.value = ''
  previewData.value = null
  selectedSampleId.value = ''
}
</script>

<style scoped>
.component-analysis-demo {
  @apply space-y-6;
}

.result-item {
  @apply min-w-0;
}

.preview-container {
  @apply shadow-sm;
}

.component-card {
  @apply transition-colors hover:bg-gray-100 dark:hover:bg-gray-700;
}
</style>
