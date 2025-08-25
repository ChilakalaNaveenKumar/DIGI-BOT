<template>
  <div class="input-area" :class="{ 'input-area--centered': !hasMessages }">
    <div class="input-container">
      <UiChatInput
        v-model="inputValue"
        :disabled="loading"
        :loading="loading"
        :show-footer="!hasMessages"
        @send="handleSend"
        @attach="handleAttach"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  loading?: boolean
  modelValue?: string
  hasMessages?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'send' | 'attach', content?: string): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  modelValue: '',
  hasMessages: false
})

const emit = defineEmits<Emits>()

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleSend = (content: string) => {
  emit('send', content)
}

const handleAttach = () => {
  emit('attach')
  // TODO: Implement file attachment logic
}
</script>

<style scoped>
.input-area {
  padding: 16px 24px;
  background: var(--bg-primary);
}

.input-area--centered {
  position: fixed;
  bottom: 15%;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 260px);
  max-width: 800px;
  background: transparent;
  z-index: 10;
  margin-left: 130px;
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
}
</style>
