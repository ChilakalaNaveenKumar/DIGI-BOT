<template>
  <div class="relative">
    <!-- Custom styled dropdown with real icons -->
    <button
      @click="isOpen = !isOpen"
      class="appearance-none bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-xl px-4 py-2 pr-10 text-sm font-medium text-gray-700 dark:text-gray-200 hover:border-blue-300 dark:hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 shadow-sm hover:shadow-md flex items-center gap-2 min-w-[120px]"
    >
      <ProviderIcon :provider="modelValue" :size="18" />
      <span>{{ getProviderName(modelValue) }}</span>
      <ChevronDown class="w-4 h-4 ml-auto text-gray-400 dark:text-gray-500" />
    </button>
    
    <!-- Dropdown menu -->
    <div 
      v-if="isOpen"
      class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-lg z-50 overflow-hidden"
    >
      <button
        v-for="option in providers"
        :key="option.value"
        @click="selectProvider(option.value)"
        class="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <ProviderIcon :provider="option.value" :size="20" />
        <span class="font-medium">{{ option.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import ProviderIcon from './ProviderIcon.vue'

defineProps({
  modelValue: {
    type: String,
    default: 'openai'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)

const providers = [
  { value: 'openai', label: 'GPT-4' },
  { value: 'grok', label: 'Grok' },
  { value: 'anthropic', label: 'Claude' }
]

const getProviderName = (provider) => {
  const names = {
    'openai': 'GPT-4',
    'grok': 'Grok',
    'anthropic': 'Claude'
  }
  return names[provider] || 'GPT-4'
}

const selectProvider = (value) => {
  emit('update:modelValue', value)
  emit('change', value)
  isOpen.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>