<template>
  <div class="min-h-screen bg-gray-100 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-center mb-8">API Debug Page</h1>
      
      <div class="space-y-6">
        <!-- API Test Component -->
        <DebugApiTest />
        
        <!-- Manual Test Section -->
        <div class="p-6 bg-white rounded-lg shadow-md">
          <h2 class="text-xl font-bold mb-4">Manual Component Analysis Test</h2>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Test Content:</label>
              <textarea
                v-model="testContent"
                class="w-full p-3 border border-gray-300 rounded-md"
                rows="4"
                placeholder="Enter content to analyze..."
              />
            </div>
            
            <button
              @click="runManualTest"
              :disabled="isManualTesting"
              class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
            >
              {{ isManualTesting ? 'Testing...' : 'Test Component Analysis' }}
            </button>
            
            <!-- Manual Results -->
            <div v-if="manualResult" class="p-4 bg-blue-50 border border-blue-200 rounded">
              <h3 class="font-bold text-blue-800">Component Analysis Result:</h3>
              <div class="mt-2">
                <p><strong>Decision:</strong> {{ manualResult.decision }}</p>
                <p><strong>Component Type:</strong> {{ manualResult.component_type || 'None' }}</p>
                <p><strong>Confidence:</strong> {{ manualResult.confidence }}</p>
                <p><strong>Reasoning:</strong> {{ manualResult.reasoning }}</p>
                
                <div v-if="manualResult.markdown" class="mt-2">
                  <strong>Generated Markdown:</strong>
                  <pre class="text-xs bg-gray-100 p-2 rounded mt-1">{{ manualResult.markdown }}</pre>
                </div>
                
                <div v-if="manualResult.extracted_data" class="mt-2">
                  <strong>Extracted Data:</strong>
                  <pre class="text-xs bg-gray-100 p-2 rounded mt-1">{{ JSON.stringify(manualResult.extracted_data, null, 2) }}</pre>
                </div>
              </div>
            </div>
            
            <div v-if="manualError" class="p-4 bg-red-50 border border-red-200 rounded">
              <h3 class="font-bold text-red-800">Manual Test Error:</h3>
              <pre class="text-sm text-red-700 mt-2">{{ manualError }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Manual test state
const testContent = ref('Quarterly Sales Report:\nQ1 2024: $150,000\nQ2 2024: $180,000\nQ3 2024: $220,000\nQ4 2024: $195,000\n\nThis shows a strong growth trend with Q3 being our best quarter.')
const isManualTesting = ref(false)
const manualResult = ref<any>(null)
const manualError = ref<string | null>(null)

// Use the component analysis composable
const { analyzeContent } = useComponentAnalysis()

const runManualTest = async () => {
  if (!testContent.value.trim()) {
    alert('Please enter some content to test')
    return
  }
  
  isManualTesting.value = true
  manualResult.value = null
  manualError.value = null
  
  try {
    console.log('Running manual component analysis test...')
    
    const result = await analyzeContent({
      content: testContent.value,
      context: 'Manual test from debug page',
      user_preferences: {}
    })
    
    console.log('Manual test result:', result)
    manualResult.value = result
    
  } catch (err: any) {
    console.error('Manual test error:', err)
    
    let errorMessage = 'Unknown error'
    if (err.data) {
      errorMessage = JSON.stringify(err.data, null, 2)
    } else if (err.message) {
      errorMessage = err.message
    } else if (typeof err === 'string') {
      errorMessage = err
    } else {
      errorMessage = JSON.stringify(err, null, 2)
    }
    
    manualError.value = errorMessage
  } finally {
    isManualTesting.value = false
  }
}

// Set page meta
useHead({
  title: 'API Debug - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Debug API endpoints and component analysis' }
  ]
})
</script>
