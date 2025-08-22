<template>
  <div class="legal-page">
    <div class="legal-container">
      <div class="legal-header">
        <NuxtLink to="/signin" class="back-link">
          <Icon name="lucide:arrow-left" />
          Back to Sign In
        </NuxtLink>
        <h1 class="legal-title">Terms of Service</h1>
        <p class="legal-subtitle">Last updated: January 2024</p>
      </div>

      <div class="legal-content">
        <section class="legal-section">
          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing and using Digi Setu AI ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
          </p>
        </section>

        <section class="legal-section">
          <h2>2. Description of Service</h2>
          <p>
            Digi Setu AI is an artificial intelligence platform that transforms static educational content into interactive learning experiences. The service provides AI-powered tools for creating engaging educational materials, quizzes, and interactive content.
          </p>
        </section>

        <section class="legal-section">
          <h2>3. User Accounts</h2>
          <p>
            To access certain features of the Service, you may be required to create an account. You are responsible for:
          </p>
          <ul>
            <li>Maintaining the confidentiality of your account credentials</li>
            <li>All activities that occur under your account</li>
            <li>Providing accurate and complete information</li>
            <li>Promptly updating your account information</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>4. Acceptable Use</h2>
          <p>You agree not to use the Service to:</p>
          <ul>
            <li>Violate any applicable laws or regulations</li>
            <li>Infringe on intellectual property rights</li>
            <li>Upload malicious code or content</li>
            <li>Attempt to gain unauthorized access to our systems</li>
            <li>Use the service for commercial purposes without permission</li>
            <li>Create content that is harmful, offensive, or inappropriate</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>5. Content and Intellectual Property</h2>
          <p>
            You retain ownership of the content you create using our Service. However, by using the Service, you grant us a limited license to process, store, and display your content as necessary to provide the Service.
          </p>
          <p>
            Our Service, including all software, text, images, and other content, is protected by copyright and other intellectual property laws.
          </p>
        </section>

        <section class="legal-section">
          <h2>6. Privacy and Data Protection</h2>
          <p>
            Your privacy is important to us. Please review our <NuxtLink to="/legal/privacy" class="legal-link">Privacy Policy</NuxtLink>, which also governs your use of the Service, to understand our practices.
          </p>
        </section>

        <section class="legal-section">
          <h2>7. Subscription and Payment</h2>
          <p>
            Some features of the Service may require a paid subscription. By subscribing, you agree to pay all applicable fees. Subscription fees are non-refundable except as required by law.
          </p>
        </section>

        <section class="legal-section">
          <h2>8. Service Availability</h2>
          <p>
            We strive to maintain high availability of our Service, but we do not guarantee uninterrupted access. We may temporarily suspend or restrict access for maintenance, updates, or other operational reasons.
          </p>
        </section>

        <section class="legal-section">
          <h2>9. Limitation of Liability</h2>
          <p>
            To the maximum extent permitted by law, Digi Setu AI shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses.
          </p>
        </section>

        <section class="legal-section">
          <h2>10. Termination</h2>
          <p>
            We may terminate or suspend your account and access to the Service immediately, without prior notice, if you breach these Terms of Service. Upon termination, your right to use the Service will cease immediately.
          </p>
        </section>

        <section class="legal-section">
          <h2>11. Changes to Terms</h2>
          <p>
            We reserve the right to modify these terms at any time. We will notify users of any material changes via email or through the Service. Your continued use of the Service after such modifications constitutes acceptance of the updated terms.
          </p>
        </section>

        <section class="legal-section">
          <h2>12. Governing Law</h2>
          <p>
            These Terms shall be interpreted and governed by the laws of [Your Jurisdiction], without regard to its conflict of law provisions.
          </p>
        </section>

        <section class="legal-section">
          <h2>13. Contact Information</h2>
          <p>
            If you have any questions about these Terms of Service, please contact us at:
          </p>
          <div class="contact-info">
            <p>Email: legal@digisetu.ai</p>
            <p>Address: [Your Business Address]</p>
          </div>
        </section>

        <section class="legal-section">
          <h2>14. Severability</h2>
          <p>
            If any provision of these Terms is found to be unenforceable or invalid, that provision will be limited or eliminated to the minimum extent necessary so that the Terms will otherwise remain in full force and effect.
          </p>
        </section>

        <section class="legal-section">
          <h2>15. Entire Agreement</h2>
          <p>
            These Terms constitute the entire agreement between you and Digi Setu AI regarding the use of the Service and supersede all prior agreements and understandings.
          </p>
        </section>
      </div>

      <div class="legal-footer">
        <p>
          By using Digi Setu AI, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
        </p>
        <div class="legal-actions">
          <NuxtLink to="/signin" class="btn-primary">
            I Agree - Continue to Sign In
          </NuxtLink>
        </div>
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
  title: 'Terms of Service - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Terms of Service for Digi Setu AI - AI-powered educational content platform.' }
  ]
})
</script>

<style scoped>
.legal-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 2rem;
}

.legal-container {
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg-primary);
}

.legal-header {
  margin-bottom: 3rem;
  text-align: center;
  position: relative;
}

.back-link {
  position: absolute;
  left: 0;
  top: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.back-link:hover {
  color: var(--accent-primary);
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

.legal-content {
  margin-bottom: 3rem;
}

.legal-section {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border-primary);
}

.legal-section:last-child {
  border-bottom: none;
}

.legal-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
}

.legal-section p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.legal-section p:last-child {
  margin-bottom: 0;
}

.legal-section ul {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.legal-section li {
  margin-bottom: 0.5rem;
}

.legal-link {
  color: var(--accent-primary);
  text-decoration: underline;
}

.legal-link:hover {
  opacity: 0.8;
}

.contact-info {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.contact-info p {
  margin: 0.5rem 0;
  font-family: monospace;
  font-size: 0.9rem;
}

.legal-footer {
  text-align: center;
  padding-top: 2rem;
  border-top: 2px solid var(--border-primary);
}

.legal-footer p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.legal-actions {
  display: flex;
  justify-content: center;
}

.btn-primary {
  display: inline-block;
  padding: 1rem 2rem;
  background: var(--accent-primary);
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* Responsive */
@media (max-width: 768px) {
  .legal-page {
    padding: 1rem;
  }
  
  .legal-header {
    margin-bottom: 2rem;
  }
  
  .back-link {
    position: static;
    justify-content: center;
    margin-bottom: 1rem;
  }
  
  .legal-title {
    font-size: 2rem;
  }
  
  .legal-section {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
  }
  
  .legal-section h2 {
    font-size: 1.25rem;
  }
}
</style>
