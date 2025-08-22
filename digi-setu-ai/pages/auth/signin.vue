<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo and Brand -->
      <div class="auth-header">
        <div class="brand-logo">
          <Icon name="lucide:bot" class="logo-icon" />
          <h1 class="brand-name">Digi Setu AI</h1>
        </div>
        <p class="auth-subtitle">
          Transform static content into interactive learning experiences
        </p>
      </div>

      <!-- Sign In Form -->
      <div class="auth-form">
        <h2 class="form-title">Welcome back</h2>
        <p class="form-description">
          Sign in to continue to your AI-powered learning dashboard
        </p>

        <!-- Google Sign In Button -->
        <div class="sign-in-section">
          <GoogleSignInButton 
            @auth-success="handleAuthSuccess" 
            @auth-error="handleAuthError" 
          />
        </div>

        <!-- Divider -->
        <div class="divider">
          <span class="divider-text">or</span>
        </div>

        <!-- Email Sign In (Optional - for future) -->
        <div class="email-section">
          <input 
            type="email" 
            placeholder="Enter your email"
            class="input"
            disabled
          />
          <p class="email-notice">
            Email sign-in coming soon. Use Google for now.
          </p>
        </div>
      </div>

      <!-- Terms and Legal -->
      <div class="auth-footer">
        <p class="legal-text">
          By continuing, you agree to our 
          <NuxtLink to="/legal/terms" class="legal-link">Terms of Service</NuxtLink>
          and acknowledge our 
          <NuxtLink to="/legal/privacy" class="legal-link">Privacy Policy</NuxtLink>.
        </p>
      </div>
    </div>

    <!-- Additional Info -->
    <div class="auth-info">
      <div class="info-card">
        <Icon name="lucide:shield-check" class="info-icon" />
        <h3 class="info-title">Secure & Private</h3>
        <p class="info-description">
          Your data is encrypted and protected. We never share your personal information.
        </p>
      </div>
      
      <div class="info-card">
        <Icon name="lucide:zap" class="info-icon" />
        <h3 class="info-title">AI-Powered Learning</h3>
        <p class="info-description">
          Advanced AI transforms your content into interactive educational experiences.
        </p>
      </div>
      
      <div class="info-card">
        <Icon name="lucide:users" class="info-icon" />
        <h3 class="info-title">Trusted by Educators</h3>
        <p class="info-description">
          Join thousands of educators already using AI to enhance their teaching.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Set page meta
definePageMeta({
  layout: 'auth'
})

// Auth handling
const handleAuthSuccess = (user: any) => {
  console.log('Authentication successful:', user)
  // Redirect to chat page after successful login
  navigateTo('/chat')
}

const handleAuthError = (error: any) => {
  console.error('Authentication failed:', error)
  // You could show a toast/notification here
}

// SEO
useHead({
  title: 'Sign In - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Sign in to Digi Setu AI - Transform static content into interactive learning experiences with AI' },
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

@media (min-width: 1024px) {
  .auth-container {
    grid-template-columns: 1fr 1fr;
    padding: 4rem;
  }
}

.auth-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 480px;
  margin: 0 auto;
  width: 100%;
}

.auth-header {
  text-align: center;
  margin-bottom: 3rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: var(--accent-primary);
}

.brand-name {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.auth-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.auth-form {
  background: var(--bg-primary);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-lg);
  margin-bottom: 2rem;
}

.form-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
  text-align: center;
}

.form-description {
  color: var(--text-secondary);
  text-align: center;
  margin: 0 0 2rem 0;
  font-size: 0.95rem;
}

.sign-in-section {
  margin-bottom: 1.5rem;
}

.divider {
  position: relative;
  margin: 1.5rem 0;
  text-align: center;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border-primary);
}

.divider-text {
  background: var(--bg-primary);
  padding: 0 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.email-section {
  margin-bottom: 1rem;
}

.email-notice {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
  text-align: center;
}

.auth-footer {
  text-align: center;
}

.legal-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.legal-link {
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 500;
}

.legal-link:hover {
  text-decoration: underline;
}

.auth-info {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  justify-content: center;
}

@media (min-width: 1024px) {
  .auth-info {
    padding-left: 2rem;
  }
}

.info-card {
  text-align: center;
  padding: 1.5rem;
  background: var(--bg-primary);
  border-radius: 0.75rem;
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
}

.info-icon {
  width: 2rem;
  height: 2rem;
  color: var(--accent-primary);
  margin-bottom: 1rem;
}

.info-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.info-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

/* Dark theme adjustments */
[data-theme="dark"] .auth-container {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
}
</style>
