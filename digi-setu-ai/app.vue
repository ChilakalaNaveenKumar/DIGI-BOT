<template>
  <div class="app-root" :data-theme="currentTheme">
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
    
    <!-- Use NuxtLayout for pages that specify a layout -->
    <NuxtLayout v-if="route.meta.layout">
      <NuxtPage />
    </NuxtLayout>
    
    <!-- Custom layout for authenticated pages without explicit layout -->
    <div v-else class="app-container" :class="{ 'has-sidebar': shouldShowSidebar }">
      <LayoutSidebar v-if="shouldShowSidebar" />
      <main class="main-content" :class="{ 'with-sidebar': shouldShowSidebar }">
        <LayoutHeader v-if="shouldShowSidebar" />
        <div class="page-content">
          <NuxtPage />
        </div>
        <LayoutFooter v-if="shouldShowFooter" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// Initialize theme system
const { theme, currentTheme } = useTheme()

// Initialize auth system
const { isAuthenticated } = useAuth()

// Get current route to determine layout
const route = useRoute()

// Apply theme to document (using currentTheme which resolves 'auto')
watch(currentTheme, (newTheme) => {
  if (import.meta.client) {
    document.documentElement.setAttribute('data-theme', newTheme)
  }
}, { immediate: true })

// Determine if sidebar should be shown (only for custom layout)
const shouldShowSidebar = computed(() => {
  // Only show sidebar if user is authenticated
  if (!isAuthenticated.value) return false
  
  // Only for pages without explicit layout (using our custom layout)
  if (route.meta.layout) return false
  
  // Show sidebar for authenticated users on pages without explicit layout
  return true
})

// Determine if footer should be shown (only for custom layout)
const shouldShowFooter = computed(() => {
  // Show footer for authenticated users on pages without explicit layout
  if (isAuthenticated.value && !route.meta.layout) return true
  
  return false
})
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
  margin-left: 0; /* Default: no sidebar margin */
  min-height: 100vh;
}

.main-content.with-sidebar {
  margin-left: 260px; /* Account for fixed sidebar when present */
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}


</style>
