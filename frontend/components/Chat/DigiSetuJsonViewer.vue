<template>
  <div class="ds-json-viewer">
    <div class="ds-json-header">
      <span class="ds-json-title">JSON</span>
      <button @click="toggleCollapse" class="ds-json-toggle">
        <ChevronDown :class="{ 'rotate-180': !isCollapsed }" class="w-4 h-4" />
      </button>
    </div>
    <div v-show="!isCollapsed" class="ds-json-content">
      <pre class="ds-json-pre">{{ formattedJson }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: [Object, Array, String],
    required: true
  },
  collapsed: {
    type: Boolean,
    default: false
  }
})

const isCollapsed = ref(props.collapsed)

const formattedJson = computed(() => {
  try {
    if (typeof props.data === 'string') {
      // Try to parse if it's a JSON string
      const parsed = JSON.parse(props.data)
      return JSON.stringify(parsed, null, 2)
    }
    return JSON.stringify(props.data, null, 2)
  } catch (error) {
    return props.data
  }
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.ds-json-viewer {
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
  background: var(--ds-surface-secondary);
}

.ds-json-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-3);
  background: var(--ds-surface-tertiary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-json-title {
  font-weight: var(--ds-font-medium);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.ds-json-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-1);
  border: none;
  background: none;
  color: var(--ds-text-secondary);
  cursor: pointer;
  border-radius: var(--ds-radius-sm);
  transition: all var(--ds-transition-fast);
}

.ds-json-toggle:hover {
  background: var(--ds-surface-primary);
  color: var(--ds-text-primary);
}

.ds-json-content {
  max-height: 400px;
  overflow-y: auto;
}

.ds-json-pre {
  margin: 0;
  padding: var(--ds-space-4);
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  line-height: 1.5;
  color: var(--ds-text-primary);
  background: transparent;
  overflow-x: auto;
  white-space: pre;
}

/* JSON syntax highlighting */
.ds-json-pre :deep(.hljs-attr) {
  color: var(--ds-primary);
}

.ds-json-pre :deep(.hljs-string) {
  color: var(--ds-success);
}

.ds-json-pre :deep(.hljs-number) {
  color: var(--ds-warning);
}

.ds-json-pre :deep(.hljs-literal) {
  color: var(--ds-info);
}

.ds-json-pre :deep(.hljs-punctuation) {
  color: var(--ds-text-secondary);
}

/* Scrollbar styling */
.ds-json-content::-webkit-scrollbar {
  width: 6px;
}

.ds-json-content::-webkit-scrollbar-track {
  background: var(--ds-surface-primary);
}

.ds-json-content::-webkit-scrollbar-thumb {
  background: var(--ds-border-primary);
  border-radius: 3px;
}

.ds-json-content::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted);
}
</style>
