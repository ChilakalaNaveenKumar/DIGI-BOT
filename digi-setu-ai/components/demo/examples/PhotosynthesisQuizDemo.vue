<template>
  <div class="demo-conversation">
    <div class="demo-message user-message">
      <div class="message-avatar">
        <Icon name="lucide:user" />
      </div>
      <div class="message-content">
        Can you also create a quiz to test their understanding?
      </div>
    </div>

    <div class="demo-message ai-message">
      <div class="message-avatar ai-avatar">
        <Icon name="lucide:graduation-cap" />
      </div>
      <div class="message-content">
        Absolutely! Here's an adaptive quiz that adjusts to each student's learning pace:

        <div class="demo-widget quiz-widget">
          <div class="widget-header">
            <Icon name="lucide:brain" class="widget-icon" />
            <span class="widget-title">Adaptive Knowledge Check</span>
          </div>
          <div class="quiz-question">
            <p class="question-text">What is the primary function of chlorophyll in photosynthesis?</p>
            <div class="quiz-options">
              <div class="quiz-option correct" data-correct="true">
                <span class="option-letter">A</span>
                <span class="option-text">Absorb light energy</span>
                <Icon name="lucide:check" class="option-check" />
              </div>
              <div class="quiz-option" data-correct="false">
                <span class="option-letter">B</span>
                <span class="option-text">Store glucose</span>
              </div>
              <div class="quiz-option" data-correct="false">
                <span class="option-letter">C</span>
                <span class="option-text">Release oxygen</span>
              </div>
            </div>
          </div>
          <div class="quiz-progress">
            <div class="progress-bar">
              <div class="progress-fill" style="width: 67%"></div>
            </div>
            <span class="progress-text">Question 2 of 3</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component animations and interactions
onMounted(() => {
  // Add quiz click handlers
  const quizOptions = document.querySelectorAll('.quiz-option')
  quizOptions.forEach(option => {
    option.addEventListener('click', () => handleQuizClick(option))
  })
})

const handleQuizClick = (option) => {
  const isCorrect = option.dataset.correct === 'true'
  const allOptions = option.parentElement.querySelectorAll('.quiz-option')
  
  // Disable all options
  allOptions.forEach(opt => opt.style.pointerEvents = 'none')
  
  if (isCorrect) {
    // Correct answer animation
    option.classList.add('selected-correct')
    option.style.transform = 'scale(1.02)'
    option.style.background = 'rgba(34, 197, 94, 0.1)'
    option.style.borderColor = '#22c55e'
    
    // Show checkmark
    const checkIcon = option.querySelector('.option-check')
    if (checkIcon) {
      checkIcon.style.opacity = '1'
    }
  } else {
    // Wrong answer animation
    option.classList.add('selected-wrong')
    option.style.animation = 'shake 0.5s ease-in-out'
    option.style.background = 'rgba(239, 68, 68, 0.1)'
    option.style.borderColor = '#ef4444'
    
    // Show correct answer after delay
    setTimeout(() => {
      const correctOption = option.parentElement.querySelector('.correct')
      if (correctOption) {
        correctOption.style.background = 'rgba(34, 197, 94, 0.1)'
        correctOption.style.borderColor = '#22c55e'
        const checkIcon = correctOption.querySelector('.option-check')
        if (checkIcon) {
          checkIcon.style.opacity = '1'
        }
      }
    }, 1000)
  }
}
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
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  width: 100%;
  height: 100%;
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
</style>
