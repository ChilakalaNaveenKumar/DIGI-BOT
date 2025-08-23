<template>
  <div class="typewriter-container">
    <span v-html="displayedContent" class="typewriter-text"></span>
    <span v-if="isTyping" class="typewriter-cursor">|</span>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useMarkdown } from '~/composables/useMarkdown'

interface Props {
  content: string
  isStreaming?: boolean
  speed?: number // Characters per second
  immediate?: boolean // Show immediately without typing effect
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: false,
  speed: 50, // 50 characters per second
  immediate: false
})

const emit = defineEmits<{
  'typing-complete': []
}>()

const { render } = useMarkdown()

const displayedContent = ref('')
const isTyping = ref(false)
const currentIndex = ref(0)
let typingInterval: NodeJS.Timeout | null = null

const startTyping = (targetContent: string) => {
  if (props.immediate) {
    displayedContent.value = render(targetContent)
    emit('typing-complete')
    return
  }

  isTyping.value = true
  
  // Don't reset if we're continuing from existing content
  const currentPlainText = displayedContent.value.replace(/<[^>]*>/g, '')
  if (currentIndex.value === 0 || currentIndex.value > targetContent.length) {
    currentIndex.value = currentPlainText.length
  }
  
  // Clear any existing interval
  if (typingInterval) {
    clearInterval(typingInterval)
  }
  
  const plainText = targetContent
  const intervalMs = 1000 / props.speed
  
  typingInterval = setInterval(() => {
    if (currentIndex.value < plainText.length) {
      const currentText = plainText.slice(0, currentIndex.value + 1)
      displayedContent.value = render(currentText)
      currentIndex.value++
    } else {
      // Typing complete
      isTyping.value = false
      if (typingInterval) {
        clearInterval(typingInterval)
        typingInterval = null
      }
      emit('typing-complete')
    }
  }, intervalMs)
}

// Watch for content changes
watch(() => props.content, (newContent, oldContent) => {
  if (newContent !== oldContent) {
    startTyping(newContent)
  }
}, { immediate: true })

// Watch for streaming state changes
watch(() => props.isStreaming, (streaming) => {
  if (!streaming && typingInterval) {
    // If streaming stops, complete the typing immediately
    clearInterval(typingInterval)
    typingInterval = null
    displayedContent.value = render(props.content)
    isTyping.value = false
    emit('typing-complete')
  }
})

onMounted(() => {
  if (props.content) {
    startTyping(props.content)
  }
})

onUnmounted(() => {
  if (typingInterval) {
    clearInterval(typingInterval)
  }
})
</script>

<style scoped>
.typewriter-container {
  position: relative;
  line-height: 1.6;
}

.typewriter-text {
  /* Inherit markdown styles */
}

.typewriter-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  font-weight: bold;
  color: #3b82f6;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>
