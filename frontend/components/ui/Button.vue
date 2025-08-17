<template>
  <button 
    :class="[
      'btn',
      `btn--${variant}`,
      `btn--${size}`,
      { 'btn--loading': loading }
    ]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <Icon v-if="loading" name="loader" class="btn__spinner" />
    <slot />
  </button>
</template>

<script setup>
interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false
})
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
  border: 1px solid transparent;
  text-decoration: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.btn--primary {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.btn--primary:hover:not(:disabled) {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

.btn--secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-primary);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn--ghost {
  background: transparent;
  color: var(--text-secondary);
}

.btn--ghost:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn--outline {
  background: transparent;
  color: var(--accent-primary);
  border-color: var(--accent-primary);
}

.btn--outline:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
}

/* Sizes */
.btn--sm {
  padding: 6px 12px;
  font-size: 14px;
}

.btn--md {
  padding: 8px 16px;
  font-size: 14px;
}

.btn--lg {
  padding: 12px 24px;
  font-size: 16px;
}

.btn__spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>