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
    <path
      v-if="iconName === 'sun'"
      d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle
      v-if="iconName === 'sun'"
      cx="12"
      cy="12"
      r="5"
      stroke="currentColor"
      stroke-width="2"
    />
    
    <path
      v-if="iconName === 'moon'"
      d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      fill="currentColor"
    />
    
    <path
      v-if="iconName === 'plus'"
      d="M12 5v14M5 12h14"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'cpu'"
      d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <rect
      v-if="iconName === 'cpu'"
      x="9"
      y="9"
      width="6"
      height="6"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'message-circle'"
      d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'send'"
      d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'chevron-down'"
      d="M6 9l6 6 6-6"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <circle
      v-if="iconName === 'alert-circle'"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      stroke-width="2"
    />
    <path
      v-if="iconName === 'alert-circle'"
      d="M12 8v4M12 16h.01"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'paperclip'"
      d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'settings'"
      d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle
      v-if="iconName === 'settings'"
      cx="12"
      cy="12"
      r="3"
      stroke="currentColor"
      stroke-width="2"
    />
    
    <path
      v-if="iconName === 'loader'"
      d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48 2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48 2.83-2.83"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'map-pin'"
      d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle
      v-if="iconName === 'map-pin'"
      cx="12"
      cy="10"
      r="3"
      stroke="currentColor"
      stroke-width="2"
    />
    
    <rect
      v-if="iconName === 'copy'"
      width="14"
      height="14"
      x="8"
      y="8"
      rx="2"
      ry="2"
      stroke="currentColor"
      stroke-width="2"
    />
    <path
      v-if="iconName === 'copy'"
      d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    
    <path
      v-if="iconName === 'refresh-cw'"
      d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      v-if="iconName === 'refresh-cw'"
      d="M21 3v5h-5M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      v-if="iconName === 'refresh-cw'"
      d="M8 16H3v5"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />

    <!-- More Horizontal Icon -->
    <circle v-if="iconName === 'more-horizontal'" cx="12" cy="12" r="1" stroke="currentColor" stroke-width="2" fill="currentColor"/>
    <circle v-if="iconName === 'more-horizontal'" cx="19" cy="12" r="1" stroke="currentColor" stroke-width="2" fill="currentColor"/>
    <circle v-if="iconName === 'more-horizontal'" cx="5" cy="12" r="1" stroke="currentColor" stroke-width="2" fill="currentColor"/>
    
    <!-- Arrow Up Icon -->
    <line v-if="iconName === 'arrow-up'" x1="12" y1="19" x2="12" y2="5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <polyline v-if="iconName === 'arrow-up'" points="5,12 12,5 19,12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Edit 3 Icon -->
    <path v-if="iconName === 'edit-3'" d="M12 20h9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'edit-3'" d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Book Open Icon -->
    <path v-if="iconName === 'book-open'" d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'book-open'" d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Code Icon -->
    <polyline v-if="iconName === 'code'" points="16,18 22,12 16,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <polyline v-if="iconName === 'code'" points="8,6 2,12 8,18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Hard Drive Icon -->
    <line v-if="iconName === 'hard-drive'" x1="22" y1="12" x2="2" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'hard-drive'" d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle v-if="iconName === 'hard-drive'" cx="6" cy="16" r="1" stroke="currentColor" stroke-width="2"/>
    <circle v-if="iconName === 'hard-drive'" cx="10" cy="16" r="1" stroke="currentColor" stroke-width="2"/>
    
    <!-- Sparkles Icon -->
    <path v-if="iconName === 'sparkles'" d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'sparkles'" d="M5 3v4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'sparkles'" d="M19 17v4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'sparkles'" d="M3 5h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'sparkles'" d="M17 19h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Globe Icon -->
    <circle v-if="iconName === 'globe'" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
    <path v-if="iconName === 'globe'" d="M2 12h20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'globe'" d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Pen Tool Icon -->
    <path v-if="iconName === 'pen-tool'" d="M12 19l7-7 3 3-7 7-3-3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'pen-tool'" d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'pen-tool'" d="M2 2l7.586 7.586" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle v-if="iconName === 'pen-tool'" cx="11" cy="11" r="2" stroke="currentColor" stroke-width="2" fill="none"/>
    
    <!-- Graduation Cap Icon -->
    <path v-if="iconName === 'graduation-cap'" d="m22 10-10-5L2 10l10 5 10-5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'graduation-cap'" d="M6 16v-3l6-3 6 3v3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'graduation-cap'" d="M22 10v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Code 2 Icon -->
    <path v-if="iconName === 'code-2'" d="m18 16 4-4-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'code-2'" d="m6 8-4 4 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="iconName === 'code-2'" d="m14.5 4-5 16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- Google Drive Icon (colorful) -->
    <g v-if="iconName === 'google-drive'">
      <path d="M8 2l4 7H2l6-7z" fill="#0066DA" stroke="none"/>
      <path d="M2 9h10l-4 7H4l-2-7z" fill="#00AC47" stroke="none"/>
      <path d="M12 9h10l-6 11-4-7z" fill="#EA4335" stroke="none"/>
      <path d="M16 16l6-11" stroke="#FBBC04" stroke-width="1" fill="none"/>
    </g>
  </svg>
</template>

<script setup lang="ts">
interface Props {
  name: string
  size?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  size: 24
})

// Remove lucide: prefix if present
const iconName = computed(() => {
  return props.name.replace('lucide:', '')
})

// List of custom icons available in /public/icons/
const customIcons = ['send', 'paperclip', 'search', 'menu']

const isCustomIcon = computed(() => {
  return customIcons.includes(iconName.value)
})

const viewBox = computed(() => '0 0 24 24')
</script>

<style scoped>
.icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}

.custom-icon {
  filter: var(--icon-filter, none);
}

/* Apply current color to custom icons in dark mode */
:root {
  --icon-filter: none;
}

[data-theme="dark"] {
  --icon-filter: brightness(0) saturate(100%) invert(100%);
}
</style>