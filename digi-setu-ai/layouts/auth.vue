<template>
  <div class="auth-layout" :data-theme="currentTheme">
    <Head>
      <Link 
        rel="stylesheet" 
        href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" 
        integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" 
        crossorigin="anonymous"
      />
    </Head>
    
    <!-- Theme Toggle -->
    <div class="theme-toggle-container">
      <button 
        @click="toggleTheme" 
        class="theme-toggle"
        :title="currentTheme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'"
      >
        <Icon 
          :name="currentTheme === 'light' ? 'lucide:moon' : 'lucide:sun'" 
          class="theme-icon"
        />
      </button>
    </div>

    <!-- Main Content -->
    <main class="auth-main">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="auth-footer">
      <div class="footer-content">
        <p class="footer-text">
          © 2025 Digi Setu AI. All rights reserved.
        </p>
        <div class="footer-links">
          <NuxtLink to="/legal/terms" class="footer-link">Terms</NuxtLink>
          <NuxtLink to="/legal/privacy" class="footer-link">Privacy</NuxtLink>
          <NuxtLink to="/legal/cookies" class="footer-link">Cookies</NuxtLink>
          <NuxtLink to="/support" class="footer-link">Support</NuxtLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Initialize theme system
const { theme, currentTheme, toggleTheme } = useTheme()

// Apply theme to document
watch(currentTheme, (newTheme) => {
  if (import.meta.client) {
    document.documentElement.setAttribute('data-theme', newTheme)
  }
}, { immediate: true })
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.theme-toggle-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 50;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.theme-toggle:hover {
  background: var(--bg-hover);
  border-color: var(--border-secondary);
  box-shadow: var(--shadow-md);
}

.theme-toggle:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.theme-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--text-primary);
}

.auth-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.auth-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  text-align: center;
}

@media (min-width: 768px) {
  .footer-content {
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }
}

.footer-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-link {
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: var(--accent-primary);
}
</style>
