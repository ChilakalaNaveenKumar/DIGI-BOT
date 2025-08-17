<template>
  <div class="ds-live-search-renderer">
    <div class="ds-search-header">
      <Icon name="mdi:web" class="ds-search-icon" />
      <h3 class="ds-search-title">Live Search Results</h3>
      <div class="ds-search-meta">
        <span class="ds-provider-badge">
          <Icon :name="getProviderIcon(metadata.provider)" class="ds-provider-icon" />
          {{ formatProviderName(metadata.provider) }}
        </span>
        <span class="ds-search-time">{{ metadata.search_time?.toFixed(3) }}s</span>
      </div>
    </div>

    <div class="ds-search-content">
      <!-- Query Information -->
      <div class="ds-query-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:magnify" class="ds-section-icon" />
          Search Query
        </h4>
        <div class="ds-query-info">
          <div class="ds-query-text">{{ metadata.query || 'Search query' }}</div>
          <div class="ds-query-stats">
            <span class="ds-result-count">{{ metadata.total_results || 0 }} results</span>
            <span class="ds-search-timestamp">{{ formatTimestamp(metadata.timestamp) }}</span>
          </div>
        </div>
      </div>

      <!-- Search Results -->
      <div class="ds-results-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:format-list-bulleted" class="ds-section-icon" />
          Top Results
          <button @click="toggleResultsView" class="ds-view-toggle">
            <Icon :name="resultsView === 'cards' ? 'mdi:view-list' : 'mdi:view-grid'" class="ds-toggle-icon" />
            {{ resultsView === 'cards' ? 'List View' : 'Card View' }}
          </button>
        </h4>
        
        <!-- Card View -->
        <div v-if="resultsView === 'cards'" class="ds-results-cards">
          <div 
            v-for="(result, index) in searchResults" 
            :key="index"
            class="ds-result-card"
          >
            <div class="ds-result-header">
              <div class="ds-result-rank">{{ index + 1 }}</div>
              <div class="ds-result-info">
                <h5 class="ds-result-title">
                  <a :href="result.url" target="_blank" rel="noopener noreferrer" class="ds-result-link">
                    {{ result.title }}
                    <Icon name="mdi:open-in-new" class="ds-external-icon" />
                  </a>
                </h5>
                <div class="ds-result-meta">
                  <span class="ds-result-source">{{ result.source }}</span>
                  <span v-if="result.published_date" class="ds-result-date">
                    {{ formatDate(result.published_date) }}
                  </span>
                  <span v-if="result.relevance_score" class="ds-relevance-score">
                    <Icon name="mdi:target" class="ds-relevance-icon" />
                    {{ Math.round(result.relevance_score * 100) }}%
                  </span>
                </div>
              </div>
            </div>
            
            <div class="ds-result-content">
              <p class="ds-result-snippet">{{ result.snippet }}</p>
              <div class="ds-result-actions">
                <button @click="copyUrl(result.url)" class="ds-action-btn">
                  <Icon name="mdi:content-copy" class="ds-action-icon" />
                  Copy URL
                </button>
                <button @click="shareResult(result)" class="ds-action-btn">
                  <Icon name="mdi:share" class="ds-action-icon" />
                  Share
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- List View -->
        <div v-else class="ds-results-list">
          <div 
            v-for="(result, index) in searchResults" 
            :key="index"
            class="ds-result-item"
          >
            <div class="ds-item-rank">{{ index + 1 }}</div>
            <div class="ds-item-content">
              <h5 class="ds-item-title">
                <a :href="result.url" target="_blank" rel="noopener noreferrer" class="ds-item-link">
                  {{ result.title }}
                </a>
              </h5>
              <p class="ds-item-snippet">{{ result.snippet }}</p>
              <div class="ds-item-meta">
                <span class="ds-item-source">{{ result.source }}</span>
                <span v-if="result.published_date" class="ds-item-date">
                  {{ formatDate(result.published_date) }}
                </span>
                <span v-if="result.relevance_score" class="ds-item-relevance">
                  {{ Math.round(result.relevance_score * 100) }}% relevant
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Search Insights -->
      <div v-if="searchInsights.length > 0" class="ds-insights-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:lightbulb" class="ds-section-icon" />
          Search Insights
        </h4>
        <div class="ds-insights-list">
          <div 
            v-for="(insight, index) in searchInsights" 
            :key="index"
            class="ds-insight-item"
          >
            <Icon :name="insight.icon" class="ds-insight-icon" />
            <span class="ds-insight-text">{{ insight.text }}</span>
          </div>
        </div>
      </div>

      <!-- Related Searches -->
      <div class="ds-related-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:link-variant" class="ds-section-icon" />
          Related Searches
        </h4>
        <div class="ds-related-searches">
          <button 
            v-for="related in relatedSearches" 
            :key="related"
            @click="performRelatedSearch(related)"
            class="ds-related-btn"
          >
            <Icon name="mdi:magnify" class="ds-related-icon" />
            {{ related }}
          </button>
        </div>
      </div>

      <!-- Provider Information -->
      <div class="ds-provider-section">
        <h4 class="ds-section-title">
          <Icon name="mdi:information" class="ds-section-icon" />
          Search Provider Details
        </h4>
        <div class="ds-provider-info">
          <div class="ds-provider-details">
            <div class="ds-provider-name">
              <Icon :name="getProviderIcon(metadata.provider)" class="ds-provider-detail-icon" />
              {{ formatProviderName(metadata.provider) }}
            </div>
            <div class="ds-provider-stats">
              <span>{{ metadata.total_results }} results in {{ metadata.search_time?.toFixed(3) }}s</span>
            </div>
          </div>
          <div class="ds-provider-note">
            <p v-if="metadata.provider === 'mock'">
              This is a demonstration using mock search results. 
              Configure real search providers for live web data.
            </p>
            <p v-else>
              Results provided by {{ formatProviderName(metadata.provider) }} search API.
            </p>
          </div>
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
const resultsView = ref('cards')

// Computed properties
const searchResults = computed(() => {
  if (props.metadata.results && Array.isArray(props.metadata.results)) {
    return props.metadata.results
  }
  
  // Try to parse results from content if not in metadata
  const results = []
  const resultMatches = props.content.match(/\*\*\d+\.\s+(.*?)\*\*(.*?)(?=\*\*\d+\.|$)/gs)
  
  if (resultMatches) {
    resultMatches.forEach((match, index) => {
      const lines = match.split('\n').filter(line => line.trim())
      const title = lines[0]?.replace(/\*\*\d+\.\s+/, '').replace(/\*\*/g, '') || `Result ${index + 1}`
      const snippet = lines[1] || 'No description available'
      const urlMatch = match.match(/🔗\s+(https?:\/\/[^\s]+)/)
      
      results.push({
        title,
        snippet,
        url: urlMatch ? urlMatch[1] : '#',
        source: new URL(urlMatch ? urlMatch[1] : 'https://example.com').hostname,
        relevance_score: 1.0 - (index * 0.1),
        published_date: null
      })
    })
  }
  
  return results.length > 0 ? results : [
    {
      title: 'No search results available',
      snippet: 'Unable to parse search results from the response.',
      url: '#',
      source: 'Unknown',
      relevance_score: 0,
      published_date: null
    }
  ]
})

const searchInsights = computed(() => {
  const insights = []
  const resultCount = searchResults.value.length
  const avgRelevance = searchResults.value.reduce((sum, r) => sum + (r.relevance_score || 0), 0) / resultCount
  
  if (resultCount > 0) {
    insights.push({
      icon: 'mdi:chart-line',
      text: `Found ${resultCount} relevant results with ${Math.round(avgRelevance * 100)}% average relevance`
    })
  }
  
  if (props.metadata.search_time && props.metadata.search_time < 1) {
    insights.push({
      icon: 'mdi:lightning-bolt',
      text: `Fast search completed in ${(props.metadata.search_time * 1000).toFixed(0)}ms`
    })
  }
  
  const uniqueSources = [...new Set(searchResults.value.map(r => r.source))]
  if (uniqueSources.length > 1) {
    insights.push({
      icon: 'mdi:web',
      text: `Results from ${uniqueSources.length} different sources`
    })
  }
  
  return insights
})

const relatedSearches = computed(() => {
  const query = props.metadata.query || ''
  const baseSearches = [
    `${query} tutorial`,
    `${query} examples`,
    `${query} best practices`,
    `how to ${query}`,
    `${query} vs alternatives`
  ]
  
  return baseSearches.slice(0, 4)
})

// Methods
const toggleResultsView = () => {
  resultsView.value = resultsView.value === 'cards' ? 'list' : 'cards'
}

const copyUrl = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    // Could add a toast notification here
  } catch (err) {
    console.error('Failed to copy URL:', err)
  }
}

const shareResult = async (result) => {
  if (navigator.share) {
    try {
      await navigator.share({
        title: result.title,
        text: result.snippet,
        url: result.url
      })
    } catch (err) {
      console.error('Failed to share:', err)
    }
  } else {
    // Fallback to copying URL
    copyUrl(result.url)
  }
}

const performRelatedSearch = (query) => {
  // Emit event to parent component to perform new search
  // This would typically trigger a new search request
  console.log('Performing related search:', query)
}

const formatProviderName = (provider) => {
  const names = {
    'mock': 'Mock Search',
    'serp_api': 'SerpAPI',
    'bing_api': 'Bing Search',
    'google_api': 'Google Search',
    'duckduckgo': 'DuckDuckGo'
  }
  return names[provider] || provider
}

const getProviderIcon = (provider) => {
  const icons = {
    'mock': 'mdi:test-tube',
    'serp_api': 'mdi:google',
    'bing_api': 'mdi:microsoft',
    'google_api': 'mdi:google',
    'duckduckgo': 'mdi:duck'
  }
  return icons[provider] || 'mdi:web'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return dateString
  }
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'Recently'
  try {
    return new Date(timestamp).toLocaleString()
  } catch {
    return timestamp
  }
}
</script>

<style scoped>
@reference "tailwindcss";
.ds-live-search-renderer {
  @apply bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-lg p-6 space-y-6;
}

.ds-search-header {
  @apply flex items-center justify-between flex-wrap gap-4;
}

.ds-search-icon {
  @apply w-6 h-6 text-blue-600;
}

.ds-search-title {
  @apply flex-1 text-lg font-semibold text-blue-900;
}

.ds-search-meta {
  @apply flex items-center gap-3;
}

.ds-provider-badge {
  @apply flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium;
}

.ds-provider-icon {
  @apply w-4 h-4;
}

.ds-search-time {
  @apply px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-medium;
}

.ds-search-content {
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

.ds-query-section {
  @apply space-y-3;
}

.ds-query-info {
  @apply p-4 bg-white rounded-lg border border-blue-200 space-y-2;
}

.ds-query-text {
  @apply font-medium text-gray-900;
}

.ds-query-stats {
  @apply flex items-center gap-4 text-sm text-gray-600;
}

.ds-result-count {
  @apply font-medium;
}

.ds-results-section {
  @apply space-y-4;
}

.ds-results-cards {
  @apply space-y-4;
}

.ds-result-card {
  @apply bg-white rounded-lg border border-blue-200 overflow-hidden hover:shadow-md transition-shadow;
}

.ds-result-header {
  @apply flex items-start gap-3 p-4 pb-2;
}

.ds-result-rank {
  @apply w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm;
}

.ds-result-info {
  @apply flex-1 space-y-2;
}

.ds-result-title {
  @apply font-medium;
}

.ds-result-link {
  @apply text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1;
}

.ds-external-icon {
  @apply w-4 h-4;
}

.ds-result-meta {
  @apply flex items-center gap-3 text-sm text-gray-600;
}

.ds-result-source {
  @apply font-medium;
}

.ds-relevance-score {
  @apply flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded;
}

.ds-relevance-icon {
  @apply w-3 h-3;
}

.ds-result-content {
  @apply px-4 pb-4 space-y-3;
}

.ds-result-snippet {
  @apply text-gray-700 leading-relaxed;
}

.ds-result-actions {
  @apply flex gap-2;
}

.ds-action-btn {
  @apply flex items-center gap-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors;
}

.ds-action-icon {
  @apply w-4 h-4;
}

.ds-results-list {
  @apply space-y-3;
}

.ds-result-item {
  @apply flex gap-3 p-4 bg-white rounded-lg border border-blue-200;
}

.ds-item-rank {
  @apply w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm;
}

.ds-item-content {
  @apply flex-1 space-y-1;
}

.ds-item-title {
  @apply font-medium;
}

.ds-item-link {
  @apply text-blue-600 hover:text-blue-800 hover:underline;
}

.ds-item-snippet {
  @apply text-gray-700 text-sm;
}

.ds-item-meta {
  @apply flex items-center gap-3 text-xs text-gray-500;
}

.ds-insights-section, .ds-related-section, .ds-provider-section {
  @apply space-y-3;
}

.ds-insights-list {
  @apply space-y-2;
}

.ds-insight-item {
  @apply flex items-center gap-2 p-3 bg-white rounded border border-blue-200;
}

.ds-insight-icon {
  @apply w-5 h-5 text-blue-600;
}

.ds-insight-text {
  @apply text-gray-700;
}

.ds-related-searches {
  @apply flex flex-wrap gap-2;
}

.ds-related-btn {
  @apply flex items-center gap-1 px-3 py-2 bg-white border border-blue-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors text-sm;
}

.ds-related-icon {
  @apply w-4 h-4 text-blue-600;
}

.ds-provider-info {
  @apply p-4 bg-white rounded-lg border border-blue-200 space-y-3;
}

.ds-provider-details {
  @apply flex items-center justify-between;
}

.ds-provider-name {
  @apply flex items-center gap-2 font-medium text-gray-900;
}

.ds-provider-detail-icon {
  @apply w-5 h-5 text-blue-600;
}

.ds-provider-stats {
  @apply text-sm text-gray-600;
}

.ds-provider-note {
  @apply text-sm text-gray-600 italic;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .ds-live-search-renderer {
    @apply from-blue-900/20 to-cyan-900/20 border-blue-700;
  }
  
  .ds-search-title {
    @apply text-blue-100;
  }
  
  .ds-result-card, .ds-result-item, .ds-query-info, .ds-insight-item, .ds-related-btn, .ds-provider-info {
    @apply bg-gray-800 border-gray-700;
  }
  
  .ds-result-title, .ds-item-title {
    @apply text-gray-100;
  }
  
  .ds-result-snippet, .ds-item-snippet, .ds-insight-text {
    @apply text-gray-300;
  }
}
</style>

