<template>
  <span 
    :class="[
      'badge',
      `badge--${variant}`,
      `badge--${size}`
    ]"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'md' | 'lg'
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md'
})
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Sizes */
.badge--sm {
  padding: 2px 6px;
  font-size: 10px;
}

.badge--md {
  padding: 2px 8px;
  font-size: 11px;
}

.badge--lg {
  padding: 4px 10px;
  font-size: 12px;
}

/* Variants */
.badge--default {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.badge--primary {
  background: var(--accent-primary);
  color: white;
}

.badge--secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.badge--success {
  background: #d1fae5;
  color: #065f46;
}

.badge--warning {
  background: #fef3c7;
  color: #92400e;
}

.badge--error {
  background: #fee2e2;
  color: #991b1b;
}
</style>
