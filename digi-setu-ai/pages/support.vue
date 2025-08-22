<template>
  <div class="support-container">
    <div class="support-content">
      <!-- Header -->
      <div class="support-header">
        <NuxtLink to="/auth/signin" class="back-link">
          <Icon name="lucide:arrow-left" class="back-icon" />
          Back to Sign In
        </NuxtLink>
        <h1 class="support-title">Support</h1>
        <p class="support-subtitle">
          We're here to help you get the most out of Digi Setu AI
        </p>
      </div>

      <!-- Content -->
      <div class="support-body">
        <div class="support-grid">
          <div class="support-card">
            <Icon name="lucide:mail" class="support-icon" />
            <h3 class="support-card-title">Email Support</h3>
            <p class="support-card-description">
              Get help with your account, technical issues, or general questions.
            </p>
            <a href="mailto:info@digi-setu.com" class="support-link">
              info@digi-setu.com
            </a>
          </div>

          <div class="support-card">
            <Icon name="lucide:book-open" class="support-icon" />
            <h3 class="support-card-title">Documentation</h3>
            <p class="support-card-description">
              Learn how to use Digi Setu AI with our comprehensive guides.
            </p>
            <button class="support-link" disabled>
              Coming Soon
            </button>
          </div>

          <div class="support-card">
            <Icon name="lucide:message-circle" class="support-icon" />
            <h3 class="support-card-title">Community</h3>
            <p class="support-card-description">
              Connect with other educators and share best practices.
            </p>
            <button class="support-link" disabled>
              Coming Soon
            </button>
          </div>

          <div class="support-card">
            <Icon name="lucide:video" class="support-icon" />
            <h3 class="support-card-title">Video Tutorials</h3>
            <p class="support-card-description">
              Watch step-by-step tutorials to master Digi Setu AI features.
            </p>
            <button class="support-link" disabled>
              Coming Soon
            </button>
          </div>
        </div>

        <section class="faq-section">
          <h2 class="faq-title">Frequently Asked Questions</h2>
          
          <div class="faq-item">
            <h3 class="faq-question">How do I get started with Digi Setu AI?</h3>
            <p class="faq-answer">
              Simply sign in with your Google account and start uploading your educational content. Our AI will help transform it into interactive learning experiences.
            </p>
          </div>

          <div class="faq-item">
            <h3 class="faq-question">What types of content can I upload?</h3>
            <p class="faq-answer">
              You can upload text documents, presentations, PDFs, and other educational materials. Our AI supports various formats and can enhance them with interactive elements.
            </p>
          </div>

          <div class="faq-item">
            <h3 class="faq-question">Is my data secure?</h3>
            <p class="faq-answer">
              Yes, we take data security seriously. All your content is encrypted and stored securely. We never share your personal information or educational content with third parties.
            </p>
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
  title: 'Support - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Get help and support for Digi Setu AI' },
    { name: 'robots', content: 'index, follow' }
  ]
})
</script>

<style scoped>
.support-container {
  min-height: 100vh;
  padding: 2rem;
  background: var(--bg-primary);
}

.support-content {
  max-width: 1000px;
  margin: 0 auto;
}

.support-header {
  text-align: center;
  margin-bottom: 3rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--accent-primary);
  text-decoration: none;
  font-size: 0.875rem;
  margin-bottom: 2rem;
  transition: color 0.2s ease;
}

.back-link:hover {
  color: var(--accent-hover);
}

.back-icon {
  width: 1rem;
  height: 1rem;
}

.support-title {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
}

.support-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin: 0;
}

.support-body {
  margin-bottom: 3rem;
}

.support-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.support-card {
  background: var(--bg-primary);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.support-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.support-icon {
  width: 3rem;
  height: 3rem;
  color: var(--accent-primary);
  margin-bottom: 1rem;
}

.support-card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
}

.support-card-description {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 1.5rem 0;
}

.support-link {
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border: 1px solid var(--accent-primary);
  border-radius: 0.5rem;
  display: inline-block;
  transition: all 0.2s ease;
  background: transparent;
  cursor: pointer;
}

.support-link:hover:not(:disabled) {
  background: var(--accent-primary);
  color: white;
}

.support-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.faq-section {
  background: var(--bg-primary);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
}

.faq-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 2rem 0;
  text-align: center;
}

.faq-item {
  margin-bottom: 2rem;
}

.faq-item:last-child {
  margin-bottom: 0;
}

.faq-question {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
}

.faq-answer {
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

@media (max-width: 768px) {
  .support-container {
    padding: 1rem;
  }
  
  .support-title {
    font-size: 2.5rem;
  }
  
  .support-subtitle {
    font-size: 1.125rem;
  }
  
  .support-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .support-card {
    padding: 1.5rem;
  }
  
  .faq-section {
    padding: 1.5rem;
  }
}
</style>
