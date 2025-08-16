<template>
  <div class="markdown-renderer">
    <div v-html="renderedContent" class="prose prose-gray dark:prose-invert max-w-none"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: {
    type: String,
    required: true
  }
})

// Configure marked for better rendering
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: false,
  mangle: false,
  pedantic: false,
  smartypants: true
})

const renderedContent = computed(() => {
  if (!props.content) return ''
  
  try {
    // Ensure proper line breaks and spacing
    let content = props.content
    
    // Add extra line breaks for better paragraph separation
    content = content.replace(/\n\n/g, '\n\n\n')
    
    // Handle numbered lists and bullet points better
    content = content.replace(/^(\d+\.\s)/gm, '\n$1')
    content = content.replace(/^([•\-\*]\s)/gm, '\n$1')
    
    return marked(content)
  } catch (error) {
    console.error('Markdown rendering error:', error)
    return `<pre>${props.content}</pre>`
  }
})
</script>

<style scoped>
.markdown-renderer {
  color: #111827;
}

.dark .markdown-renderer {
  color: #f3f4f6;
}

.prose {
  font-size: 0.875rem;
  line-height: 1.25rem;
  max-width: none;
}

@media (min-width: 1024px) {
  .prose {
    font-size: 1rem;
    line-height: 1.5rem;
  }
}

.prose :deep(pre) {
  background-color: #f3f4f6;
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-x: auto;
}

.dark .prose :deep(pre) {
  background-color: #1f2937;
}

.prose :deep(code) {
  background-color: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.dark .prose :deep(code) {
  background-color: #1f2937;
}

.prose :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  background-color: #eff6ff;
  padding-left: 1rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  margin: 1rem 0;
}

.dark .prose :deep(blockquote) {
  background-color: rgba(30, 58, 138, 0.2);
}

.prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e5e7eb;
}

.dark .prose :deep(table) {
  border-color: #374151;
}

.prose :deep(th) {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
}

.dark .prose :deep(th) {
  background-color: #1f2937;
  border-color: #374151;
}

.prose :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
}

.dark .prose :deep(td) {
  border-color: #374151;
}
</style>