<template>
  <div class="legal-container">
    <div class="legal-content">
      <!-- Header -->
      <div class="legal-header">
        <NuxtLink to="/auth/signin" class="back-link">
          <Icon name="lucide:arrow-left" class="back-icon" />
          Back to Sign In
        </NuxtLink>
        <h1 class="legal-title">Cookie Policy</h1>
        <p class="legal-subtitle">
          Last updated: {{ lastUpdated }}
        </p>
      </div>

      <!-- Content -->
      <div class="legal-body">
        <section class="legal-section">
          <h2>What Are Cookies</h2>
          <p>
            Cookies are small text files that are placed on your computer or mobile device when you visit our website. They help us provide you with a better experience by remembering your preferences and improving our services.
          </p>
        </section>

        <section class="legal-section">
          <h2>How We Use Cookies</h2>
          <p>We use cookies for the following purposes:</p>
          <ul>
            <li><strong>Essential Cookies:</strong> Required for basic website functionality</li>
            <li><strong>Authentication:</strong> To keep you signed in</li>
            <li><strong>Preferences:</strong> To remember your settings and preferences</li>
            <li><strong>Analytics:</strong> To understand how you use our service</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>Managing Cookies</h2>
          <p>
            You can control and manage cookies through your browser settings. However, disabling certain cookies may affect the functionality of our website.
          </p>
        </section>

        <section class="legal-section">
          <h2>Contact Us</h2>
          <p>
            If you have questions about our cookie policy, contact us at:
          </p>
          <div class="contact-info">
            <p><strong>Email:</strong> info@digi-setu.com</p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Set page meta
definePageMeta({
  layout: 'auth'
})

// SEO
useHead({
  title: 'Cookie Policy - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Cookie Policy for Digi Setu AI' },
    { name: 'robots', content: 'index, follow' }
  ]
})

const lastUpdated = 'January 15, 2024'
</script>

<style scoped>
.legal-container {
  min-height: 100vh;
  padding: 2rem;
  background: var(--bg-primary);
}

.legal-content {
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg-primary);
  border-radius: 1rem;
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.legal-header {
  padding: 2rem 2rem 1rem 2rem;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--accent-primary);
  text-decoration: none;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  transition: color 0.2s ease;
}

.back-link:hover {
  color: var(--accent-hover);
}

.back-icon {
  width: 1rem;
  height: 1rem;
}

.legal-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.legal-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  margin: 0;
}

.legal-body {
  padding: 2rem;
}

.legal-section {
  margin-bottom: 2rem;
}

.legal-section:last-child {
  margin-bottom: 0;
}

.legal-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--accent-primary);
}

.legal-section p {
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 1rem;
}

.legal-section p:last-child {
  margin-bottom: 0;
}

.legal-section ul {
  color: var(--text-secondary);
  line-height: 1.7;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.legal-section li {
  margin-bottom: 0.5rem;
}

.contact-info {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-primary);
}

.contact-info p {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.contact-info p:last-child {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .legal-container {
    padding: 1rem;
  }
  
  .legal-header {
    padding: 1.5rem;
  }
  
  .legal-body {
    padding: 1.5rem;
  }
  
  .legal-title {
    font-size: 2rem;
  }
  
  .legal-section h2 {
    font-size: 1.25rem;
  }
}
</style>
