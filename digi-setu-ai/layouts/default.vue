<template>
  <div class="default-layout">
    <slot />
  </div>
</template>

<script setup lang="ts">
// Ensure theme is applied
if (process.client) {
  const savedTheme = localStorage.getItem('theme') || 'auto'
  let actualTheme = savedTheme
  if (savedTheme === 'auto') {
    actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  document.documentElement.setAttribute('data-theme', actualTheme)
}
</script>

<style scoped>
.default-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}
</style>
