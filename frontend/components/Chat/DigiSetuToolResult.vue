<template>
  <div class="ds-tool-result">
    <div class="ds-tool-header">
      <Wrench class="w-4 h-4" />
      <span class="ds-tool-title">Tool Result</span>
      <span v-if="metadata?.confidence" class="ds-confidence">
        {{ Math.round(metadata.confidence * 100) }}% confidence
      </span>
    </div>
    <div class="ds-tool-content">
      <pre v-if="isJsonLike" class="ds-json-content">{{ formattedContent }}</pre>
      <div v-else class="ds-text-content" v-html="processedContent"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Wrench } from 'lucide-vue-next'

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

const isJsonLike = computed(() => {
  const trimmed = props.content.trim()
  return trimmed.startsWith('{') || trimmed.startsWith('[')
})

const formattedContent = computed(() => {
  if (isJsonLike.value) {
    try {
      const parsed = JSON.parse(props.content)
      return JSON.stringify(parsed, null, 2)
    } catch {
      return props.content
    }
  }
  return props.content
})

const processedContent = computed(() => {
  let processed = String(props.content)
  
  // Convert URLs to clickable links
  const urlRegex = /(https?:\/\/[^\s]+)/g
  processed = processed.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="ds-link">$1</a>')
  
  // Convert line breaks to <br> tags
  processed = processed.replace(/\n/g, '<br>')
  
  return processed
})
</script>

<style scoped>
.ds-tool-result {
  border: 1px solid var(--ds-border-secondary);
  border-radius: var(--ds-radius-md);
  background: var(--ds-surface-secondary);
  overflow: hidden;
  margin: var(--ds-space-2) 0;
}

.ds-tool-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-tertiary);
  border-bottom: 1px solid var(--ds-border-secondary);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
}

.ds-tool-title {
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

.ds-tool-content {
  padding: var(--ds-space-3);
}

.ds-json-content {
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-primary);
  background: var(--ds-surface-primary);
  padding: var(--ds-space-3);
  border-radius: var(--ds-radius-sm);
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.ds-text-content {
  color: var(--ds-text-primary);
  line-height: var(--ds-leading-relaxed);
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.ds-text-content :deep(.ds-link) {
  color: var(--ds-primary);
  text-decoration: underline;
  text-decoration-color: color-mix(in srgb, var(--ds-primary) 50%, transparent);
  transition: all var(--ds-transition-fast);
}

.ds-text-content :deep(.ds-link:hover) {
  text-decoration-color: var(--ds-primary);
  background: color-mix(in srgb, var(--ds-primary) 5%, transparent);
  padding: 2px 4px;
  border-radius: var(--ds-radius-sm);
  margin: -2px -4px;
}
</style>
