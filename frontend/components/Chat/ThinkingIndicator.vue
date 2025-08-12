<template>
  <div class="flex items-start space-x-4 animate-pulse">
    <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
      <span class="text-white text-lg animate-pulse">{{ getProviderEmoji(provider) }}</span>
    </div>
    
    <div class="flex-1 max-w-2xl">
      <div class="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center space-x-3 mb-4">
          <div class="flex space-x-1">
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
          <span class="text-sm font-medium text-blue-700">{{ getProviderName(provider) }} is thinking...</span>
        </div>
        
        <p class="text-sm text-blue-600 italic leading-relaxed">{{ stage }}</p>
        
        <!-- Progress bar -->
        <div class="mt-4 w-full bg-blue-100 rounded-full h-1.5">
          <div class="bg-gradient-to-r from-blue-400 to-purple-500 h-1.5 rounded-full animate-pulse" 
               style="width: 60%"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  provider: String,
  stage: String
})

const getProviderEmoji = (provider) => {
  const emojis = {
    'openai': '⚡',
    'anthropic': '🧠',
    'grok': '✨'
  }
  return emojis[provider] || '⚡'
}

const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-4',
    'anthropic': 'Claude',
    'grok': 'Grok'
  }
  return names[provider] || 'AI'
}
</script>