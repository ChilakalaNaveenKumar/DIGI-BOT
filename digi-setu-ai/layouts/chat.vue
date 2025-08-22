<template>
  <div class="app-root" :data-theme="theme">
    <div class="app-container">
      <LayoutSidebar />
      <main class="main-content">
        <LayoutHeader />
        <slot />
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

<style scoped>
.app-root {
  min-height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.app-container {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: visible;
  margin-left: 260px; /* Account for fixed sidebar */
}
</style>
