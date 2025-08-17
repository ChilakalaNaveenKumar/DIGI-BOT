<template>
  <div class="input-area">
    <div class="input-container">
      <div class="input-wrapper">
        <Input
          ref="inputRef"
          v-model="inputValue"
          type="textarea"
          placeholder="Message Claude..."
          :disabled="loading"
          size="md"
          @keydown="handleKeydown"
          class="message-input"
        />
        
        <Button
          variant="primary"
          size="sm"
          class="send-button"
          :disabled="!inputValue.trim() || loading"
          @click="handleSend"
        >
          <Icon name="send" :size="16" />
        </Button>
      </div>
      
      <div class="input-footer">
        <span class="input-hint">
          Press Enter to send, Shift+Enter for new line
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
interface Props {
  loading?: boolean
  modelValue?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'send', content: string): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  modelValue: ''
})

const emit = defineEmits<Emits>()

const inputRef = ref()
const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

const handleSend = () => {
  const content = inputValue.value.trim()
  if (content && !props.loading) {
    emit('send', content)
    inputValue.value = ''
  }
}
</script>

<style scoped>
.input-area {
  border-top: 1px solid var(--border-primary);
  background: var(--bg-primary);
  padding: 16px 24px;
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  padding: 12px;
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.message-input {
  flex: 1;
}

.send-button {
  border-radius: 8px;
  padding: 8px;
  min-width: 36px;
  height: 36px;
}

.input-footer {
  margin-top: 8px;
  text-align: center;
}

.input-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
