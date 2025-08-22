<template>
  <div class="chat-page" :data-theme="currentTheme">
    <!-- Loading fallback for SSR -->
    <div v-if="!mounted" class="loading-container">
      <div class="loading-content">
        <div class="loading-spinner" />
        <p>Loading Digi Setu AI...</p>
      </div>
    </div>
    
    <!-- Client-side content -->
    <div v-else class="chat-content">
      <ChatContainer />
    </div>
  </div>
</template>

<script setup lang="ts">
// Set page meta
definePageMeta({
  layout: 'chat',
  ssr: false,
  middleware: 'auth'
})

// Client-side detection
const mounted = ref(false)
const currentTheme = ref('auto')

onMounted(() => {
  mounted.value = true
  
  // Theme management
  const savedTheme = localStorage.getItem('theme') || 'auto'
  let actualTheme = savedTheme
  if (savedTheme === 'auto') {
    actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  currentTheme.value = actualTheme
  document.documentElement.setAttribute('data-theme', actualTheme)
})

// SEO
useHead({
  title: 'Chat - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Chat with Digi Setu AI - experience advanced markdown rendering, code highlighting, and interactive conversations.' }
  ]
})
</script>

<style scoped>
.chat-page {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: visible;
  min-height: 100%;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-primary);
  border-top: 3px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
