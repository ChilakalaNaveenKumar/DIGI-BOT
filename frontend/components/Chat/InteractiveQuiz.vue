<template>
  <div class="interactive-quiz-container">
    <!-- Quiz Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
          <HelpCircle class="w-5 h-5 text-green-600 dark:text-green-400" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ quiz.title }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ quiz.questions?.length || 0 }} questions • Interactive Learning
          </p>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <UBadge 
          :color="isCompleted ? 'green' : 'blue'" 
          variant="soft"
        >
          {{ currentQuestionIndex + 1 }} / {{ quiz.questions?.length || 0 }}
        </UBadge>
        <UButton 
          @click="resetQuiz" 
          size="sm" 
          variant="ghost"
          icon="i-lucide-rotate-ccw"
        />
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
        <span class="text-sm text-gray-600 dark:text-gray-400">
          {{ Math.round(progress) }}% Complete
        </span>
      </div>
      <UProgress 
        :value="progress" 
        :color="isCompleted ? 'green' : 'blue'"
        size="sm"
        class="transition-all duration-500"
      />
    </div>

    <!-- Quiz Content -->
    <div v-if="!isCompleted" class="space-y-6">
      <!-- Current Question -->
      <div class="question-card">
        <div class="flex items-start space-x-3 mb-4">
          <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
            {{ currentQuestionIndex + 1 }}
          </div>
          <div class="flex-1">
            <h4 class="text-lg font-medium text-gray-900 dark:text-white leading-relaxed">
              {{ currentQuestion.question }}
            </h4>
          </div>
        </div>

        <!-- Answer Options -->
        <div class="space-y-3">
          <button
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            @click="selectAnswer(index)"
            :disabled="hasAnswered"
            class="w-full text-left p-4 rounded-xl border-2 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
            :class="{
              'border-blue-300 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-600': selectedAnswer === index && !hasAnswered,
              'border-green-300 bg-green-50 dark:bg-green-900/20 dark:border-green-600': hasAnswered && index === currentQuestion.correct,
              'border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-600': hasAnswered && selectedAnswer === index && index !== currentQuestion.correct,
              'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600': selectedAnswer !== index && !hasAnswered,
              'opacity-50': hasAnswered && index !== currentQuestion.correct && selectedAnswer !== index
            }"
          >
            <div class="flex items-center space-x-3">
              <div 
                class="w-6 h-6 rounded-full border-2 flex items-center justify-center text-sm font-bold transition-colors"
                :class="{
                  'border-blue-500 bg-blue-500 text-white': selectedAnswer === index && !hasAnswered,
                  'border-green-500 bg-green-500 text-white': hasAnswered && index === currentQuestion.correct,
                  'border-red-500 bg-red-500 text-white': hasAnswered && selectedAnswer === index && index !== currentQuestion.correct,
                  'border-gray-300 dark:border-gray-600': selectedAnswer !== index && !hasAnswered
                }"
              >
                <Check v-if="hasAnswered && index === currentQuestion.correct" class="w-3 h-3" />
                <X v-else-if="hasAnswered && selectedAnswer === index && index !== currentQuestion.correct" class="w-3 h-3" />
                <span v-else>{{ String.fromCharCode(65 + index) }}</span>
              </div>
              <span class="text-gray-900 dark:text-white">{{ option }}</span>
            </div>
          </button>
        </div>

        <!-- Explanation -->
        <div 
          v-if="hasAnswered && currentQuestion.explanation" 
          class="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-600 animate-fade-in"
        >
          <div class="flex items-start space-x-2">
            <Lightbulb class="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
            <div>
              <h5 class="font-medium text-gray-900 dark:text-white mb-1">Explanation</h5>
              <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                {{ currentQuestion.explanation }}
              </p>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex items-center justify-between mt-6">
          <UButton 
            @click="previousQuestion"
            :disabled="currentQuestionIndex === 0"
            variant="outline"
            size="sm"
            icon="i-lucide-chevron-left"
          >
            Previous
          </UButton>
          
          <UButton 
            v-if="hasAnswered"
            @click="nextQuestion"
            color="blue"
            size="sm"
            :icon="isLastQuestion ? 'i-lucide-flag' : 'i-lucide-chevron-right'"
            :trailing="!isLastQuestion"
          >
            {{ isLastQuestion ? 'Finish Quiz' : 'Next Question' }}
          </UButton>
        </div>
      </div>
    </div>

    <!-- Quiz Results -->
    <div v-else class="quiz-results">
      <div class="text-center py-8">
        <div class="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <Trophy class="w-10 h-10 text-green-600 dark:text-green-400" />
        </div>
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Quiz Completed! 🎉
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          You scored {{ correctAnswers }} out of {{ quiz.questions.length }} questions
        </p>
        
        <!-- Score Display -->
        <div class="max-w-sm mx-auto mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Your Score</span>
            <span class="text-sm text-gray-600 dark:text-gray-400">{{ scorePercentage }}%</span>
          </div>
          <UProgress 
            :value="scorePercentage" 
            :color="scorePercentage >= 80 ? 'green' : scorePercentage >= 60 ? 'yellow' : 'red'"
            size="lg"
          />
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-center space-x-3">
          <UButton @click="resetQuiz" variant="outline" icon="i-lucide-rotate-ccw">
            Retake Quiz
          </UButton>
          <UButton @click="exportResults" color="green" icon="i-lucide-download">
            Export Results
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { HelpCircle, Check, X, Lightbulb, Trophy } from 'lucide-vue-next'

const props = defineProps({
  quiz: {
    type: Object,
    required: true,
    default: () => ({
      title: 'Interactive Quiz',
      questions: []
    })
  }
})

// Quiz state
const currentQuestionIndex = ref(0)
const selectedAnswer = ref(null)
const hasAnswered = ref(false)
const answers = ref([])

// Computed properties
const currentQuestion = computed(() => {
  return props.quiz.questions?.[currentQuestionIndex.value] || {}
})

const isLastQuestion = computed(() => {
  return currentQuestionIndex.value === (props.quiz.questions?.length || 0) - 1
})

const isCompleted = computed(() => {
  return answers.value.length === (props.quiz.questions?.length || 0)
})

const correctAnswers = computed(() => {
  return answers.value.filter((answer, index) => 
    answer === props.quiz.questions[index].correct
  ).length
})

const scorePercentage = computed(() => {
  if (!props.quiz.questions?.length) return 0
  return Math.round((correctAnswers.value / props.quiz.questions.length) * 100)
})

const progress = computed(() => {
  if (!props.quiz.questions?.length) return 0
  return (answers.value.length / props.quiz.questions.length) * 100
})

// Quiz actions
const selectAnswer = (answerIndex) => {
  if (hasAnswered.value) return
  
  selectedAnswer.value = answerIndex
  hasAnswered.value = true
  
  // Store answer
  answers.value[currentQuestionIndex.value] = answerIndex
}

const nextQuestion = () => {
  if (isLastQuestion.value) {
    // Quiz completed
    return
  }
  
  currentQuestionIndex.value++
  selectedAnswer.value = answers.value[currentQuestionIndex.value] ?? null
  hasAnswered.value = answers.value[currentQuestionIndex.value] !== undefined
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    selectedAnswer.value = answers.value[currentQuestionIndex.value] ?? null
    hasAnswered.value = answers.value[currentQuestionIndex.value] !== undefined
  }
}

const resetQuiz = () => {
  currentQuestionIndex.value = 0
  selectedAnswer.value = null
  hasAnswered.value = false
  answers.value = []
}

const exportResults = () => {
  const results = {
    quiz: props.quiz.title,
    timestamp: new Date().toISOString(),
    score: `${correctAnswers.value}/${props.quiz.questions.length}`,
    percentage: scorePercentage.value,
    answers: props.quiz.questions.map((question, index) => ({
      question: question.question,
      selectedAnswer: question.options[answers.value[index]],
      correctAnswer: question.options[question.correct],
      isCorrect: answers.value[index] === question.correct
    }))
  }
  
  const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `quiz-results-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.interactive-quiz-container {
  background-color: white;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.interactive-quiz-container:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dark .interactive-quiz-container {
  background-color: #1f2937;
  border-color: #374151;
}

.question-card {
  background-color: rgba(249, 250, 251, 0.5);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid rgba(229, 231, 235, 0.5);
}

.dark .question-card {
  background-color: rgba(55, 65, 81, 0.3);
  border-color: rgba(75, 85, 99, 0.5);
}

.quiz-results {
  background: linear-gradient(to bottom right, #f0fdf4, #eff6ff);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid rgba(34, 197, 94, 0.5);
}

.dark .quiz-results {
  background: linear-gradient(to bottom right, rgba(20, 83, 45, 0.1), rgba(30, 58, 138, 0.1));
  border-color: rgba(34, 197, 94, 0.3);
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
