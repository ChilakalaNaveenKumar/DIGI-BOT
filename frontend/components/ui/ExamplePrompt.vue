<template>
  <button 
    class="example-prompt"
    :disabled="disabled"
    @click="handleClick"
  >
    <UiIcon 
      v-if="icon" 
      :name="icon" 
      :size="iconSize" 
      class="prompt-icon" 
    />
    <span class="prompt-text">{{ text }}</span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  text: string
  icon?: string
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  icon: '',
  disabled: false,
  size: 'md'
})

interface Emits {
  (e: 'click', text: string): void
}



const emit = defineEmits<Emits>()

const iconSize = computed(() => {
  switch (props.size) {
    case 'sm': return 12
    case 'lg': return 16
    default: return 14
  }
})

const handleClick = () => {
  if (!props.disabled) {
    emit('click', props.text)
  }
}
</script>

<style scoped>
.example-prompt {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: auto;
  min-width: auto;
  min-height: 48px;
  justify-content: flex-start;
}

.example-prompt:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-secondary);
  color: var(--text-primary);
}

.example-prompt:active:not(:disabled) {
  transform: scale(0.98);
}

.example-prompt:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.prompt-icon {
  color: var(--accent-primary);
  flex-shrink: 0;
}

.prompt-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
