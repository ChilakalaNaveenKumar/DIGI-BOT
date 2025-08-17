<template>
  <div class="app-root" :data-theme="theme">
    <Head>
      <Link 
        rel="stylesheet" 
        href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" 
        integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" 
        crossorigin="anonymous"
      />
      <Link 
        rel="stylesheet" 
        href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css"
        crossorigin="anonymous"
      />
    </Head>
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
  if (import.meta.client) {
    document.documentElement.setAttribute('data-theme', newTheme)
  }
}, { immediate: true })
</script>

<style>
/* Import theme variables */
@import '~/assets/css/theme.css';
/* Import KaTeX CSS for math rendering */
@import 'katex/dist/katex.min.css';
/* Import highlight.js CSS for syntax highlighting */
@import 'highlight.js/styles/github-dark.css';

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