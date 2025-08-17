<template>
  <button 
    class="send-button"
    :class="[`send-button--${size}`, { 'send-button--disabled': disabled }]"
    :disabled="disabled"
    @click="handleClick"
  >
    <UiIcon 
      v-if="loading"
      name="lucide:loader" 
      :size="iconSize"
      class="send-icon send-icon--loading"
    />
    <UiIcon 
      v-else
      name="lucide:send" 
      :size="iconSize"
      class="send-icon"
    />
  </button>
</template>

<script setup lang="ts">
interface Props {
  disabled?: boolean
  loading?: boolean
  size?: 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'click'): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  loading: false,
  size: 'md'
})

const emit = defineEmits<Emits>()

const iconSize = computed(() => {
  switch (props.size) {
    case 'sm': return 14
    case 'lg': return 20
    default: return 16
  }
})

const handleClick = () => {
  if (!props.disabled && !props.loading) {
    emit('click')
  }
}
</script>

<style scoped>
.send-button {
  background: var(--accent-primary);
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: scale(1.05);
}

.send-button:active:not(:disabled) {
  transform: scale(0.95);
}

.send-button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.send-button--sm {
  padding: 6px;
  min-width: 28px;
  height: 28px;
}

.send-button--md {
  padding: 8px;
  min-width: 32px;
  height: 32px;
}

.send-button--lg {
  padding: 10px;
  min-width: 36px;
  height: 36px;
}

.send-icon {
  transition: transform 0.2s ease;
}

.send-icon--loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
