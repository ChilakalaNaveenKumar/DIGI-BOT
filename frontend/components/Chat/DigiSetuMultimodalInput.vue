<template>
  <div class="ds-multimodal-input">
    <!-- Upload Options -->
    <div class="ds-upload-options">
      <div class="ds-upload-tabs">
        <button 
          v-for="tab in uploadTabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['ds-upload-tab', { 'ds-tab-active': activeTab === tab.id }]"
        >
          <Icon :name="tab.icon" class="ds-tab-icon" />
          {{ tab.label }}
        </button>
      </div>
    </div>
    
    <!-- Upload Content -->
    <div class="ds-upload-content">
      <!-- Image Upload -->
      <div v-if="activeTab === 'image'" class="ds-upload-panel">
        <DigiSetuImageUpload 
          @imageAnalyzed="handleImageAnalyzed"
          @streamingUpdate="handleStreamingUpdate"
        />
      </div>
      
      <!-- Audio Upload -->
      <div v-if="activeTab === 'audio'" class="ds-upload-panel">
        <DigiSetuAudioUpload 
          @audioTranscribed="handleAudioTranscribed"
          @audioAnalyzed="handleAudioAnalyzed"
        />
      </div>
      
      <!-- Tool Execution -->
      <div v-if="activeTab === 'tools'" class="ds-upload-panel">
        <div class="ds-tool-panel">
          <h3 class="ds-panel-title">Execute Tools</h3>
          
          <!-- Available Tools -->
          <div class="ds-available-tools">
            <div 
              v-for="tool in availableTools" 
              :key="tool.name"
              class="ds-tool-card"
              @click="selectTool(tool)"
            >
              <div class="ds-tool-header">
                <Icon name="mdi:tools" class="ds-tool-icon" />
                <span class="ds-tool-name">{{ tool.name }}</span>
              </div>
              <p class="ds-tool-description">{{ tool.description }}</p>
            </div>
          </div>
          
          <!-- Tool Execution Form -->
          <div v-if="selectedTool" class="ds-tool-form">
            <h4 class="ds-form-title">{{ selectedTool.name }}</h4>
            <p class="ds-form-description">{{ selectedTool.description }}</p>
            
            <!-- Dynamic Parameter Inputs -->
            <div class="ds-parameter-inputs">
              <div 
                v-for="(param, key) in selectedTool.parameters.properties" 
                :key="key"
                class="ds-parameter-input"
              >
                <label :for="key" class="ds-parameter-label">
                  {{ key }}
                  <span v-if="selectedTool.parameters.required?.includes(key)" class="ds-required">*</span>
                </label>
                <input 
                  :id="key"
                  v-model="toolParameters[key]"
                  :type="getInputType(param.type)"
                  :placeholder="param.description"
                  class="ds-parameter-field"
                />
              </div>
            </div>
            
            <div class="ds-form-actions">
              <button 
                @click="executeTool" 
                class="ds-execute-btn"
                :disabled="isExecuting"
              >
                <Icon name="mdi:play" class="ds-btn-icon" />
                {{ isExecuting ? 'Executing...' : 'Execute Tool' }}
              </button>
              <button 
                @click="clearTool" 
                class="ds-clear-btn"
              >
                <Icon name="mdi:close" class="ds-btn-icon" />
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Web Search -->
      <div v-if="activeTab === 'search'" class="ds-upload-panel">
        <div class="ds-search-panel">
          <h3 class="ds-panel-title">Web Search</h3>
          
          <div class="ds-search-form">
            <div class="ds-search-input-group">
              <input 
                v-model="searchQuery"
                type="text"
                placeholder="Enter your search query..."
                class="ds-search-input"
                @keydown.enter="performSearch"
              />
              <button 
                @click="performSearch"
                class="ds-search-btn"
                :disabled="isSearching || !searchQuery.trim()"
              >
                <Icon name="mdi:magnify" class="ds-btn-icon" />
                {{ isSearching ? 'Searching...' : 'Search' }}
              </button>
            </div>
            
            <div class="ds-search-options">
              <div class="ds-search-option">
                <label for="searchType" class="ds-option-label">Type:</label>
                <select id="searchType" v-model="searchType" class="ds-option-select">
                  <option value="web">Web</option>
                  <option value="news">News</option>
                  <option value="images">Images</option>
                </select>
              </div>
              
              <div class="ds-search-option">
                <label for="maxResults" class="ds-option-label">Results:</label>
                <select id="maxResults" v-model="maxResults" class="ds-option-select">
                  <option value="5">5</option>
                  <option value="10">10</option>
                  <option value="20">20</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Results Display -->
    <div v-if="hasResults" class="ds-results-section">
      <h3 class="ds-results-title">Results</h3>
      
      <!-- Image Analysis Results -->
      <div v-if="imageResults.length > 0" class="ds-result-group">
        <h4 class="ds-result-group-title">Image Analysis</h4>
        <div 
          v-for="(result, index) in imageResults" 
          :key="index"
          class="ds-result-item"
        >
          <DigiSetuVisionRenderer 
            :content="result.analysis"
            :metadata="result.metadata"
          />
        </div>
      </div>
      
      <!-- Audio Results -->
      <div v-if="audioResults.length > 0" class="ds-result-group">
        <h4 class="ds-result-group-title">Audio Processing</h4>
        <div 
          v-for="(result, index) in audioResults" 
          :key="index"
          class="ds-result-item"
        >
          <DigiSetuAudioRenderer 
            :content="result"
            :metadata="result.metadata"
          />
        </div>
      </div>
      
      <!-- Tool Results -->
      <div v-if="toolResults.length > 0" class="ds-result-group">
        <h4 class="ds-result-group-title">Tool Execution</h4>
        <div 
          v-for="(result, index) in toolResults" 
          :key="index"
          class="ds-result-item"
        >
          <DigiSetuToolRenderer 
            :content="result"
            :metadata="{ type: 'tool_result' }"
          />
        </div>
      </div>
      
      <!-- Search Results -->
      <div v-if="searchResults.length > 0" class="ds-result-group">
        <h4 class="ds-result-group-title">Search Results</h4>
        <div 
          v-for="(result, index) in searchResults" 
          :key="index"
          class="ds-result-item"
        >
          <DigiSetuSearchRenderer 
            :content="result"
            :metadata="{ type: 'search_result' }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Import upload components
import DigiSetuImageUpload from './DigiSetuImageUpload.vue'
import DigiSetuAudioUpload from './DigiSetuAudioUpload.vue'
import DigiSetuVisionRenderer from './DigiSetuVisionRenderer.vue'
import DigiSetuAudioRenderer from './DigiSetuAudioRenderer.vue'
import DigiSetuToolRenderer from './DigiSetuToolRenderer.vue'
import DigiSetuSearchRenderer from './DigiSetuSearchRenderer.vue'

// Reactive state
const activeTab = ref('image')
const selectedTool = ref(null)
const toolParameters = ref({})
const isExecuting = ref(false)
const searchQuery = ref('')
const searchType = ref('web')
const maxResults = ref(10)
const isSearching = ref(false)

// Results storage
const imageResults = ref([])
const audioResults = ref([])
const toolResults = ref([])
const searchResults = ref([])
const availableTools = ref([])

// Upload tabs configuration
const uploadTabs = [
  { id: 'image', label: 'Image', icon: 'mdi:image' },
  { id: 'audio', label: 'Audio', icon: 'mdi:microphone' },
  { id: 'tools', label: 'Tools', icon: 'mdi:tools' },
  { id: 'search', label: 'Search', icon: 'mdi:web' }
]

// Computed properties
const hasResults = computed(() => {
  return imageResults.value.length > 0 || 
         audioResults.value.length > 0 || 
         toolResults.value.length > 0 || 
         searchResults.value.length > 0
})

// Methods
const handleImageAnalyzed = (result) => {
  imageResults.value.push(result)
}

const handleStreamingUpdate = (update) => {
  // Handle streaming updates if needed
  console.log('Streaming update:', update)
}

const handleAudioTranscribed = (result) => {
  audioResults.value.push(result)
}

const handleAudioAnalyzed = (result) => {
  audioResults.value.push(result)
}

const loadAvailableTools = async () => {
  try {
    const response = await fetch('/api/v1/tools/available')
    if (response.ok) {
      const data = await response.json()
      availableTools.value = data.tools || []
    }
  } catch (error) {
    console.error('Failed to load available tools:', error)
  }
}

const selectTool = (tool) => {
  selectedTool.value = tool
  toolParameters.value = {}
  
  // Initialize parameters with default values
  if (tool.parameters?.properties) {
    Object.keys(tool.parameters.properties).forEach(key => {
      toolParameters.value[key] = ''
    })
  }
}

const clearTool = () => {
  selectedTool.value = null
  toolParameters.value = {}
}

const getInputType = (paramType) => {
  switch (paramType) {
    case 'number':
    case 'integer':
      return 'number'
    case 'boolean':
      return 'checkbox'
    default:
      return 'text'
  }
}

const executeTool = async () => {
  if (!selectedTool.value) return
  
  try {
    isExecuting.value = true
    
    const response = await fetch('/api/v1/tools/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tool_name: selectedTool.value.name,
        parameters: toolParameters.value
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      toolResults.value.push(result)
    } else {
      const error = await response.json()
      console.error('Tool execution failed:', error)
    }
  } catch (error) {
    console.error('Tool execution error:', error)
  } finally {
    isExecuting.value = false
  }
}

const performSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  try {
    isSearching.value = true
    
    const params = new URLSearchParams({
      query: searchQuery.value,
      max_results: maxResults.value,
      search_type: searchType.value
    })
    
    const response = await fetch(`/api/v1/search/web?${params}`)
    
    if (response.ok) {
      const result = await response.json()
      searchResults.value.push(result)
    } else {
      const error = await response.json()
      console.error('Search failed:', error)
    }
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    isSearching.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAvailableTools()
})
</script>

<style scoped>
.ds-multimodal-input {
  @apply space-y-6 p-6 bg-white rounded-lg border border-gray-200;
}

.ds-upload-options {
  @apply border-b border-gray-200 pb-4;
}

.ds-upload-tabs {
  @apply flex gap-2;
}

.ds-upload-tab {
  @apply flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors;
}

.ds-upload-tab.ds-tab-active {
  @apply bg-blue-600 text-white border-blue-600;
}

.ds-tab-icon {
  @apply w-4 h-4;
}

.ds-upload-content {
  @apply min-h-96;
}

.ds-upload-panel {
  @apply space-y-4;
}

.ds-tool-panel, .ds-search-panel {
  @apply space-y-4;
}

.ds-panel-title {
  @apply text-lg font-semibold text-gray-900;
}

.ds-available-tools {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.ds-tool-card {
  @apply p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors;
}

.ds-tool-header {
  @apply flex items-center gap-2 mb-2;
}

.ds-tool-icon {
  @apply w-5 h-5 text-blue-600;
}

.ds-tool-name {
  @apply font-medium text-gray-900;
}

.ds-tool-description {
  @apply text-sm text-gray-600;
}

.ds-tool-form {
  @apply p-4 bg-gray-50 rounded-lg space-y-4;
}

.ds-form-title {
  @apply font-medium text-gray-900;
}

.ds-form-description {
  @apply text-sm text-gray-600;
}

.ds-parameter-inputs {
  @apply space-y-3;
}

.ds-parameter-input {
  @apply space-y-1;
}

.ds-parameter-label {
  @apply block text-sm font-medium text-gray-700;
}

.ds-required {
  @apply text-red-500;
}

.ds-parameter-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.ds-form-actions {
  @apply flex gap-2;
}

.ds-execute-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.ds-clear-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors;
}

.ds-btn-icon {
  @apply w-4 h-4;
}

.ds-search-form {
  @apply space-y-4;
}

.ds-search-input-group {
  @apply flex gap-2;
}

.ds-search-input {
  @apply flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.ds-search-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.ds-search-options {
  @apply flex gap-4;
}

.ds-search-option {
  @apply flex items-center gap-2;
}

.ds-option-label {
  @apply text-sm font-medium text-gray-700;
}

.ds-option-select {
  @apply px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.ds-results-section {
  @apply space-y-6 pt-6 border-t border-gray-200;
}

.ds-results-title {
  @apply text-lg font-semibold text-gray-900;
}

.ds-result-group {
  @apply space-y-3;
}

.ds-result-group-title {
  @apply font-medium text-gray-800;
}

.ds-result-item {
  @apply space-y-2;
}
</style>

