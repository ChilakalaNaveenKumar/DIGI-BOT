<template>
  <div class="flex items-center justify-center" :style="{ width: size + 'px', height: size + 'px' }">
    <!-- OpenAI Icon -->
    <Icon 
      v-if="provider === 'openai'" 
      name="simple-icons:openai" 
      :size="iconSize"
      class="text-black dark:text-white"
    />
    
    <!-- Anthropic/Claude Icon -->
    <Icon 
      v-else-if="provider === 'anthropic'" 
      name="simple-icons:anthropic" 
      :size="iconSize"
      class="text-orange-500"
    />
    
    <!-- Grok/xAI Icon -->
    <Icon 
      v-else-if="provider === 'grok'" 
      name="simple-icons:x" 
      :size="iconSize"
      class="text-black dark:text-white"
    />
    
    <!-- Fallback AI Icon -->
    <Icon 
      v-else 
      name="lucide:bot" 
      :size="iconSize"
      class="text-blue-500"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  provider: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    default: 24
  }
})

const iconSize = computed(() => Math.max(16, props.size - 4))
</script>

