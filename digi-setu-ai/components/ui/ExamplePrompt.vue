<template>
  <button class="example-prompt" @click="handleClick">
    <Icon :name="icon" :size="16" />
    <span>{{ text }}</span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  text: string
  icon: string
}

interface Emits {
  (e: 'click', text: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleClick = () => {
  emit('click', props.text)
}
</script>

<style scoped>
.example-prompt {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  text-align: left;
}

.example-prompt:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
  border-color: var(--border-secondary);
  transform: translateY(-1px);
}
</style>
