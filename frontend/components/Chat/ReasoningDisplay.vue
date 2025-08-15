<template>
  <div class="reasoning-container">
    <!-- Reasoning Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2">
          <div class="relative">
            <Brain class="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <div class="absolute -top-1 -right-1 w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
          </div>
          <h3 class="text-sm font-semibold text-blue-700 dark:text-blue-300">
            AI Reasoning Process
          </h3>
        </div>
        <UBadge 
          v-if="state === 'streaming'" 
          color="purple" 
          variant="soft" 
          size="xs"
          class="animate-pulse"
        >
          Thinking...
        </UBadge>
        <UBadge 
          v-else-if="isToolExecuting" 
          color="blue" 
          variant="soft" 
          size="xs"
          class="animate-pulse"
        >
          <Loader2 class="w-3 h-3 mr-1 animate-spin" />
          Executing Tool
        </UBadge>
        <UBadge 
          v-else-if="state === 'done'" 
          color="green" 
          variant="soft" 
          size="xs"
        >
          Complete
        </UBadge>
      </div>
      
      <button 
        @click="toggleExpanded"
        class="p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        :title="isExpanded ? 'Collapse reasoning' : 'Expand reasoning'"
      >
        <ChevronDown 
          class="w-4 h-4 transition-transform duration-200"
          :class="{ 'rotate-180': isExpanded }"
        />
      </button>
    </div>

    <!-- Reasoning Content -->
    <UCollapsible v-model="isExpanded">
      <div class="space-y-3">
        <!-- Reasoning Steps -->
        <div 
          v-for="(step, index) in reasoningSteps" 
          :key="index"
          class="reasoning-step group"
          :class="{
            'opacity-50': step.status === 'pending',
            'animate-pulse': step.status === 'streaming'
          }"
        >
          <div class="flex items-start space-x-3">
            <!-- Step Indicator -->
            <div class="flex-shrink-0 mt-1">
              <div 
                class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium transition-all duration-200"
                :class="{
                  'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400': step.status === 'pending',
                  'bg-blue-500 text-white animate-spin': step.status === 'streaming',
                  'bg-green-500 text-white': step.status === 'completed'
                }"
              >
                <Loader2 v-if="step.status === 'streaming'" class="w-3 h-3" />
                <Check v-else-if="step.status === 'completed'" class="w-3 h-3" />
                <span v-else>{{ index + 1 }}</span>
              </div>
            </div>
            
            <!-- Step Content -->
            <div class="flex-1 min-w-0">
                              <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                <div class="text-sm text-purple-800 dark:text-purple-200 leading-relaxed">
                  <MarkdownRenderer 
                    :content="step.content" 
                    class="reasoning-markdown"
                  />
                </div>
                
                <!-- Step Metadata -->
                <div v-if="step.metadata" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div class="flex items-center space-x-4 text-xs text-gray-600 dark:text-gray-400">
                    <span v-if="step.metadata.duration">
                      <Clock class="w-3 h-3 inline mr-1" />
                      {{ step.metadata.duration }}ms
                    </span>
                    <span v-if="step.metadata.tokens">
                      <Hash class="w-3 h-3 inline mr-1" />
                      {{ step.metadata.tokens }} tokens
                    </span>
                    <span v-if="step.metadata.confidence">
                      <TrendingUp class="w-3 h-3 inline mr-1" />
                      {{ Math.round(step.metadata.confidence * 100) }}% confidence
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Current Thinking (Live Stream) -->
        <div 
          v-if="currentThinking && state === 'streaming'" 
          class="reasoning-step animate-fade-in"
        >
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0 mt-1">
              <div 
                class="w-6 h-6 rounded-full flex items-center justify-center animate-spin"
                :class="isToolExecuting ? 'bg-blue-500' : 'bg-purple-500'"
              >
                <Loader2 class="w-3 h-3 text-white" />
              </div>
            </div>
            <div class="flex-1">
              <div 
                class="rounded-xl p-4 border"
                :class="isToolExecuting 
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700' 
                  : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'"
              >
                <div 
                  class="text-sm leading-relaxed flex items-center"
                  :class="isToolExecuting 
                    ? 'text-blue-800 dark:text-blue-200' 
                    : 'text-purple-800 dark:text-purple-200'"
                >
                  <!-- Tool execution icon -->
                  <div v-if="isToolExecuting" class="mr-2">
                    <div class="w-4 h-4 bg-blue-500 rounded animate-pulse"></div>
                  </div>
                  {{ currentThinking }}
                  <span class="animate-pulse ml-1">|</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </UCollapsible>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { 
  Brain, ChevronDown, Loader2, Check, Clock, Hash, TrendingUp 
} from 'lucide-vue-next'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps({
  reasoning: {
    type: Array,
    default: () => []
  },
  state: {
    type: String,
    default: 'done' // 'streaming' | 'done' | 'error'
  },
  currentThinking: {
    type: String,
    default: ''
  },
  initialExpanded: {
    type: Boolean,
    default: false
  }
})

const isExpanded = ref(props.initialExpanded)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

// Detect tool execution states
const isToolExecuting = computed(() => {
  return props.currentThinking && (
    props.currentThinking.includes('Generating') ||
    props.currentThinking.includes('Executing') ||
    props.currentThinking.includes('Creating') ||
    props.currentThinking.includes('Preparing tools')
  )
})

// Process reasoning into steps
const reasoningSteps = computed(() => {
  if (!props.reasoning || props.reasoning.length === 0) return []
  
  return props.reasoning.map((reasoningPart, index) => {
    // Parse reasoning text into structured steps
    const content = reasoningPart.text || reasoningPart
    const lines = content.split('\n').filter(line => line.trim())
    
    return {
      id: `step-${index}`,
      content: content,
      status: reasoningPart.state || 'completed',
      metadata: {
        duration: Math.random() * 1000 + 200, // Simulated for demo
        tokens: content.length / 4, // Rough token estimate
        confidence: 0.85 + Math.random() * 0.15 // Simulated confidence
      }
    }
  })
})

// Auto-expand when reasoning starts
watch(() => props.state, (newState) => {
  if (newState === 'streaming' && reasoningSteps.value.length > 0) {
    isExpanded.value = true
  }
})
</script>

<style scoped>
.reasoning-container {
  background: linear-gradient(135deg, #f3e8ff 0%, #dbeafe 100%);
  border: 1px solid #e9d5ff;
  border-radius: 1rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.dark .reasoning-container {
  background: linear-gradient(135deg, #581c87 0%, #1e3a8a 100%);
  border-color: #7c3aed;
}

.reasoning-step {
  transition: all 0.3s;
}

.reasoning-markdown {
  max-width: none;
  font-size: 0.875rem;
  line-height: 1.5;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
