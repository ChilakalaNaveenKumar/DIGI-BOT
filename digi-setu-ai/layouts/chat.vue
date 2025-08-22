<template>
  <div class="app-root" :data-theme="currentTheme">
    <div class="app-container">
      <LayoutSidebar />
      <main class="main-content">
        <LayoutHeader />
        <div class="page-content">
          <slot />
        </div>
        <LayoutFooter />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// Initialize theme system
const { theme, currentTheme } = useTheme()

// Apply theme to document  
watch(currentTheme, (newTheme) => {
  if (import.meta.client) {
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
  min-height: 100vh;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
