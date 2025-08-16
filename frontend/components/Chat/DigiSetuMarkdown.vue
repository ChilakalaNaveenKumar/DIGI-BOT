<template>
  <div class="ds-markdown" v-html="renderedMarkdown"></div>
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

// Configure marked with highlight.js
marked.setOptions({
  highlight: function(code, lang) {
    if (typeof window !== 'undefined' && window.hljs) {
      if (lang && window.hljs.getLanguage(lang)) {
        try {
          return window.hljs.highlight(code, { language: lang }).value
        } catch (err) {
          console.warn('Highlight.js error:', err)
        }
      }
      return window.hljs.highlightAuto(code).value
    }
    return code
  },
  breaks: true,
  gfm: true
})

const renderedMarkdown = computed(() => {
  try {
    return marked(props.content)
  } catch (error) {
    console.error('Markdown parsing error:', error)
    return `<pre>${props.content}</pre>`
  }
})
</script>

<style scoped>
.ds-markdown {
  line-height: 1.6;
  color: var(--ds-text-primary);
}

.ds-markdown :deep(h1),
.ds-markdown :deep(h2),
.ds-markdown :deep(h3),
.ds-markdown :deep(h4),
.ds-markdown :deep(h5),
.ds-markdown :deep(h6) {
  margin: 1.5em 0 0.5em 0;
  font-weight: 600;
  color: var(--ds-text-primary);
}

.ds-markdown :deep(h1) { font-size: 1.875rem; }
.ds-markdown :deep(h2) { font-size: 1.5rem; }
.ds-markdown :deep(h3) { font-size: 1.25rem; }
.ds-markdown :deep(h4) { font-size: 1.125rem; }

.ds-markdown :deep(p) {
  margin: 0.75em 0;
}

.ds-markdown :deep(strong) {
  font-weight: 600;
  color: var(--ds-text-primary);
}

.ds-markdown :deep(em) {
  font-style: italic;
}

.ds-markdown :deep(code) {
  background: var(--ds-surface-secondary);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: var(--ds-font-mono);
  font-size: 0.875em;
}

.ds-markdown :deep(pre) {
  background: var(--ds-surface-secondary);
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.ds-markdown :deep(pre code) {
  background: none;
  padding: 0;
}

.ds-markdown :deep(ul),
.ds-markdown :deep(ol) {
  margin: 0.75em 0;
  padding-left: 1.5rem;
}

.ds-markdown :deep(li) {
  margin: 0.25em 0;
}

.ds-markdown :deep(blockquote) {
  border-left: 4px solid var(--ds-primary);
  padding-left: 1rem;
  margin: 1rem 0;
  color: var(--ds-text-secondary);
  font-style: italic;
}

.ds-markdown :deep(a) {
  color: var(--ds-primary);
  text-decoration: underline;
}

.ds-markdown :deep(a:hover) {
  color: var(--ds-primary-dark);
}

.ds-markdown :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}

.ds-markdown :deep(th),
.ds-markdown :deep(td) {
  border: 1px solid var(--ds-border-primary);
  padding: 0.5rem;
  text-align: left;
}

.ds-markdown :deep(th) {
  background: var(--ds-surface-secondary);
  font-weight: 600;
}
</style>
