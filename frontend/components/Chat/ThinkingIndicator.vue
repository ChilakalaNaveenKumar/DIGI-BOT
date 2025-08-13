<template>
  <div class="flex items-start space-x-4">
    <div class="w-10 h-10 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-2xl flex items-center justify-center shadow-lg">
      <ProviderIcon :provider="provider" :size="24" />
    </div>
    
    <div class="flex-1 max-w-2xl">
      <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 border border-blue-200 dark:border-gray-600 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center space-x-3 mb-4">
          <div class="flex space-x-1">
            <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce"></div>
            <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.15s"></div>
            <div class="w-1.5 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.3s"></div>
          </div>
          <span class="text-sm font-medium text-blue-700 dark:text-blue-300">{{ getProviderName(provider) }} is thinking...</span>
        </div>
        
        <p class="text-sm text-blue-600 dark:text-blue-400 italic leading-relaxed">{{ stage }}</p>
        
        <!-- Enhanced Progress bar -->
        <div class="mt-4 w-full bg-blue-100 dark:bg-gray-600 rounded-full h-1.5 overflow-hidden">
          <div class="bg-gradient-to-r from-blue-400 to-purple-500 h-1.5 rounded-full animate-pulse-slow" 
               :style="{ width: progressWidth + '%' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ProviderIcon from '../UI/ProviderIcon.vue'

defineProps({
  provider: String,
  stage: String
})

const progressWidth = ref(0)
let progressInterval = null

const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-5',
    'anthropic': 'Claude 4',
    'grok': 'Grok 4'
  }
  return names[provider] || 'AI'
}

onMounted(() => {
  // Animate progress bar
  progressInterval = setInterval(() => {
    if (progressWidth.value < 90) {
      progressWidth.value += Math.random() * 10
    } else {
      progressWidth.value = Math.max(20, progressWidth.value - Math.random() * 30)
    }
  }, 800)
})

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})
</script>