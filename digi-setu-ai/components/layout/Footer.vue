<template>
  <footer class="app-footer">
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
</template>

<script setup lang="ts">
// Footer component logic
</script>

<style scoped>
.app-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  margin-top: auto; /* Push to bottom */
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
