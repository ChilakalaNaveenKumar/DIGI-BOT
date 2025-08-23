<template>
  <!-- Use custom SVG files when available -->
  <img 
    v-if="isCustomIcon" 
    :src="`/icons/${iconName}.svg`" 
    :width="size" 
    :height="size" 
    :alt="iconName"
    class="icon custom-icon"
  >
  
  <!-- Fallback to inline SVG for other icons -->
  <svg
    v-else
    :class="['icon', `icon-${iconName}`, $attrs.class]"
    :width="size"
    :height="size"
    :viewBox="viewBox"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <!-- Chevron Down -->
    <path
      v-if="iconName === 'chevron-down'"
      d="M6 9l6 6 6-6"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <!-- Chevron Up -->
    <path
      v-if="iconName === 'chevron-up'"
      d="M18 15l-6-6-6 6"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <!-- Globe (web search) -->
    <circle
      v-if="iconName === 'globe'"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      stroke-width="2"
    />
    <path
      v-if="iconName === 'globe'"
      d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"
      stroke="currentColor"
      stroke-width="2"
    />
    
    <!-- Book Open -->
    <path
      v-if="iconName === 'book-open'"
      d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      v-if="iconName === 'book-open'"
      d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <!-- Edit 3 -->
    <path
      v-if="iconName === 'edit-3'"
      d="M12 20h9"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      v-if="iconName === 'edit-3'"
      d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <!-- Plus -->
    <path
      v-if="iconName === 'plus'"
      d="M12 5v14M5 12h14"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <!-- Hard Drive -->
    <line
      v-if="iconName === 'hard-drive'"
      x1="22"
      y1="12"
      x2="2"
      y2="12"
      stroke="currentColor"
      stroke-width="2"
    />
    <path
      v-if="iconName === 'hard-drive'"
      d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle
      v-if="iconName === 'hard-drive'"
      cx="6"
      cy="14"
      r="1"
      stroke="currentColor"
      stroke-width="2"
    />
    
    <!-- Code 2 -->
    <path
      v-if="iconName === 'code-2'"
      d="M16 18l6-6-6-6M8 6l-6 6 6 6"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <!-- Alert Circle -->
    <circle
      v-if="iconName === 'alert-circle'"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      stroke-width="2"
    />
    <line
      v-if="iconName === 'alert-circle'"
      x1="12"
      y1="8"
      x2="12"
      y2="12"
      stroke="currentColor"
      stroke-width="2"
    />
    <line
      v-if="iconName === 'alert-circle'"
      x1="12"
      y1="16"
      x2="12.01"
      y2="16"
      stroke="currentColor"
      stroke-width="2"
    />
    
    <!-- Sparkles -->
    <path
      v-if="iconName === 'sparkles'"
      d="M9 12l2 2 4-4M21 12c0 1.2-.4 2.3-1.1 3.1-.7.8-1.7 1.3-2.8 1.4-.2 0-.4.1-.6.1-.1 0-.3 0-.4 0-1.1-.1-2.1-.6-2.8-1.4-.7-.8-1.1-1.9-1.1-3.1 0-1.2.4-2.3 1.1-3.1.7-.8 1.7-1.3 2.8-1.4.1 0 .3 0 .4 0 .2 0 .4.1.6.1 1.1.1 2.1.6 2.8 1.4.7.8 1.1 1.9 1.1 3.1z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <!-- Settings -->
    <circle
      v-if="iconName === 'settings'"
      cx="12"
      cy="12"
      r="3"
      stroke="currentColor"
      stroke-width="2"
    />
    <path
      v-if="iconName === 'settings'"
      d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>

<script setup lang="ts">
interface Props {
  name: string
  size?: number | string
  viewBox?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 24,
  viewBox: '0 0 24 24'
})

const iconName = computed(() => props.name)

const isCustomIcon = computed(() => {
  // List of custom icons that have SVG files in /public/icons/
  const customIcons = ['digi-setu', 'logo', 'brand']
  return customIcons.includes(iconName.value)
})
</script>

<style scoped>
.icon {
  display: inline-block;
  vertical-align: middle;
  color: currentColor;
}

.custom-icon {
  object-fit: contain;
}
</style>
