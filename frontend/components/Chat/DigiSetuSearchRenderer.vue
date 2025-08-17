<template>
  <div class="ds-search-renderer">
    <!-- Header -->
    <div class="ds-search-header">
      <div class="ds-header-info">
        <Icon :name="headerIcon" class="ds-header-icon" />
        <h3 class="ds-header-title">{{ headerTitle }}</h3>
        <span class="ds-results-badge">{{ searchData.total_results }} results</span>
      </div>
      <div class="ds-header-actions">
        <button @click="copyResults" class="ds-action-btn">
          <Icon name="mdi:content-copy" class="ds-action-icon" />
          Copy
        </button>
        <button @click="toggleView" class="ds-action-btn">
          <Icon :name="isCompactView ? 'mdi:view-list' : 'mdi:view-grid'" class="ds-action-icon" />
          {{ isCompactView ? 'Detailed' : 'Compact' }}
        </button>
      </div>
    </div>
    
    <!-- Search Query -->
    <div class="ds-search-query">
      <div class="ds-query-info">
        <Icon name="mdi:magnify" class="ds-query-icon" />
        <span class="ds-query-text">{{ searchData.query }}</span>
        <div class="ds-query-metadata">
          <span v-if="searchData.search_type" class="ds-metadata-tag">{{ searchData.search_type }}</span>
          <span v-if="searchData.time_range" class="ds-metadata-tag">{{ searchData.time_range }}</span>
          <span v-if="searchTime" class="ds-metadata-tag">{{ searchTime }}s</span>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div class="ds-search-results">
      <div v-if="searchData.results && searchData.results.length > 0">
        <div 
          v-for="(result, index) in displayedResults" 
          :key="index"
          class="ds-search-result"
          :class="{ 'ds-compact-result': isCompactView }"
        >
          <!-- Result Header -->
          <div class="ds-result-header">
            <a 
              :href="result.url" 
              target="_blank" 
              rel="noopener noreferrer"
              class="ds-result-title"
            >
              {{ result.title }}
            </a>
            <div class="ds-result-meta">
              <span class="ds-result-domain">{{ getDomain(result.url) }}</span>
              <span v-if="result.published_date" class="ds-result-date">{{ formatDate(result.published_date) }}</span>
            </div>
          </div>

          <!-- Result Content -->
          <div v-if="!isCompactView" class="ds-result-content">
            <p class="ds-result-snippet">{{ result.snippet }}</p>
            <div class="ds-result-url">
              <Icon name="mdi:link" class="ds-url-icon" />
              <span class="ds-url-text">{{ result.url }}</span>
            </div>
          </div>

          <!-- Result Actions -->
          <div class="ds-result-actions">
            <button @click="openResult(result)" class="ds-result-action" title="Open">
              <Icon name="mdi:open-in-new" class="ds-action-icon" />
            </button>
            <button @click="copyResult(result)" class="ds-result-action" title="Copy">
              <Icon name="mdi:content-copy" class="ds-action-icon" />
            </button>
            <button @click="shareResult(result)" class="ds-result-action" title="Share">
              <Icon name="mdi:share" class="ds-action-icon" />
            </button>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="canLoadMore" class="ds-load-more">
          <button @click="loadMore" class="ds-load-more-btn">
            <Icon name="mdi:chevron-down" class="ds-load-more-icon" />
            Show More Results
          </button>
        </div>
      </div>

      <!-- No Results -->
      <div v-else class="ds-no-results">
        <Icon name="mdi:magnify-close" class="ds-no-results-icon" />
        <h4 class="ds-no-results-title">No results found</h4>
        <p class="ds-no-results-text">Try adjusting your search terms or filters</p>
      </div>
    </div>

    <!-- Search Stats -->
    <div v-if="searchData.search_metadata" class="ds-search-stats">
      <div class="ds-stats-grid">
        <div class="ds-stat-item">
          <Icon name="mdi:clock-outline" class="ds-stat-icon" />
          <span class="ds-stat-label">Search Time</span>
          <span class="ds-stat-value">{{ searchData.search_metadata.search_time || 'N/A' }}</span>
        </div>
        <div class="ds-stat-item">
          <Icon name="mdi:database" class="ds-stat-icon" />
          <span class="ds-stat-label">Total Results</span>
          <span class="ds-stat-value">{{ searchData.total_results || 0 }}</span>
        </div>
        <div class="ds-stat-item">
          <Icon name="mdi:web" class="ds-stat-icon" />
          <span class="ds-stat-label">Sources</span>
          <span class="ds-stat-value">{{ uniqueSources }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

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

// Parse search data
const searchData = computed(() => {
  try {
    return typeof props.content === 'string' ? JSON.parse(props.content) : props.content
  } catch {
    return { results: [], total_results: 0, query: 'Search query' }
  }
})

// Component state
const isCompactView = ref(false)
const displayLimit = ref(5)

// Computed properties
const headerIcon = computed(() => {
  const type = searchData.value.search_type?.toLowerCase()
  if (type === 'news') return 'mdi:newspaper'
  if (type === 'images') return 'mdi:image'
  if (type === 'videos') return 'mdi:video'
  return 'mdi:web'
})

const headerTitle = computed(() => {
  const type = searchData.value.search_type
  return type ? `${type} Search Results` : 'Search Results'
})

const displayedResults = computed(() => {
  return searchData.value.results?.slice(0, displayLimit.value) || []
})

const canLoadMore = computed(() => {
  return searchData.value.results?.length > displayLimit.value
})

const searchTime = computed(() => {
  return searchData.value.search_metadata?.search_time || 
         props.metadata.search_time || 
         null
})

const uniqueSources = computed(() => {
  const domains = new Set()
  searchData.value.results?.forEach(result => {
    if (result.url) {
      try {
        domains.add(new URL(result.url).hostname)
      } catch {}
    }
  })
  return domains.size
})

// Methods
const toggleView = () => {
  isCompactView.value = !isCompactView.value
}

const loadMore = () => {
  displayLimit.value += 5
}

const getDomain = (url) => {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return 'Unknown'
  }
}

const formatDate = (dateString) => {
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return dateString
  }
}

const openResult = (result) => {
  window.open(result.url, '_blank', 'noopener,noreferrer')
}

const copyResult = async (result) => {
  try {
    await navigator.clipboard.writeText(result.url)
    // Could add toast notification here
  } catch (error) {
    console.error('Failed to copy:', error)
  }
}

const shareResult = async (result) => {
  if (navigator.share) {
    try {
      await navigator.share({
        title: result.title,
        url: result.url
      })
    } catch (error) {
      console.error('Failed to share:', error)
    }
  } else {
    copyResult(result)
  }
}

const copyResults = async () => {
  try {
    const text = searchData.value.results?.map(r => `${r.title}\n${r.url}`).join('\n\n')
    await navigator.clipboard.writeText(text)
  } catch (error) {
    console.error('Failed to copy results:', error)
  }
}
</script>

<style scoped>
.ds-search-renderer {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  padding: var(--ds-space-6);
  margin: var(--ds-space-4) 0;
}

.ds-search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--ds-space-4);
  padding-bottom: var(--ds-space-4);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-header-info {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--ds-primary);
}

.ds-header-title {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
  margin: 0;
}

.ds-results-badge {
  background: var(--ds-primary);
  color: white;
  padding: var(--ds-space-1) var(--ds-space-3);
  border-radius: var(--ds-radius-full);
  font-size: var(--ds-text-xs);
  font-weight: var(--ds-font-medium);
}

.ds-header-actions {
  display: flex;
  gap: var(--ds-space-2);
}

.ds-action-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  color: var(--ds-text-secondary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.ds-action-btn:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-text-primary);
}

.ds-search-query {
  margin-bottom: var(--ds-space-6);
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
}

.ds-query-info {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
  flex-wrap: wrap;
}

.ds-query-icon {
  width: 1rem;
  height: 1rem;
  color: var(--ds-text-muted);
}

.ds-query-text {
  font-weight: var(--ds-font-medium);
  color: var(--ds-text-primary);
}

.ds-query-metadata {
  display: flex;
  gap: var(--ds-space-2);
  margin-left: auto;
}

.ds-metadata-tag {
  padding: var(--ds-space-1) var(--ds-space-2);
  background: var(--ds-primary);
  color: white;
  font-size: var(--ds-text-xs);
  border-radius: var(--ds-radius-sm);
}

.ds-search-results {
  display: flex;
  flex-direction: column;
  gap: var(--ds-space-4);
}

.ds-search-result {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  transition: all 0.2s ease;
}

.ds-search-result:hover {
  background: var(--ds-surface-hover);
  border-color: var(--ds-border-secondary);
}

.ds-compact-result {
  padding: var(--ds-space-3);
}

.ds-result-header {
  margin-bottom: var(--ds-space-3);
}

.ds-result-title {
  display: block;
  font-size: var(--ds-text-base);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-primary);
  text-decoration: none;
  margin-bottom: var(--ds-space-2);
  line-height: var(--ds-leading-tight);
}

.ds-result-title:hover {
  text-decoration: underline;
}

.ds-result-meta {
  display: flex;
  gap: var(--ds-space-3);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
}

.ds-result-content {
  margin-bottom: var(--ds-space-3);
}

.ds-result-snippet {
  color: var(--ds-text-secondary);
  line-height: var(--ds-leading-relaxed);
  margin-bottom: var(--ds-space-3);
}

.ds-result-url {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
}

.ds-url-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.ds-url-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ds-result-actions {
  display: flex;
  gap: var(--ds-space-2);
  margin-top: var(--ds-space-3);
  padding-top: var(--ds-space-3);
  border-top: 1px solid var(--ds-border-primary);
}

.ds-result-action {
  padding: var(--ds-space-2);
  background: transparent;
  border: none;
  color: var(--ds-text-muted);
  cursor: pointer;
  border-radius: var(--ds-radius-sm);
  transition: all 0.2s ease;
}

.ds-result-action:hover {
  background: var(--ds-surface-hover);
  color: var(--ds-primary);
}

.ds-load-more {
  display: flex;
  justify-content: center;
  padding-top: var(--ds-space-2);
}

.ds-load-more-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-3) var(--ds-space-4);
  background: transparent;
  border: 1px solid var(--ds-border-primary);
  color: var(--ds-primary);
  border-radius: var(--ds-radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.ds-load-more-btn:hover {
  background: var(--ds-surface-hover);
  border-color: var(--ds-primary);
}

.ds-no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-8);
  color: var(--ds-text-muted);
  text-align: center;
}

.ds-no-results-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: var(--ds-space-4);
  opacity: 0.5;
}

.ds-no-results-title {
  font-size: var(--ds-text-lg);
  font-weight: var(--ds-font-semibold);
  margin-bottom: var(--ds-space-2);
  color: var(--ds-text-secondary);
}

.ds-no-results-text {
  color: var(--ds-text-muted);
}

.ds-search-stats {
  margin-top: var(--ds-space-6);
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
}

.ds-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--ds-space-4);
}

.ds-stat-item {
  text-align: center;
}

.ds-stat-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin: 0 auto var(--ds-space-1);
  color: var(--ds-primary);
}

.ds-stat-label {
  display: block;
  font-size: var(--ds-text-xs);
  color: var(--ds-text-muted);
  margin-bottom: var(--ds-space-1);
}

.ds-stat-value {
  display: block;
  font-size: var(--ds-text-sm);
  font-weight: var(--ds-font-semibold);
  color: var(--ds-text-primary);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .ds-search-renderer {
    background: var(--ds-dark-surface-primary);
    border-color: var(--ds-dark-border-primary);
  }
  
  .ds-header-title {
    color: var(--ds-dark-text-primary);
  }
  
  .ds-action-btn {
    background: var(--ds-dark-surface-secondary);
    border-color: var(--ds-dark-border-primary);
    color: var(--ds-dark-text-secondary);
  }
  
  .ds-action-btn:hover {
    background: var(--ds-dark-surface-hover);
    color: var(--ds-dark-text-primary);
  }
}
</style>