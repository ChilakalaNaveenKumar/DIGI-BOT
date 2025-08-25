<template>
  <div class="input-wrapper" :class="{ 'input-wrapper--focused': isFocused }">
    <textarea
      v-if="type === 'textarea'"
      ref="inputRef"
      v-model="inputValue"
      :class="[
        'input',
        'input--textarea',
        `input--${size}`,
        { 'input--error': error }
      ]"
      :placeholder="placeholder"
      :disabled="disabled"
      :rows="rows"
      @focus="handleFocus"
      @blur="handleBlur"
      @input="handleInput"
      @keydown="handleKeydown"
    />
    
    <input
      v-else
      ref="inputRef"
      v-model="inputValue"
      :type="type"
      :class="[
        'input',
        `input--${size}`,
        { 'input--error': error }
      ]"
      :placeholder="placeholder"
      :disabled="disabled"
      @focus="handleFocus"
      @blur="handleBlur"
      @input="handleInput"
      @keydown="handleKeydown"
    />
    
    <div v-if="icon" class="input-icon">
      <UiIcon :name="icon" :size="iconSize" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  type?: 'text' | 'email' | 'password' | 'textarea'
  size?: 'sm' | 'md' | 'lg'
  placeholder?: string
  disabled?: boolean
  error?: boolean
  icon?: string
  rows?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
  (e: 'keydown', event: KeyboardEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  size: 'md',
  placeholder: '',
  disabled: false,
  error: false,
  rows: 1
})

const emit = defineEmits<Emits>()

const inputRef = ref<HTMLInputElement | HTMLTextAreaElement>()
const isFocused = ref(false)

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const iconSize = computed(() => {
  switch (props.size) {
    case 'sm': return 14
    case 'lg': return 20
    default: return 16
  }
})

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleInput = () => {
  // Auto-resize textarea
  if (props.type === 'textarea' && inputRef.value) {
    nextTick(() => {
      if (inputRef.value) {
        inputRef.value.style.height = 'auto'
        inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 120) + 'px'
      }
    })
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

// Focus method
const focus = () => {
  inputRef.value?.focus()
}

// Expose focus method
defineExpose({ focus })
</script>

<style scoped>
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper--focused {
  /* Add focus styles if needed */
}

.input {
  width: 100%;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  color: var(--text-primary);
  font-family: inherit;
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--bg-tertiary);
}

.input--error {
  border-color: #ef4444;
}

.input--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Sizes */
.input--sm {
  padding: 6px 12px;
  font-size: 14px;
}

.input--md {
  padding: 8px 12px;
  font-size: 14px;
}

.input--lg {
  padding: 12px 16px;
  font-size: 16px;
}

.input--textarea {
  resize: none;
  min-height: 40px;
  max-height: 120px;
  line-height: 1.5;
}

.input::placeholder {
  color: var(--text-tertiary);
}

.input-icon {
  position: absolute;
  right: 12px;
  color: var(--text-tertiary);
  pointer-events: none;
}
</style>