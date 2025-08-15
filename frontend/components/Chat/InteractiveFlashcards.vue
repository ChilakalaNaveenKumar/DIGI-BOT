<template>
  <div class="interactive-flashcards-container">
    <!-- Flashcards Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
          <BookOpen class="w-5 h-5 text-orange-600 dark:text-orange-400" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ flashcards.title }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ flashcards.cards?.length || 0 }} flashcards • Interactive Learning
          </p>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <UBadge 
          :color="studyMode ? 'green' : 'blue'" 
          variant="soft"
        >
          {{ studyMode ? 'Study Mode' : 'Review Mode' }}
        </UBadge>
        <UButton 
          @click="toggleStudyMode" 
          size="sm" 
          variant="ghost"
          :icon="studyMode ? 'i-lucide-eye' : 'i-lucide-brain'"
        />
      </div>
    </div>

    <!-- Progress -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
        <span class="text-sm text-gray-600 dark:text-gray-400">
          {{ currentCardIndex + 1 }} / {{ flashcards.cards?.length || 0 }}
        </span>
      </div>
      <UProgress 
        :value="progressPercentage" 
        color="orange"
        size="sm"
      />
    </div>

    <!-- Flashcard Display -->
    <div v-if="currentCard" class="flashcard-area">
      <div 
        class="flashcard"
        :class="{ 'flipped': isFlipped }"
        @click="flipCard"
      >
        <!-- Front Side -->
        <div class="flashcard-side flashcard-front">
          <div class="flex items-center justify-center h-full p-8">
            <div class="text-center">
              <div class="text-sm text-orange-600 dark:text-orange-400 mb-4 font-medium">
                {{ currentCard.category || 'Flashcard' }}
              </div>
              <div class="text-xl font-semibold text-gray-900 dark:text-white leading-relaxed">
                {{ currentCard.front }}
              </div>
              <div class="mt-6 text-sm text-gray-500 dark:text-gray-400">
                Click to reveal answer
              </div>
            </div>
          </div>
        </div>

        <!-- Back Side -->
        <div class="flashcard-side flashcard-back">
          <div class="flex items-center justify-center h-full p-8">
            <div class="text-center">
              <div class="text-sm text-green-600 dark:text-green-400 mb-4 font-medium">
                Answer
              </div>
              <div class="text-lg text-gray-900 dark:text-white leading-relaxed">
                {{ currentCard.back }}
              </div>
              
              <!-- Study Mode Actions -->
              <div v-if="studyMode && isFlipped" class="mt-6 flex items-center justify-center space-x-3">
                <UButton 
                  @click.stop="markDifficult"
                  color="red" 
                  variant="soft" 
                  size="sm"
                  icon="i-lucide-x"
                >
                  Difficult
                </UButton>
                <UButton 
                  @click.stop="markEasy"
                  color="green" 
                  variant="soft" 
                  size="sm"
                  icon="i-lucide-check"
                >
                  Easy
                </UButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="flex items-center justify-between mt-6">
      <UButton 
        @click="previousCard"
        :disabled="currentCardIndex === 0"
        variant="outline"
        size="sm"
        icon="i-lucide-chevron-left"
      >
        Previous
      </UButton>
      
      <div class="flex items-center space-x-3">
        <UButton 
          @click="shuffleCards"
          variant="ghost"
          size="sm"
          icon="i-lucide-shuffle"
        >
          Shuffle
        </UButton>
        
        <UButton 
          @click="resetProgress"
          variant="ghost"
          size="sm"
          icon="i-lucide-rotate-ccw"
        >
          Reset
        </UButton>
      </div>
      
      <UButton 
        @click="nextCard"
        :disabled="currentCardIndex === (flashcards.cards?.length || 0) - 1"
        variant="outline"
        size="sm"
        icon="i-lucide-chevron-right"
        trailing
      >
        Next
      </UButton>
    </div>

    <!-- Study Statistics -->
    <div v-if="studyMode && studyStats.total > 0" class="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-600">
      <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Study Session Stats</h4>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <div class="text-lg font-bold text-green-600 dark:text-green-400">{{ studyStats.easy }}</div>
          <div class="text-xs text-gray-600 dark:text-gray-400">Easy</div>
        </div>
        <div>
          <div class="text-lg font-bold text-red-600 dark:text-red-400">{{ studyStats.difficult }}</div>
          <div class="text-xs text-gray-600 dark:text-gray-400">Difficult</div>
        </div>
        <div>
          <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ studyStats.total }}</div>
          <div class="text-xs text-gray-600 dark:text-gray-400">Total</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { BookOpen } from 'lucide-vue-next'

const props = defineProps({
  flashcards: {
    type: Object,
    required: true,
    default: () => ({
      title: 'Interactive Flashcards',
      cards: []
    })
  }
})

// Flashcard state
const currentCardIndex = ref(0)
const isFlipped = ref(false)
const studyMode = ref(false)
const studyResults = ref([])

// Computed properties
const currentCard = computed(() => {
  return props.flashcards.cards?.[currentCardIndex.value] || null
})

const progressPercentage = computed(() => {
  if (!props.flashcards.cards?.length) return 0
  return ((currentCardIndex.value + 1) / props.flashcards.cards.length) * 100
})

const studyStats = computed(() => {
  return {
    total: studyResults.value.length,
    easy: studyResults.value.filter(r => r.difficulty === 'easy').length,
    difficult: studyResults.value.filter(r => r.difficulty === 'difficult').length
  }
})

// Flashcard actions
const flipCard = () => {
  isFlipped.value = !isFlipped.value
}

const nextCard = () => {
  if (currentCardIndex.value < (props.flashcards.cards?.length || 0) - 1) {
    currentCardIndex.value++
    isFlipped.value = false
  }
}

const previousCard = () => {
  if (currentCardIndex.value > 0) {
    currentCardIndex.value--
    isFlipped.value = false
  }
}

const toggleStudyMode = () => {
  studyMode.value = !studyMode.value
  if (!studyMode.value) {
    studyResults.value = []
  }
}

const markEasy = () => {
  if (studyMode.value && currentCard.value) {
    studyResults.value.push({
      cardIndex: currentCardIndex.value,
      difficulty: 'easy',
      timestamp: new Date().toISOString()
    })
    nextCard()
  }
}

const markDifficult = () => {
  if (studyMode.value && currentCard.value) {
    studyResults.value.push({
      cardIndex: currentCardIndex.value,
      difficulty: 'difficult',
      timestamp: new Date().toISOString()
    })
    nextCard()
  }
}

const shuffleCards = () => {
  // Simple shuffle implementation
  currentCardIndex.value = Math.floor(Math.random() * (props.flashcards.cards?.length || 1))
  isFlipped.value = false
}

const resetProgress = () => {
  currentCardIndex.value = 0
  isFlipped.value = false
  studyResults.value = []
}
</script>

<style scoped>
.interactive-flashcards-container {
  background-color: white;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.interactive-flashcards-container:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dark .interactive-flashcards-container {
  background-color: #1f2937;
  border-color: #374151;
}

.flashcard-area {
  position: relative;
  height: 20rem;
  perspective: 1000px;
}

.flashcard {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
  transform-style: preserve-3d;
  transition: transform 0.7s;
}

.flashcard.flipped {
  transform: rotateY(180deg);
}

.flashcard-side {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 1rem;
  border: 2px solid;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.flashcard-front {
  background: linear-gradient(to bottom right, #fef3c7, #fde68a);
  border-color: #f59e0b;
}

.dark .flashcard-front {
  background: linear-gradient(to bottom right, rgba(180, 83, 9, 0.2), rgba(217, 119, 6, 0.2));
  border-color: #f59e0b;
}

.flashcard-back {
  background: linear-gradient(to bottom right, #d1fae5, #a7f3d0);
  border-color: #10b981;
  transform: rotateY(180deg);
}

.dark .flashcard-back {
  background: linear-gradient(to bottom right, rgba(6, 78, 59, 0.2), rgba(4, 120, 87, 0.2));
  border-color: #10b981;
}

/* Custom Tailwind utilities */
.perspective-1000 {
  perspective: 1000px;
}

.transform-style-preserve-3d {
  transform-style: preserve-3d;
}

.backface-hidden {
  backface-visibility: hidden;
}

.rotate-y-180 {
  transform: rotateY(180deg);
}
</style>
