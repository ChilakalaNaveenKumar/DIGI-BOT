<template>
  <div class="legal-container">
    <div class="legal-content">
      <!-- Header -->
      <div class="legal-header">
        <NuxtLink to="/auth/signin" class="back-link">
          <Icon name="lucide:arrow-left" class="back-icon" />
          Back to Sign In
        </NuxtLink>
        <h1 class="legal-title">Privacy Policy</h1>
        <p class="legal-subtitle">
          Last updated: {{ lastUpdated }}
        </p>
      </div>

      <!-- Content -->
      <div class="legal-body">
        <section class="legal-section">
          <h2>1. Information We Collect</h2>
          
          <h3>Personal Information</h3>
          <p>When you create an account, we collect:</p>
          <ul>
            <li>Name and email address (from Google OAuth)</li>
            <li>Profile picture (if provided by Google)</li>
            <li>Account preferences and settings</li>
          </ul>

          <h3>Content Data</h3>
          <p>When you use our Service, we collect:</p>
          <ul>
            <li>Educational content you upload or input</li>
            <li>AI-generated transformations and enhancements</li>
            <li>Usage patterns and interaction data</li>
          </ul>

          <h3>Technical Information</h3>
          <p>We automatically collect:</p>
          <ul>
            <li>IP address and device information</li>
            <li>Browser type and version</li>
            <li>Usage analytics and performance metrics</li>
            <li>Error logs and diagnostic data</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>2. How We Use Your Information</h2>
          <p>We use your information to:</p>
          <ul>
            <li><strong>Provide the Service:</strong> Process your content with AI and deliver enhanced learning materials</li>
            <li><strong>Account Management:</strong> Maintain your account and provide customer support</li>
            <li><strong>Service Improvement:</strong> Analyze usage patterns to improve our AI models and features</li>
            <li><strong>Communication:</strong> Send important updates about your account and the Service</li>
            <li><strong>Legal Compliance:</strong> Meet legal obligations and protect our rights</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>3. AI Processing and Third Parties</h2>
          <p>
            Our Service uses third-party AI providers to process your content:
          </p>
          <ul>
            <li><strong>OpenAI:</strong> For content analysis and generation</li>
            <li><strong>Anthropic (Claude):</strong> For advanced content transformation</li>
            <li><strong>Google AI:</strong> For additional processing capabilities</li>
          </ul>
          <p>
            These providers may process your content according to their own privacy policies. We ensure all providers meet enterprise-grade security standards.
          </p>
        </section>

        <section class="legal-section">
          <h2>4. Data Security</h2>
          <p>We implement industry-standard security measures:</p>
          <ul>
            <li>Encryption in transit and at rest</li>
            <li>Regular security audits and monitoring</li>
            <li>Access controls and authentication</li>
            <li>Secure cloud infrastructure (AWS/Google Cloud)</li>
            <li>Regular backups and disaster recovery</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>5. Data Retention</h2>
          <p>We retain your data as follows:</p>
          <ul>
            <li><strong>Account Data:</strong> Until you delete your account</li>
            <li><strong>Content Data:</strong> Until you delete specific content or your account</li>
            <li><strong>Usage Analytics:</strong> Up to 2 years for service improvement</li>
            <li><strong>Legal Requirements:</strong> As required by applicable law</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>6. Your Rights and Choices</h2>
          <p>You have the right to:</p>
          <ul>
            <li><strong>Access:</strong> Request a copy of your personal data</li>
            <li><strong>Correction:</strong> Update or correct your information</li>
            <li><strong>Deletion:</strong> Request deletion of your account and data</li>
            <li><strong>Portability:</strong> Export your content and data</li>
            <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
          </ul>
          <p>
            To exercise these rights, contact us at 
            <a href="mailto:privacy@digisetu.ai" class="inline-link">privacy@digisetu.ai</a>
          </p>
        </section>

        <section class="legal-section">
          <h2>7. Cookies and Tracking</h2>
          <p>We use cookies and similar technologies for:</p>
          <ul>
            <li>Authentication and session management</li>
            <li>User preferences and settings</li>
            <li>Analytics and performance monitoring</li>
            <li>Security and fraud prevention</li>
          </ul>
          <p>
            You can control cookies through your browser settings. See our 
            <NuxtLink to="/legal/cookies" class="inline-link">Cookie Policy</NuxtLink> 
            for more details.
          </p>
        </section>

        <section class="legal-section">
          <h2>8. International Data Transfers</h2>
          <p>
            Your data may be processed in countries other than your own. We ensure appropriate safeguards are in place for international transfers, including:
          </p>
          <ul>
            <li>Standard Contractual Clauses (SCCs)</li>
            <li>Adequacy decisions by relevant authorities</li>
            <li>Certification under recognized frameworks</li>
          </ul>
        </section>

        <section class="legal-section">
          <h2>9. Children's Privacy</h2>
          <p>
            Our Service is not intended for children under 13 years old. We do not knowingly collect personal information from children under 13. If you believe we have collected such information, please contact us immediately.
          </p>
        </section>

        <section class="legal-section">
          <h2>10. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify you of significant changes via email or through the Service. Your continued use after changes indicates acceptance of the updated policy.
          </p>
        </section>

        <section class="legal-section">
          <h2>11. Contact Us</h2>
          <p>
            For privacy-related questions or requests, contact us at:
          </p>
          <div class="contact-info">
            <p><strong>Email:</strong> privacy@digisetu.ai</p>
            <p><strong>Data Protection Officer:</strong> dpo@digisetu.ai</p>
            <p><strong>Address:</strong> [Your Company Address]</p>
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
  title: 'Privacy Policy - Digi Setu AI',
  meta: [
    { name: 'description', content: 'Privacy Policy for Digi Setu AI - How we collect, use, and protect your data' },
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

.legal-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 1.5rem 0 0.75rem 0;
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

.inline-link {
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 500;
}

.inline-link:hover {
  text-decoration: underline;
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
  
  .legal-section h3 {
    font-size: 1.125rem;
  }
}
</style>
