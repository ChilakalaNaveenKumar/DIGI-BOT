<template>
  <div class="p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4">API Debug Test</h2>
    
    <!-- Test Button -->
    <button 
      @click="testAnalyzeAPI" 
      :disabled="isLoading"
      class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
    >
      {{ isLoading ? 'Testing...' : 'Test Analyze API' }}
    </button>
    
    <!-- Results -->
    <div class="mt-4 space-y-4">
      <!-- Success -->
      <div v-if="result" class="p-4 bg-green-50 border border-green-200 rounded">
        <h3 class="font-bold text-green-800">Success!</h3>
        <pre class="text-sm text-green-700 mt-2">{{ JSON.stringify(result, null, 2) }}</pre>
      </div>
      
      <!-- Error -->
      <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded">
        <h3 class="font-bold text-red-800">Error!</h3>
        <pre class="text-sm text-red-700 mt-2">{{ error }}</pre>
      </div>
      
      <!-- Debug Info -->
      <div class="p-4 bg-gray-50 border border-gray-200 rounded">
        <h3 class="font-bold text-gray-800">Debug Info</h3>
        <div class="text-sm text-gray-700 mt-2">
          <p><strong>API Base URL:</strong> {{ config.public.apiBase }}</p>
          <p><strong>Full URL:</strong> {{ config.public.apiBase }}/v1/components/analyze</p>
          <p><strong>Current Origin:</strong> {{ currentOrigin }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const config = useRuntimeConfig()
const isLoading = ref(false)
const result = ref<any>(null)
const error = ref<string | null>(null)
const currentOrigin = ref('')

// Get current origin
onMounted(() => {
  currentOrigin.value = window.location.origin
})

const testAnalyzeAPI = async () => {
  isLoading.value = true
  result.value = null
  error.value = null
  
  try {
    console.log('Testing analyze API...')
    console.log('API Base:', config.public.apiBase)
    console.log('Full URL:', `${config.public.apiBase}/v1/components/analyze`)
    
    const testRequest = {
      content: "Show me quarterly sales data: Q1: $100k, Q2: $150k, Q3: $200k, Q4: $180k",
      context: "Testing from frontend debug component",
      user_preferences: {}
    }
    
    console.log('Request payload:', testRequest)
    
    // Test using $fetch (Nuxt's built-in fetch)
    const response = await $fetch('/v1/components/analyze', {
      method: 'POST',
      baseURL: config.public.apiBase,
      body: testRequest,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer dev-token'
      }
    })
    
    console.log('Response:', response)
    result.value = response
    
  } catch (err: any) {
    console.error('API Test Error:', err)
    
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
    
    error.value = errorMessage
  } finally {
    isLoading.value = false
  }
}

// Alternative test with native fetch
const testWithNativeFetch = async () => {
  try {
    console.log('Testing with native fetch...')
    
    const response = await fetch(`${config.public.apiBase}/v1/components/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer dev-token'
      },
      body: JSON.stringify({
        content: "Test with native fetch",
        context: "Native fetch test"
      })
    })
    
    console.log('Native fetch response status:', response.status)
    console.log('Native fetch response headers:', [...response.headers.entries()])
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    console.log('Native fetch data:', data)
    
  } catch (err) {
    console.error('Native fetch error:', err)
  }
}

// Expose for debugging
defineExpose({
  testAnalyzeAPI,
  testWithNativeFetch
})
</script>
