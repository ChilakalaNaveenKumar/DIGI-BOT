<template>
  <div class="streaming-demo">
    <div class="demo-header">
      <h2>🚀 Streaming Markdown Demo</h2>
      <div class="demo-controls">
        <UiButton 
          @click="startDemo" 
          :disabled="isStreaming"
          size="sm"
          variant="primary"
        >
          {{ isStreaming ? 'Streaming...' : 'Start Demo' }}
        </UiButton>
        <UiButton 
          @click="resetDemo" 
          size="sm"
          variant="ghost"
        >
          Reset
        </UiButton>
        <UiButton 
          @click="toggleMode" 
          size="sm"
          variant="outline"
        >
          Mode: {{ currentMode }}
        </UiButton>
      </div>
    </div>

    <div class="demo-content">
      <UiStreamingMarkdown
        :content="streamedContent"
        :is-streaming="isStreaming"
        :show-cursor="true"
        :show-streaming-indicator="isStreaming"
        :mode="currentMode"
        :auto-scroll="false"
        :debug="true"
        @content-updated="onContentUpdated"
        @streaming-complete="onStreamingComplete"
        @block-completed="onBlockCompleted"
      />
    </div>

    <div class="demo-stats">
      <div class="stat">
        <span class="stat-label">Blocks completed:</span>
        <span class="stat-value">{{ completedBlocks }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Characters:</span>
        <span class="stat-value">{{ streamedContent.length }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Speed:</span>
        <span class="stat-value">{{ streamingSpeed }}ms/char</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const streamedContent = ref('')
const isStreaming = ref(false)
const currentMode = ref<'streaming' | 'static'>('streaming')
const completedBlocks = ref(0)
const streamingSpeed = ref(50)

const demoContent = `# 🎯 Streaming Markdown Demo

This demonstrates **real-time streaming** with intelligent block parsing!

## 🚀 Features

- ✅ **Smart block detection** - Complete blocks render immediately
- ✅ **Partial block handling** - Incomplete syntax doesn't break
- ✅ **Typing animation** - Smooth cursor and transitions
- ✅ **Performance optimized** - Only re-renders new content

## 📊 Code Example

\`\`\`javascript
// Streaming markdown parser
function parseStreamingContent(content) {
  const blocks = splitIntoBlocks(content)
  const completeBlocks = []
  let incompleteBlock = null
  
  for (const block of blocks) {
    if (isCompleteBlock(block)) {
      completeBlocks.push({
        rendered: md.render(block),
        type: detectBlockType(block)
      })
    } else {
      incompleteBlock = {
        rendered: renderPartialBlock(block),
        type: detectBlockType(block)
      }
    }
  }
  
  return { completeBlocks, incompleteBlock }
}
\`\`\`

## 🎨 Advanced Features

### Math Support
Inline math: $E = mc^2$ and block math:

$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

### Custom Containers

::: info
💡 This is an info container with **formatted text** and \`code\`!
:::

::: warning
⚠️ This is a warning with important information
:::

::: tip
✨ Pro tip: Streaming works with all markdown features!
:::

### Task Lists

- [x] Implement streaming parser
- [x] Add block detection
- [x] Create smooth animations  
- [ ] Add more advanced features
- [ ] Optimize performance further

### Enhanced Formatting

Here's some ==highlighted text== and ++inserted content++.

Chemical formulas: H~2~O, CO~2~

Mathematical expressions: x^2^ + y^2^ = z^2^

### Tables

| Feature | Status | Priority |
|---------|--------|----------|
| **Streaming** | ✅ Complete | High |
| **Animations** | ✅ Complete | High |
| **Performance** | 🚧 Optimizing | Medium |

## 🔥 Performance Benefits

1. **Incremental rendering** - Only new content re-renders
2. **Block caching** - Stable blocks cached permanently  
3. **Smart parsing** - Avoids breaking incomplete syntax
4. **Smooth UX** - No jarring re-layouts during streaming

Perfect for **AI chat interfaces** where content streams in real-time! 🤖✨`

const startDemo = async () => {
  if (isStreaming.value) return
  
  resetDemo()
  isStreaming.value = true
  completedBlocks.value = 0
  
  const content = demoContent
  let currentIndex = 0
  
  const streamInterval = setInterval(() => {
    if (currentIndex >= content.length) {
      clearInterval(streamInterval)
      isStreaming.value = false
      return
    }
    
    // Add characters in chunks for more realistic streaming
    const chunkSize = Math.random() > 0.7 ? 1 : Math.floor(Math.random() * 5) + 1
    const nextIndex = Math.min(currentIndex + chunkSize, content.length)
    
    streamedContent.value = content.substring(0, nextIndex)
    currentIndex = nextIndex
    
  }, streamingSpeed.value)
}

const resetDemo = () => {
  streamedContent.value = ''
  isStreaming.value = false
  completedBlocks.value = 0
}

const toggleMode = () => {
  currentMode.value = currentMode.value === 'streaming' ? 'static' : 'streaming'
}

const onContentUpdated = () => {
  console.log('Content updated, length:', streamedContent.value.length)
}

const onStreamingComplete = () => {
  console.log('Streaming completed!')
}

const onBlockCompleted = (block: any) => {
  completedBlocks.value++
  console.log('Block completed:', block.type)
}
</script>

<style scoped>
.streaming-demo {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-primary);
}

.demo-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
}

.demo-controls {
  display: flex;
  gap: 8px;
}

.demo-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  min-height: 400px;
}

.demo-stats {
  display: flex;
  gap: 24px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  font-size: 14px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
}

.stat-value {
  color: var(--text-primary);
  font-weight: 600;
  font-family: monospace;
}

@media (max-width: 768px) {
  .demo-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .demo-controls {
    justify-content: center;
  }
  
  .demo-stats {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
