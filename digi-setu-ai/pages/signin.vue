<template>
  <div class="landing-container">
    <!-- Left Panel - Sign In -->
    <div class="auth-panel">
      <div class="auth-content">
        <!-- Brand Header -->
        <div class="brand-header">
          <div class="brand-logo">
            <Icon name="lucide:graduation-cap" class="logo-icon" />
            <span class="brand-name">Digi Setu AI</span>
          </div>
        </div>

        <!-- Main Content -->
        <div class="auth-main">
          <div class="hero-section">
            <h1 class="hero-title">Transform Learning<br />Into Experience.</h1>
            <p class="hero-subtitle">The AI that turns static content into interactive educational journeys</p>
          </div>

          <!-- Sign In Form -->
          <div class="signin-form">
            <GoogleSignInButton 
              @auth-success="handleAuthSuccess" 
              @auth-error="handleAuthError" 
            />
            
            <div class="divider">
              <span class="divider-text">OR</span>
            </div>

            <input 
              type="email" 
              placeholder="Enter your personal or work email"
              class="email-input"
              v-model="email"
            />
            
            <button class="continue-btn" :disabled="!email">
              Continue with email
            </button>

            <p class="legal-notice">
              By continuing, you acknowledge our 
              <NuxtLink to="/legal/privacy" class="legal-link">Privacy Policy</NuxtLink> 
              and agree to get occasional product updates.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel - Interactive Demo -->
    <div class="demo-panel">
      <div class="demo-content">
                <!-- Demo Messages -->
        <div ref="messagesContainer" class="demo-messages">
          <!-- Dynamic component rendering -->
          <component 
            :is="currentDemoComponent" 
            :key="currentDemoIndex"
            class="demo-component-wrapper"
          />
        </div>

          <!-- Demo Indicators -->
         <div class="demo-indicators">
           <div 
             v-for="(_, index) in demoComponents" 
             :key="index"
             class="indicator" 
             :class="{ active: currentDemoIndex === index }"
           />
         </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Explicit component imports
import PhotosynthesisDemo from '~/components/demo/examples/PhotosynthesisDemo.vue'
import PhotosynthesisQuizDemo from '~/components/demo/examples/PhotosynthesisQuizDemo.vue'
import FractionsDemo from '~/components/demo/examples/FractionsDemo.vue'
import FractionsQuizDemo from '~/components/demo/examples/FractionsQuizDemo.vue'
import HistoryDemo from '~/components/demo/examples/HistoryDemo.vue'
import HistoryQuizDemo from '~/components/demo/examples/HistoryQuizDemo.vue'

// Set page meta
definePageMeta({
  layout: 'auth'
})

// Reactive data
const email = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const currentDemoIndex = ref(0)
const isAnimating = ref(false)

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
    { name: 'description', content: 'Sign in to Digi Setu AI - The AI that turns static content into interactive educational journeys.' },
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

// Demo components array - these will cycle through
const demoComponents = [
  PhotosynthesisDemo,
  PhotosynthesisQuizDemo, 
  FractionsDemo,
  FractionsQuizDemo,
  HistoryDemo,
  HistoryQuizDemo
]

// Current demo component computed property
const currentDemoComponent = computed(() => {
  return demoComponents[currentDemoIndex.value]
})

// Start the demo cycle
onMounted(() => {
  startDemoAnimation()
})

const startDemoAnimation = async () => {
  // Auto-scroll through demo components every 6 seconds
  setInterval(async () => {
    if (!isAnimating.value) {
      await switchToNextDemo()
    }
  }, 6000)
}

const switchToNextDemo = async () => {
  if (isAnimating.value) return
  
  isAnimating.value = true
  
  // Fade out current demo
  if (messagesContainer.value) {
    messagesContainer.value.style.opacity = '0'
    messagesContainer.value.style.transform = 'translateY(20px)'
    await new Promise(resolve => setTimeout(resolve, 300))
  }
  
  // Switch to next component
  currentDemoIndex.value = (currentDemoIndex.value + 1) % demoComponents.length
  
  // Fade in new demo
  if (messagesContainer.value) {
    messagesContainer.value.style.transition = 'all 0.5s ease'
    messagesContainer.value.style.opacity = '1'
    messagesContainer.value.style.transform = 'translateY(0)'
  }
  
  // Reset animation flag
  setTimeout(() => {
    isAnimating.value = false
  }, 500)
}
</script>

<style scoped>
.landing-container {
  min-height: 100vh;
  display: flex;
  background: var(--bg-primary);
}

/* Left Panel - Auth */
.auth-panel {
  flex: 1;
  max-width: 50%;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-content {
  width: 100%;
  max-width: 480px;
}

.brand-header {
  margin-bottom: 3rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 2rem;
  height: 2rem;
  color: var(--accent-primary);
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.hero-section {
  margin-bottom: 2.5rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
  margin: 0 0 1rem 0;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.signin-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.divider {
  position: relative;
  text-align: center;
  margin: 1rem 0;
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

.email-input {
  padding: 0.875rem 1rem;
  border: 1px solid var(--border-primary);
  border-radius: 0.5rem;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.email-input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.email-input::placeholder {
  color: var(--text-muted);
}

.continue-btn {
  padding: 0.875rem 1rem;
  background: var(--text-primary);
  color: var(--bg-primary);
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.continue-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.continue-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.legal-notice {
  font-size: 0.875rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0.5rem 0 0 0;
}

.legal-link {
  color: var(--text-secondary);
  text-decoration: underline;
}

/* Right Panel - Demo */
.demo-panel {
  flex: 1;
  max-width: 50%;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  padding: 2rem;
  overflow-y: auto;
}

.demo-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.demo-messages {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
  transition: all 0.5s ease;
}

.demo-component-wrapper {
  width: 100%;
}

.demo-message {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.message-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
}

.ai-avatar {
  background: var(--accent-primary);
  color: white;
  border: none;
}

.message-content {
  background: var(--bg-primary);
  padding: 1rem;
  border-radius: 1rem;
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--text-primary);
}

.user-message .message-content {
  background: var(--accent-primary);
  color: white;
  border: none;
}

.demo-widget {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 0.75rem;
  padding: 1rem;
  margin-top: 1rem;
}

.widget-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.widget-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--accent-primary);
}

.widget-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.interactive-diagram {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.process-step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.process-step.active {
  background: rgba(255, 107, 53, 0.1);
}

.step-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  background: var(--border-primary);
  transition: all 0.3s ease;
}

.process-step.active .step-dot {
  background: var(--accent-primary);
}

.process-step span {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.process-step.active span {
  color: var(--text-primary);
  font-weight: 500;
}

.widget-stats {
  display: flex;
  gap: 1rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-weight: 700;
  color: var(--accent-primary);
  font-size: 1.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.quiz-widget {
  background: var(--bg-secondary);
}

.quiz-question {
  margin-bottom: 1rem;
}

.question-text {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quiz-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border: 1px solid var(--border-primary);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.quiz-option:hover {
  background: var(--bg-hover);
}

.quiz-option.correct {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
}

.option-letter {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-primary);
}

.quiz-option.correct .option-letter {
  background: #22c55e;
  color: white;
}

.option-text {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.option-check {
  width: 1rem;
  height: 1rem;
  color: #22c55e;
  margin-left: auto;
}

.quiz-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
}

.progress-bar {
  flex: 1;
  height: 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-primary);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.demo-indicators {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.indicator {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: var(--border-primary);
  transition: all 0.3s ease;
}

.indicator.active {
  background: var(--accent-primary);
}

/* Quiz interaction animations */
.quiz-option {
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.quiz-option:hover {
  background: var(--bg-hover);
  transform: translateY(-1px);
}

.quiz-option .option-feedback {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-weight: bold;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.quiz-option.selected-correct .option-feedback,
.quiz-option.selected-wrong .option-feedback,
.quiz-option.highlight-correct .option-feedback {
  opacity: 1;
}

.quiz-option.selected-correct {
  animation: success-pulse 0.6s ease;
}

.quiz-option.highlight-correct {
  animation: highlight-correct 0.8s ease;
}

/* Shake animation for wrong answers */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* Success pulse animation */
@keyframes success-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

/* Highlight correct answer animation */
@keyframes highlight-correct {
  0% { 
    transform: scale(1);
    box-shadow: none;
  }
  50% { 
    transform: scale(1.01);
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
  }
  100% { 
    transform: scale(1);
    box-shadow: 0 0 10px rgba(34, 197, 94, 0.2);
  }
}

/* Message animation improvements */
.demo-message {
  animation: messageSlideIn 0.3s ease;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  color: var(--text-muted);
  font-style: italic;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
}

.typing-dot {
  width: 0.5rem;
  height: 0.5rem;
  background: var(--text-muted);
  border-radius: 50%;
  animation: typingDot 1.4s infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingDot {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  30% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Widget icons */
.widget-icon {
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Responsive */
@media (max-width: 1024px) {
  .landing-container {
    flex-direction: column;
  }
  
  .auth-panel,
  .demo-panel {
    max-width: 100%;
  }
  
  .demo-panel {
    display: none; /* Hide demo on mobile */
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .auth-panel {
    padding: 1rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
}
</style>
