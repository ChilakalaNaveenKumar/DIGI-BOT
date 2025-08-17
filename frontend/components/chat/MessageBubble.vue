<template>
  <div class="message-bubble" :class="[`message--${message.role}`]">
    <UiAvatar 
      v-if="message.role === 'assistant'"
      icon="lucide:cpu"
      variant="primary"
      size="md"
    />
    <UiAvatar 
      v-else
      initials="NK"
      variant="secondary"
      size="md"
    />
    
    <div class="message-content">
      <div class="message-header">
        <span class="message-author">
          {{ message.role === 'assistant' ? 'Claude' : 'You' }}
        </span>
        <span class="message-time">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>
      
      <div class="message-text">
        <UiLoadingDots v-if="message.isLoading" size="sm" />
        <div v-else>
          <!-- Reasoning section -->
          <div v-if="message.reasoning" class="reasoning-section">
            <div class="reasoning-header">
              <UiIcon name="lucide:cpu" :size="14" />
              <span>Thinking...</span>
            </div>
            <div class="reasoning-content markdown-content" v-html="renderMarkdown(message.reasoning)" />
          </div>
          
          <!-- Tool calls section -->
          <div v-if="message.toolCalls && message.toolCalls.length > 0" class="tools-section">
            <div v-for="toolCall in message.toolCalls" :key="toolCall.id" class="tool-call">
              <div class="tool-header">
                <UiIcon name="lucide:cpu" :size="14" />
                <span class="tool-name">{{ toolCall.name }}</span>
                <UiBadge 
                  :variant="toolCall.status === 'completed' ? 'success' : toolCall.status === 'error' ? 'error' : 'warning'"
                  size="sm"
                >
                  {{ toolCall.status || 'running' }}
                </UiBadge>
              </div>
              <div v-if="toolCall.result" class="tool-result">
                <pre>{{ JSON.stringify(toolCall.result, null, 2) }}</pre>
              </div>
            </div>
          </div>
          
          <!-- Main content -->
          <div v-if="message.content" class="markdown-content" v-html="renderMarkdown(message.content)" />
          
          <!-- Error display -->
          <div v-if="message.error" class="error-message">
            <UiIcon name="lucide:alert-circle" :size="14" />
            <span>{{ message.error }}</span>
          </div>
        </div>
        
        <!-- Message Actions (for assistant messages) -->
        <div v-if="message.role === 'assistant' && message.content" class="message-actions">
          <UiButton variant="ghost" size="sm" class="action-btn" @click="copyMessage">
            <UiIcon name="lucide:copy" :size="12" />
            Copy
          </UiButton>
          <UiButton variant="ghost" size="sm" class="action-btn" @click="regenerateMessage">
            <UiIcon name="lucide:refresh-cw" :size="12" />
            Regenerate
          </UiButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import markdownItTaskLists from 'markdown-it-task-lists'
import markdownItKatex from 'markdown-it-katex'
import markdownItContainer from 'markdown-it-container'
// Note: Emoji plugin temporarily disabled due to ESM import issues
// import markdownItEmoji from 'markdown-it-emoji'
import markdownItFootnote from 'markdown-it-footnote'
import markdownItMark from 'markdown-it-mark'
import markdownItIns from 'markdown-it-ins'
import markdownItSub from 'markdown-it-sub'
import markdownItSup from 'markdown-it-sup'
import markdownItDeflist from 'markdown-it-deflist'
import markdownItAbbr from 'markdown-it-abbr'

interface Message {
  id?: number
  content: string
  role: 'user' | 'assistant'
  timestamp?: Date
  isLoading?: boolean
  reasoning?: string
  toolCalls?: Array<{
    id: string
    name: string
    status?: 'running' | 'completed' | 'error'
    result?: unknown
  }>
  error?: string
}

interface Props {
  message: Message
}

const props = defineProps<Props>()

// Configure markdown-it with syntax highlighting
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch {
        // Ignore highlighting errors
      }
    }
    return '' // use external default escaping
  }
})

// Enable all markdown extensions
md.use(markdownItTaskLists, {
  enabled: true,
  label: true,        // Enable labels
  labelAfter: true    // Put label after checkbox
})
md.use(markdownItKatex)
// md.use(markdownItEmoji) // temporarily disabled
md.use(markdownItFootnote)
md.use(markdownItMark)
md.use(markdownItIns)
md.use(markdownItSub)
md.use(markdownItSup)
md.use(markdownItDeflist)
md.use(markdownItAbbr)

// Custom containers (simplified for MessageBubble)
md.use(markdownItContainer, 'info')
md.use(markdownItContainer, 'warning')
md.use(markdownItContainer, 'tip')
md.use(markdownItContainer, 'danger')

const renderMarkdown = (content: string) => {
  if (!content) return ''
  return md.render(content)
}

const formatTime = (timestamp?: Date) => {
  if (!timestamp) return ''
  return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    console.log('Message copied to clipboard')
  } catch (err) {
    console.error('Failed to copy message:', err)
  }
}

const regenerateMessage = () => {
  console.log('Regenerate message:', props.message.id)
  // Could emit an event to parent component
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 12px;
  max-width: 100%;
  margin-bottom: 16px;
}

/* Avatar styles handled by Avatar component */

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.message-author {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

.message-text :deep(code) {
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(em) {
  font-style: italic;
}

/* Enhanced sections styling */
.reasoning-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.reasoning-content {
  font-size: 13px;
  color: var(--text-secondary);
  font-style: italic;
}

.tools-section {
  margin-bottom: 12px;
}

.tool-call {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.tool-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.tool-result {
  background: var(--bg-primary);
  border-radius: 4px;
  padding: 8px;
  overflow-x: auto;
}

.tool-result pre {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
  color: var(--text-secondary);
  margin: 0;
  white-space: pre-wrap;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 8px;
}

.message-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message-bubble:hover .message-actions {
  opacity: 1;
}

.action-btn {
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
  color: var(--text-secondary);
}

.action-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

/* Loading dots styles handled by LoadingDots component */

/* 🎨 COMPREHENSIVE MARKDOWN STYLING */
.markdown-content {
  max-width: 100%;
  overflow-wrap: break-word;
}

/* Headers */
.markdown-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 24px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--border-primary);
}

.markdown-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 20px 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-primary);
}

.markdown-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 16px 0 8px 0;
}

.markdown-content :deep(h4), 
.markdown-content :deep(h5), 
.markdown-content :deep(h6) {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 12px 0 6px 0;
}

/* Paragraphs */
.markdown-content :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

/* Links */
.markdown-content :deep(a) {
  color: var(--accent-primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.2s ease;
}

.markdown-content :deep(a:hover) {
  border-bottom-color: var(--accent-primary);
}

/* Text formatting */
.markdown-content :deep(strong) {
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(del) {
  text-decoration: line-through;
  opacity: 0.7;
}

/* Inline code */
.markdown-content :deep(code) {
  background: var(--bg-tertiary);
  color: var(--accent-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  border: 1px solid var(--border-primary);
}

/* Code blocks */
.markdown-content :deep(pre) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.markdown-content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-primary);
}

/* Lists */
.markdown-content :deep(ul), 
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
  line-height: 1.5;
}

.markdown-content :deep(ul li) {
  list-style: disc;
}

.markdown-content :deep(ol li) {
  list-style: decimal;
}

/* Nested lists */
.markdown-content :deep(ul ul), 
.markdown-content :deep(ol ol), 
.markdown-content :deep(ul ol), 
.markdown-content :deep(ol ul) {
  margin: 4px 0;
}

/* Blockquotes */
.markdown-content :deep(blockquote) {
  background: var(--bg-secondary);
  border-left: 4px solid var(--accent-primary);
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 6px 6px 0;
}

.markdown-content :deep(blockquote p) {
  margin: 0;
  color: var(--text-secondary);
  font-style: italic;
}

/* Tables */
.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-primary);
}

.markdown-content :deep(th), 
.markdown-content :deep(td) {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-primary);
}

.markdown-content :deep(th) {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-content :deep(tr:last-child td) {
  border-bottom: none;
}

.markdown-content :deep(tr:nth-child(even)) {
  background: var(--bg-secondary);
}

/* Horizontal rules */
.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-primary);
  margin: 24px 0;
}

/* Images */
.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 8px 0;
  border: 1px solid var(--border-primary);
}

/* Task Lists - Enhanced with proper styling */
.markdown-content :deep(.task-list-item) {
  list-style: none;
  margin: 4px 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding-left: 0;
}

.markdown-content :deep(.task-list-item-checkbox) {
  margin: 0;
  margin-top: 2px;
  width: 16px;
  height: 16px;
  accent-color: var(--accent-primary);
  cursor: pointer;
  flex-shrink: 0;
}

.markdown-content :deep(.task-list-item-checkbox:checked + .task-list-item-label) {
  text-decoration: line-through;
  opacity: 0.7;
  color: var(--text-secondary);
}

.markdown-content :deep(.task-list-item-label) {
  flex: 1;
  line-height: 1.5;
  cursor: pointer;
}

/* Task list container */
.markdown-content :deep(ul.contains-task-list) {
  padding-left: 0;
}

.markdown-content :deep(ul.contains-task-list li) {
  list-style: none;
}

/* Legacy support for basic checkbox syntax */
.markdown-content :deep(input[type="checkbox"]) {
  margin-right: 8px;
  accent-color: var(--accent-primary);
}

/* Syntax highlighting styles - Theme adaptive using data-theme */
.markdown-content :deep(.hljs) {
  background: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border-radius: 8px;
}

/* Light theme syntax colors */
:root .markdown-content :deep(.hljs-keyword) { 
  color: #d73a49; 
  font-weight: 600;
}

:root .markdown-content :deep(.hljs-string) { 
  color: #22863a; 
}

:root .markdown-content :deep(.hljs-comment) { 
  color: #6a737d; 
  font-style: italic;
}

:root .markdown-content :deep(.hljs-function) { 
  color: #6f42c1; 
  font-weight: 600;
}

:root .markdown-content :deep(.hljs-number) { 
  color: #005cc5; 
}

:root .markdown-content :deep(.hljs-variable) { 
  color: #e36209; 
}

:root .markdown-content :deep(.hljs-title) { 
  color: #6f42c1; 
  font-weight: 600;
}

:root .markdown-content :deep(.hljs-attr) { 
  color: #005cc5; 
}

:root .markdown-content :deep(.hljs-built_in) { 
  color: #d73a49; 
}

:root .markdown-content :deep(.hljs-literal) { 
  color: #005cc5; 
}

:root .markdown-content :deep(.hljs-meta) { 
  color: #6a737d; 
}

:root .markdown-content :deep(.hljs-tag) { 
  color: #22863a; 
}

:root .markdown-content :deep(.hljs-type) { 
  color: #6f42c1; 
}

:root .markdown-content :deep(.hljs-operator) { 
  color: #e36209; 
}

:root .markdown-content :deep(.hljs-symbol) { 
  color: #005cc5; 
}

/* Dark theme syntax colors */
[data-theme="dark"] .markdown-content :deep(.hljs-keyword) { 
  color: #ff6b6b; 
  font-weight: 600;
}

[data-theme="dark"] .markdown-content :deep(.hljs-string) { 
  color: #51cf66; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-comment) { 
  color: #868e96; 
  font-style: italic;
}

[data-theme="dark"] .markdown-content :deep(.hljs-function) { 
  color: #74c0fc; 
  font-weight: 600;
}

[data-theme="dark"] .markdown-content :deep(.hljs-number) { 
  color: #ffd43b; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-variable) { 
  color: #ff8cc8; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-title) { 
  color: #74c0fc; 
  font-weight: 600;
}

[data-theme="dark"] .markdown-content :deep(.hljs-attr) { 
  color: #ffd43b; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-built_in) { 
  color: #ff6b6b; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-literal) { 
  color: #ffd43b; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-meta) { 
  color: #868e96; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-tag) { 
  color: #51cf66; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-type) { 
  color: #74c0fc; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-operator) { 
  color: #ff8cc8; 
}

[data-theme="dark"] .markdown-content :deep(.hljs-symbol) { 
  color: #ffd43b; 
}

/* 🎨 ENHANCED MARKDOWN FEATURES */
.markdown-content :deep(.katex) { font-size: 1.1em; }
.markdown-content :deep(.katex-display) { margin: 16px 0; text-align: center; }
.markdown-content :deep(.emoji) { height: 1.2em; width: 1.2em; vertical-align: -0.1em; }
.markdown-content :deep(mark) { background: light-dark(#fef08a, rgba(254, 240, 138, 0.3)); padding: 2px 4px; border-radius: 3px; }
.markdown-content :deep(ins) { background: light-dark(#dcfce7, rgba(220, 252, 231, 0.2)); padding: 1px 3px; border-radius: 3px; text-decoration: none; }
.markdown-content :deep(sub), .markdown-content :deep(sup) { font-size: 0.8em; }
.markdown-content :deep(dt) { font-weight: 600; margin-top: 12px; margin-bottom: 4px; }
.markdown-content :deep(dd) { margin-left: 20px; margin-bottom: 6px; }
.markdown-content :deep(.footnote-ref) { color: var(--accent-primary); text-decoration: none; font-weight: 600; }
.markdown-content :deep(.footnotes) { margin-top: 24px; padding-top: 12px; border-top: 1px solid var(--border-primary); font-size: 13px; }
.markdown-content :deep(abbr) { border-bottom: 1px dotted var(--text-secondary); cursor: help; }

/* Container support */
.markdown-content :deep(.container) { margin: 12px 0; padding: 12px; border-radius: 6px; border-left: 3px solid var(--accent-primary); background: var(--bg-secondary); }
</style>
