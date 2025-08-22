<template>
  <div class="demo-conversation">
    <div class="demo-message user-message">
      <div class="message-avatar">
        <Icon name="lucide:user" />
      </div>
      <div class="message-content">
        I want to teach world history in a more engaging way. Can you help?
      </div>
    </div>

    <div class="demo-message ai-message">
      <div class="message-avatar ai-avatar">
        <Icon name="lucide:graduation-cap" />
      </div>
      <div class="message-content">
        Absolutely! I'll create an interactive timeline and immersive content to bring history to life:
        
        <div class="demo-widget">
          <div class="widget-header">
            <Icon name="lucide:clock" class="widget-icon" />
            <span class="widget-title">World War II Timeline</span>
          </div>
          <div class="interactive-diagram">
            <div class="process-step active" data-step="1">
              <div class="step-dot"></div>
              <span>War Begins (1939)</span>
            </div>
            <div class="process-step" data-step="2">
              <div class="step-dot"></div>
              <span>Pearl Harbor (1941)</span>
            </div>
            <div class="process-step" data-step="3">
              <div class="step-dot"></div>
              <span>D-Day Landing (1944)</span>
            </div>
            <div class="process-step" data-step="4">
              <div class="step-dot"></div>
              <span>War Ends (1945)</span>
            </div>
          </div>
          <div class="widget-stats">
            <div class="stat">
              <span class="stat-value">89%</span>
              <span class="stat-label">Retention Rate</span>
            </div>
            <div class="stat">
              <span class="stat-value">4.6★</span>
              <span class="stat-label">Engagement</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component animations
onMounted(() => {
  // Animate process steps
  const steps = document.querySelectorAll('.process-step')
  let currentStep = 0
  
  const animateSteps = () => {
    steps.forEach(step => step.classList.remove('active'))
    if (steps[currentStep]) {
      steps[currentStep]?.classList.add('active')
    }
    currentStep = (currentStep + 1) % steps.length
  }
  
  // Start animation
  if (steps.length > 0) {
    animateSteps()
    setInterval(animateSteps, 2000)
  }
})
</script>

<style scoped>
.demo-conversation {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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
  display: flex;
  align-items: center;
  justify-content: center;
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
</style>
