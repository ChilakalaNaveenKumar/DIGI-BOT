<template>
  <div class="ds-search-results">
    <div class="ds-search-header">
      <Search class="w-4 h-4" />
      <span class="ds-search-title">Live Search Results</span>
      <span v-if="metadata?.confidence" class="ds-confidence">
        {{ Math.round(metadata.confidence * 100) }}% confidence
      </span>
    </div>
    <div class="ds-search-content">
      <div class="ds-search-text" v-html="processedContent"></div>
      <div v-if="metadata?.sources" class="ds-sources">
        <div class="ds-sources-title">Sources:</div>
        <div v-for="(source, index) in metadata.sources" :key="index" class="ds-source">
          <a :href="source.url" target="_blank" rel="noopener noreferrer" class="ds-source-link">
            {{ source.title || source.url }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Search } from 'lucide-vue-next'

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

const processedContent = computed(() => {
  let processed = String(props.content)
  
  // Convert URLs to clickable links
  const urlRegex = /(https?:\/\/[^\s]+)/g
  processed = processed.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="ds-link">$1</a>')
  
  // Convert line breaks to <br> tags
  processed = processed.replace(/\n/g, '<br>')
  
  // Highlight search terms (if provided)
  if (props.metadata?.searchTerms) {
    for (const term of props.metadata.searchTerms) {
      const regex = new RegExp(`(${term})`, 'gi')
      processed = processed.replace(regex, '<mark class="ds-highlight">$1</mark>')
    }
  }
  
  return processed
})
</script>

<style scoped>
.ds-search-results {
  border: 1px solid var(--ds-border-secondary);
  border-radius: var(--ds-radius-md);
  background: var(--ds-surface-secondary);
  overflow: hidden;
  margin: var(--ds-space-2) 0;
}

.ds-search-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: color-mix(in srgb, var(--ds-primary) 10%, var(--ds-surface-tertiary));
  border-bottom: 1px solid var(--ds-border-secondary);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
}

.ds-search-title {
  font-weight: 500;
}

.ds-confidence {
  margin-left: auto;
  font-size: var(--ds-text-xs);
  color: var(--ds-text-tertiary);
  background: var(--ds-surface-primary);
  padding: var(--ds-space-1) var(--ds-space-2);
  border-radius: var(--ds-radius-sm);
}

.ds-search-content {
  padding: var(--ds-space-3);
}

.ds-search-text {
  color: var(--ds-text-primary);
  line-height: var(--ds-leading-relaxed);
  word-wrap: break-word;
  overflow-wrap: break-word;
  margin-bottom: var(--ds-space-3);
}

.ds-search-text :deep(.ds-link) {
  color: var(--ds-primary);
  text-decoration: underline;
  text-decoration-color: color-mix(in srgb, var(--ds-primary) 50%, transparent);
  transition: all var(--ds-transition-fast);
}

.ds-search-text :deep(.ds-link:hover) {
  text-decoration-color: var(--ds-primary);
  background: color-mix(in srgb, var(--ds-primary) 5%, transparent);
  padding: 2px 4px;
  border-radius: var(--ds-radius-sm);
  margin: -2px -4px;
}

.ds-search-text :deep(.ds-highlight) {
  background: color-mix(in srgb, var(--ds-warning) 30%, transparent);
  padding: 2px 4px;
  border-radius: var(--ds-radius-sm);
  font-weight: 500;
}

.ds-sources {
  border-top: 1px solid var(--ds-border-secondary);
  padding-top: var(--ds-space-3);
}

.ds-sources-title {
  font-size: var(--ds-text-sm);
  font-weight: 500;
  color: var(--ds-text-secondary);
  margin-bottom: var(--ds-space-2);
}

.ds-source {
  margin-bottom: var(--ds-space-1);
}

.ds-source-link {
  font-size: var(--ds-text-sm);
  color: var(--ds-primary);
  text-decoration: none;
  transition: all var(--ds-transition-fast);
}

.ds-source-link:hover {
  text-decoration: underline;
  color: color-mix(in srgb, var(--ds-primary) 80%, black);
}
</style>
