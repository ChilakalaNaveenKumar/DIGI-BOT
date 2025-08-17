<template>
  <div class="ds-svg-renderer">
    <div class="ds-svg-header">
      <div class="ds-svg-icon">🎨</div>
      <div class="ds-svg-title">SVG Diagram</div>
      <div v-if="isStreaming" class="ds-streaming-indicator">⏳ Generating...</div>
    </div>
    <div class="ds-svg-content">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="ds-svg-container" v-html="sanitizedSvg" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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

// Sanitize and process SVG content
const sanitizedSvg = computed(() => {
  let svgContent = props.content
  
  // Basic SVG validation and sanitization
  if (!svgContent.includes('<svg')) {
    return '<p>Invalid SVG content</p>'
  }
  
  // Ensure SVG has proper viewBox for responsiveness
  if (!svgContent.includes('viewBox') && svgContent.includes('<svg')) {
    svgContent = svgContent.replace(
      '<svg',
      '<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid meet"'
    )
  }
  
  // Add responsive styling
  if (!svgContent.includes('width=') || !svgContent.includes('height=')) {
    svgContent = svgContent.replace(
      '<svg',
      '<svg width="100%" height="auto"'
    )
  }
  
  // Add CSS classes for styling
  svgContent = svgContent.replace(
    '<svg',
    '<svg class="ds-responsive-svg"'
  )
  
  return svgContent
})
</script>

<style scoped>
.ds-svg-renderer {
  margin: 1rem 0;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.ds-svg-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-weight: 600;
}

.ds-svg-icon {
  font-size: 1.2em;
}

.ds-svg-title {
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ds-streaming-indicator {
  margin-left: auto;
  font-size: 0.8em;
  opacity: 0.9;
  animation: pulse 2s infinite;
}

.ds-svg-content {
  padding: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.ds-svg-container {
  width: 100%;
  max-width: 600px;
  text-align: center;
}

.ds-svg-container :deep(.ds-responsive-svg) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Styling for common SVG elements */
.ds-svg-container :deep(circle) {
  stroke-width: 2;
}

.ds-svg-container :deep(text) {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 14px;
  font-weight: 500;
}

.ds-svg-container :deep(rect) {
  stroke-width: 1;
}

.ds-svg-container :deep(path) {
  stroke-width: 2;
}

@keyframes pulse {
  0%, 100% { opacity: 0.9; }
  50% { opacity: 0.6; }
}

/* Loading state */
.ds-svg-renderer.streaming {
  border-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
}
</style>
