<template>
  <div class="app-root" :data-theme="theme">
    <div class="app-container">
      <LayoutSidebar />
      <main class="main-content">
        <LayoutHeader />
        <NuxtPage />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// Initialize theme system
const { theme } = useTheme()

// Apply theme to document
watch(theme, (newTheme) => {
  if (process.client) {
    document.documentElement.setAttribute('data-theme', newTheme)
  }
}, { immediate: true })
</script>

<style>
/* Import theme variables */
@import '~/assets/css/theme.css';

.app-root {
  height: 100vh;
  overflow: hidden;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.app-container {
  display: flex;
  height: 100%;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>