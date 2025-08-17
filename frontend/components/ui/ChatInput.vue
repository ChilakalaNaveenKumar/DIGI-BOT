<template>
  <div class="chat-input-wrapper">
    <div class="chat-input" :class="{ 'chat-input--focused': isFocused }">
      <!-- Attach Button -->
      <button
        class="attach-button"
        :disabled="disabled"
        @click="$emit('attach')"
      >
        <UiIcon name="lucide:paperclip" :size="16" />
      </button>
      
      <!-- Text Input -->
      <textarea
        ref="textareaRef"
        v-model="inputValue"
        class="input-field"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        @focus="handleFocus"
        @blur="handleBlur"
        @input="handleInput"
        @keydown="handleKeydown"
      />
      
      <!-- Send Button -->
      <UiSendButton
        :disabled="!canSend"
        :loading="loading"
        @click="handleSend"
      />
    </div>
    
    <!-- Footer Text -->
    <div v-if="showFooter" class="input-footer">
      <span class="input-hint">{{ footerText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  showFooter?: boolean
  footerText?: string
  maxHeight?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'send', content: string): void
  (e: 'attach'): void
  (e: 'focus'): void
  (e: 'blur'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: 'Message Claude...',
  disabled: false,
  loading: false,
  showFooter: true,
  footerText: 'Press Enter to send, Shift+Enter for new line',
  maxHeight: 120
})

const emit = defineEmits<Emits>()

const textareaRef = ref<HTMLTextAreaElement>()
const isFocused = ref(false)

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const canSend = computed(() => {
  return inputValue.value.trim().length > 0 && !props.disabled && !props.loading
})

const handleFocus = () => {
  isFocused.value = true
  emit('focus')
}

const handleBlur = () => {
  isFocused.value = false
  emit('blur')
}

const handleInput = () => {
  autoResize()
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

const handleSend = () => {
  const content = inputValue.value.trim()
  if (content && !props.disabled && !props.loading) {
    emit('send', content)
    inputValue.value = ''
    nextTick(() => {
      autoResize()
    })
  }
}

const autoResize = () => {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      const newHeight = Math.min(textareaRef.value.scrollHeight, props.maxHeight)
      textareaRef.value.style.height = newHeight + 'px'
    }
  })
}

const focus = () => {
  textareaRef.value?.focus()
}

defineExpose({ focus })
</script>

<style scoped>
.chat-input-wrapper {
  width: 100%;
}

.chat-input {
  position: relative;
  display: flex;
  align-items: flex-end;
  background: var(--bg-primary);
  border: 1.5px solid var(--border-primary);
  border-radius: 24px;
  padding: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-input--focused {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1), 0 2px 8px rgba(0, 0, 0, 0.1);
}

.attach-button {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s ease;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.attach-button:hover:not(:disabled) {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.attach-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-field {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  padding: 12px 16px 12px 44px;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-primary);
  resize: none;
  min-height: 24px;
  max-height: 120px;
}

.input-field::placeholder {
  color: var(--text-tertiary);
}

.input-footer {
  margin-top: 12px;
  text-align: center;
}

.input-hint {
  font-size: 13px;
  color: var(--text-tertiary);
}
</style>
