<template>
  <button 
    :class="[
      'toggle',
      `toggle--${size}`,
      { 'toggle--on': modelValue }
    ]"
    :disabled="disabled"
    @click="handleToggle"
    :aria-pressed="modelValue"
    role="switch"
  >
    <div class="toggle-track">
      <div class="toggle-thumb">
        <Icon 
          v-if="onIcon && modelValue"
          :name="onIcon" 
          :size="iconSize"
          class="toggle-icon"
        />
        <Icon 
          v-else-if="offIcon && !modelValue"
          :name="offIcon" 
          :size="iconSize"
          class="toggle-icon"
        />
      </div>
    </div>
    
    <span v-if="label" class="toggle-label">
      {{ modelValue ? (onLabel || label) : (offLabel || label) }}
    </span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  label?: string
  onLabel?: string
  offLabel?: string
  onIcon?: string
  offIcon?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  disabled: false
})

const emit = defineEmits<Emits>()

const iconSize = computed(() => {
  switch (props.size) {
    case 'sm': return 10
    case 'lg': return 16
    default: return 12
  }
})

const handleToggle = () => {
  if (!props.disabled) {
    emit('update:modelValue', !props.modelValue)
  }
}
</script>

<style scoped>
.toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);
}

.toggle:hover:not(:disabled) {
  color: var(--text-primary);
}

.toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-track {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  position: relative;
  transition: all 0.3s ease;
}

.toggle--on .toggle-track {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
}

.toggle-thumb {
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
  box-shadow: var(--shadow-sm);
}

/* Sizes */
.toggle--sm .toggle-track {
  width: 32px;
  height: 18px;
}

.toggle--sm .toggle-thumb {
  width: 14px;
  height: 14px;
}

.toggle--sm.toggle--on .toggle-thumb {
  transform: translateX(14px);
}

.toggle--md .toggle-track {
  width: 44px;
  height: 24px;
}

.toggle--md .toggle-thumb {
  width: 20px;
  height: 20px;
}

.toggle--md.toggle--on .toggle-thumb {
  transform: translateX(20px);
}

.toggle--lg .toggle-track {
  width: 56px;
  height: 30px;
}

.toggle--lg .toggle-thumb {
  width: 26px;
  height: 26px;
}

.toggle--lg.toggle--on .toggle-thumb {
  transform: translateX(26px);
}

.toggle-icon {
  color: var(--accent-primary);
}

.toggle--on .toggle-icon {
  color: white;
}

.toggle-label {
  font-size: 14px;
  font-weight: 500;
  min-width: 36px;
}
</style>
