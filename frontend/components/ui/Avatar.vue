<template>
  <div 
    :class="[
      'avatar',
      `avatar--${size}`,
      `avatar--${variant}`,
      { 'avatar--clickable': clickable }
    ]"
    @click="handleClick"
  >
    <img
      v-if="src"
      :src="src"
      :alt="alt"
      class="avatar-image"
      @error="handleImageError"
    />
    
    <Icon
      v-else-if="icon"
      :name="icon"
      :size="iconSize"
      class="avatar-icon"
    />
    
    <span v-else class="avatar-text">
      {{ initials }}
    </span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  src?: string
  alt?: string
  icon?: string
  initials?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'primary' | 'secondary' | 'accent'
  clickable?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
  (e: 'error'): void
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  size: 'md',
  variant: 'primary',
  clickable: false
})

const emit = defineEmits<Emits>()

const iconSize = computed(() => {
  switch (props.size) {
    case 'xs': return 10
    case 'sm': return 12
    case 'md': return 16
    case 'lg': return 20
    case 'xl': return 24
    default: return 16
  }
})

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}

const handleImageError = () => {
  emit('error')
}
</script>

<style scoped>
.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
  overflow: hidden;
  transition: all 0.2s ease;
}

.avatar--clickable {
  cursor: pointer;
}

.avatar--clickable:hover {
  opacity: 0.8;
}

/* Sizes */
.avatar--xs {
  width: 20px;
  height: 20px;
  font-size: 10px;
}

.avatar--sm {
  width: 28px;
  height: 28px;
  font-size: 12px;
}

.avatar--md {
  width: 32px;
  height: 32px;
  font-size: 12px;
}

.avatar--lg {
  width: 40px;
  height: 40px;
  font-size: 14px;
}

.avatar--xl {
  width: 48px;
  height: 48px;
  font-size: 16px;
}

/* Variants */
.avatar--primary {
  background: var(--accent-primary);
  color: white;
}

.avatar--secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.avatar--accent {
  background: var(--accent-secondary);
  color: white;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-icon,
.avatar-text {
  font-weight: 600;
}
</style>
