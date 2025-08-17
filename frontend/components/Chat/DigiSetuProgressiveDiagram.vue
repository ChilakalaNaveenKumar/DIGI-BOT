<template>
  <div class="ds-progressive-diagram-container">
    <!-- SIMPLIFIED: User said "no need of customizations as its just a text" -->
    <!-- Removed all controls and complex features -->
    
    <!-- Simple Text Content -->
    <div class="ds-simple-text-content">
      <pre class="ds-plain-text">{{ content }}</pre>
    </div>
  </div>
</template>

<script setup>
// Simple props for basic diagram display
const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.ds-progressive-diagram-container {
  width: 100%;
  padding: var(--ds-space-4);
}

.ds-simple-text-content {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-subtle);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-4);
}

.ds-plain-text {
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  line-height: 1.6;
  color: var(--ds-text-primary);
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>