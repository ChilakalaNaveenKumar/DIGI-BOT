<template>
  <div class="ds-text-content" v-html="processedContent"></div>
</template>

<script setup>
import { computed } from 'vue'

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
  
  return processed
})
</script>

<style scoped>
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

.ds-text-content :deep(.ds-link:focus-visible) {
  outline: 2px solid var(--ds-primary);
  outline-offset: 2px;
}
</style>
