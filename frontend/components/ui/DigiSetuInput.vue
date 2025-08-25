<template>
  <div class="digi-setu-input-wrapper">
    <!-- Main Input Field -->
    <div class="digi-setu-input" :class="{ 'digi-setu-input--focused': isFocused }">
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
      
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <button class="toolbar-btn toolbar-btn--icon" @click="$emit('add')">
            <UiIcon name="lucide:plus" :size="16" />
          </button>
          
          <button class="toolbar-btn toolbar-btn--research" @click="$emit('research')">
            <UiIcon name="lucide:globe" :size="16" />
            <span>Research</span>
          </button>
        </div>
        
        <div class="toolbar-right">
          <div class="model-selector" @click="$emit('model-select')">
            <span>Digi Setu AI</span>
            <UiIcon name="lucide:chevron-down" :size="16" />
          </div>
          
          <button 
            class="send-btn"
            :disabled="!canSend"
            :class="{ 'send-btn--disabled': !canSend }"
            @click="handleSend"
          >
            <UiIcon 
              v-if="loading"
              name="lucide:loader" 
              :size="16"
              class="send-icon send-icon--loading"
            />
            <UiIcon 
              v-else
              name="lucide:arrow-up" 
              :size="16"
              class="send-icon"
            />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  disabled?: boolean
  loading?: boolean
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue' | 'send', value: string): void
  (e: 'add' | 'options' | 'research' | 'upload' | 'model-select' | 'focus' | 'blur'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  disabled: false,
  loading: false,
  placeholder: 'How can I help you today?'
})

const emit = defineEmits<Emits>()

const textareaRef = ref<HTMLTextAreaElement>()
const isFocused = ref(false)
const inputValue = ref(props.modelValue || '')

const canSend = computed(() => {
  return inputValue.value.trim().length > 0 && !props.disabled && !props.loading
})

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  if (newValue !== undefined) {
    inputValue.value = newValue
  }
})

// Emit changes to parent
watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue)
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
      const newHeight = Math.min(textareaRef.value.scrollHeight, 120)
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
.digi-setu-input-wrapper {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.digi-setu-input {
  background: var(--bg-secondary);
  border: 1.5px solid var(--border-primary);
  border-radius: 16px;
  padding: 0;
  transition: all 0.2s ease;
  overflow: hidden;
}

.digi-setu-input--focused {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.input-field {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  padding: 20px 24px 16px;
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

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border-primary);
  background: var(--bg-tertiary);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.toolbar-btn:hover:not(:disabled) {
  color: var(--text-primary);
  background: var(--bg-hover);
  border-color: var(--border-secondary);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn--icon {
  padding: 8px;
  min-width: 36px;
  height: 36px;
  justify-content: center;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.toolbar-btn--icon:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.toolbar-btn--research {
  padding: 8px 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.toolbar-btn--research:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 4px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.model-selector:hover {
  color: var(--text-primary);
}

.send-btn {
  background: var(--accent-primary);
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.send-btn .send-icon {
  color: white !important;
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: scale(1.05);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-btn--disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.send-icon--loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
