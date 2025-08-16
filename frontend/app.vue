<template>
  <div id="digi-setu-app">
    <!-- Nuxt Layout and Page Router -->
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

// App metadata
useHead({
  title: 'Digi Setu AI - Intelligent Assistant',
  meta: [
    { name: 'description', content: 'Your intelligent AI assistant powered by multiple AI models. Transform content, get insights, and create interactive experiences.' },
    { name: 'theme-color', content: '#2563eb' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
  ]
})

// Initialize app
onMounted(() => {
  // Add global CSS classes
  document.body.classList.add('digi-setu-body')
  
  console.log('🚀 Digi Setu AI Application Initialized')
})
</script>

<style>
/* Import Digi Setu Design System */
@import '~/assets/css/digi-setu-design-system.css';

/* Global app styles */
#digi-setu-app {
  height: 100vh;
  overflow: hidden;
}

.digi-setu-body {
  margin: 0;
  padding: 0;
  font-family: var(--ds-font-primary);
  background: var(--ds-bg-primary);
  color: var(--ds-text-primary);
  line-height: var(--ds-leading-normal);
}

/* Ensure smooth transitions for theme changes */
* {
  transition: background-color var(--ds-transition-normal), 
              color var(--ds-transition-normal),
              border-color var(--ds-transition-normal);
}

/* Prevent transition on initial load */
.no-transition * {
  transition: none !important;
}
</style>
